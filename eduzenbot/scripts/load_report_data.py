import csv
import sys

import logfire
from peewee import IntegrityError

from eduzenbot.models import Report, db

logfire.configure()


def load_reports_from_csv(csv_file: str):
    """
    Loads user data from a CSV file into the User table.
    Expects columns: chat_id, first_name, last_name, username
    """
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # We'll accumulate all rows in a list first
        rows = list(reader)
        logfire.info(f"Loaded {len(rows)} rows from {csv_file}")

    with db.atomic():
        for row in rows:
            row["id"] = int(row["id"])

            try:
                Report.insert(**row).on_conflict_ignore().execute()
                # Or use `.on_conflict_replace()`, depending on your needs
            except IntegrityError as e:
                logfire.error(f"Error inserting user {row}: {e}")
    logfire.info("Data import complete.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_data.py <csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]
    load_reports_from_csv(csv_path)
