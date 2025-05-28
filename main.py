from concurrent import futures

from common.v1 import common_pb2_grpc
import grpc
from grpc_reflection.v1alpha import reflection

from server.load.config import load_config
from server.load.db import init_db
from server.router.service_router import CommonServiceRouter


def serve():
  config = load_config()
  init_db(config.sql)

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  common_pb2_grpc.add_CommonServiceServicer_to_server(CommonServiceRouter(), server)

  SERVICE_NAMES = (
      'common.v1.CommonService',
      reflection.SERVICE_NAME,
  )
  reflection.enable_server_reflection(SERVICE_NAMES, server)

  server.add_insecure_port('[::]:50051')
  print('grpc server is running on 50051')
  server.start()
  server.wait_for_termination()


if __name__ == "__main__":
  serve()
