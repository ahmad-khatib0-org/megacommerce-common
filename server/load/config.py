import yaml
from google.protobuf.json_format import ParseDict
from common.v1 import config_pb2


def load_config():
  with open("config.yaml", "r") as f:
    yamal_data = yaml.safe_load(f)

  config_proto = config_pb2.Config()
  ParseDict(yamal_data, config_proto)

  print(config_proto)

  return config_proto
