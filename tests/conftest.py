import pytest
from flask.testing import FlaskClient

from app import create_app
from app.config import TestingConfig
from app.database import db
from app.models import User

# --------
# Fixtures
# --------


@pytest.fixture(scope="module")
def test_client():
    # Create a Flask app configured for testing
    flask_app = create_app(TestingConfig)

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope="module")
def new_user(test_client: FlaskClient):
    user = User("username", "password")
    return user


@pytest.fixture(scope="module")
def init_database(test_client: FlaskClient):
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(email="username", password_plaintext="password")
    user2 = User(email="username2", password_plaintext="password")
    db.session.add(user1)
    db.session.add(user2)

    # Commit the changes for the users
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()


@pytest.fixture(scope="function")
def login_default_user(test_client: FlaskClient):
    test_client.post(
        "/login",
        data=dict(email="username", password="password"),
        follow_redirects=True,
    )

    yield  # this is where the testing happens!

    test_client.get("/logout", follow_redirects=True)


@pytest.fixture(scope="module")
def cli_test_client():
    flask_app = create_app()
    flask_app.config.from_object("config.TestingConfig")

    runner = flask_app.test_cli_runner()

    yield runner  # this is where the testing happens!
