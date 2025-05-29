from pydantic import BaseModel


class Service(BaseModel):
  env: str
  grpc_host: str
  grpc_port: int


class Config(BaseModel):
  service: Service
