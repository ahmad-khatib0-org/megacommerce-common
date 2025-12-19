"""OpenTelemetry initialization for gRPC services."""

import os
import logging

from pythonjsonlogger.json import JsonFormatter

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource


class MetricsCollector:
  """OpenTelemetry metrics collector for Python services."""
  def __init__(self, meter):
    """Initialize metrics collector with a meter."""
    self.meter = meter

    # Config Manager metrics
    self.config_loads_total = meter.create_counter("config_loads_total",
                                                   unit="1",
                                                   description="Total configuration loads")
    self.config_load_errors = meter.create_counter("config_load_errors_total",
                                                   unit="1",
                                                   description="Total configuration load errors")
    self.config_updates_total = meter.create_counter("config_updates_total",
                                                     unit="1",
                                                     description="Total configuration updates")
    self.config_update_errors = meter.create_counter(
        "config_update_errors_total", unit="1", description="Total configuration update errors")
    self.config_load_duration = meter.create_histogram(
        "config_load_duration_seconds",
        unit="s",
        description="Configuration load duration in seconds")
    self.config_update_duration = meter.create_histogram(
        "config_update_duration_seconds",
        unit="s",
        description="Configuration update duration in seconds")

    # Translation Manager metrics
    self.translations_loaded_total = meter.create_counter("translations_loaded_total",
                                                          unit="1",
                                                          description="Total translations loaded")
    self.translation_load_errors = meter.create_counter("translation_load_errors_total",
                                                        unit="1",
                                                        description="Total translation load errors")
    self.translations_fetch_total = meter.create_counter(
        "translations_fetch_total", unit="1", description="Total translation fetch requests")
    self.translations_fetch_errors = meter.create_counter(
        "translations_fetch_errors_total", unit="1", description="Total translation fetch errors")
    self.translation_fetch_duration = meter.create_histogram(
        "translation_fetch_duration_seconds",
        unit="s",
        description="Translation fetch duration in seconds")

    # Database metrics
    self.db_operations_total = meter.create_counter("db_operations_total",
                                                    unit="1",
                                                    description="Total database operations")
    self.db_operation_errors = meter.create_counter("db_operation_errors_total",
                                                    unit="1",
                                                    description="Total database operation errors")
    self.db_operation_duration = meter.create_histogram(
        "db_operation_duration_seconds",
        unit="s",
        description="Database operation duration in seconds")

    # gRPC metrics
    self.grpc_requests_total = meter.create_counter("grpc_requests_total",
                                                    unit="1",
                                                    description="Total gRPC requests")
    self.grpc_request_errors = meter.create_counter("grpc_request_errors_total",
                                                    unit="1",
                                                    description="Total gRPC request errors")
    self.grpc_request_duration = meter.create_histogram(
        "grpc_request_duration_seconds", unit="s", description="gRPC request duration in seconds")

  def record_config_load(self):
    """Record a configuration load event."""
    self.config_loads_total.add(1)

  def record_config_load_error(self):
    """Record a configuration load error."""
    self.config_load_errors.add(1)

  def record_config_update(self):
    """Record a configuration update."""
    self.config_updates_total.add(1)

  def record_config_update_error(self):
    """Record a configuration update error."""
    self.config_update_errors.add(1)

  def observe_config_load_duration(self, duration_secs: float):
    """Record configuration load duration."""
    self.config_load_duration.record(duration_secs)

  def observe_config_update_duration(self, duration_secs: float):
    """Record configuration update duration."""
    self.config_update_duration.record(duration_secs)

  def record_translation_loaded(self):
    """Record a translation loaded event."""
    self.translations_loaded_total.add(1)

  def record_translation_load_error(self):
    """Record a translation load error."""
    self.translation_load_errors.add(1)

  def record_translation_fetch(self):
    """Record a translation fetch request."""
    self.translations_fetch_total.add(1)

  def record_translation_fetch_error(self):
    """Record a translation fetch error."""
    self.translations_fetch_errors.add(1)

  def observe_translation_fetch_duration(self, duration_secs: float):
    """Record translation fetch duration."""
    self.translation_fetch_duration.record(duration_secs)

  def record_db_operation(self):
    """Record a database operation."""
    self.db_operations_total.add(1)

  def record_db_operation_error(self):
    """Record a database operation error."""
    self.db_operation_errors.add(1)

  def observe_db_operation_duration(self, duration_secs: float):
    """Record database operation duration."""
    self.db_operation_duration.record(duration_secs)

  def record_grpc_request(self):
    """Record a gRPC request."""
    self.grpc_requests_total.add(1)

  def record_grpc_request_error(self):
    """Record a gRPC request error."""
    self.grpc_request_errors.add(1)

  def observe_grpc_request_duration(self, duration_secs: float):
    """Record gRPC request duration."""
    self.grpc_request_duration.record(duration_secs)


def init_otel(service_name: str):
  """Initialize OpenTelemetry for Python services."""

  otel_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://otel-collector:4317')

  # Resource
  resource = Resource.create({
      'service.name': service_name,
      'service.version': '0.1.0',
      'deployment.environment': os.getenv('ENV', 'dev'),
  })

  # Tracing
  otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint)
  trace_provider = TracerProvider(resource=resource)
  trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
  trace.set_tracer_provider(trace_provider)

  # Metrics
  metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=otel_endpoint),
                                                export_interval_millis=30000)
  meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
  metrics.set_meter_provider(meter_provider)

  # Create metrics collector
  meter = meter_provider.get_meter("megacommerce", "0.1.0")
  metrics_collector = MetricsCollector(meter)

  # Instrumentors
  GrpcInstrumentorServer().instrument()
  GrpcInstrumentorClient().instrument()
  Psycopg2Instrumentor().instrument()

  return trace_provider, meter_provider, metrics_collector


def setup_json_logging():
  """Setup structured JSON logging."""

  log_handler = logging.StreamHandler()
  formatter = JsonFormatter()
  log_handler.setFormatter(formatter)

  root_logger = logging.getLogger()
  root_logger.addHandler(log_handler)
  root_logger.setLevel(logging.INFO)
