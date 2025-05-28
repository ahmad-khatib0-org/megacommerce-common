from common.v1 import common_pb2, common_pb2_grpc
from config.config_manager import ConfigManager


class CommonServiceRouter(common_pb2_grpc.CommonServiceServicer):
  def __init__(self) -> None:
    self.config = ConfigManager()

  def ConfigGet(self, request, context):
    return self.config.get_config()
