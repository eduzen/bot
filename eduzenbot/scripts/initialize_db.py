import sys

import logfire
from peewee import BooleanField
from playhouse.migrate import SqliteMigrator, migrate

from eduzenbot.models import EventLog, Question, Report, User, db

migrator = SqliteMigrator(db)


@db.connection_context()
def create_db_tables():
    User.create_table()
    Question.create_table()
    EventLog.create_table()
    Report.create_table()
    logfire.info("Tables created!")


@db.atomic()
def migrate_tables():
    # Define the new columns
    add_show_weather = migrator.add_column("report", "show_weather", BooleanField(default=True))
    add_show_crypto = migrator.add_column("report", "show_crypto", BooleanField(default=True))
    add_show_dollar = migrator.add_column("report", "show_dollar", BooleanField(default=True))
    add_show_news = migrator.add_column("report", "show_news", BooleanField(default=True))
    migrate(
        add_show_weather,
        add_show_crypto,
        add_show_dollar,
        add_show_news,
    )
    logfire.info("Columns added!")


if __name__ == "__main__":
    sys.exit(create_db_tables())
