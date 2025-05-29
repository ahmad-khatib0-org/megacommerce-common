from queue import Queue
import threading

from common.v1 import common_pb2, common_pb2_grpc
from grpc import StatusCode
import psycopg2
from ulid import ULID

from utils.app_error import AppError
from utils.db import DatabasePool
from utils.time_utils import TimeUtils


class ConfigManager(common_pb2_grpc.CommonServiceServicer):
  def __init__(self) -> None:
    self._lock = threading.Lock()
    self._db = DatabasePool()
    self._current_config = None
    self._listeners = {}
    self._shutdown_event = threading.Event()

  def get_config(self):
    conn = self._db.get_conn()
    try:
      with conn.cursor() as cur:
        cur.execute('SELECT value FROM configurations WHERE active = TRUE')
        row = cur.fetchone()
        if not row:
          sc = StatusCode.NOT_FOUND.value[0]
          error = AppError("common.config.get_config", "common.config.not_found", status_code=sc)
          return common_pb2.ConfigGetResponse(error=error.to_proto)
        config = common_pb2.Config(value=row[0])
        return common_pb2.ConfigGetResponse(data=config)
    except Exception as e:
      sc = StatusCode.INTERNAL.value[0]
      error = AppError(
          "common.config.get_config",
          "common.config.not_found",
          status_code=sc,
          detailed_error=str(e),
      )
      return common_pb2.ConfigGetResponse(error=error.to_proto())
    finally:
      self._db.release_conn(conn)

  def update_config(self, config):
    conn = self._db.get_conn()
    try:
      with self._lock:
        with conn.cursor() as cur:
          cur.execute("UPDATE configuration SET active = NULL WHERE active = TRUE")

          id = str(ULID())
          cur.execute(
              """
              INSERT INTO configuration (id, value, created_at, active)
              VALUES(%s, %s, %s, TRUE)
              """,
              (id, psycopg2.Binary(config.value), TimeUtils.time_in_milies()),
          )
          conn.commit()

          with self._lock:
            for q in self._listeners.values():
              q.put(config)

          return common_pb2.ConfigUpdateResponse(data=config)
    except Exception as e:
      conn.rollback()
      sc = StatusCode.INTERNAL.value[0]
      error = AppError(
          "common.config.get_config",
          "common.config.not_found",
          status_code=sc,
          detailed_error=str(e),
      )
      return common_pb2.ConfigGetResponse(error=error.to_proto())

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
        yield common_pb2.ConfigListenerResponse(data=config)
    finally:
      with self._lock:
        self._listeners.pop(client_id, None)

  def shutdown(self):
    self._shutdown_event.set()
    with self._lock:
      for q in self._listeners.values():
        q.put(None)  # wake all listeners
      self._listeners.clear()
