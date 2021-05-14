import os
from datetime import datetime
from functools import cached_property

from peewee import (
    BigIntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    PrimaryKeyField,
    TextField,
)
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict

db = connect(os.getenv("DATABASE_URL", "sqlite:///:memory:"))


class BaseModel(Model):
    class Meta:
        database = db

    def todict(self):
        return model_to_dict(self)

    def to_dict(self):
        return model_to_dict(self)


class User(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)
    is_bot = BooleanField(default=False)
    language_code = CharField(null=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"<{self.username}: {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        full = ""
        if self.first_name:
            full = self.first_name
        if self.last_name:
            full += " " + self.last_name

        return full

    def to_str(self):
        return (
            f"{self.created_at.strftime('%Y/%m/%d %H:%M')} | {'bot! ' if self.is_bot else '|'}"
            f"{self.username: <12} | {self.full_name: <10}"
        )


class Question(BaseModel):
    user = ForeignKeyField(User, backref="questions")
    question = TextField()
    answer = TextField(null=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"<{self.question}>"


class EventLog(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref="eventlogs", null=True)
    command = TextField()
    data = TextField(null=True)
    timestamp = DateTimeField(default=datetime.now)

    def __str__(self):
        return f"<{self.id} {self.user}>"

    @cached_property
    def telegram(self):
        return f"{self.user.username} - {self.command} - {self.timestamp.strftime('%Y/%m/%d -%H.%M')}"
