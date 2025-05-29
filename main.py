from server.load.config import load_config
from server.load.db import init_db
from server.load.grpc import init_grpc


def serve():
  config = load_config()
  init_db(config.sql)
  init_grpc()


if __name__ == "__main__":
  serve()
