import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog

import auth_manager
import file_handler

ALL_ITEMS = "All Items"

COLORS = {
    "app_bg": "#F3F6FB",
    "sidebar": "#EAF1FA",
    "panel": "#FFFFFF",
    "panel_alt": "#F8FAFC",
    "card": "#FFFFFF",
    "card_hover": "#EEF4FF",
    "selected": "#DCEAFE",
    "selected_deep": "#C7DBFF",
    "accent": "#1E3A8A",
    "accent_hover": "#162D6B",
    "purple": "#5B3CC4",
    "purple_hover": "#472FA0",
    "danger": "#B42318",
    "danger_hover": "#8E1C13",
    "text": "#0F172A",
    "muted": "#64748B",
    "muted_light": "#94A3B8",
    "line": "#D9E2EF",
    "input": "#FAFBFE",
    "button_dark": "#1E293B",
    "button_dark_hover": "#0F172A",
    "success": "#0F766E",
    "success_hover": "#115E59"
}


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command,
        bg=None,
        hover_bg=None,
        fg="white",
        width=86,
        height=34,
        radius=14,
        font=("Arial", 10, "bold"),
        tooltip=""
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

        self.text = text
        self.command = command
        self.normal_bg = bg or COLORS["accent"]
        self.hover_bg = hover_bg or COLORS["accent_hover"]
        self.fg = fg
        self.radius = radius
        self.font = font
        self.width_value = width
        self.height_value = height
        self.tooltip_text = tooltip
        self.tooltip_window = None

        self.draw_button(self.normal_bg)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw_button(self, fill):
        self.delete("all")

        w = self.width_value
        h = self.height_value
        r = self.radius

        self.create_arc(0, 0, r * 2, r * 2, start=90, extent=90, fill=fill, outline=fill)
        self.create_arc(w - r * 2, 0, w, r * 2, start=0, extent=90, fill=fill, outline=fill)
        self.create_arc(w - r * 2, h - r * 2, w, h, start=270, extent=90, fill=fill, outline=fill)
        self.create_arc(0, h - r * 2, r * 2, h, start=180, extent=90, fill=fill, outline=fill)

        self.create_rectangle(r, 0, w - r, h, fill=fill, outline=fill)
        self.create_rectangle(0, r, w, h - r, fill=fill, outline=fill)

        self.create_text(
            w / 2,
            h / 2,
            text=self.text,
            fill=self.fg,
            font=self.font
        )

    def on_enter(self, event=None):
        self.draw_button(self.hover_bg)
        self.show_tooltip()

    def on_leave(self, event=None):
        self.draw_button(self.normal_bg)
        self.hide_tooltip()

    def on_click(self, event=None):
        self.hide_tooltip()
        self.command()

    def show_tooltip(self):
        if self.tooltip_text == "" or self.tooltip_window is not None:
            return

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.height_value + 6

        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.overrideredirect(True)
        self.tooltip_window.geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.tooltip_text,
            bg=COLORS["button_dark"],
            fg="white",
            font=("Arial", 9),
            padx=8,
            pady=4
        )
        label.pack()

    def hide_tooltip(self):
        if self.tooltip_window is not None:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)

        self.canvas = tk.Canvas(
            self,
            bg=bg,
            highlightthickness=0,
            bd=0
        )

        self.inner = tk.Frame(self.canvas, bg=bg)

        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_inner)

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_inner(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)


