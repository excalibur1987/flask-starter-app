from flask import Blueprint

bp = Blueprint("hellow", __name__)


@bp.route("/hello-world")
def hello_world():
    return "Hello World"
