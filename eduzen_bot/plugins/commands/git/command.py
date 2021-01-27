"""
pull - update_repo
"""
import subprocess

import structlog

from eduzen_bot.auth.restricted import restricted
from eduzen_bot.decorators import create_user

logger = structlog.get_logger(filename=__name__)


@restricted
@create_user
def update_repo(update, context, *args, **kwargs):
    logger.warn("Trying to update bot code")

    result = subprocess.run(["git", "pull", "origin", "master"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    msg = "No paso naranja!"

    if result.returncode == 0:
        logger.warn("Code updated!")
        msg = result.stdout.decode("utf-8")
    elif result.returncode == 1:
        msg = result.stderr.decode("utf-8")

    update.message.reply_text(msg)