class NoteCard(tk.Frame):
    def __init__(self, parent, entry, selected, command):
        border = COLORS["accent"] if selected else COLORS["line"]
        inner_bg = COLORS["selected"] if selected else COLORS["card"]

        super().__init__(
            parent,
            bg=border,
            padx=1,
            pady=1,
            cursor="hand2"
        )

        self.entry = entry
        self.command = command
        self.normal_inner = inner_bg
        self.hover_inner = COLORS["card_hover"]

        self.inner = tk.Frame(self, bg=inner_bg, padx=14, pady=12, cursor="hand2")
        self.inner.pack(fill="both", expand=True)

        title = entry["title"]

        if entry["is_favourite"] == "True":
            title = "★ " + title

        self.title_label = tk.Label(
            self.inner,
            text=self.shorten(title, 36),
            bg=inner_bg,
            fg=COLORS["text"],
            font=("Arial", 13, "bold"),
            anchor="w",
            cursor="hand2"
        )
        self.title_label.pack(fill="x", anchor="w")

        preview = entry["content"].replace("\n", " ").strip()

        if preview == "":
            preview = "No additional details"

        self.preview_label = tk.Label(
            self.inner,
            text=self.shorten(preview, 72),
            bg=inner_bg,
            fg=COLORS["muted"],
            font=("Arial", 10),
            anchor="w",
            justify="left",
            cursor="hand2"
        )
        self.preview_label.pack(fill="x", anchor="w", pady=(5, 8))

        footer_text = entry["category"]

        if entry["status"] == "Archived":
            footer_text += "  •  Archived"

        if entry["attachment_path"] != "":
            footer_text += "  •  Attached"

        self.footer_label = tk.Label(
            self.inner,
            text=footer_text,
            bg=inner_bg,
            fg=COLORS["muted_light"],
            font=("Arial", 9),
            anchor="w",
            cursor="hand2"
        )
        self.footer_label.pack(fill="x", anchor="w")

        self.widgets = [
            self,
            self.inner,
            self.title_label,
            self.preview_label,
            self.footer_label
        ]

        for widget in self.widgets:
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)

    def on_click(self, event=None):
        self.command(self.entry["entry_id"])

    def on_enter(self, event=None):
        for widget in self.widgets:
            if widget != self:
                widget.configure(bg=self.hover_inner)

    def on_leave(self, event=None):
        for widget in self.widgets:
            if widget != self:
                widget.configure(bg=self.normal_inner)

    def shorten(self, text, limit):
        text = text.strip()

        if len(text) <= limit:
            return text

        return text[:limit - 1].rstrip() + "…"


