import threading
from queue import Queue
from grpc import StatusCode
from common.v1 import common_pb2_grpc, common_pb2

from utils.db import DatabasePool
from utils.app_error import AppError


class ConfigManager(common_pb2_grpc.CommonServiceServicer):
  def __init__(self) -> None:
    self._lock = threading.Lock()
    self._db = DatabasePool()
    self._cond = threading.Condition()
    self._current_config = None

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
