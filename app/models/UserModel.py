import sqlalchemy as sa
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db


class User(db.Model):
    """
    Class that represents a user of the application

    The following attributes of a user are stored in this table:
        * email - email address of the user
        * hashed password - hashed password (using werkzeug.security)
        * added_at - date & time that the user added
        * updated_at - date & time that the user added

    REMEMBER: Never store the plaintext password in a database!
    """

    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    email = sa.Column(sa.String, unique=True, nullable=False)
    password_hashed = sa.Column(sa.String(128), nullable=False)
    added_at = sa.Column(sa.DateTime(True), nullable=False)
    updated_at = sa.Column(sa.DateTime(True), nullable=False)

    def __init__(self, email: str, password_plaintext: str):
        """Create a new User object using the email address and hashing the
        plaintext password using Werkzeug.Security.
        """
        self.email = email
        self.password_hashed = self._generate_password_hash(password_plaintext)
        self.added_at = current_app.config["NOW"]()
        self.updated_at = current_app.config["NOW"]()

    def is_password_correct(self, password_plaintext: str):
        return check_password_hash(self.password_hashed, password_plaintext)

    def set_password(self, password_plaintext: str):
        self.password_hashed = self._generate_password_hash(password_plaintext)

    @staticmethod
    def _generate_password_hash(password_plaintext):
        return generate_password_hash(password_plaintext)

    def __repr__(self):
        return f"<User: {self.email}>"

    @property
    def is_authenticated(self):
        """Return True if the user has been successfully registered."""
        return True

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    def get_id(self):
        """Return the user ID as a unicode string (`str`)."""
        return str(self.id)
