import csv
import os
import shutil
from datetime import datetime

BASE_DATA_FOLDER = "data"
USER_DATA_FOLDER = os.path.join(BASE_DATA_FOLDER, "user_files")

current_user = None

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


def set_current_user(username):
    global current_user
    current_user = username


def clear_current_user():
    global current_user
    current_user = None


def get_safe_username():
    if current_user is None or current_user == "":
        raise PermissionError("User must be logged in before accessing data.")

    safe_name = ""

    for character in current_user:
        if character.isalnum() or character in ["_", "-"]:
            safe_name += character

    if safe_name == "":
        raise PermissionError("Invalid username.")

    return safe_name


def get_user_folder():
    return os.path.join(USER_DATA_FOLDER, get_safe_username())


def get_backup_folder():
    return os.path.join(get_user_folder(), "backups")


def get_entries_file():
    return os.path.join(get_user_folder(), "file_cabinet_entries.csv")


def get_categories_file():
    return os.path.join(get_user_folder(), "file_cabinet_categories.csv")


def setup_files():
    os.makedirs(BASE_DATA_FOLDER, exist_ok=True)
    os.makedirs(USER_DATA_FOLDER, exist_ok=True)
    os.makedirs(get_user_folder(), exist_ok=True)
    os.makedirs(get_backup_folder(), exist_ok=True)

    if not os.path.exists(get_entries_file()):
        with open(get_entries_file(), "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ENTRY_FIELDS)
            writer.writeheader()

    if not os.path.exists(get_categories_file()):
        with open(get_categories_file(), "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["category"])

            for category in DEFAULT_CATEGORIES:
                writer.writerow([category])


def load_entries():
    setup_files()
    entries = []

    with open(get_entries_file(), "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            entries.append({
                "entry_id": row.get("entry_id", ""),
                "title": row.get("title", ""),
                "category": row.get("category", ""),
                "content": row.get("content", ""),
                "attachment_path": row.get("attachment_path", ""),
                "date_created": row.get("date_created", ""),
                "date_modified": row.get("date_modified", ""),
                "is_favourite": row.get("is_favourite", "False"),
                "status": row.get("status", "Active")
            })

    return entries


def save_entries(entries):
    setup_files()

    with open(get_entries_file(), "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ENTRY_FIELDS)
        writer.writeheader()
        writer.writerows(entries)


def load_categories():
    setup_files()
    categories = []

    with open(get_categories_file(), "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            category = row.get("category", "").strip()

            if category != "":
                categories.append(category)

    return categories


def save_categories(categories):
    setup_files()

    with open(get_categories_file(), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["category"])

        for category in categories:
            writer.writerow([category])


def get_next_entry_id(entries):
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


def backup_data():
    setup_files()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    entries_backup = os.path.join(
        get_backup_folder(),
        "file_cabinet_entries_backup_" + timestamp + ".csv"
    )

    categories_backup = os.path.join(
        get_backup_folder(),
        "file_cabinet_categories_backup_" + timestamp + ".csv"
    )

    shutil.copy(get_entries_file(), entries_backup)
    shutil.copy(get_categories_file(), categories_backup)

    return entries_backup, categories_backup
