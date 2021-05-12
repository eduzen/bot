# import unittest
# from faker import Faker
# from eduzen_bot.models import EventLog, User
# from eduzen_bot.plugins.commands.events.command import get_users_usage

# class UserTesCase(unittest.TestCase):
#     def setUp(self, db):
#         self.faker = Faker()
#         # Bind model classes to test db. Since we have a complete list of
#         # all models, we do not need to recursively bind dependencies.
#         # breakpoint()
#         self.user = User.create(
#             **{
#                 "id": 3652654,
#                 "first_name": "Eduardo",
#                 "is_bot": False,
#                 "last_name": "Enriquez",
#                 "username": "eduzen",
#                 "language_code": "en",
#             }
#         )
#         # self.user_2 = User.create(
#         #     **{
#         #         "id": 3652655,
#         #         "first_name": "Arturo",
#         #         "is_bot": False,
#         #         "last_name": "Enriquez",
#         #         "username": "edu_zen",
#         #         "language_code": "es",
#         #     }
#         # )
#         self.events = []
#         for _ in range(5):
#             self.events.append(EventLog.create(user=self.user, command="btc"))
#             self.events.append(EventLog.create(user=self.user_2, command="btc"))

#     def test_count_aggregation_of_usage(self):
#         txt = get_users_usage()
#         txt = txt.split("\n")
#         assert len(txt) == 2
