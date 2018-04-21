import sys
from peewee import SqliteDatabase
import structlog

from eduzen_bot.models import User, Question
from eduzen_bot.config import DB_PATH

logger = structlog.get_logger()


def create_db_tables():
    logger.info("Checking database...")
    if not DB_PATH.exists():
        logger.info("Database does not exist...")
        db = SqliteDatabase(str(DB_PATH))
        with db:
            db.create_tables([User, Question])
            logger.info("Tables created!")


if __name__ == "__main__":
    sys.exit(create_db_tables())
