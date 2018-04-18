from datetime import datetime

from peewee import (
    Model, SqliteDatabase, ForeignKeyField, DateTimeField, TextField,
    CharField, BooleanField
)
from config import db_path


db = SqliteDatabase(str(db_path))


class BaseModel(Model):

    class Meta:
        database = db


class User(BaseModel):
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(unique=True)
    is_bot = BooleanField(default=False)
    language_code = CharField(null=True)

    def __str__(self):
        return f"<{self.username}>"


class Question(BaseModel):
    user = ForeignKeyField(User, backref="user")
    created_date = DateTimeField(default=datetime.now)
    question = TextField()
    answer = TextField(null=True)


def create_db_tables(db_path):
    db.connect()
    db.create_tables([User, Question])
