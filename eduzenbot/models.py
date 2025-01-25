import os
from datetime import datetime

from peewee import (
    BigIntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    PrimaryKeyField,
    TextField,
)
from playhouse.db_url import connect
from playhouse.shortcuts import ThreadSafeDatabaseMetadata, model_to_dict

database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
db = connect(database_url)


class BaseModel(Model):
    class Meta:
        database = db
        # Instruct peewee to use our thread-safe metadata implementation.
        model_metadata_class = ThreadSafeDatabaseMetadata

    def todict(self):
        return model_to_dict(self)

    def to_dict(self):
        return model_to_dict(self)

    def __str__(self):
        return str(self.todict())


class User(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)
    is_bot = BooleanField(default=False)
    language_code = CharField(null=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)

    def save(self, force_insert=False, *args, **kwargs) -> None:
        self.updated_at = datetime.now()
        return super().save(force_insert=force_insert, *args, **kwargs)

    def __str__(self) -> str:
        return f"<{self.username or ''}: {self.first_name or ''} {self.last_name or ''}>"

    @property
    def full_name(self) -> str:
        full = ""
        if self.first_name:
            full = self.first_name
        if self.last_name:
            full += " " + self.last_name

        return full

    def to_str(self) -> str:
        return (
            f"{self.created_at.strftime('%Y/%m/%d %H:%M')} | {'bot! ' if self.is_bot else '|'}"
            f"{self.username: <12} | {self.full_name: <10}"
        )


class EventLog(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref="eventlogs", null=True)
    command = TextField()
    data = TextField(null=True)
    timestamp = DateTimeField(default=datetime.now)

    def __str__(self):
        return f"<{self.id} {self.user}>"

    @property
    def telegram(self):
        return f"{self.user.username} - {self.command} - {self.timestamp.strftime('%Y/%m/%d -%H.%M')}"


class Report(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    chat_id = TextField()
    data = TextField(null=True)
    hour = IntegerField(default=10)
    min = IntegerField(default=0)
    show_weather = BooleanField(default=True)
    show_crypto = BooleanField(default=True)
    show_dollar = BooleanField(default=True)
    show_news = BooleanField(default=True)

    timestamp = DateTimeField(default=datetime.now)

    def __str__(self):
        return f"<{self.chat_id} {self.hour}:{self.min} Weather: {self.show_weather}, Dollar: {self.show_dollar}, Crypto: {self.show_crypto}>"
