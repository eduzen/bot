#!/usr/bin/env python
import os
import time

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def postgres_ready():
    try:
        psycopg2.connect(DATABASE_URL)
        return True
    except psycopg2.OperationalError:
        print("ups")
    return False


def main():
    while not postgres_ready():
        print("Postgres is unavailable - sleeping")
        time.sleep(1)

    print("Postgres is up - continuing...")


if __name__ == "__main__":
    main()
