import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import file_handler


class FileCabinetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cabinet")
        self.root.geometry("1000x600")
        self.root.minsize(900, 500)

        self.entries = file_handler.load_entries()
        self.categories = file_handler.load_categories()

        self.visible_entries = []
        self.selected_entry_id = None

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

        self.entry_frame = tk.Frame(main_frame, bg="#ffffff", width=280)
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
        self.preview_meta.pack(anchor="w", padx=18, pady=(0, 12))

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

    def refresh_entry_list(self):
        self.entry_listbox.delete(0, tk.END)
        self.visible_entries = []

        selected_category = self.get_selected_category()

        for entry in self.entries:
            if entry["status"] != "Active":
                continue

            if selected_category == "All Items" or entry["category"] == selected_category:
                self.visible_entries.append(entry)

        for entry in self.visible_entries:
            display_text = entry["title"]

            if entry["is_favourite"] == "True":
                display_text = "★ " + display_text

            self.entry_listbox.insert(tk.END, display_text)

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
        self.refresh_entry_list()
        self.clear_preview()

    def entry_selected(self, event):
        entry = self.get_selected_entry()

        if entry is None:
            return

        self.selected_entry_id = entry["entry_id"]
        self.show_preview(entry)

    def show_preview(self, entry):
        self.preview_title.config(text=entry["title"])

        meta_text = (
            "Category: " + entry["category"] +
            "    Created: " + entry["date_created"] +
            "    Modified: " + entry["date_modified"]
        )

        self.preview_meta.config(text=meta_text)

        self.preview_content.config(state="normal")
        self.preview_content.delete("1.0", tk.END)
        self.preview_content.insert(tk.END, entry["content"])
        self.preview_content.config(state="disabled")

    def clear_preview(self):
        self.preview_title.config(text="Select an entry")
        self.preview_meta.config(text="No entry selected.")

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
        window.geometry("500x420")
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

        title_entry = tk.Entry(window, width=55)
        title_entry.pack(anchor="w", padx=15)

        tk.Label(
            window,
            text="Content",
            bg="#f4f6f8"
        ).pack(anchor="w", padx=15, pady=(15, 0))

        content_text = tk.Text(window, width=58, height=12, wrap="word")
        content_text.pack(anchor="w", padx=15)

        if mode == "edit" and entry is not None:
            title_entry.insert(0, entry["title"])
            content_text.insert(tk.END, entry["content"])

        def save_from_window():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()

            if title == "":
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            current_date = file_handler.get_current_date()

            if mode == "new":
                new_entry = {
                    "entry_id": file_handler.get_next_entry_id(self.entries),
                    "title": title,
                    "category": category,
                    "content": content,
                    "attachment_path": "",
                    "date_created": current_date,
                    "date_modified": current_date,
                    "is_favourite": "False",
                    "status": "Active"
                }

                self.entries.append(new_entry)

            else:
                for saved_entry in self.entries:
                    if saved_entry["entry_id"] == entry["entry_id"]:
                        saved_entry["title"] = title
                        saved_entry["content"] = content
                        saved_entry["date_modified"] = current_date
                        break

            file_handler.save_entries(self.entries)

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
            self.refresh_entry_list()
            self.clear_preview()

            messagebox.showinfo("Deleted", "Entry deleted successfully.")


if __name__ == "__main__":
    file_handler.setup_files()

    root = tk.Tk()
    app = FileCabinetApp(root)
    root.mainloop()
