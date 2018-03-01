import os
from datetime import datetime

from peewee import (
    Model, SqliteDatabase, ForeignKeyField, DateTimeField, TextField,
    CharField
)

db = SqliteDatabase('my_database.db')


class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)

class Question(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    created_date = DateTimeField(default=datetime.now)
    question = TextField()
    answer = TextField()


def create_db_tables():
    db.connect()
    db.create_tables([User, Question])
