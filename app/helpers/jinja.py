import json
from datetime import date, datetime, timedelta

from dateutil import parser
from flask import render_template_string


def extend_string(val, attr, args=[]):
    if len(args) == 0:
        return getattr(val, attr)()
    else:
        return getattr(val, attr)(*args)


def dateformatter(value, format="iso"):
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d")
    if format == "iso":
        return value.isoformat()
    elif format == "timestamp":
        return value.timestamp()
    else:
        return value.strftime(format)


def extract_property(arr, attr):
    return [getattr(el, attr) for el in arr]


def reqstyler(value):
    if value == "low":
        return "rgb(66, 134, 244)"
    elif value == "medium":
        return "rgb(58, 242, 79)"
    elif value == "high":
        return "rgb(214, 25, 41)"


def htmlEscaper(value):
    if not isinstance(value, str):
        value = json.dumps(value)
    result = ""
    for i in value:
        if i == '"':
            result += "'"
        else:
            result += i
    return result


def htmlgenerator(tag):
    if tag["name"] == "br":
        return "<br>"
    else:
        if isinstance(tag["inner"], list):
            inner = "".join(htmlgenerator(x) for x in tag["inner"])
        else:
            inner = tag["inner"]
        html = render_template_string(
            "<{{tag.name}} {% if 'tag_components' in tag%}{% for key_, value_ "
            + 'in tag.tag_components.items()%} {{key_}}="{{value_}}" {% endfor %}'
            + "{% endif %}>{{inner|safe}}</{{tag.name}}>",
            tag=tag,
            inner=inner,
        )

        return html


def date_operations(dt, operation, **kwargs):
    timedeltas = {
        "days": 0,
        "hours": 0,
        "minutes": 0,
        "seconds": 0,
        "years": 0,
        "months": 0,
    }

    timedeltas.update(**kwargs)

    if operation == "replace":
        return dt.replace(
            year=timedeltas["years"] if timedeltas["years"] != 0 else dt.year,
            month=timedeltas["months"] if timedeltas["months"] != 0 else dt.month,
            day=timedeltas["days"] if timedeltas["days"] != 0 else dt.day,
        )

    if not isinstance(dt, datetime) and not isinstance(dt, date):
        dt = parser.parse(dt)
    time_interval = timedelta(
        days=timedeltas["days"]
        + (timedeltas["years"] * 365)
        + (timedeltas["months"] * 30),
        hours=timedeltas["hours"],
        minutes=timedeltas["minutes"],
        seconds=timedeltas["seconds"],
    )
    if operation == "sub":
        return dt + (time_interval * -1)
    else:
        return dt + (time_interval)
