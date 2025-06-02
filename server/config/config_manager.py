from queue import Queue
import threading
from typing import Optional

from common.v1 import common_pb2_grpc, config_pb2
from grpc import StatusCode
from psycopg2 import Binary, DatabaseError
from ulid import ULID

from server.config.config_helpers import ConfigHelpers
from utils.app_error import AppError
from utils.db import DatabasePool
from utils.time_utils import TimeUtils


class ConfigManager(common_pb2_grpc.CommonServiceServicer):
  def __init__(self) -> None:
    self._lock = threading.Lock()
    self._db = DatabasePool()
    self._current_config: Optional[config_pb2.Config] = None
    self._listeners = {}
    self._shutdown_event = threading.Event()
    self._helpers = ConfigHelpers()
    self._init_config()

  def _init_config(self):
    try:
      conn = self._db.get_conn()
      with self._lock:
        with conn.cursor() as cur:
          cur.execute("SELECT value FROM configurations WHERE active = TRUE")
          row = cur.fetchone()
          if row:
            self._current_config = self._helpers.load_config_from_yaml_bytes(row[0])
            return
          else:
            with open("config_all.yaml", "rb") as f:
              config_bin = f.read()
              config_msg = self._helpers.load_config_from_yaml_bytes(config_bin)

              id = str(ULID())
              cur.execute(
                  """
                 INSERT INTO configurations (id, value, created_at, active)
                 VALUES(%s, %s, %s, TRUE)
                """, (id, Binary(config_bin), TimeUtils.time_in_milies()))
              conn.commit()
              self._current_config = config_msg
            # store config
    except DatabaseError as e:
      raise RuntimeError(
          AppError(
              where="common.config._init_config",
              id="failed_to_load_config",
              detailed_error=f"failed to load configurations {str(e)}",
              status_code=StatusCode.INTERNAL.value[0],
          ))

  def get_config(self):
    if self._current_config is not None:
      return config_pb2.ConfigGetResponse(data=self._current_config)
    conn = self._db.get_conn()
    try:
      with conn.cursor() as cur:
        cur.execute('SELECT value FROM configurations WHERE active = TRUE')
        row = cur.fetchone()
        if not row:
          sc = StatusCode.NOT_FOUND.value[0]
          error = AppError("common.config.get_config", "common.config.not_found", status_code=sc)
          return config_pb2.ConfigGetResponse(error=error.to_proto())
        data = self._helpers.load_config_from_yaml_bytes(row[0])
        with self._lock:
          self._current_config = data
        return config_pb2.ConfigGetResponse(data=data)
    except Exception as e:
      sc = StatusCode.INTERNAL.value[0]
      error = AppError(
          "common.config.get_config",
          "common.config.not_found",
          status_code=sc,
          detailed_error=str(e),
      )
      return config_pb2.ConfigGetResponse(error=error.to_proto())
    finally:
      self._db.release_conn(conn)

  def update_config(self, config):
    conn = self._db.get_conn()
    try:
      with self._lock:
        with conn.cursor() as cur:
          cur.execute("UPDATE configurations SET active = NULL WHERE active = TRUE")

          # TODO: validate the incoming request
          id = str(ULID())
          cur.execute(
              """
              INSERT INTO configurations (id, value, created_at, active)
              VALUES(%s, %s, %s, TRUE)
              """,
              (id, Binary(config.value), TimeUtils.time_in_milies()),
          )
          conn.commit()

          with self._lock:
            for q in self._listeners.values():
              q.put(config)

          return config_pb2.ConfigUpdateResponse(data=config)
    except Exception as e:
      conn.rollback()
      sc = StatusCode.INTERNAL.value[0]
      error = AppError(
          "common.config.update_config",
          "common.config.update.internal",
          status_code=sc,
          detailed_error=str(e),
      )
      return config_pb2.ConfigGetResponse(error=error.to_proto())

    finally:
      self._db.release_conn(conn)

  def listen_config(self, client_id: str):
    q = Queue()
    with self._lock:
      self._listeners[client_id] = q

    try:
      while not self._shutdown_event.is_set():
        config = q.get()  # Block until update is available
        if config is None:
          break  # graceful shutdown
        yield config_pb2.ConfigListenerResponse(data=config)
    finally:
      with self._lock:
        self._listeners.pop(client_id, None)

  def shutdown(self):
    self._shutdown_event.set()
    with self._lock:
      for q in self._listeners.values():
        q.put(None)  # wake all listeners
      self._listeners.clear()
