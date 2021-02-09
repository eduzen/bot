from eduzen_bot.plugins.commands.events.command import get_users_usage

from .conftest import BaseTestCase


class UserTesCase(BaseTestCase):
    def test_count_aggregation_of_usage(self):
        txt = get_users_usage()
        txt = txt.split("\n")
        assert len(txt) == 2
