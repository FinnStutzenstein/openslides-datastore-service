from flask import Flask

from shared.flask_frontend import register_error_handlers

from .routes import URL_PREFIX
from .routes_handler import register_routes


from .ot import tracer
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

class FlaskFrontend:
    @classmethod
    def create_application(cls):
        app = Flask("datastore_reader")
        FlaskInstrumentor().instrument_app(app)
        register_routes(app, URL_PREFIX)
        register_error_handlers(app)
        #with tracer.start_as_current_span("TesT"):
        #    print("HELLO")
        #tracer2 = trace.get_tracer(__name__)
        #with tracer2.start_as_current_span("TesT2"):
        #    print("HELLO2")
        return app
