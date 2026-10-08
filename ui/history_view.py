import customtkinter as ctk
from tkinter import messagebox
from ui.theme import *
from ui.widgets import DataTable
from models import RentalModel, UserModel

class HistoryView(ctk.CTkFrame):
    """Rental History and Transaction Audit Log."""
    def __init__(self, parent, current_user: dict, navigate_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.navigate_callback = navigate_callback

        self._build_header_filters()
        self._build_table()
        self._build_summary_bar()

        self.refresh_history()

    def _build_header_filters(self):
        filter_box = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        filter_box.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(filter_box, text="Rental Audit Log & History", font=FONT_SUBHEADING)
        title.pack(side="left", padx=15, pady=12)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filter_box,
            placeholder_text="Search customer, vehicle, aadhar...",
            textvariable=self.search_var,
            width=240,
            height=32
        )
        search_entry.pack(side="left", padx=8)
        search_entry.bind("<Return>", lambda e: self.refresh_history())

        search_btn = ctk.CTkButton(filter_box, text="Search", width=75, height=32, command=self.refresh_history)
        search_btn.pack(side="left", padx=4)

        reset_btn = ctk.CTkButton(filter_box, text="Reset", width=65, height=32, fg_color="gray50", command=self._reset_filters)
        reset_btn.pack(side="left", padx=4)

        # Status Filter
        ctk.CTkLabel(filter_box, text="Status:", font=FONT_SMALL).pack(side="left", padx=(15, 4))
        self.status_filter = ctk.CTkOptionMenu(
            filter_box,
            values=["All", "Returned", "Rented"],
            width=105,
            height=32,
            command=lambda v: self.refresh_history()
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=4)

        # Staff filter
        ctk.CTkLabel(filter_box, text="Staff:", font=FONT_SMALL).pack(side="left", padx=(10, 4))
        staff_list = ["All"] + [s["username"] for s in UserModel.get_staff_list()]
        self.staff_filter = ctk.CTkOptionMenu(
            filter_box,
            values=staff_list,
            width=100,
            height=32,
            command=lambda v: self.refresh_history()
        )
        self.staff_filter.set("All")
        self.staff_filter.pack(side="left", padx=4)

    def _build_table(self):
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=5)

        columns = [
            ("id", "ID", 50),
            ("vehicle_name", "Vehicle Details", 170),
            ("customer_name", "Customer Name", 130),
            ("customer_phone", "Phone", 100),
            ("customer_aadhar", "Aadhar", 110),
            ("rent_date", "Rented Date", 90),
            ("return_date", "Return Date", 90),
            ("hours_used", "Hours", 60),
            ("rate_per_hour", "Rate (₹)", 70),
            ("total_rent", "Total (₹)", 85),
            ("staff_username", "Staff", 80),
            ("status", "Status", 80)
        ]

        self.table = DataTable(table_container, columns)
        self.table.pack(fill="both", expand=True)

    def _build_summary_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(10, 15))

        view_receipt_btn = ctk.CTkButton(
            bar,
            text="👁️ View Full Receipt",
            height=36,
            font=FONT_BODY_BOLD,
            command=self._view_receipt
        )
        view_receipt_btn.pack(side="left", padx=5)

        self.summary_lbl = ctk.CTkLabel(bar, text="", font=FONT_SMALL, text_color=("gray30", "gray70"))
        self.summary_lbl.pack(side="right", padx=10)

    def _reset_filters(self):
        self.search_var.set("")
        self.status_filter.set("All")
        self.staff_filter.set("All")
        self.refresh_history()

    def refresh_history(self):
        query = self.search_var.get().strip()
        status = self.status_filter.get()
        staff = self.staff_filter.get()

        data = RentalModel.get_rental_history(search_query=query, status_filter=status, staff_filter=staff)
        self.table.populate(data, tag_key="status")

        total_rev = sum(float(r["total_rent"] or 0) for r in data if r["status"] == "Returned")
        self.summary_lbl.configure(text=f"Total Records: {len(data)} | Revenue Collected: ₹{total_rev:,.2f}")

    def _view_receipt(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a rental record from the table.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Rental Transaction Record #{sel['id']}")
        modal.geometry("480x560")
        modal.grab_set()
        modal.resizable(False, False)

        frame = ctk.CTkFrame(modal, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Transaction Record", font=FONT_HEADING).pack(pady=(10, 4))
        ctk.CTkLabel(frame, text=f"Rental ID #{sel['id']} | Status: {sel['status']}", font=FONT_SMALL).pack(pady=(0, 15))

        card = ctk.CTkFrame(frame, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        card.pack(fill="both", expand=True, padx=15, pady=5)

        fields = [
            ("Vehicle:", sel["vehicle_name"]),
            ("Customer Name:", sel["customer_name"]),
            ("Customer Phone:", sel["customer_phone"]),
            ("Customer Aadhar:", sel["customer_aadhar"]),
            ("Rent Date:", sel["rent_date"]),
            ("Return Date:", sel["return_date"] or "Not returned yet"),
            ("Duration Used:", f"{float(sel['hours_used'] or 0):.2f} hrs"),
            ("Hourly Rate:", f"₹{float(sel['rate_per_hour'] or 0):.2f}"),
            ("Total Amount:", f"₹{float(sel['total_rent'] or 0):.2f}"),
            ("Handled by Staff:", sel["staff_username"] or "N/A"),
        ]

        for label, val in fields:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(row, text=label, font=FONT_BODY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=FONT_BODY_BOLD, anchor="e").pack(side="right")

        ctk.CTkButton(frame, text="Close", height=36, command=modal.destroy).pack(pady=(15, 10))
