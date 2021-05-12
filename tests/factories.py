import factory

from eduzen_bot import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    id = factory.Faker("pyint")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.LazyAttribute(lambda obj: f"{obj.first_name}{obj.last_name}")
    language_code = factory.Faker("language_code")
    is_bot = False


class EventFactory(factory.Factory):
    class Meta:
        model = models.EventLog

    id = factory.Faker("pyint")
    user = factory.SubFactory(UserFactory)
    command = factory.Faker("sentence")
