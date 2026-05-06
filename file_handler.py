import csv
import os
from datetime import datetime

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "file_cabinet_entries.csv")

FIELD_NAMES = [
    "entry_id",
    "title",
    "category",
    "tags",
    "content",
    "attachment_path",
    "date_created",
    "date_modified",
    "is_favourite",
    "status"
]


def setup_file():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELD_NAMES)
            writer.writeheader()


def load_entries():
    setup_file()

    entries = []

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            entries.append(row)

    return entries


def save_entries(entries):
    setup_file()

    with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELD_NAMES)
        writer.writeheader()
        writer.writerows(entries)


def get_next_entry_id(entries):
    if len(entries) == 0:
        return "1"

    highest_id = 0

    for entry in entries:
        try:
            current_id = int(entry["entry_id"])

            if current_id > highest_id:
                highest_id = current_id

        except ValueError:
            pass

    return str(highest_id + 1)


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M")
