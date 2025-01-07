import sys

import logfire

from eduzenbot.models import EventLog, Question, Report, User, db


@db.connection_context()
def create_db_tables():
    User.create_table()
    Question.create_table()
    EventLog.create_table()
    Report.create_table()
    logfire.info("Tables created!")


if __name__ == "__main__":
    sys.exit(create_db_tables())
