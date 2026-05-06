import csv
import os
from datetime import datetime

DATA_FOLDER = "data"
ENTRIES_FILE = os.path.join(DATA_FOLDER, "file_cabinet_entries.csv")
CATEGORIES_FILE = os.path.join(DATA_FOLDER, "file_cabinet_categories.csv")

ENTRY_FIELDS = [
    "entry_id",
    "title",
    "category",
    "content",
    "attachment_path",
    "date_created",
    "date_modified",
    "is_favourite",
    "status"
]

DEFAULT_CATEGORIES = [
    "Personal",
    "Receipts",
    "Documents",
    "Groceries",
    "Travel",
    "Other"
]


def setup_files():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.exists(ENTRIES_FILE):
        with open(ENTRIES_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ENTRY_FIELDS)
            writer.writeheader()

    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["category"])

            for category in DEFAULT_CATEGORIES:
                writer.writerow([category])


def load_entries():
    setup_files()
    entries = []

    with open(ENTRIES_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            entry = {
                "entry_id": row.get("entry_id", ""),
                "title": row.get("title", ""),
                "category": row.get("category", ""),
                "content": row.get("content", ""),
                "attachment_path": row.get("attachment_path", ""),
                "date_created": row.get("date_created", ""),
                "date_modified": row.get("date_modified", ""),
                "is_favourite": row.get("is_favourite", "False"),
                "status": row.get("status", "Active")
            }

            entries.append(entry)

    return entries


def save_entries(entries):
    setup_files()

    with open(ENTRIES_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ENTRY_FIELDS)
        writer.writeheader()
        writer.writerows(entries)


def load_categories():
    setup_files()
    categories = []

    with open(CATEGORIES_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            categories.append(row["category"])

    return categories


def save_categories(categories):
    setup_files()

    with open(CATEGORIES_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["category"])

        for category in categories:
            writer.writerow([category])


def get_next_entry_id(entries):
    if len(entries) == 0:
        return "1"

    highest_id = 0

    for entry in entries:
        try:
            entry_id = int(entry["entry_id"])

            if entry_id > highest_id:
                highest_id = entry_id

        except ValueError:
            pass

    return str(highest_id + 1)


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M")
