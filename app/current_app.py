from datetime import datetime
from typing import TYPE_CHECKING, Callable, List, TypedDict

from flask import Flask
from pytz.tzinfo import DstTzInfo

if TYPE_CHECKING:
    from app.config import (
        date_operations,
        dateformatter,
        extend_string,
        extract_property,
        htmlEscaper,
        htmlgenerator,
        is_even,
        local_relativedelta,
    )
    from app.helpers import MyJSONEncoder


class TypedConfig(TypedDict):
    SORTED_MONTHS: List[str]

    TZ: DstTzInfo

    JSON_ENCODER: "MyJSONEncoder"

    JINJA_DATE_FORMATTER: "dateformatter"
    JINJA_HTML_GENERATOR: "htmlgenerator"
    JINJA_DATE_OPERATIONS: "date_operations"
    JINJA_DOUBLEQUOTE_ESCAPER: "htmlEscaper"
    JINJA_EXTEND_STRING: "extend_string"
    JINJA_RELATIVE_DELTA: "local_relativedelta"
    JINJA_EXTRACT_PROPERTY: "extract_property"
    JINJA_IS_EVEN: "is_even"

    NOW: Callable[[], datetime]
    SQL_NOW: Callable[[], str]


class Typed_Flask(Flask):
    config: TypedConfig


current_app: Typed_Flask
