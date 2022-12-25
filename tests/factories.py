from typing import Any

import factory

from eduzenbot import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.LazyAttribute(lambda obj: f"{obj.first_name}{obj.last_name}")
    language_code = factory.Faker("language_code")
    is_bot = False

    @classmethod
    def _create(cls, target_class, *args: int, **kwargs: str) -> models.User:
        """Create an instance of the model, and save it to the database."""
        obj = target_class.create(**kwargs)
        return obj


class EventFactory(factory.Factory):
    class Meta:
        model = models.EventLog

    user = factory.SubFactory(UserFactory)
    command = factory.Faker("sentence")

    @classmethod
    def _create(cls, target_class: models.EventLog, *args: Any, **kwargs: dict[Any, Any]) -> models.EventLog:
        """Create an instance of the model, and save it to the database."""
        obj = target_class.create(**kwargs)
        return obj
