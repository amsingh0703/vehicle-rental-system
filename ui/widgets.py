import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from ui.theme import *

class StatCard(ctk.CTkFrame):
    """Modern statistic indicator card with title, large metric value, and accent color."""
    def __init__(self, parent, title: str, value: str, subtitle: str = "", accent_color=None, width=190, height=105):
        super().__init__(parent, width=width, height=height, corner_radius=12, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER)
        self.pack_propagate(False)

        # Top Accent indicator line
        indicator = ctk.CTkFrame(self, height=4, corner_radius=2, fg_color=accent_color or COLOR_PRIMARY)
        indicator.pack(fill="x", side="top", padx=12, pady=(8, 4))

        # Title Label
        self.title_lbl = ctk.CTkLabel(self, text=title, font=FONT_SMALL, text_color=("gray30", "gray70"), anchor="w")
        self.title_lbl.pack(fill="x", padx=14, pady=(2, 0))

        # Value Label
        self.val_lbl = ctk.CTkLabel(self, text=value, font=FONT_STAT_VAL, anchor="w")
        self.val_lbl.pack(fill="x", padx=14, pady=(0, 2))

        # Subtitle
        if subtitle:
            self.sub_lbl = ctk.CTkLabel(self, text=subtitle, font=FONT_SMALL, text_color=("gray40", "gray60"), anchor="w")
            self.sub_lbl.pack(fill="x", padx=14, pady=(0, 4))

    def update_value(self, new_value: str, new_subtitle: str = None):
        self.val_lbl.configure(text=new_value)
        if new_subtitle and hasattr(self, 'sub_lbl'):
            self.sub_lbl.configure(text=new_subtitle)


class DataTable(ctk.CTkFrame):
    """Reusable Treeview table with scrollbars and alternating row tags."""
    def __init__(self, parent, columns: list[tuple[str, str, int]], on_select=None):
        """
        columns: List of tuples (col_id, display_heading, width)
        """
        super().__init__(parent, corner_radius=10, fg_color="transparent")
        self.columns = columns
        self.col_ids = [c[0] for c in columns]
        self.on_select = on_select

        # Setup modern Treeview styling
        self._setup_style()

        # Container for table and scrollbars
        self.table_container = ctk.CTkFrame(self, corner_radius=8)
        self.table_container.pack(fill="both", expand=True)

        self.y_scroll = ctk.CTkScrollbar(self.table_container, orientation="vertical")
        self.y_scroll.pack(side="right", fill="y", padx=(0, 2), pady=2)

        self.x_scroll = ctk.CTkScrollbar(self.table_container, orientation="horizontal")
        self.x_scroll.pack(side="bottom", fill="x", padx=2, pady=(0, 2))

        self.tree = ttk.Treeview(
            self.table_container,
            columns=self.col_ids,
            show="headings",
            selectmode="browse",
            yscrollcommand=self.y_scroll.set,
            xscrollcommand=self.x_scroll.set
        )
        self.y_scroll.configure(command=self.tree.yview)
        self.x_scroll.configure(command=self.tree.xview)

        for col_id, heading_text, width in columns:
            self.tree.heading(col_id, text=heading_text, anchor="center")
            self.tree.column(col_id, width=width, minwidth=60, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Alternating row colors
        self.tree.tag_configure("even", background="#f8f9fa", foreground="#212529")
        self.tree.tag_configure("odd", background="#ffffff", foreground="#212529")
        self.tree.tag_configure("rented", background="#fff3cd", foreground="#856404")
        self.tree.tag_configure("available", background="#d4edda", foreground="#155724")

        if on_select:
            self.tree.bind("<<TreeviewSelect>>", lambda e: on_select(self.get_selected_values()))

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#212529",
            rowheight=32,
            fieldbackground="#ffffff",
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#2c3e50",
            foreground="#ffffff",
            padding=(6, 6),
            relief="flat"
        )
        style.map("Treeview.Heading", background=[("active", "#34495e")])
        style.map("Treeview", background=[("selected", "#3498db")], foreground=[("selected", "#ffffff")])

    def populate(self, rows_data: list[dict], tag_key: str = None):
        """Clears and inserts rows into the treeview."""
        self.clear()
        for idx, row in enumerate(rows_data):
            values = [row.get(cid, "") for cid in self.col_ids]
            tag = "even" if idx % 2 == 0 else "odd"
            if tag_key and tag_key in row:
                val = str(row[tag_key]).lower()
                if val == "available":
                    tag = "available"
                elif val in ["rented", "returned"]:
                    tag = "rented"
            self.tree.insert("", "end", values=values, tags=(tag,))

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected_values(self):
        selected_item = self.tree.focus()
        if not selected_item:
            return None
        return self.tree.item(selected_item, "values")

    def get_selected_dict(self):
        vals = self.get_selected_values()
        if not vals:
            return None
        return dict(zip(self.col_ids, vals))
