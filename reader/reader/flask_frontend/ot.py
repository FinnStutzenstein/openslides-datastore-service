import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.metrics_exporter import OTLPMetricsExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export.controller import PushController
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor


docker_id = os.environ.get("DOCKER_ID")  # TODO: env service
resource = Resource.create({
    "service.name": "datastore_reader",
    "service.instance.id": docker_id
})

tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
span_exporter = OTLPSpanExporter(endpoint="otel-collector:55680")
#span_processor = SimpleExportSpanProcessor(span_exporter)
span_processor = BatchExportSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)

tracer = tracer_provider.get_tracer(__name__)
#with tracer.start_as_current_span("foo"):
#    print("Hello world!")

Psycopg2Instrumentor().instrument()

meter_provider = MeterProvider(resource=resource)
metrics.set_meter_provider(meter_provider)
metric_exporter = OTLPMetricsExporter(endpoint="otel-collector:55680") # 55681 ??
meter = meter_provider.get_meter(__name__)
meter_provider.start_pipeline(meter, metric_exporter, 5)
#controller = PushController(meter, metric_exporter, 5)
