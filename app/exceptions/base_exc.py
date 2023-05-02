from typing import Any, List

from flask import jsonify


def template(data, code=500, error_code=None):
    return {"errors": data, "error_code": error_code, "status_code": code}


USER_NOT_FOUND = template(["User not found"], code=404)
WRONG_LOGIN_CREDS = template(["Username or password are not correct"], code=404)
USER_ALREADY_REGISTERED = template(["User already registered"], code=422)
UNKNOWN_ERROR = template(["Something wrong happened"], code=500)
USER_NOT_AUTHORIZED = template(["Unauthorized access"], code=401)
EMPTY_MISSING_FILE = template(["File is empty or not uploaded correctly"], code=400)
SIZE_LIMIT_EXCEEDED = template(["File size is larger than 1MB"], code=400)
UNSUPPORTED_FORMAT = template(["Unsupported file format"], code=415)
INVALID_SEARCH_PARAMS = template("No data available to fit your search", code=404)


class InvalidUsage(Exception):
    status_code = 500
    data: List[Any] = None
    exception: Exception

    def __init__(
        self,
        errors,
        status_code=None,
        payload=None,
        error_code=None,
        data: List[Any] = None,
        exception: Exception = None,
        *args
    ):
        Exception.__init__(self)
        self.data = data
        self.errors = errors
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.error_code = error_code
        exc = [arg for arg in args if isinstance(arg, Exception)] + [None]
        self.exception = exc[0] or exception

    def to_json(self):
        if self.exception:
            self.save_to_database()
        return jsonify(self.to_dict()), self.status_code

    def to_dict(self):
        if self.exception:
            self.save_to_database()
        return {
            "errors": self.errors,
            "errorCode": self.error_code,
            **({"data": self.data} if self.data else {}),
        }

    def save_to_database(self):
        from app.database import db
        from app.exceptions.error_handler import ErrorHandler
        from app.models import ErrorLogging

        err = ErrorHandler(
            self.exception, logger=self.__class__.__name__, msg="\n".join(self.errors)
        )
        logged_error = ErrorLogging(
            trace=err.trace, level=err.level, logger=err.logger, msg=err.msg
        )
        db.session.add(logged_error)
        db.session.commit()

    @classmethod
    def custom_error(cls, message, code=500, **kwargs):
        return cls(**template([message], code), **kwargs)

    @classmethod
    def user_not_found(cls, **kwargs):
        return cls(**USER_NOT_FOUND, **kwargs)

    @classmethod
    def user_already_registered(cls, **kwargs):
        return cls(**USER_ALREADY_REGISTERED, **kwargs)

    @classmethod
    def user_not_authorized(cls, **kwargs):
        return cls(**USER_NOT_AUTHORIZED, **kwargs)

    @classmethod
    def unknown_error(cls, **kwargs):
        return cls(**UNKNOWN_ERROR, **kwargs)

    @classmethod
    def empty_missing_file(cls, **kwargs):
        return cls(**EMPTY_MISSING_FILE, **kwargs)

    @classmethod
    def wrong_login_creds(cls, **kwargs):
        return cls(**WRONG_LOGIN_CREDS, **kwargs)

    @classmethod
    def unsupported_format(cls, **kwargs):
        return cls(**UNSUPPORTED_FORMAT, **kwargs)

    @classmethod
    def size_limit_exceeded(cls, **kwargs):
        return cls(**SIZE_LIMIT_EXCEEDED, **kwargs)

    @classmethod
    def invalid_search_params(cls, **kwargs):
        return cls(**INVALID_SEARCH_PARAMS, **kwargs)
