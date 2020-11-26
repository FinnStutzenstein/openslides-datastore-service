from shared import create_base_application
from writer.flask_frontend import FlaskFrontend
from shared.opentelemetry import setup as setup_opentelemetry
from .services import register_services

def create_application():
    setup_opentelemetry("datastore_writer")
    register_services()
    return create_base_application(FlaskFrontend)


application = create_application()
