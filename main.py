import tkinter as tk
from tkinter import ttk


class FileCabinetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cabinet")
        self.root.geometry("800x500")

        self.build_layout()

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

        for category in ["Personal", "Receipts", "Documents", "Groceries", "Other"]:
            self.category_list.insert(tk.END, category)

        ttk.Label(right_frame, text="Entry Details").pack(anchor="w")

        ttk.Label(right_frame, text="Title").pack(anchor="w", pady=(10, 0))
        self.title_entry = ttk.Entry(right_frame, width=45)
        self.title_entry.pack(anchor="w")

        ttk.Label(right_frame, text="Content").pack(anchor="w", pady=(10, 0))
        self.content_text = tk.Text(right_frame, width=55, height=10)
        self.content_text.pack(anchor="w")

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(anchor="w", pady=15)

        ttk.Button(button_frame, text="Save Entry").pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Search").pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Attach File").pack(side="left")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCabinetApp(root)
    root.mainloop()