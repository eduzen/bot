import unittest

import pytest
from faker import Faker
from playhouse.sqlite_ext import SqliteExtDatabase

from eduzen_bot.models import EventLog, User

MODELS = [User, EventLog]

# use an in-memory SQLite for tests.
tmp_db = SqliteExtDatabase(":memory:")


@pytest.fixture(scope="function")
def db():
    db = SqliteExtDatabase(":memory:")
    db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(MODELS)
    yield db
    db.close()


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.faker = Faker()
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        # breakpoint()
        # tmp_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        # tmp_db.connect()
        # tmp_db.create_tables(MODELS)
        self.user = User.create(
            **{
                "id": 3652654,
                "first_name": "Eduardo",
                "is_bot": False,
                "last_name": "Enriquez",
                "username": "eduzen",
                "language_code": "en",
            }
        )
        self.user_2 = User.create(
            **{
                "id": 3652655,
                "first_name": "Arturo",
                "is_bot": False,
                "last_name": "Enriquez",
                "username": "edu_zen",
                "language_code": "es",
            }
        )
        self.events = []
        for _ in range(5):
            self.events.append(EventLog.create(user=self.user, command="btc"))
            self.events.append(EventLog.create(user=self.user_2, command="btc"))

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        tmp_db.drop_tables(MODELS)

        # Close connection to db.
        tmp_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.
