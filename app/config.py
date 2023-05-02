import os
import re
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import pytz
import redis
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from flask import current_app
from sqlalchemy.pool import NullPool

from app.helpers import (
    MyJSONEncoder,
    date_operations,
    dateformatter,
    extend_string,
    extract_property,
    htmlEscaper,
    htmlgenerator,
)

load_dotenv(".env")


def local_relativedelta(dt: datetime, **kwargs):
    _dt = dt
    for key, val in kwargs.items():
        if val < 0:
            _dt -= relativedelta(**{key: val * -1})
        else:
            _dt += relativedelta(**{key: val})

    return _dt


def get_now():
    return datetime.now().astimezone(current_app.config["TZ"])


def get_now_sql():
    return str(datetime.now().astimezone(current_app.config["TZ"]))


def is_even(num: int) -> bool:
    return num // 2 == 0


redis_pattern = re.compile(r".*\/\/:(?P<password>.*)@(?P<host>.*):(?P<port>\d*)")


def create_url(creds):
    return "mssql+pyodbc:///?odbc_connect=" + quote_plus(
        "DRIVER={ODBC Driver "
        + creds["odbc_version"]
        + " for SQL Server};"
        + f"SERVER={creds.get('host', 'localhost')};DATABASE={creds['database']};"
        + f"UID={creds['username']};PWD={creds['password']};MARS_Connection=Yes"
    )


class Config:
    DATABASE_URL = create_url(
        {
            "username": os.getenv("db_username"),
            "password": os.getenv("db_password"),
            "host": os.getenv("db_host"),
            "port": os.getenv("db_port"),
            "database": os.getenv("db_name"),
            "odbc_version": os.getenv("odbc_version"),
        }
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SERVER_NAME = os.getenv("SERVER_NAME", "localhost")
    PORT = int(os.getenv("PORT", "5000"))
    FLASK_DEBUG = bool(int(os.getenv("DASH_DEBUG", os.getenv("FLASK_DEBUG", "1"))))
    FLASK_APP = os.getenv("FLASK_APP")

    SESSION_PERMANENT = True
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = False

    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}

    REDIS_URL = os.getenv("REDIS_URL")
    TZ = pytz.timezone(os.getenv("TZ", "UTC"))

    JSON_ENCODER = MyJSONEncoder

    JINJA_DATE_FORMATTER = dateformatter
    JINJA_HTML_GENERATOR = htmlgenerator
    JINJA_DATE_OPERATIONS = date_operations
    JINJA_DOUBLEQUOTE_ESCAPER = htmlEscaper
    JINJA_EXTEND_STRING = extend_string
    JINJA_RELATIVE_DELTA = local_relativedelta
    JINJA_EXTRACT_PROPERTY = extract_property
    JINJA_IS_EVEN = is_even

    SERVER_NAME = os.getenv("SERVER_NAME", None)

    NOW = get_now
    SQLNOW = get_now_sql

    REDIS_CONNECTION = redis.Redis(
        connection_pool=redis.ConnectionPool(
            host=redis_pattern.match(os.getenv("REDIS_URL")).group("host"),
            port=int(redis_pattern.match(os.getenv("REDIS_URL")).group("port")),
            password=redis_pattern.match(os.getenv("REDIS_URL")).group("password")
            or "",
            db=0,
            connection_class=getattr(
                redis, os.getenv("REDIS_CONN_CLASS", "SSLConnection")
            ),
            **(
                {}
                if not os.getenv("SSL_CERT_REQS")
                else dict(
                    ssl_cert_reqs=os.getenv("SSL_CERT_REQS"),
                )
            ),
        )
    )

    SECRET_KEY = bytes(os.getenv("secret_key"), "utf-8").decode("unicode_escape")

    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(str(os.getenv("PERMANENT_SESSION_LIFETIME", "60")))
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_TYPE = "redis"


class DevConfig(Config):
    SESSION_TYPE = "redis"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProdConfig(Config):
    PGSSLMODE = os.getenv("PGSSLMODE")
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(ProdConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    DATABASE_URL = "sqlite://"


app_config = DevConfig if Config.FLASK_DEBUG else ProdConfig
