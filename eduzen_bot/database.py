from peewee import SqliteDatabase

from eduzen_bot.config import DB_PATH


db = SqliteDatabase(str(DB_PATH))
