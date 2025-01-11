#!/usr/bin/env python3
import os
from pathlib import Path

import logfire
import sentry_sdk
from dotenv import load_dotenv
from telegram.error import InvalidToken
from telegram.ext import Application, CommandHandler, ExtBot, MessageHandler, filters

from eduzenbot.plugins.job_queue.alarms.command import set_timer, unset
from eduzenbot.plugins.messages.unknown import unknown
from eduzenbot.services.services import load_and_register_plugins

# Load environment variables from .env file
env_path = Path("../.env")
load_dotenv(env_path)

TOKEN = os.environ["TOKEN"]
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
EDUZEN_ID = os.environ["EDUZEN_ID"]
PORT = int(os.getenv("PORT", 5000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")


logfire.configure()

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.8,
)

# async def start_bot(
#     token: str,
#     eduzen_id: str = "3652654",
#     use_polling: bool = True,
#     port: int = 80,
# ) -> None:
#     """
#     Creates an Application, loads plugins, sets up error handling,
#     and runs the bot via polling or webhook.
#     """
#     try:
#         application = Application.builder().token(token).build()
#     except TelegramError as exc:
#         logfire.exception("Something went wrong initializing the application...")
#         raise SystemExit(str(exc))

#     logfire.info(f"Application created for token ending in {token[-4:]}")

#     # Register the global error handler
#     application.add_error_handler(telegram_error_handler)

#     # Load and register plugins
#     load_and_register_plugins(application)

#     # Startup callbacks
#     # If you want PTB to call on_startup for both polling and webhook:
#     # application.post_init_callbacks.append(partial(on_startup, application, eduzen_id))

#     # if use_polling:
#         # logfire.info("Starting bot with polling...")
#         # await application.run_polling()
#     # else:
#     logfire.info("Starting bot with webhook...")
#     await application.run_webhook(
#         listen="0.0.0.0",
#         port=port,
#         webhook_url=f"https://eduzenbot.herokuapp.com/{token}",
#     )


async def send_startup_message(bot: ExtBot):
    """Sends a message to a specific chat when the bot starts."""
    await bot.send_message(chat_id=EDUZEN_ID, text="🤖 Bot has started and is running!")


# async def main() -> None:
#     create_db_tables()
# bot = TelegramBot(token=TOKEN, eduzen_id=EDUZEN_ID, polling=False, port=PORT)
# db.connect(reuse_if_open=True)
# # asyncio.run(start_bot(token=TOKEN, use_polling=False, port=PORT, eduzen_id=EDUZEN_ID))


# # application = Application.builder().token(TOKEN).build()
# async with Bot(TOKEN) as bot:
#     try:
#         update_id = (await bot.get_updates())[0].update_id
#     except IndexError:
#         update_id = None
#     except InvalidToken:
#         logfire.error("Invalid token")
#         return

#     breakpoint( )
#     bot.add_handler(CommandHandler("set", set_timer))
#     # bot.add_handler(CommandHandler("config_reporte", set_timer))
#     # bot.add_handler(CommandHandler("unset", unset))
#     # bot.add_handler(MessageHandler(filters.COMMAND, unknown))
#     while True:
#         try:
#             logfire.info("listening for new messages...")
#             update_id = await echo(bot, update_id)

#         except NetworkError:
#             await asyncio.sleep(1)
#         except Forbidden:
#             # The user has removed or blocked the bot.
#             update_id += 1

# job_queue = application.job_queue
# kwargs = {"msg": "eduzenbot reiniciado!", "eduzen_id": EDUZEN_ID}
# breakpoint()

# job_queue.run_repeating(
#     # partial(...) will create a new function with those arguments 'pre-filled'
#     partial(send_msg_to_eduzen, application.context, EDUZEN_ID, "Hello from repeated job!"),
#     interval=60,  # run every 60 seconds
#     first=10,     # start after 10 seconds
#     name="SendMsgToEduzenJob"
# )
# job_minute = job_queue.run_repeating(send_msg_to_eduzen, interval=60, first=10, job_kwargs=kwargs)

# application.add_error_handler(telegram_error_handler)
# load_and_register_plugins(application)
# application.run_polling()

# await send_msg_to_eduzen(application, EDUZEN_ID, "eduzenbot reiniciado!")
# schedule_reports(
#     application.job_queue,
#     send_msg_to_chatid,
#     EDUZEN_ID,
# )
# bot.add_handler(CommandHandler("set", set_timer))
# bot.add_handler(CommandHandler("config_reporte", set_timer))
# bot.add_handler(CommandHandler("unset", unset))
# bot.add_handler(MessageHandler(filters.COMMAND, unknown))
# # bot.start()
# asyncio.run(bot.start())


# loop = asyncio.new_event_loop()  # Changed from get_event_loop()
# asyncio.set_event_loop(loop)     # Set it as the current loop
# loop.run_until_complete(bot.start())
async def on_startup(app: Application):
    await send_startup_message(app.bot)


def main():
    try:
        bot = ExtBot(token=TOKEN)
        app = Application.builder().bot(bot).build()
    except InvalidToken:
        print("Invalid token")
        return

    app.post_init = on_startup

    # Register command handlers
    app.add_handler(CommandHandler("set", set_timer))
    app.add_handler(CommandHandler("config_reporte", set_timer))
    app.add_handler(CommandHandler("unset", unset))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    load_and_register_plugins(app)
    app.run_polling()


if __name__ == "__main__":
    main()
