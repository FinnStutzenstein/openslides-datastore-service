from textwrap import dedent

from werkzeug.exceptions import default_exceptions

from shared.util import (
    InvalidFormat,
    ModelDoesNotExist,
    ModelExists,
    ModelLocked,
    ModelNotDeleted,
)


# internal errors


class ERROR_CODES:
    INVALID_FORMAT = 1
    INVALID_REQUEST = 2
    MODEL_DOES_NOT_EXIST = 3
    MODEL_EXISTS = 4
    MODEL_NOT_DELETED = 5
    MODEL_LOCKED = 6


def handle_internal_errors(fn):
    def wrapper(*args, **kwargs):
        error_dict = None
        try:
            return fn(*args, **kwargs)
        except InvalidFormat as e:
            error_dict = {
                "type": ERROR_CODES.INVALID_FORMAT,
                "msg": e.msg,
                "type_verbose": "INVALID_FORMAT",
            }
        except InvalidRequest as e:
            error_dict = {
                "type": ERROR_CODES.INVALID_REQUEST,
                "msg": e.msg,
                "type_verbose": "INVALID_REQUEST",
            }
        except ModelDoesNotExist as e:
            error_dict = {
                "type": ERROR_CODES.MODEL_DOES_NOT_EXIST,
                "fqid": e.fqid,
                "type_verbose": "MODEL_DOES_NOT_EXIST",
            }
        except ModelExists as e:
            error_dict = {
                "type": ERROR_CODES.MODEL_EXISTS,
                "fqid": e.fqid,
                "type_verbose": "MODEL_EXISTS",
            }
        except ModelNotDeleted as e:
            error_dict = {
                "type": ERROR_CODES.MODEL_NOT_DELETED,
                "fqid": e.fqid,
                "type_verbose": "MODEL_NOT_DELETED",
            }
        except ModelLocked as e:
            error_dict = {
                "type": ERROR_CODES.MODEL_LOCKED,
                "key": e.key,
                "type_verbose": "MODEL_LOCKED",
            }
        return {"error": error_dict}, 400

    return wrapper


# http errors


class InvalidRequest(Exception):
    def __init__(self, msg):
        self.msg = msg


def handle_http_error(ex):
    return (
        dedent(
            f"""\
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
        <title>{ex.code} {ex.name}</title>
        <h1>{ex.name}</h1>
        <p><img src="https://http.cat/{ex.code}"></img></p>
        """
        ),
        ex.code,
    )


def register_error_handlers(app):
    # register for all error status codes
    for code in default_exceptions.keys():
        app.register_error_handler(code, handle_http_error)
