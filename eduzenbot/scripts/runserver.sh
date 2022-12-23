#!/bin/sh

poetry run python /code/eduzenbot/scripts/wait_for_db.py

exec poetry run python -m eduzenbot
