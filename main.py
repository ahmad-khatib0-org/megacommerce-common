from server.load.config import load_all_config, load_service_config
from server.load.db import init_db
from server.load.grpc import init_grpc


def serve():
  all_config = load_all_config()
  service_config = load_service_config()

  init_db(all_config.sql)
  init_grpc(service_config)


if __name__ == "__main__":
  serve()
