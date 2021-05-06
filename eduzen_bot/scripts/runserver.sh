#!/bin/sh

poetry run python /code/eduzen_bot/scripts/wait_for_db.py

exec poetry run python -m eduzen_bot
