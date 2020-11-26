from typing import Any, Dict, Optional

import redis
import json

from shared.di import service_as_singleton
from shared.services import EnvironmentService, ShutdownService
from shared.opentelemetry import enabled

from opentelemetry import propagators
from opentelemetry.instrumentation.redis import RedisInstrumentor

# TODO: Test this. Add something like a @ensure_connection decorator, that wraps a
# function that uses redis. It should ensure, that there is a connection (create one
# if not) and should retry the operation, if there was some kind of connection error.
# Note: Which one is a connection error?


class ENVIRONMENT_VARIABLES:
    HOST = "MESSAGE_BUS_HOST"
    PORT = "MESSAGE_BUS_PORT"

def set_opentelemetry_header(data: Dict[str, Any], key: str, value: str) -> None:
    if "__opentelemetry" not in data:
        data["__opentelemetry"] = {}
    data["__opentelemetry"][key] = value

@service_as_singleton
class RedisConnectionHandlerService:

    environment: EnvironmentService
    shutdown_service: ShutdownService
    connection: Optional[Any] = None

    propagator: Any = None

    def __init__(self, shutdown_service: ShutdownService):
        if enabled():
            RedisInstrumentor().instrument()
            self.propagator = propagators.get_global_textmap()

        shutdown_service.register(self)

    def ensure_connection(self):
        if not self.connection:
            self.connection = self.get_connection()
        else:
            # todo check if alive
            pass
        return self.connection

    def get_connection(self):
        host = self.environment.get(ENVIRONMENT_VARIABLES.HOST)
        port = int(self.environment.try_get(ENVIRONMENT_VARIABLES.PORT) or 6379)
        return redis.Redis(host=host, port=port)

    def xadd(self, topic: str, fields: Dict[str, str]) -> None:
        if not fields or not topic:
            return
        connection = self.ensure_connection()

        if enabled():
            self.propagator.inject(
                set_opentelemetry_header,
                fields
            )
            if "__opentelemetry" in fields:
                fields["__opentelemetry"] = json.dumps(fields["__opentelemetry"])

        connection.xadd(topic, fields)

    def shutdown(self):
        if self.connection:
            self.connection.close()
            self.connection = None
