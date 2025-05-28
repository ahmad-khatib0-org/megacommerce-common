from server.load.config import load_config
from utils.db import DatabasePool


def serve():
  # DatabasePool.initialize()
  config = load_config()


if __name__ == "__main__":
  serve()
