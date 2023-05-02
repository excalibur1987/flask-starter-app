import decimal
from datetime import date, datetime, timedelta
from json import JSONEncoder


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if str(type(obj)) == "<class 'sqlalchemy.util._collections.result'>":
            return obj._asdict()
        if isinstance(obj, decimal.Decimal):
            if obj - int(obj) > 0:
                # Convert decimal instances to strings.
                return str(round(obj, 2))
            else:
                return int(obj)
        if isinstance(obj, datetime) or isinstance(obj, date):
            # Convert Datetime and date objects.
            return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
        if isinstance(obj, timedelta):
            return {"timedelta": obj.total_seconds()}
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, object):
            return dict(
                (key, obj.__dict__[key])
                for key in list(
                    filter(lambda k: not k.startswith("_"), obj.__dict__.keys())
                )
            )

        return super(MyJSONEncoder, self).default(obj)
