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

    username = ForeignKeyField(User, backref='entries')
    title = CharField(max_length=255)
    slug = CharField(max_length=255, unique=True)
    date = DateField()
    timeSpent = IntegerField()
    whatILearned = TextField()
    resourcesToRemember = TextField()

    class Meta:
        """Define the DB."""

        database = DATABASE


class Tag(Model):
    """Define the Tag Model."""

    # def __str__(self):
    #     """Return the tag name."""
    #     return self.tag

    # Typically a foreign key will contain the primary key
    # of the model it relates to.
    tag = CharField(max_length=60, unique=True)

    class Meta:
        """Define the DB (and set the indexes?)."""

        database = DATABASE


class Tagged(Model):
    """Set up the relationsships."""

    entry = ForeignKeyField(User, backref='tags')
    tags = ForeignKeyField(Tag, backref='posts')

    class Meta:
        """Define the DB (and set the indexes?)."""

        database = DATABASE

        indexes = (
            (('entry', 'tags'), True),  # True sets index to unique
        )


def initalize():
    """Initialize the DB."""
    DATABASE.connect()
    DATABASE.create_tables([User, Entries, Tag, Tagged], safe=True)
    DATABASE.close()
