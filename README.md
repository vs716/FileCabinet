# File Cabinet

File Cabinet is a local desktop application built with Python and Tkinter. It allows users to organise notes, documents and personal information into folders, save entries to CSV files, attach local files, search saved data, archive old entries and create backups.

The final version also includes a login system with password hashing and user-specific data folders.

---

## Features

- Create an account
- Login before accessing saved data
- Passwords stored as salted hashes, not plain text
- Account lockout after 3 incorrect password attempts
- Separate CSV data folders for each user
- Create and delete folders/categories
- Add, view, edit and delete entries
- Search entries by title, category, content or attachment name
- Mark entries as favourite
- Archive and restore entries
- Attach a local file path to an entry
- Open attached files from inside the app
- Error handling for missing attachments
- Create backup copies of CSV files
- Clean three-panel interface
- Rounded buttons with hover effects and tooltips

---

## Files

```text
main.py
auth_manager.py
file_handler.py