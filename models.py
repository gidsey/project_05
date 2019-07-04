"""Journal models."""

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

import datetime

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    """Define the User model."""

    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        """Define the DB."""

        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        """Create the user."""
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")


class Entries(Model):
    """Define the Entry model."""

    username = ForeignKeyField(User, related_name='entries')
    title = CharField(max_length=255)
    date = DateField()
    timeSpent = IntegerField()
    whatILearned = TextField()
    resourcesToRemember = TextField()

    class Meta:
        """Define the DB."""

        database = DATABASE


def initalize():
    """Initialize the DB."""
    DATABASE.connect()
    DATABASE.create_tables([User, Entries], safe=True)
    DATABASE.close()
