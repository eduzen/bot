import pytest
from playhouse.sqlite_ext import SqliteExtDatabase

from eduzenbot.models import EventLog, Report, User

from .factories import EventFactory, UserFactory

MODELS = [User, EventLog, Report]

db = SqliteExtDatabase(":memory:")


def vcr_config() -> dict[str, str]:
    return {
        "filter_headers": ["authorization"],
        "ignore_localhost": True,
        "record_mode": "once",
    }


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> SqliteExtDatabase:
    db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(MODELS)
    users = UserFactory.create_batch(2)
    EventFactory.create_batch(2, command="btc", user=users[0])

    yield db

    db.drop_tables(MODELS)
    db.close()
