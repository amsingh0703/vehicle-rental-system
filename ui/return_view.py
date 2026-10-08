import customtkinter as ctk
from tkinter import messagebox
from ui.theme import *
from ui.widgets import DataTable
from models import RentalModel

class ReturnView(ctk.CTkFrame):
    """Return Vehicle View with automatic time-based billing and receipt popup."""
    def __init__(self, parent, current_user: dict, navigate_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.navigate_callback = navigate_callback

        self._build_header()
        self._build_table()
        self._build_actions()

        self.refresh_rentals()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="Return Vehicle & Auto-Calculate Rent", font=FONT_SUBHEADING)
        title.pack(side="left", padx=15, pady=12)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            header,
            placeholder_text="Search customer name, phone, vehicle...",
            textvariable=self.search_var,
            width=280,
            height=32
        )
        search_entry.pack(side="left", padx=10)
        search_entry.bind("<Return>", lambda e: self.refresh_rentals())

        search_btn = ctk.CTkButton(header, text="Search", width=80, height=32, command=self.refresh_rentals)
        search_btn.pack(side="left", padx=4)

        refresh_btn = ctk.CTkButton(header, text="Reset", width=70, height=32, fg_color="gray50", command=self._reset_search)
        refresh_btn.pack(side="left", padx=4)

    def _build_table(self):
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=5)

        columns = [
            ("id", "Rental ID", 70),
            ("vehicle_name", "Vehicle Name", 180),
            ("customer_name", "Customer", 130),
            ("customer_phone", "Phone", 110),
            ("customer_aadhar", "Aadhar", 120),
            ("rent_date", "Date", 90),
            ("rent_time", "Pickup Time", 85),
            ("rate_per_hour", "Rate/Hr (₹)", 80),
            ("staff_username", "Staff", 80),
            ("status", "Status", 75)
        ]

        self.table = DataTable(table_container, columns)
        self.table.pack(fill="both", expand=True)

    def _build_actions(self):
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(10, 15))

        calc_btn = ctk.CTkButton(
            action_bar,
            text="🧾 Calculate Bill & Return Vehicle",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=38,
            font=FONT_BODY_BOLD,
            command=self._open_billing_modal
        )
        calc_btn.pack(side="left", padx=5)

        self.count_lbl = ctk.CTkLabel(action_bar, text="", font=FONT_SMALL, text_color=("gray40", "gray60"))
        self.count_lbl.pack(side="right", padx=10)

    def _reset_search(self):
        self.search_var.set("")
        self.refresh_rentals()

    def refresh_rentals(self):
        query = self.search_var.get().strip()
        data = RentalModel.get_active_rentals(search_query=query)
        self.table.populate(data, tag_key="status")
        self.count_lbl.configure(text=f"{len(data)} active vehicle rentals on road")

    def _open_billing_modal(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an active rental record from the table first.")
            return

        rental_id = int(sel["id"])
        calc_data, err = RentalModel.preview_return_calculation(rental_id)
        if not calc_data:
            messagebox.showerror("Error", err)
            return

        # Modal Window
        modal = ctk.CTkToplevel(self)
        modal.title(f"Rental Invoice & Return - #{rental_id}")
        modal.geometry("520x620")
        modal.grab_set()
        modal.resizable(False, False)

        frame = ctk.CTkFrame(modal, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="🧾 Rental Return Invoice", font=FONT_HEADING).pack(pady=(12, 4))
        ctk.CTkLabel(frame, text=f"Transaction #{rental_id} | DriveEase Vehicle Rental", font=FONT_SMALL, text_color=("gray40", "gray60")).pack(pady=(0, 12))

        # Receipt Container Card
        receipt_box = ctk.CTkFrame(frame, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        receipt_box.pack(fill="both", expand=True, padx=15, pady=5)

        details = [
            ("Customer Name:", calc_data["customer_name"]),
            ("Vehicle Model:", calc_data["vehicle_name"]),
            ("Rental Pickup:", f"{calc_data['rent_date']} at {calc_data['rent_time']}"),
            ("Return Timestamp:", f"{calc_data['return_date']} at {calc_data['return_time']}"),
            ("Duration Used:", f"{calc_data['hours_used']:.2f} hours"),
            ("Hourly Rate:", f"₹{calc_data['rate_per_hour']:.2f} / hr"),
        ]

        for label, val in details:
            row = ctk.CTkFrame(receipt_box, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(row, text=label, font=FONT_BODY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=FONT_BODY_BOLD, anchor="e").pack(side="right")

        # Divider line
        div = ctk.CTkFrame(receipt_box, height=2, fg_color=COLOR_CARD_BORDER)
        div.pack(fill="x", padx=15, pady=10)

        # Big Total Due
        total_row = ctk.CTkFrame(receipt_box, fg_color="transparent")
        total_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(total_row, text="Total Amount Due:", font=FONT_SUBHEADING).pack(side="left")
        ctk.CTkLabel(total_row, text=f"₹{calc_data['total_rent']:,.2f}", font=(FONT_FAMILY, 22, "bold"), text_color=COLOR_ACCENT[1]).pack(side="right")

        def confirm_return():
            success, msg, _ = RentalModel.process_return(rental_id)
            if success:
                messagebox.showinfo("Return Completed", msg)
                modal.destroy()
                self.refresh_rentals()
            else:
                messagebox.showerror("Error", msg)

        # Confirm & Close Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkButton(
            btn_frame,
            text="Confirm Return & Payment",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            height=40,
            font=FONT_BODY_BOLD,
            command=confirm_return
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="gray50",
            hover_color="gray40",
            height=40,
            command=modal.destroy
        ).pack(side="right", fill="x", expand=True, padx=(6, 0))
