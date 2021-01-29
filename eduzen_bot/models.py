import os
from datetime import datetime

from dotenv import load_dotenv
from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    TextField,
)
from playhouse.db_url import connect

load_dotenv(".env")
db = connect(os.getenv("DATABASE_URL", "sqlite:///default.db"))


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(unique=True)
    is_bot = BooleanField(default=False)
    language_code = CharField(null=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"<{self.username}: {self.first_name} {self.last_name}>"

    def to_str(self):
        return (
            f"{'bot! ' if self.is_bot else ''}{self.username} | "
            f"{self.first_name} | {self.last_name} | {self.created_at}"
        )


class Question(BaseModel):
    user = ForeignKeyField(User, backref="user")
    question = TextField()
    answer = TextField(null=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"<{self.question}>"
