from common.v1 import common_pb2_grpc, types_pb2
from models.app import Config
from server.config.config_manager import ConfigManager
from server.trans.trans_manager import TransManager


class CommonServiceRouter(common_pb2_grpc.CommonServiceServicer):
  def __init__(self, service_config: Config) -> None:
    self.config = ConfigManager(service_config)
    self.trans = TransManager()

  def Ping(self, request, context):
    return types_pb2.PingResponse()

  def ConfigGet(self, request, context):
    return self.config.get_config()

  def ConfigUpdate(self, request, context):
    return self.config.update_config(request.comfig)

  def ConfigListener(self, request, context):
    return self.config.listen_config(request.client_id)

  def TranslationsGet(self, request, context):
    return self.trans.get_translations()

  def TranslationsForLangGet(self, request, context):
    return self.trans.get_translation_for_lang(request.lang)
