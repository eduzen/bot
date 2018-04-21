import sys
from peewee import SqliteDatabase

from models import User, Question
from config import DB_PATH


def create_db_tables():
    if not DB_PATH.exists():
        db = SqliteDatabase(str(DB_PATH))
        with db:
            db.create_tables([User, Question])


if __name__ == '__main__':
    sys.exit(create_db_tables())
