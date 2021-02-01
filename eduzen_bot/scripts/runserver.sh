#!/bin/sh

sh /code/eduzen_bot/scripts/wait_for_db.sh

exec python3 eduzen_bot
