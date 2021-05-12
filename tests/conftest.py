import pytest
from playhouse.sqlite_ext import SqliteExtDatabase

from eduzen_bot.models import EventLog, User

from .factories import EventFactory, UserFactory

MODELS = [User, EventLog]


@pytest.fixture(autouse=True)
def db():
    tmp_db = SqliteExtDatabase(":memory:")
    tmp_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    tmp_db.create_tables(MODELS)
    users = UserFactory.create_batch(2)
    EventFactory.create_batch(2, command="btc", user=users[0])
    yield tmp_db
    tmp_db.close()
