from concurrent import futures

from common.v1 import common_pb2_grpc, common_pb2
import grpc
from grpc_reflection.v1alpha import reflection

from models.app import Config
from server.router.service_router import CommonServiceRouter


def init_grpc(config: Config):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  router = CommonServiceRouter()
  common_pb2_grpc.add_CommonServiceServicer_to_server(router, server)

  SERVICE_NAMES = (
      common_pb2.DESCRIPTOR.services_by_name['CommonService'].full_name,
      reflection.SERVICE_NAME,
  )
  reflection.enable_server_reflection(SERVICE_NAMES, server)

  target = f"{config.service.grpc_host}:{config.service.grpc_port}"
  server.add_insecure_port(target)
  print(f"grpc server is running on: {target}")
  server.start()

  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    print("Shutting down gRPC server...")
    router.config.shutdown()
    server.stop(0)
