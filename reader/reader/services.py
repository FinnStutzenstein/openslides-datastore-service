from reader.core import setup_di as core_setup_di
from shared.postgresql_backend import setup_di as postgresql_setup_di
from shared.services import setup_di as util_setup_di


def register_services():
    util_setup_di()
    postgresql_setup_di()
    core_setup_di()
