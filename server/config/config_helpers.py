from typing import Union
import yaml
from common.v1 import config_pb2
from google.protobuf.json_format import MessageToDict, ParseDict, ParseError
from utils.app_error import AppError


class ConfigHelpers():
  def load_config_from_yaml_bytes(self, data: Union[bytes, memoryview]) -> config_pb2.Config:
    """Convert YAML bytes to a Config proto message."""

    if isinstance(data, memoryview):
      data = data.tobytes()
    yaml_dict = yaml.safe_load(data.decode())
    return ParseDict(yaml_dict, config_pb2.Config())

  def dump_config_to_yaml_bytes(self, config: config_pb2.Config) -> bytes:
    """Convert Config proto message to YAML binary."""
    config_dict = MessageToDict(config, preserving_proto_field_name=True)
    yaml_str = yaml.safe_dump(config_dict)
    return yaml_str.encode()
