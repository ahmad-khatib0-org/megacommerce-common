from queue import Queue
import threading
from typing import Optional, Dict

from common.v1 import common_pb2_grpc, config_pb2
from grpc import StatusCode
from psycopg2 import Binary, DatabaseError
from ulid import ULID

from models.app import Config
from server.config.config_helpers import ConfigHelpers
from utils.app_error import AppError
from utils.db import DatabasePool
from utils.time_utils import TimeUtils


class ConfigManager(common_pb2_grpc.CommonServiceServicer):
  def __init__(self, service_config: Config) -> None:
    self._lock = threading.Lock()
    self._db = DatabasePool()
    self._service_config: Config = service_config
    self._current_config: Dict[str, Optional[config_pb2.Config]] = {}
    self._listeners = {}
    self._shutdown_event = threading.Event()
    self._helpers = ConfigHelpers()
    self._init_config()

  def _init_config(self):
    self._cleanup_config_in_dev_mode()
    try:
      conn = self._db.get_conn()
      with self._lock:
        with conn.cursor() as cur:
          cur.execute("SELECT env, value FROM configurations WHERE active = TRUE")
          rows = cur.fetchall()
          if rows:
            for row in rows:
              env = row[0]
              self._current_config[env] = self._helpers.load_config_from_yaml_bytes(row[1])
            return
          else:
            with open("config_all.yaml", "rb") as f:
              config_bin = f.read()
              config_msg = self._helpers.load_config_from_yaml_bytes(config_bin)

              id = str(ULID())
              env = self._service_config.service.env
              cur.execute(
                  """
                 INSERT INTO configurations (id, env, value, created_at, active)
                 VALUES(%s, %s, %s, %s, TRUE)
                """, (id, env, Binary(config_bin), TimeUtils.time_in_milies()))
              conn.commit()
              self._current_config[env] = config_msg
            # store config
    except DatabaseError as e:
      raise RuntimeError(
          AppError(
              where="common.config._init_config",
              id="failed_to_load_config",
              detailed_error=f"failed to load configurations {str(e)}",
              status_code=StatusCode.INTERNAL.value[0],
          ), )

  def _cleanup_config_in_dev_mode(self):
    if self._service_config.service.env not in ["dev", "local"]:
      return
    conn = self._db.get_conn()
    try:
      with self._lock:
        with conn.cursor() as cur:
          cur.execute("DELETE FROM configurations WHERE env = %s", (self._service_config.service.env,))
          conn.commit()
    except DatabaseError as e:
      conn.rollback()
      raise RuntimeError(
          AppError(
              where="common.config._cleanup_config_in_dev_mode",
              id="failed_to_load_config",
              detailed_error=f"failed to cleanup configurations in dev/local mode {str(e)}",
              status_code=StatusCode.INTERNAL.value[0],
          ))

  def get_config(self, request):
    env = request.env if request.env else 1  # default to DEV
    env_str = self._env_int_to_str(env)
    
    if env_str in self._current_config and self._current_config[env_str] is not None:
      return config_pb2.ConfigGetResponse(data=self._current_config[env_str])
    
    conn = self._db.get_conn()
    try:
      with conn.cursor() as cur:
        cur.execute('SELECT value FROM configurations WHERE env = %s AND active = TRUE', (env_str,))
        row = cur.fetchone()
        if not row:
          sc = StatusCode.NOT_FOUND.value[0]
          error = AppError("common.config.get_config", "common.config.not_found", status_code=sc)
          return config_pb2.ConfigGetResponse(error=error.to_proto())
        data = self._helpers.load_config_from_yaml_bytes(row[0])
        with self._lock:
          self._current_config[env_str] = data
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

  def _env_int_to_str(self, env_int: int) -> str:
    env_map = {0: "local", 1: "dev", 2: "production"}
    return env_map.get(env_int, "dev")

  # TODO: validate the incoming request
  def update_config(self, request):
    env_str = self._env_int_to_str(request.config_env if hasattr(request, 'config_env') else 1)
    config = request.config if hasattr(request, 'config') else request
    
    conn = self._db.get_conn()
    try:
      with self._lock:
        with conn.cursor() as cur:
          cur.execute("UPDATE configurations SET active = NULL WHERE env = %s AND active = TRUE", (env_str,))

          id = str(ULID())
          cur.execute(
              """
              INSERT INTO configurations (id, env, value, created_at, active)
              VALUES(%s, %s, %s, %s, TRUE)
              """,
              (id, env_str, Binary(config.value), TimeUtils.time_in_milies()),
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
