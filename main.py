import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

import file_handler


class FileCabinetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cabinet")
        self.root.geometry("1050x620")
        self.root.minsize(930, 520)

        self.entries = file_handler.load_entries()
        self.categories = file_handler.load_categories()

        self.visible_entries = []
        self.selected_entry_id = None
        self.search_var = tk.StringVar()
        self.show_archived_var = tk.IntVar()

        self.build_layout()
        self.refresh_categories()
        self.refresh_entry_list()
        self.clear_preview()

    def build_layout(self):
        self.root.configure(bg="#f4f6f8")

        title = tk.Label(
            self.root,
            text="File Cabinet",
            font=("Arial", 22, "bold"),
            fg="#0b2341",
            bg="#f4f6f8"
        )
        title.pack(pady=(12, 0))

        subtitle = tk.Label(
            self.root,
            text="A light-weight digital filing cabinet",
            font=("Arial", 10),
            fg="#444444",
            bg="#f4f6f8"
        )
        subtitle.pack(pady=(2, 12))

        main_frame = tk.Frame(self.root, bg="#f4f6f8")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.category_frame = tk.Frame(main_frame, bg="#e8eef5", width=200)
        self.category_frame.pack(side="left", fill="y", padx=(0, 10))
        self.category_frame.pack_propagate(False)

        self.entry_frame = tk.Frame(main_frame, bg="#ffffff", width=310)
        self.entry_frame.pack(side="left", fill="y", padx=(0, 10))
        self.entry_frame.pack_propagate(False)

        self.preview_frame = tk.Frame(main_frame, bg="#ffffff")
        self.preview_frame.pack(side="left", fill="both", expand=True)

        self.build_category_panel()
        self.build_entry_panel()
        self.build_preview_panel()

    def build_category_panel(self):
        label = tk.Label(
            self.category_frame,
            text="Categories",
            font=("Arial", 13, "bold"),
            fg="#0b2341",
            bg="#e8eef5"
        )
        label.pack(anchor="w", padx=12, pady=(15, 5))

        self.category_listbox = tk.Listbox(
            self.category_frame,
            borderwidth=0,
            font=("Arial", 10),
            selectbackground="#b9d4f0",
            activestyle="none"
        )
        self.category_listbox.pack(fill="both", expand=True, padx=12, pady=8)
        self.category_listbox.bind("<<ListboxSelect>>", self.category_selected)

        tk.Button(
            self.category_frame,
            text="Add Category",
            command=self.add_category
        ).pack(fill="x", padx=12, pady=(5, 4))

        tk.Button(
            self.category_frame,
            text="Delete Category",
            command=self.delete_category
        ).pack(fill="x", padx=12, pady=(0, 4))

        tk.Button(
            self.category_frame,
            text="Backup Data",
            command=self.backup_data
        ).pack(fill="x", padx=12, pady=(0, 12))

    def build_entry_panel(self):
        label = tk.Label(
            self.entry_frame,
            text="Entries",
            font=("Arial", 13, "bold"),
            fg="#0b2341",
            bg="#ffffff"
        )
        label.pack(anchor="w", padx=12, pady=(15, 5))

        search_label = tk.Label(
            self.entry_frame,
            text="Search entries",
            font=("Arial", 9),
            fg="#444444",
            bg="#ffffff"
        )
        search_label.pack(anchor="w", padx=12)

        self.search_entry = tk.Entry(
            self.entry_frame,
            textvariable=self.search_var,
            width=28
        )
        self.search_entry.pack(anchor="w", padx=12, pady=(3, 5), fill="x")
        self.search_entry.bind("<Return>", lambda event: self.search_entries())

        search_button_frame = tk.Frame(self.entry_frame, bg="#ffffff")
        search_button_frame.pack(fill="x", padx=12, pady=(0, 8))

        tk.Button(
            search_button_frame,
            text="Search",
            command=self.search_entries
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        tk.Button(
            search_button_frame,
            text="Clear",
            command=self.clear_search
        ).pack(side="left", fill="x", expand=True)

        self.show_archived_check = tk.Checkbutton(
            self.entry_frame,
            text="Show archived entries",
            variable=self.show_archived_var,
            command=self.refresh_entry_list,
            bg="#ffffff"
        )
        self.show_archived_check.pack(anchor="w", padx=12, pady=(0, 6))

        self.result_label = tk.Label(
            self.entry_frame,
            text="",
            font=("Arial", 9),
            fg="#555555",
            bg="#ffffff"
        )
        self.result_label.pack(anchor="w", padx=12)

        self.entry_listbox = tk.Listbox(
            self.entry_frame,
            borderwidth=0,
            font=("Arial", 10),
            selectbackground="#d7e8fa",
            activestyle="none"
        )
        self.entry_listbox.pack(fill="both", expand=True, padx=12, pady=8)
        self.entry_listbox.bind("<<ListboxSelect>>", self.entry_selected)

        tk.Button(
            self.entry_frame,
            text="New Entry",
            command=self.new_entry
        ).pack(fill="x", padx=12, pady=(5, 4))

        tk.Button(
            self.entry_frame,
            text="Edit Entry",
            command=self.edit_entry
        ).pack(fill="x", padx=12, pady=(0, 4))

        tk.Button(
            self.entry_frame,
            text="Archive / Restore",
            command=self.archive_or_restore_entry
        ).pack(fill="x", padx=12, pady=(0, 4))

        tk.Button(
            self.entry_frame,
            text="Delete Entry",
            command=self.delete_entry
        ).pack(fill="x", padx=12, pady=(0, 12))

    def build_preview_panel(self):
        self.preview_title = tk.Label(
            self.preview_frame,
            text="Select an entry",
            font=("Arial", 18, "bold"),
            fg="#0b2341",
            bg="#ffffff"
        )
        self.preview_title.pack(anchor="w", padx=18, pady=(18, 4))

        self.preview_meta = tk.Label(
            self.preview_frame,
            text="",
            font=("Arial", 10),
            fg="#555555",
            bg="#ffffff"
        )
        self.preview_meta.pack(anchor="w", padx=18, pady=(0, 10))

        self.attachment_label = tk.Label(
            self.preview_frame,
            text="",
            font=("Arial", 10),
            fg="#333333",
            bg="#ffffff"
        )
        self.attachment_label.pack(anchor="w", padx=18, pady=(0, 6))

        self.open_attachment_button = tk.Button(
            self.preview_frame,
            text="Open Attachment",
            command=self.open_attachment
        )
        self.open_attachment_button.pack(anchor="w", padx=18, pady=(0, 12))

        self.preview_content = tk.Text(
            self.preview_frame,
            wrap="word",
            height=18,
            font=("Arial", 11),
            bg="#f9fafb",
            borderwidth=1,
            relief="solid"
        )
        self.preview_content.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.preview_content.config(state="disabled")

    def refresh_categories(self):
        self.category_listbox.delete(0, tk.END)
        self.category_listbox.insert(tk.END, "All Items")

        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

        if self.category_listbox.size() > 0:
            self.category_listbox.selection_set(0)

    def refresh_entry_list(self, custom_entries=None):
        self.entry_listbox.delete(0, tk.END)

        if custom_entries is None:
            self.visible_entries = self.get_entries_for_current_view()
        else:
            self.visible_entries = custom_entries

        for entry in self.visible_entries:
            display_text = entry["title"]

            if entry["is_favourite"] == "True":
                display_text = "★ " + display_text

            if entry["status"] == "Archived":
                display_text = "[Archived] " + display_text

            if entry["attachment_path"] != "":
                display_text = display_text + " 📎"

            self.entry_listbox.insert(tk.END, display_text)

        if len(self.visible_entries) == 1:
            self.result_label.config(text="1 entry shown")
        else:
            self.result_label.config(text=str(len(self.visible_entries)) + " entries shown")

    def get_entries_for_current_view(self):
        selected_category = self.get_selected_category()
        show_archived = self.show_archived_var.get() == 1

        filtered_entries = []

        for entry in self.entries:
            if not show_archived and entry["status"] == "Archived":
                continue

            if selected_category == "All Items" or entry["category"] == selected_category:
                filtered_entries.append(entry)

        filtered_entries.sort(key=lambda item: item["is_favourite"] == "True", reverse=True)

        return filtered_entries

    def get_selected_category(self):
        selected = self.category_listbox.curselection()

        if not selected:
            return "All Items"

        return self.category_listbox.get(selected[0])

    def get_selected_entry(self):
        selected = self.entry_listbox.curselection()

        if not selected:
            return None

        index = selected[0]

        if index >= len(self.visible_entries):
            return None

        return self.visible_entries[index]

    def category_selected(self, event):
        self.selected_entry_id = None
        self.search_var.set("")
        self.refresh_entry_list()
        self.clear_preview()

    def entry_selected(self, event):
        entry = self.get_selected_entry()

        if entry is None:
            return

        self.selected_entry_id = entry["entry_id"]
        self.show_preview(entry)

    def show_preview(self, entry):
        title_text = entry["title"]

        if entry["is_favourite"] == "True":
            title_text = "★ " + title_text

        self.preview_title.config(text=title_text)

        meta_text = (
            "Category: " + entry["category"] +
            "    Created: " + entry["date_created"] +
            "    Modified: " + entry["date_modified"] +
            "    Status: " + entry["status"]
        )

        self.preview_meta.config(text=meta_text)

        if entry["attachment_path"] == "":
            self.attachment_label.config(text="Attachment: None")
        else:
            self.attachment_label.config(text="Attachment: " + entry["attachment_path"])

        self.preview_content.config(state="normal")
        self.preview_content.delete("1.0", tk.END)
        self.preview_content.insert(tk.END, entry["content"])
        self.preview_content.config(state="disabled")

    def clear_preview(self):
        self.preview_title.config(text="Select an entry")
        self.preview_meta.config(text="No entry selected.")
        self.attachment_label.config(text="Attachment: None")

        self.preview_content.config(state="normal")
        self.preview_content.delete("1.0", tk.END)
        self.preview_content.insert(tk.END, "Choose an entry from the middle panel to view its contents.")
        self.preview_content.config(state="disabled")

    def add_category(self):
        new_category = simpledialog.askstring("Add Category", "Enter new category name:")

        if new_category is None:
            return

        new_category = new_category.strip()

        if new_category == "":
            messagebox.showerror("Error", "Category name cannot be empty.")
            return

        if new_category in self.categories:
            messagebox.showerror("Error", "This category already exists.")
            return

        self.categories.append(new_category)
        file_handler.save_categories(self.categories)

        self.refresh_categories()
        messagebox.showinfo("Saved", "Category added successfully.")

    def delete_category(self):
        selected_category = self.get_selected_category()

        if selected_category == "All Items":
            messagebox.showerror("Error", "You cannot delete All Items.")
            return

        for entry in self.entries:
            if entry["category"] == selected_category:
                messagebox.showerror(
                    "Error",
                    "This category still has entries. Delete those entries first."
                )
                return

        confirm = messagebox.askyesno(
            "Confirm",
            "Delete this category?"
        )

        if confirm:
            self.categories.remove(selected_category)
            file_handler.save_categories(self.categories)

            self.refresh_categories()
            self.refresh_entry_list()
            self.clear_preview()

    def new_entry(self):
        selected_category = self.get_selected_category()

        if selected_category == "All Items":
            messagebox.showerror("Error", "Please select a category before creating an entry.")
            return

        self.open_entry_window("new", selected_category)

    def edit_entry(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Please select an entry to edit.")
            return

        self.open_entry_window("edit", entry["category"], entry)

    def open_entry_window(self, mode, category, entry=None):
        window = tk.Toplevel(self.root)
        window.title("Entry Editor")
        window.geometry("540x510")
        window.configure(bg="#f4f6f8")

        tk.Label(
            window,
            text="Entry Editor",
            font=("Arial", 16, "bold"),
            fg="#0b2341",
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        tk.Label(
            window,
            text="Category: " + category,
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15)

        tk.Label(
            window,
            text="Title",
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15, pady=(15, 0))

        title_entry = tk.Entry(window, width=60)
        title_entry.pack(anchor="w", padx=15)

        favourite_var = tk.IntVar()

        tk.Checkbutton(
            window,
            text="Mark as important",
            variable=favourite_var,
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15, pady=(10, 0))

        tk.Label(
            window,
            text="Content",
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15, pady=(12, 0))

        content_text = tk.Text(window, width=62, height=10, wrap="word")
        content_text.pack(anchor="w", padx=15)

        attachment_var = tk.StringVar()

        tk.Label(
            window,
            text="Attachment",
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15, pady=(12, 0))

        attachment_frame = tk.Frame(window, bg="#f4f6f8")
        attachment_frame.pack(fill="x", padx=15)

        attachment_entry = tk.Entry(
            attachment_frame,
            textvariable=attachment_var,
            width=48
        )
        attachment_entry.pack(side="left", fill="x", expand=True)

        def browse_file():
            file_path = filedialog.askopenfilename(title="Select a file to attach")

            if file_path:
                attachment_var.set(file_path)

        tk.Button(
            attachment_frame,
            text="Browse",
            command=browse_file
        ).pack(side="left", padx=(5, 0))

        if mode == "edit" and entry is not None:
            title_entry.insert(0, entry["title"])
            content_text.insert(tk.END, entry["content"])
            attachment_var.set(entry["attachment_path"])

            if entry["is_favourite"] == "True":
                favourite_var.set(1)

        def save_from_window():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            attachment_path = attachment_var.get().strip()
            favourite_value = "True" if favourite_var.get() == 1 else "False"

            if title == "":
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            if attachment_path != "" and not os.path.exists(attachment_path):
                confirm = messagebox.askyesno(
                    "Attachment Warning",
                    "This attachment path does not exist. Do you still want to save it?"
                )

                if not confirm:
                    return

            current_date = file_handler.get_current_date()

            if mode == "new":
                new_entry = {
                    "entry_id": file_handler.get_next_entry_id(self.entries),
                    "title": title,
                    "category": category,
                    "content": content,
                    "attachment_path": attachment_path,
                    "date_created": current_date,
                    "date_modified": current_date,
                    "is_favourite": favourite_value,
                    "status": "Active"
                }

                self.entries.append(new_entry)

            else:
                for saved_entry in self.entries:
                    if saved_entry["entry_id"] == entry["entry_id"]:
                        saved_entry["title"] = title
                        saved_entry["content"] = content
                        saved_entry["attachment_path"] = attachment_path
                        saved_entry["date_modified"] = current_date
                        saved_entry["is_favourite"] = favourite_value
                        break

            file_handler.save_entries(self.entries)

            self.search_var.set("")
            self.refresh_entry_list()
            self.clear_preview()

            window.destroy()
            messagebox.showinfo("Saved", "Entry saved successfully.")

        tk.Button(
            window,
            text="Save",
            command=save_from_window
        ).pack(anchor="e", padx=15, pady=15)

    def delete_entry(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Please select an entry to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm",
            "Delete this entry permanently?"
        )

        if confirm:
            self.entries = [
                saved_entry for saved_entry in self.entries
                if saved_entry["entry_id"] != entry["entry_id"]
            ]

            file_handler.save_entries(self.entries)

            self.selected_entry_id = None
            self.search_var.set("")
            self.refresh_entry_list()
            self.clear_preview()

            messagebox.showinfo("Deleted", "Entry deleted successfully.")

    def archive_or_restore_entry(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Please select an entry first.")
            return

        for saved_entry in self.entries:
            if saved_entry["entry_id"] == entry["entry_id"]:
                if saved_entry["status"] == "Archived":
                    saved_entry["status"] = "Active"
                    message = "Entry restored successfully."
                else:
                    saved_entry["status"] = "Archived"
                    message = "Entry archived successfully."

                saved_entry["date_modified"] = file_handler.get_current_date()
                break

        file_handler.save_entries(self.entries)

        self.search_var.set("")
        self.refresh_entry_list()
        self.clear_preview()

        messagebox.showinfo("Updated", message)

    def open_attachment(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Please select an entry first.")
            return

        attachment_path = entry["attachment_path"]

        if attachment_path == "":
            messagebox.showerror("Error", "This entry does not have an attachment.")
            return

        if not os.path.exists(attachment_path):
            messagebox.showerror(
                "Error",
                "The attached file could not be found. It may have been moved or deleted."
            )
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(attachment_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", attachment_path])
            else:
                subprocess.call(["xdg-open", attachment_path])

        except Exception:
            messagebox.showerror("Error", "The attached file could not be opened.")

    def backup_data(self):
        try:
            file_handler.backup_data()
            messagebox.showinfo(
                "Backup Complete",
                "A backup copy of the CSV files has been created."
            )

        except Exception:
            messagebox.showerror("Error", "Backup could not be created.")

    def search_entries(self):
        keyword = self.search_var.get().strip().lower()

        if keyword == "":
            self.refresh_entry_list()
            self.clear_preview()
            return

        selected_category = self.get_selected_category()
        show_archived = self.show_archived_var.get() == 1
        results = []

        for entry in self.entries:
            if not show_archived and entry["status"] == "Archived":
                continue

            if selected_category != "All Items" and entry["category"] != selected_category:
                continue

            searchable_text = (
                entry["title"] + " " +
                entry["category"] + " " +
                entry["content"]
            ).lower()

            if keyword in searchable_text:
                results.append(entry)

        self.refresh_entry_list(results)
        self.clear_preview()

    def clear_search(self):
        self.search_var.set("")
        self.refresh_entry_list()
        self.clear_preview()


if __name__ == "__main__":
    file_handler.setup_files()

    root = tk.Tk()
    app = FileCabinetApp(root)
    root.mainloop()
