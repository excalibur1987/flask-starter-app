from datetime import datetime
from typing import Type

from flask_sqlalchemy import SQLAlchemy, model
from sqlalchemy.sql.schema import MetaData

from .exceptions import InvalidUsage


class ExtendedModel(model.Model):
    def update(self, persist=False, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs.get(key))
        if getattr(self, "updated_at", None):
            self.updated_at = datetime.now()
        if persist:
            db.session.commit()

    def save(self, persist=False):
        try:
            db.session.add(self)
            db.session.flush()
            if persist:
                db.session.commit()
        except Exception:
            raise InvalidUsage.custom_error("Error saving to database", 400)

    def __iter__(self):
        for key in self.__dict__:
            if not key.startswith("_"):
                yield key, getattr(self, key)


class TypedSAL(SQLAlchemy):
    Model: Type[ExtendedModel]


db = TypedSAL(
    model_class=ExtendedModel,
    metadata=MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    ),
)
