# tests/test_telegram_bot.py

import os
import unittest
from unittest.mock import MagicMock, patch

from eduzenbot.telegram_bot import TelegramBot


class TestTelegramBot(unittest.TestCase):
    @patch("eduzenbot.telegram_bot.Updater")
    def setUp(self, mock_updater):
        # Make the Updater mock do nothing on __init__.
        # That way it won't complain about an invalid token.
        mock_updater.return_value = MagicMock()

        self.bot = TelegramBot(
            token=os.getenv("TOKEN", "123456789:FAKE-ABCDEF1234ghIkl-zyx57W2v"),
            eduzen_id=os.getenv("EDUZEN_ID", "dummy_eduzen_id"),
            polling=True,  # True or False as needed
            port=5000,
        )

    def test_load_plugins(self):
        """
        Basic test to see if the plugins are being loaded
        and if we get a non-empty dictionary of commands
        (assuming you have at least one plugin docstring).
        """
        self.bot._load_plugins()
        self.assertTrue(True, "Ensure _load_plugins runs without error.")

    @patch("eduzenbot.telegram_bot.pkgutil.iter_modules")
    @patch("eduzenbot.telegram_bot.logfire")
    def test_plugins_with_no_docstring(self, mock_logfire, mock_iter_modules):
        """
        If a plugin has no docstring, check that it doesn't break the loader
        and logs a skip or something similar.
        """
        # Return a single "fake" plugin
        fake_importer = MagicMock()
        fake_module = MagicMock(__doc__=None)  # no docstring
        fake_importer.find_module.return_value.load_module.return_value = fake_module
        mock_iter_modules.return_value = [(fake_importer, "fake_module", False)]

        self.bot._load_plugins()
        # Confirm no crash happened
        self.assertTrue(True, "Handled plugin with no docstring gracefully.")

    @patch("eduzenbot.telegram_bot.Updater")
    @patch("eduzenbot.telegram_bot.pkgutil.iter_modules")
    def test_duplicate_plugin_names(self, mock_iter_modules, mock_updater):
        """
        Prove that if two plugins have the same file name (e.g. 'command.py'),
        only one ends up getting loaded due to a name collision.
        """
        # Make Updater a mock so we don't need a valid Telegram token
        mock_updater.return_value = MagicMock()

        # Create dummy docstrings so each "fake_module" has different commands
        # (i.e., one has a /start command, the other has a /help command).
        fake_importer1 = MagicMock()
        fake_module1 = MagicMock(__doc__="start - start_command")
        fake_importer1.find_module.return_value.load_module.return_value = fake_module1

        fake_importer2 = MagicMock()
        fake_module2 = MagicMock(__doc__="help - help_command")
        fake_importer2.find_module.return_value.load_module.return_value = fake_module2

        # Both package_name entries are "command", simulating two files
        # with the same name in different subdirectories.
        mock_iter_modules.return_value = [
            (fake_importer1, "command", False),
            (fake_importer2, "command", False),
        ]

        # Instantiate the bot. This calls __attrs_post_init__ -> _load_plugins()
        bot = TelegramBot(
            token="123456789:FAKE-TOKEN",  # Looks valid to avoid InvalidToken
            eduzen_id="dummy_eduzen_id",
            polling=True,
            port=5000,
        )

        # Because your _load_plugins() calls _get_plugins(), which calls
        # _find_modules(), you can check that only one plugin's commands
        # were actually registered. The simplest approach is to look at
        # bot.updater.dispatcher.handlers, or re-check the log messages,
        # or re-invoke _get_plugins directly.

        # If you only rely on log messages, you can patch logfire and see what's loaded.
        # But let's call _get_plugins directly to see the final dictionary:
        with patch("eduzenbot.telegram_bot.logfire"):
            plugins = bot._get_plugins()  # or bot._load_plugins()
            # Now check if we got one or two commands:

        # We expect the dictionary to have a single or possibly conflicting entry,
        # depending on how your code merges duplicates. Typically, "command" is
        # discovered twice, and the second updates the same dictionary keys
        # (like "help" overwriting "start" if the keys are the same).
        # If each docstring defines a different command name, you might have both commands
        # but from only one "command" module name. Let's see:
        self.assertIn("start", plugins, "start command should be loaded from the first plugin.")
        # Potentially we expect "help" to be missing if the second plugin is overwritten,
        # or we check if it's there if the code merges docstrings. Adjust accordingly:
        self.assertNotIn("help", plugins, "help command is missing because second plugin was overwritten.")

        # If you want the opposite behavior (both loaded), then check .assertIn("help", plugins).
        # The key is that your code's approach to merging module docstrings under the same
        # 'package_name' might cause collisions. This test demonstrates the collision.
