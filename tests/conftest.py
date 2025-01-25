import pytest
from playhouse.sqlite_ext import SqliteExtDatabase

from eduzenbot.models import EventLog, Report, User

MODELS = [User, EventLog, Report]

db = SqliteExtDatabase(":memory:")


def vcr_config() -> dict[str, str]:
    return {
        "filter_headers": ["authorization"],
        "ignore_localhost": True,
        "record_mode": "once",
    }


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(MODELS)

    yield db

    db.drop_tables(MODELS)
    db.close()
