from concurrent import futures

from common.v1 import common_pb2_grpc
import grpc
from grpc_reflection.v1alpha import reflection

from models.app import Config
from server.router.service_router import CommonServiceRouter


def init_grpc(config: Config):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  router = CommonServiceRouter()
  common_pb2_grpc.add_CommonServiceServicer_to_server(router, server)

  SERVICE_NAMES = (
      'common.v1.CommonService',
      reflection.SERVICE_NAME,
  )
  reflection.enable_server_reflection(SERVICE_NAMES, server)

  server.add_insecure_port(f"{config.service.grpc_host}:{config.service.grpc_port}")
  print('grpc server is running on 50051')
  server.start()

  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    print("Shutting down gRPC server...")
    router.config.shutdown()
    server.stop(0)
