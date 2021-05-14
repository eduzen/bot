import pytest
from playhouse.sqlite_ext import SqliteExtDatabase

from eduzen_bot.models import EventLog, User

from .factories import EventFactory, UserFactory

MODELS = [User, EventLog]


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    db = SqliteExtDatabase(":memory:")
    db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    db.create_tables(MODELS)
    users = UserFactory.create_batch(2)
    EventFactory.create_batch(2, command="btc", user=users[0])
    yield db
    db.close()
