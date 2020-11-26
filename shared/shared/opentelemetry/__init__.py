import os
import time
import threading

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
from opentelemetry.instrumentation.flask import FlaskInstrumentor

_tracer = None
_meter = None
_requests_counter = None
_enabled = False

def tracer():
    global _tracer
    return _tracer


def meter():
    global _meter
    return _meter


def requests_counter():
    global _requests_counter
    return _requests_counter

def enabled():
    global _enabled
    return _enabled


class TT(threading.Thread):
    def __init__(self, counter):
        super().__init__()
        self.counter = counter
        self.start()

    def run(self, *args, **kwargs):
        while True:
            print("count tt")
            self.counter.add(1, {"route": "tt"})
            time.sleep(1)

def setup(service_name: str) -> None:
    docker_id = os.environ.get("DOCKER_ID")  # TODO: env service
    resource = Resource.create({
        "service.name": service_name,
        "service.instance.id": docker_id
    })

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    span_exporter = OTLPSpanExporter(endpoint="otel-collector:55680", insecure=True)
    span_processor = BatchExportSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)

    global _tracer
    _tracer = tracer_provider.get_tracer(__name__)
    #with _tracer.start_as_current_span("foo"):
    #    print("Hello world!")

    meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)
    metric_exporter = OTLPMetricsExporter(endpoint="otel-collector:55681", insecure=True) # 55680 ??
    global _meter
    _meter = meter_provider.get_meter(__name__)
    meter_provider.start_pipeline(_meter, metric_exporter, 5)
    #controller = PushController(_meter, metric_exporter, 5)

    global _requests_counter
    _requests_counter = meter().create_counter(
        name="DataStoreRequests",
        description="number of requests",
        unit="1",
        value_type=int,
    )

    """
    tt_counter = meter().create_counter(
        name="tt",
        description="some other counter",
        unit="1",
        value_type=int,
        metric_type=Counter,
    )

    TT(tt_counter)
    """

    global _enabled
    _enabled = True