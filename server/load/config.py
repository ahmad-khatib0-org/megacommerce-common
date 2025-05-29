from common.v1 import config_pb2
from google.protobuf.json_format import ParseDict
import yaml

from models.app import Config


def load_all_config():
  with open("config_all.yaml", "r") as f:
    data = yaml.safe_load(f)

  config_proto = config_pb2.Config()
  ParseDict(data, config_proto)

  return config_proto


def load_service_config() -> Config:
  with open("config_service.yaml", "r") as f:
    data = yaml.safe_load(f)

  config = Config(**data)
  return config
