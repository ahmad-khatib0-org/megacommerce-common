import grpc
from concurrent import futures
from common.v1 import common_pb2_grpc
from grpc_reflection.v1alpha import reflection
from server.router.service_router import CommonServiceRouter


def init_grpc():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  router = CommonServiceRouter()
  common_pb2_grpc.add_CommonServiceServicer_to_server(router, server)

  SERVICE_NAMES = (
      'common.v1.CommonService',
      reflection.SERVICE_NAME,
  )
  reflection.enable_server_reflection(SERVICE_NAMES, server)

  server.add_insecure_port('[::]:50051')
  print('grpc server is running on 50051')
  server.start()

  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    print("Shutting down gRPC server...")
    router.config.shutdown()
    server.stop(0)
