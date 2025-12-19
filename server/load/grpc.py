from concurrent import futures
import time

from common.v1 import common_pb2, common_pb2_grpc
import grpc
from grpc_reflection.v1alpha import reflection

from models.app import Config
from server.router.service_router import CommonServiceRouter
from server.load.otel import init_otel, setup_json_logging


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector():
  """Get the global metrics collector instance."""
  global _metrics_collector
  return _metrics_collector


def init_grpc(config: Config):
  """Initialize gRPC server with OpenTelemetry instrumentation."""
  global _metrics_collector
  
  # Initialize OpenTelemetry
  trace_provider, meter_provider, metrics_collector = init_otel("megacommerce-common")
  _metrics_collector = metrics_collector
  setup_json_logging()

  # Create interceptor for gRPC metrics
  def grpc_metrics_interceptor(continuation, client_call_details):
    """Intercept gRPC calls to record metrics."""
    start_time = time.time()
    try:
      metrics_collector.record_grpc_request()
      response = continuation(client_call_details)
      duration = time.time() - start_time
      metrics_collector.observe_grpc_request_duration(duration)
      return response
    except Exception as e:
      duration = time.time() - start_time
      metrics_collector.record_grpc_request_error()
      metrics_collector.observe_grpc_request_duration(duration)
      raise

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  router = CommonServiceRouter(config)
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
