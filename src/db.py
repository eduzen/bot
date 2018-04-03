from datetime import datetime

from peewee import (
    Model, SqliteDatabase, ForeignKeyField, DateTimeField, TextField, CharField
)

db = SqliteDatabase("my_database.db")


class BaseModel(Model):

    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)

    def __str__(self):
        return f"<{self.username}>"


class Question(BaseModel):
    user = ForeignKeyField(User, backref="user")
    created_date = DateTimeField(default=datetime.now)
    question = TextField()
    answer = TextField(null=True)


def create_db_tables():
    db.connect()
    db.create_tables([User, Question])
