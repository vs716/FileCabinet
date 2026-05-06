import tkinter as tk
from tkinter import ttk, messagebox

import file_handler


class FileCabinetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cabinet")
        self.root.geometry("850x550")

        self.entries = file_handler.load_entries()

        self.build_layout()
        self.load_entries_to_list()

    def build_layout(self):
        title = ttk.Label(
            self.root,
            text="File Cabinet",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=15)

        subtitle = ttk.Label(
            self.root,
            text="A light-weight digital filing cabinet"
        )
        subtitle.pack(pady=(0, 15))

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 15))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        ttk.Label(left_frame, text="Categories").pack(anchor="w")

        self.category_list = tk.Listbox(left_frame, width=25)
        self.category_list.pack(fill="y", expand=True)

        categories = [
            "Personal",
            "Receipts",
            "Documents",
            "Groceries",
            "Travel",
            "Other"
        ]

        for category in categories:
            self.category_list.insert(tk.END, category)

        ttk.Label(right_frame, text="Entry Details").pack(anchor="w")

        ttk.Label(right_frame, text="Title").pack(anchor="w", pady=(10, 0))
        self.title_entry = ttk.Entry(right_frame, width=45)
        self.title_entry.pack(anchor="w")

        ttk.Label(right_frame, text="Tags").pack(anchor="w", pady=(10, 0))
        self.tags_entry = ttk.Entry(right_frame, width=45)
        self.tags_entry.pack(anchor="w")

        ttk.Label(right_frame, text="Content").pack(anchor="w", pady=(10, 0))
        self.content_text = tk.Text(right_frame, width=55, height=8)
        self.content_text.pack(anchor="w")

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(anchor="w", pady=15)

        ttk.Button(
            button_frame,
            text="Save Entry",
            command=self.save_entry
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Clear Fields",
            command=self.clear_fields
        ).pack(side="left", padx=(0, 5))

        ttk.Label(right_frame, text="Saved Entries").pack(anchor="w", pady=(10, 0))

        self.entry_list = tk.Listbox(right_frame, width=70, height=8)
        self.entry_list.pack(anchor="w", fill="x")

    def get_selected_category(self):
        selected = self.category_list.curselection()

        if not selected:
            return ""

        return self.category_list.get(selected[0])

    def save_entry(self):
        title = self.title_entry.get().strip()
        category = self.get_selected_category()
        tags = self.tags_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if title == "":
            messagebox.showerror("Error", "Please enter a title.")
            return

        if category == "":
            messagebox.showerror("Error", "Please select a category.")
            return

        current_date = file_handler.get_current_date()

        new_entry = {
            "entry_id": file_handler.get_next_entry_id(self.entries),
            "title": title,
            "category": category,
            "tags": tags,
            "content": content,
            "attachment_path": "",
            "date_created": current_date,
            "date_modified": current_date,
            "is_favourite": "False",
            "status": "Active"
        }

        self.entries.append(new_entry)
        file_handler.save_entries(self.entries)

        self.load_entries_to_list()
        self.clear_fields()

        messagebox.showinfo("Saved", "Entry saved successfully.")

    def load_entries_to_list(self):
        self.entry_list.delete(0, tk.END)

        for entry in self.entries:
            display_text = f"{entry['entry_id']}. {entry['title']} ({entry['category']})"
            self.entry_list.insert(tk.END, display_text)

    def clear_fields(self):
        self.title_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)


if __name__ == "__main__":
    file_handler.setup_file()

    root = tk.Tk()
    app = FileCabinetApp(root)
    root.mainloop()
