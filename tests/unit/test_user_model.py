from flask.testing import FlaskClient

from app.models import User

"""
This file (test_models.py) contains the unit tests for the models.py file.
"""


def test_new_user(test_client: FlaskClient):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password_hashed, authenticated, and active fields are defined correctly
    """
    user = User("username", "password")
    assert user.email == "username"
    assert user.password_hashed != "password"
    assert user.__repr__() == "<User: username>"
    assert user.is_authenticated
    assert user.is_active


def test_new_user_with_fixture(new_user: User):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email and password_hashed fields are defined correctly
    """
    assert new_user.email == "username"
    assert new_user.password_hashed != "password"


def test_setting_password(new_user: User):
    """
    GIVEN an existing User
    WHEN the password for the user is set
    THEN check the password is stored correctly and not as plaintext
    """
    new_user.set_password("MyNewPassword")
    assert new_user.password_hashed != "MyNewPassword"
    assert new_user.is_password_correct("MyNewPassword")
    assert not new_user.is_password_correct("MyNewPassword2")
    assert not new_user.is_password_correct("FlaskIsAwesome")


def test_user_id(new_user: User):
    """
    GIVEN an existing User
    WHEN the ID of the user is defined to a value
    THEN check the user ID returns a string (and not an integer) as needed by Flask-WTF
    """
    new_user.id = 17
    assert isinstance(new_user.get_id(), str)
    assert not isinstance(new_user.get_id(), int)
    assert new_user.get_id() == "17"
