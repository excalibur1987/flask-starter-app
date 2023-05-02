import logging

from flask import Flask

from app.config import app_config

from .commands import register_commands
from .database import db
from .routes import register_routes


def create_app(conf=app_config):
    app = Flask(__name__)
    app.config.from_object(conf)

    db.init_app(app)

    app = register_commands(app)
    app = register_routes(app)

    logging.basicConfig()

    return app
