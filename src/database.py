from peewee import SqliteDatabase
from config import db_path


db = SqliteDatabase(str(db_path))
