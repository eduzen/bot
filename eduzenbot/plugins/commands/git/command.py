"""
pull - update_repo
"""

import subprocess

import logfire
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user


@restricted
@create_user
async def update_repo(update: ContextTypes, context: ContextTypes.DEFAULT_TYPE, *args: int, **kwargs: str):
    logfire.warn("Trying to update bot code")

    result = subprocess.run(["git", "pull", "origin", "master"], capture_output=True)
    msg = "No paso naranja!"

    if result.returncode == 0:
        logfire.warn("Code updated!")
        msg = result.stdout.decode("utf-8")
    elif result.returncode == 1:
        msg = result.stderr.decode("utf-8")

    await update.message.reply_text(msg)
