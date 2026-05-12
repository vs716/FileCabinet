import csv
import hashlib
import os
import secrets
import time

DATA_FOLDER = "data"
ACCOUNTS_FILE = os.path.join(DATA_FOLDER, "accounts.csv")

ACCOUNT_FIELDS = [
    "username",
    "salt",
    "password_hash",
    "failed_attempts",
    "lock_until"
]


def setup_auth_file():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ACCOUNT_FIELDS)
            writer.writeheader()


def load_accounts():
    setup_auth_file()
    accounts = []

    with open(ACCOUNTS_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            accounts.append({
                "username": row.get("username", ""),
                "salt": row.get("salt", ""),
                "password_hash": row.get("password_hash", ""),
                "failed_attempts": row.get("failed_attempts", "0"),
                "lock_until": row.get("lock_until", "0")
            })

    return accounts


def save_accounts(accounts):
    setup_auth_file()

    with open(ACCOUNTS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ACCOUNT_FIELDS)
        writer.writeheader()
        writer.writerows(accounts)


def hash_password(password, salt):
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        100000
    )

    return hashed.hex()


def create_account(username, password):
    username = username.strip()

    if username == "":
        return False, "Username cannot be empty."

    if password == "":
        return False, "Password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    accounts = load_accounts()

    for account in accounts:
        if account["username"] == username:
            return False, "This username already exists."

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    accounts.append({
        "username": username,
        "salt": salt,
        "password_hash": password_hash,
        "failed_attempts": "0",
        "lock_until": "0"
    })

    save_accounts(accounts)
    return True, "Account created successfully."


def login(username, password):
    username = username.strip()
    accounts = load_accounts()

    for account in accounts:
        if account["username"] == username:
            current_time = int(time.time())
            lock_until = int(account["lock_until"])

            if current_time < lock_until:
                seconds_left = lock_until - current_time
                minutes_left = max(1, seconds_left // 60)
                return False, f"Account locked. Try again in about {minutes_left} minute(s)."

            entered_hash = hash_password(password, account["salt"])

            if entered_hash == account["password_hash"]:
                account["failed_attempts"] = "0"
                account["lock_until"] = "0"
                save_accounts(accounts)
                return True, "Login successful."

            failed_attempts = int(account["failed_attempts"]) + 1
            account["failed_attempts"] = str(failed_attempts)

            if failed_attempts >= 3:
                account["failed_attempts"] = "0"
                account["lock_until"] = str(current_time + 300)
                save_accounts(accounts)
                return False, "Too many incorrect attempts. Account locked for 5 minutes."

            attempts_left = 3 - failed_attempts
            save_accounts(accounts)
            return False, f"Incorrect password. {attempts_left} attempt(s) remaining."

    return False, "Account not found."