class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cabinet")
        self.root.geometry("560x560")
        self.root.minsize(500, 520)
        self.root.configure(bg=COLORS["app_bg"])

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.logo_image = None

        self.build_layout()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_layout(self):
        self.clear_root()

        wrapper = tk.Frame(self.root, bg=COLORS["app_bg"])
        wrapper.pack(fill="both", expand=True)

        card = tk.Frame(
            wrapper,
            bg=COLORS["panel"],
            padx=36,
            pady=32,
            highlightbackground=COLORS["line"],
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=470, height=475)

        logo_path = os.path.join("assets", "file_cabinet_logo.png")

        if os.path.exists(logo_path):
            try:
                self.logo_image = tk.PhotoImage(file=logo_path)
                logo_label = tk.Label(
                    card,
                    image=self.logo_image,
                    bg=COLORS["panel"]
                )
                logo_label.pack(pady=(0, 16))
            except tk.TclError:
                self.show_text_logo(card)
        else:
            self.show_text_logo(card)

        subtitle = tk.Label(
            card,
            text="Login to access your local filing cabinet",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 11)
        )
        subtitle.pack(pady=(0, 24))

        username_label = tk.Label(
            card,
            text="Username",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 10, "bold")
        )
        username_label.pack(anchor="w")

        self.username_entry = tk.Entry(
            card,
            textvariable=self.username_var,
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
            font=("Arial", 12)
        )
        self.username_entry.pack(fill="x", ipady=10, pady=(5, 12))

        password_label = tk.Label(
            card,
            text="Password",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 10, "bold")
        )
        password_label.pack(anchor="w")

        self.password_entry = tk.Entry(
            card,
            textvariable=self.password_var,
            show="*",
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
            font=("Arial", 12)
        )
        self.password_entry.pack(fill="x", ipady=10, pady=(5, 18))
        self.password_entry.bind("<Return>", lambda event: self.login())

        button_row = tk.Frame(card, bg=COLORS["panel"])
        button_row.pack(fill="x", pady=(0, 8))

        login_button = RoundedButton(
            button_row,
            "Login",
            self.login,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=185,
            height=38,
            tooltip="Login to your account"
        )
        login_button.pack(side="left", padx=(0, 10))

        create_button = RoundedButton(
            button_row,
            "Create Account",
            self.create_account,
            bg=COLORS["purple"],
            hover_bg=COLORS["purple_hover"],
            width=185,
            height=38,
            tooltip="Create a new account"
        )
        create_button.pack(side="right")

        self.status_label = tk.Label(
            card,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["danger"],
            font=("Arial", 10),
            wraplength=360
        )
        self.status_label.pack(pady=(12, 0))

        self.username_entry.focus_set()

    def show_text_logo(self, parent):
        logo = tk.Label(
            parent,
            text="File Cabinet",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Arial", 30, "bold")
        )
        logo.pack(pady=(0, 8))

        tagline = tk.Label(
            parent,
            text="ORGANIZE. PROTECT. ACCESS.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 10, "bold")
        )
        tagline.pack(pady=(0, 14))

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        success, message = auth_manager.login(username, password)

        if success:
            self.open_app(username)
        else:
            self.status_label.configure(text=message)

    def create_account(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        success, message = auth_manager.create_account(username, password)

        if success:
            messagebox.showinfo("Account Created", message)
            self.open_app(username)
        else:
            self.status_label.configure(text=message)

    def open_app(self, username):
        file_handler.set_current_user(username)

        for widget in self.root.winfo_children():
            widget.destroy()

        FileCabinetApp(self.root, username)


class FileCabinetApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username

        self.root.title("File Cabinet")
        self.root.geometry("1180x720")
        self.root.minsize(1000, 620)
        self.root.configure(bg=COLORS["app_bg"])

        self.entries = file_handler.load_entries()
        self.categories = file_handler.load_categories()

        self.selected_category = ALL_ITEMS
        self.selected_entry_id = None
        self.visible_entries = []
        self.search_var = tk.StringVar()
        self.show_archived_var = tk.BooleanVar(value=False)

        self.build_layout()

        self.search_var.trace_add("write", lambda *args: self.refresh_notes())

        self.refresh_categories()
        self.refresh_notes()
        self.show_empty_preview()
        self.show_status(f"Logged in as {self.username}")

    def build_layout(self):
        self.root.grid_columnconfigure(0, weight=0, minsize=245)
        self.root.grid_columnconfigure(1, weight=0, minsize=390)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.notes_panel = tk.Frame(self.root, bg=COLORS["panel_alt"])
        self.notes_panel.grid(row=0, column=1, sticky="nsew")

        self.preview_panel = tk.Frame(self.root, bg=COLORS["app_bg"])
        self.preview_panel.grid(row=0, column=2, sticky="nsew")

        self.build_sidebar()
        self.build_notes_panel()
        self.build_preview_panel()

    def build_sidebar(self):
        top = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        top.pack(fill="x", padx=18, pady=(20, 16))

        tk.Label(
            top,
            text="File Cabinet",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("Arial", 21, "bold")
        ).pack(anchor="w")

        tk.Label(
            top,
            text=f"Signed in as {self.username}",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Arial", 10)
        ).pack(anchor="w", pady=(4, 0))

        button_row = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        button_row.pack(fill="x", padx=18, pady=(2, 14))

        RoundedButton(
            button_row,
            "+",
            self.add_category,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=38,
            height=34,
            tooltip="Add folder"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            button_row,
            "−",
            self.delete_category,
            bg=COLORS["button_dark"],
            hover_bg=COLORS["button_dark_hover"],
            width=38,
            height=34,
            tooltip="Delete selected folder"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            button_row,
            "Backup",
            self.backup_data,
            bg=COLORS["purple"],
            hover_bg=COLORS["purple_hover"],
            width=92,
            height=34,
            tooltip="Create backup"
        ).pack(side="right")

        self.category_scroll = ScrollFrame(self.sidebar, COLORS["sidebar"])
        self.category_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        bottom = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        bottom.pack(fill="x", padx=18, pady=(0, 18))

        self.sidebar_footer = tk.Label(
            bottom,
            text="",
            bg=COLORS["sidebar"],
            fg=COLORS["muted_light"],
            font=("Arial", 9)
        )
        self.sidebar_footer.pack(side="left")

        RoundedButton(
            bottom,
            "Logout",
            self.logout,
            bg=COLORS["button_dark"],
            hover_bg=COLORS["button_dark_hover"],
            width=82,
            height=32,
            font=("Arial", 9, "bold"),
            tooltip="Logout"
        ).pack(side="right")

    def build_notes_panel(self):
        header = tk.Frame(self.notes_panel, bg=COLORS["panel_alt"])
        header.pack(fill="x", padx=20, pady=(20, 12))

        self.notes_heading = tk.Label(
            header,
            text="All Items",
            bg=COLORS["panel_alt"],
            fg=COLORS["text"],
            font=("Arial", 20, "bold")
        )
        self.notes_heading.pack(side="left")

        RoundedButton(
            header,
            "+",
            self.new_entry,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=40,
            height=34,
            tooltip="New entry"
        ).pack(side="right")

        search_frame = tk.Frame(
            self.notes_panel,
            bg=COLORS["panel"],
            padx=12,
            pady=9,
            highlightbackground=COLORS["line"],
            highlightthickness=1
        )
        search_frame.pack(fill="x", padx=20, pady=(0, 12))

        tk.Label(
            search_frame,
            text="Search",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=0,
            font=("Arial", 11)
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

        clear_button = tk.Label(
            search_frame,
            text="×",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 13, "bold"),
            cursor="hand2"
        )
        clear_button.pack(side="right", padx=(8, 0))
        clear_button.bind("<Button-1>", lambda event: self.clear_search())
        clear_button.bind("<Enter>", lambda event: clear_button.configure(fg=COLORS["accent"]))
        clear_button.bind("<Leave>", lambda event: clear_button.configure(fg=COLORS["muted"]))

        filter_row = tk.Frame(self.notes_panel, bg=COLORS["panel_alt"])
        filter_row.pack(fill="x", padx=20, pady=(0, 8))

        self.note_count_label = tk.Label(
            filter_row,
            text="",
            bg=COLORS["panel_alt"],
            fg=COLORS["muted"],
            font=("Arial", 10)
        )
        self.note_count_label.pack(side="left")

        self.archive_check = tk.Checkbutton(
            filter_row,
            text="Show archived",
            variable=self.show_archived_var,
            command=self.refresh_notes,
            bg=COLORS["panel_alt"],
            fg=COLORS["muted"],
            selectcolor=COLORS["panel"],
            activebackground=COLORS["panel_alt"],
            activeforeground=COLORS["text"],
            font=("Arial", 10)
        )
        self.archive_check.pack(side="right")

        self.notes_scroll = ScrollFrame(self.notes_panel, COLORS["panel_alt"])
        self.notes_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def build_preview_panel(self):
        self.preview_card = tk.Frame(
            self.preview_panel,
            bg=COLORS["panel"],
            padx=26,
            pady=24,
            highlightbackground=COLORS["line"],
            highlightthickness=1
        )
        self.preview_card.pack(fill="both", expand=True, padx=22, pady=22)

        title_area = tk.Frame(self.preview_card, bg=COLORS["panel"])
        title_area.pack(fill="x")

        self.preview_title = tk.Label(
            title_area,
            text="Select an entry",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Arial", 24, "bold"),
            anchor="w"
        )
        self.preview_title.pack(anchor="w")

        self.preview_meta = tk.Label(
            title_area,
            text="Choose an item from the middle panel.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 11),
            anchor="w"
        )
        self.preview_meta.pack(anchor="w", pady=(6, 0))

        actions = tk.Frame(self.preview_card, bg=COLORS["panel"])
        actions.pack(fill="x", pady=(18, 0))

        RoundedButton(
            actions,
            "★",
            self.toggle_favourite,
            bg=COLORS["purple"],
            hover_bg=COLORS["purple_hover"],
            width=42,
            height=34,
            tooltip="Mark as favourite"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            actions,
            "✎",
            self.edit_entry,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=42,
            height=34,
            tooltip="Edit entry"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            actions,
            "↗",
            self.open_attachment,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=42,
            height=34,
            tooltip="Open attachment"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            actions,
            "A",
            self.archive_or_restore_entry,
            bg=COLORS["button_dark"],
            hover_bg=COLORS["button_dark_hover"],
            width=42,
            height=34,
            tooltip="Archive or restore entry"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            actions,
            "×",
            self.delete_entry,
            bg=COLORS["danger"],
            hover_bg=COLORS["danger_hover"],
            width=42,
            height=34,
            tooltip="Delete entry"
        ).pack(side="left")

        self.line = tk.Frame(self.preview_card, bg=COLORS["line"], height=1)
        self.line.pack(fill="x", pady=18)

        self.attachment_label = tk.Label(
            self.preview_card,
            text="",
            bg=COLORS["selected"],
            fg=COLORS["accent"],
            font=("Arial", 10, "bold"),
            padx=12,
            pady=7,
            cursor="hand2"
        )
        self.attachment_label.bind("<Button-1>", lambda event: self.open_attachment())

        self.content_text = tk.Text(
            self.preview_card,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=0,
            wrap="word",
            font=("Arial", 14),
            spacing1=3,
            spacing3=8
        )

        self.empty_message = tk.Label(
            self.preview_card,
            text="No entry selected\n\nChoose an item from the middle panel to view it here.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 16),
            justify="center"
        )

        self.status_label = tk.Label(
            self.preview_card,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["muted_light"],
            font=("Arial", 9)
        )
        self.status_label.pack(side="bottom", anchor="w", pady=(10, 0))

    def refresh_categories(self):
        for widget in self.category_scroll.inner.winfo_children():
            widget.destroy()

        self.create_category_button(ALL_ITEMS)

        for category in self.categories:
            self.create_category_button(category)

        self.sidebar_footer.configure(text=f"{len(self.categories)} folders")

    def create_category_button(self, category):
        selected = category == self.selected_category
        bg = COLORS["selected_deep"] if selected else COLORS["sidebar"]
        fg = COLORS["text"] if selected else COLORS["muted"]

        button = tk.Label(
            self.category_scroll.inner,
            text=category,
            bg=bg,
            fg=fg,
            padx=14,
            pady=11,
            anchor="w",
            font=("Arial", 12, "bold" if selected else "normal"),
            cursor="hand2"
        )
        button.pack(fill="x", pady=2)

        button.bind("<Button-1>", lambda event, name=category: self.select_category(name))
        button.bind("<Enter>", lambda event: button.configure(bg=COLORS["card_hover"]))
        button.bind("<Leave>", lambda event, original=bg: button.configure(bg=original))

    def select_category(self, category):
        self.selected_category = category
        self.selected_entry_id = None

        self.refresh_categories()
        self.refresh_notes()
        self.show_empty_preview()

    def refresh_notes(self):
        for widget in self.notes_scroll.inner.winfo_children():
            widget.destroy()

        self.visible_entries = self.get_visible_entries()
        self.notes_heading.configure(text=self.selected_category)

        count = len(self.visible_entries)
        word = "entry" if count == 1 else "entries"
        self.note_count_label.configure(text=f"{count} {word}")

        if count == 0:
            tk.Label(
                self.notes_scroll.inner,
                text="No entries found.",
                bg=COLORS["panel_alt"],
                fg=COLORS["muted"],
                font=("Arial", 12)
            ).pack(anchor="w", padx=14, pady=20)
            return

        for entry in self.visible_entries:
            card = NoteCard(
                self.notes_scroll.inner,
                entry,
                entry["entry_id"] == self.selected_entry_id,
                self.select_entry
            )
            card.pack(fill="x", padx=6, pady=6)

    def get_visible_entries(self):
        keyword = self.search_var.get().strip().lower()
        show_archived = self.show_archived_var.get()

        results = []

        for entry in self.entries:
            if not show_archived and entry["status"] == "Archived":
                continue

            if self.selected_category != ALL_ITEMS and entry["category"] != self.selected_category:
                continue

            searchable_text = (
                entry["title"] + " " +
                entry["category"] + " " +
                entry["content"] + " " +
                os.path.basename(entry["attachment_path"])
            ).lower()

            if keyword != "" and keyword not in searchable_text:
                continue

            results.append(entry)

        results.sort(key=self.sort_key)
        return results

    def sort_key(self, entry):
        try:
            modified = datetime.strptime(entry["date_modified"], "%Y-%m-%d %H:%M").timestamp()
        except ValueError:
            modified = 0

        favourite_order = 0 if entry["is_favourite"] == "True" else 1
        archive_order = 0 if entry["status"] == "Active" else 1

        return (favourite_order, archive_order, -modified)

    def select_entry(self, entry_id):
        self.selected_entry_id = entry_id
        self.refresh_notes()
        self.show_entry_preview()

    def get_selected_entry(self):
        for entry in self.entries:
            if entry["entry_id"] == self.selected_entry_id:
                return entry

        return None

    def show_empty_preview(self):
        self.preview_title.configure(text="Select an entry")
        self.preview_meta.configure(text="Choose an item from the middle panel.")

        self.attachment_label.pack_forget()
        self.content_text.pack_forget()
        self.empty_message.pack(fill="both", expand=True)

    def show_entry_preview(self):
        entry = self.get_selected_entry()

        if entry is None:
            self.show_empty_preview()
            return

        self.empty_message.pack_forget()

        title = entry["title"]

        if entry["is_favourite"] == "True":
            title = "★ " + title

        self.preview_title.configure(text=title)

        meta = entry["category"]
        meta += "  •  Created " + self.format_date(entry["date_created"])
        meta += "  •  Edited " + self.format_date(entry["date_modified"])

        if entry["status"] == "Archived":
            meta += "  •  Archived"

        self.preview_meta.configure(text=meta)

        if entry["attachment_path"] != "":
            filename = os.path.basename(entry["attachment_path"])
            self.attachment_label.configure(text="Attachment: " + filename)
            self.attachment_label.pack(anchor="w", pady=(0, 14))
        else:
            self.attachment_label.pack_forget()

        self.content_text.pack(fill="both", expand=True)
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, entry["content"])
        self.content_text.configure(state="disabled")

    def add_category(self):
        category = simpledialog.askstring("New Folder", "Enter folder name:")

        if category is None:
            return

        category = category.strip()

        if category == "":
            messagebox.showerror("Error", "Folder name cannot be empty.")
            return

        if category in self.categories:
            messagebox.showerror("Error", "That folder already exists.")
            return

        self.categories.append(category)
        self.categories.sort(key=str.lower)
        file_handler.save_categories(self.categories)

        self.selected_category = category
        self.refresh_categories()
        self.refresh_notes()
        self.show_status("Folder created")

    def delete_category(self):
        if self.selected_category == ALL_ITEMS:
            messagebox.showerror("Error", "You cannot delete All Items.")
            return

        for entry in self.entries:
            if entry["category"] == self.selected_category:
                messagebox.showerror("Error", "This folder still contains entries.")
                return

        confirm = messagebox.askyesno("Delete Folder", f"Delete '{self.selected_category}'?")

        if confirm:
            self.categories.remove(self.selected_category)
            file_handler.save_categories(self.categories)

            self.selected_category = ALL_ITEMS
            self.refresh_categories()
            self.refresh_notes()
            self.show_empty_preview()
            self.show_status("Folder deleted")

    def new_entry(self):
        if self.selected_category == ALL_ITEMS:
            messagebox.showerror("Error", "Select a folder before creating an entry.")
            return

        self.open_editor("new", self.selected_category)

    def edit_entry(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Select an entry first.")
            return

        self.open_editor("edit", entry["category"], entry)

    def open_editor(self, mode, category, entry=None):
        editor = tk.Toplevel(self.root)
        editor.title("New Entry" if mode == "new" else "Edit Entry")
        editor.geometry("660x590")
        editor.minsize(560, 500)
        editor.configure(bg=COLORS["app_bg"])
        editor.transient(self.root)
        editor.grab_set()

        shell = tk.Frame(
            editor,
            bg=COLORS["panel"],
            padx=24,
            pady=24,
            highlightbackground=COLORS["line"],
            highlightthickness=1
        )
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            shell,
            text=category,
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        title_entry = tk.Entry(
            shell,
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
            font=("Arial", 18, "bold")
        )
        title_entry.pack(fill="x", pady=(10, 14), ipady=10)

        content_text = tk.Text(
            shell,
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
            wrap="word",
            font=("Arial", 13),
            padx=12,
            pady=12,
            height=12
        )
        content_text.pack(fill="both", expand=True)

        attachment_var = tk.StringVar()

        attachment_row = tk.Frame(shell, bg=COLORS["panel"])
        attachment_row.pack(fill="x", pady=(14, 0))

        attachment_label = tk.Label(
            attachment_row,
            text="No attachment",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Arial", 10)
        )
        attachment_label.pack(side="left")

        def update_attachment_label():
            path = attachment_var.get().strip()

            if path == "":
                attachment_label.configure(text="No attachment")
            else:
                attachment_label.configure(text="Attached: " + os.path.basename(path))

        def browse_file():
            file_path = filedialog.askopenfilename(title="Select file")

            if file_path:
                attachment_var.set(file_path)
                update_attachment_label()

        def clear_attachment():
            attachment_var.set("")
            update_attachment_label()

        def clear_fields():
            confirm = messagebox.askyesno(
                "Clear Fields",
                "Clear the title, content and attachment fields?"
            )

            if confirm:
                title_entry.delete(0, tk.END)
                content_text.delete("1.0", tk.END)
                attachment_var.set("")
                update_attachment_label()
                title_entry.focus_set()

        def save_entry():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            attachment_path = attachment_var.get().strip()

            if title == "":
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            if attachment_path != "" and not os.path.exists(attachment_path):
                confirm = messagebox.askyesno(
                    "Attachment Warning",
                    "This file path does not exist. Save it anyway?"
                )

                if not confirm:
                    return

            now = file_handler.get_current_date()

            if mode == "new":
                new_entry = {
                    "entry_id": file_handler.get_next_entry_id(self.entries),
                    "title": title,
                    "category": category,
                    "content": content,
                    "attachment_path": attachment_path,
                    "date_created": now,
                    "date_modified": now,
                    "is_favourite": "False",
                    "status": "Active"
                }

                self.entries.append(new_entry)
                self.selected_entry_id = new_entry["entry_id"]

            else:
                for saved_entry in self.entries:
                    if saved_entry["entry_id"] == entry["entry_id"]:
                        saved_entry["title"] = title
                        saved_entry["content"] = content
                        saved_entry["attachment_path"] = attachment_path
                        saved_entry["date_modified"] = now
                        self.selected_entry_id = saved_entry["entry_id"]
                        break

            file_handler.save_entries(self.entries)

            self.refresh_notes()
            self.show_entry_preview()
            self.show_status("Entry saved")

            editor.destroy()

        toolbar = tk.Frame(shell, bg=COLORS["panel"])
        toolbar.pack(fill="x", pady=(14, 0))

        RoundedButton(
            toolbar,
            "Attach",
            browse_file,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=82,
            height=34,
            tooltip="Attach a file"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            toolbar,
            "Clear File",
            clear_attachment,
            bg=COLORS["button_dark"],
            hover_bg=COLORS["button_dark_hover"],
            width=92,
            height=34,
            tooltip="Remove attachment"
        ).pack(side="left", padx=(0, 8))

        RoundedButton(
            toolbar,
            "Clear Fields",
            clear_fields,
            bg=COLORS["purple"],
            hover_bg=COLORS["purple_hover"],
            width=112,
            height=34,
            tooltip="Clear title, content and attachment"
        ).pack(side="left")

        RoundedButton(
            toolbar,
            "Save Entry",
            save_entry,
            bg=COLORS["accent"],
            hover_bg=COLORS["accent_hover"],
            width=112,
            height=36,
            tooltip="Save entry"
        ).pack(side="right")

        if mode == "edit" and entry is not None:
            title_entry.insert(0, entry["title"])
            content_text.insert(tk.END, entry["content"])
            attachment_var.set(entry["attachment_path"])
            update_attachment_label()

        title_entry.focus_set()

    def delete_entry(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Select an entry first.")
            return

        confirm = messagebox.askyesno("Delete Entry", f"Delete '{entry['title']}' permanently?")

        if confirm:
            self.entries = [
                saved_entry for saved_entry in self.entries
                if saved_entry["entry_id"] != entry["entry_id"]
            ]

            file_handler.save_entries(self.entries)

            self.selected_entry_id = None
            self.refresh_notes()
            self.show_empty_preview()
            self.show_status("Entry deleted")

    def toggle_favourite(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Select an entry first.")
            return

        if entry["is_favourite"] == "True":
            entry["is_favourite"] = "False"
        else:
            entry["is_favourite"] = "True"

        entry["date_modified"] = file_handler.get_current_date()
        file_handler.save_entries(self.entries)

        self.refresh_notes()
        self.show_entry_preview()
        self.show_status("Favourite updated")

    def archive_or_restore_entry(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Select an entry first.")
            return

        if entry["status"] == "Archived":
            entry["status"] = "Active"
            message = "Entry restored"
        else:
            entry["status"] = "Archived"
            message = "Entry archived"

        entry["date_modified"] = file_handler.get_current_date()
        file_handler.save_entries(self.entries)

        if entry["status"] == "Archived" and not self.show_archived_var.get():
            self.selected_entry_id = None
            self.show_empty_preview()

        self.refresh_notes()
        self.show_status(message)

    def open_attachment(self):
        entry = self.get_selected_entry()

        if entry is None:
            messagebox.showerror("Error", "Select an entry first.")
            return

        path = entry["attachment_path"]

        if path == "":
            messagebox.showerror("Error", "This entry does not have an attachment.")
            return

        if not os.path.exists(path):
            messagebox.showerror(
                "Error",
                "The attached file could not be found. It may have been moved or deleted."
            )
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])

        except Exception:
            messagebox.showerror("Error", "The file could not be opened.")

    def backup_data(self):
        try:
            file_handler.backup_data()
            messagebox.showinfo("Backup Complete", "Backup files were created successfully.")
            self.show_status("Backup created")

        except Exception:
            messagebox.showerror("Error", "Backup could not be created.")

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")

        if not confirm:
            return

        self.entries = []
        self.categories = []
        self.selected_entry_id = None
        file_handler.clear_current_user()

        for widget in self.root.winfo_children():
            widget.destroy()

        LoginScreen(self.root)

    def clear_search(self):
        self.search_var.set("")
        self.refresh_notes()

    def show_status(self, message):
        self.status_label.configure(text=message)
        self.root.after(2500, lambda: self.status_label.configure(text=""))

    def format_date(self, date_text):
        try:
            parsed = datetime.strptime(date_text, "%Y-%m-%d %H:%M")
            return parsed.strftime("%d %b %Y")
        except ValueError:
            return date_text


if __name__ == "__main__":
    auth_manager.setup_auth_file()

    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()
