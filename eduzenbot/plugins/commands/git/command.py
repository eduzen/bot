"""
pull - update_repo
"""
import logging
import subprocess

from eduzenbot.auth.restricted import restricted
from eduzenbot.decorators import create_user

logger = logging.getLogger("rich")


@restricted
@create_user
def update_repo(update, context, *args, **kwargs):
    logger.warn("Trying to update bot code")

    result = subprocess.run(["git", "pull", "origin", "master"], capture_output=True)
    msg = "No paso naranja!"

    if result.returncode == 0:
        logger.warn("Code updated!")
        msg = result.stdout.decode("utf-8")
    elif result.returncode == 1:
        msg = result.stderr.decode("utf-8")

    update.message.reply_text(msg)
