import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.theme import *
from ui.widgets import DataTable
from models import VehicleModel, RentalModel
from auth import validate_aadhar, validate_phone

class RentView(ctk.CTkFrame):
    """Rental Dispatch View: Select available vehicle and record customer details."""
    def __init__(self, parent, current_user: dict, navigate_callback=None, preselected_vehicle_id=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.navigate_callback = navigate_callback
        self.preselected_id = preselected_vehicle_id

        self.available_vehicles = []
        self._build_ui()
        self.load_vehicles()

    def _build_ui(self):
        # Two-column layout: Form on Left, Available Vehicles on Right
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # Left Column - Form
        left_frame = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER, width=440)
        left_frame.pack(side="left", fill="y", padx=(0, 15), pady=0)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="New Rental Booking", font=FONT_SUBHEADING).pack(pady=(15, 5), padx=20, anchor="w")
        ctk.CTkLabel(left_frame, text="Customer identity and vehicle dispatch form", font=FONT_SMALL, text_color=("gray40", "gray60")).pack(padx=20, pady=(0, 15), anchor="w")

        # Vehicle Dropdown Selector
        ctk.CTkLabel(left_frame, text="Select Available Vehicle: *", font=FONT_BODY_BOLD).pack(anchor="w", padx=20, pady=(4, 2))
        self.vehicle_combo = ctk.CTkComboBox(left_frame, values=[], width=390, height=36, command=self._on_vehicle_selected)
        self.vehicle_combo.pack(padx=20, pady=(0, 8))

        # Vehicle summary info banner
        self.veh_info_banner = ctk.CTkLabel(left_frame, text="No vehicle selected.", font=FONT_SMALL, text_color=COLOR_PRIMARY[1], anchor="w", justify="left")
        self.veh_info_banner.pack(fill="x", padx=20, pady=(0, 12))

        # Customer Details
        ctk.CTkLabel(left_frame, text="Customer Full Name: *", font=FONT_BODY_BOLD).pack(anchor="w", padx=20, pady=(4, 2))
        self.name_entry = ctk.CTkEntry(left_frame, placeholder_text="e.g. Rahul Sharma", width=390, height=36)
        self.name_entry.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(left_frame, text="Aadhar Number (12 Digits): *", font=FONT_BODY_BOLD).pack(anchor="w", padx=20, pady=(4, 2))
        self.aadhar_entry = ctk.CTkEntry(left_frame, placeholder_text="12-digit number (e.g. 450943773007)", width=390, height=36)
        self.aadhar_entry.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(left_frame, text="Mobile Number (10 Digits): *", font=FONT_BODY_BOLD).pack(anchor="w", padx=20, pady=(4, 2))
        self.phone_entry = ctk.CTkEntry(left_frame, placeholder_text="10-digit mobile (e.g. 9876543210)", width=390, height=36)
        self.phone_entry.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(left_frame, text="Customer Village / City Address:", font=FONT_BODY_BOLD).pack(anchor="w", padx=20, pady=(4, 2))
        self.addr_entry = ctk.CTkEntry(left_frame, placeholder_text="Address / City", width=390, height=36)
        self.addr_entry.pack(padx=20, pady=(0, 15))

        # Submit Button
        submit_btn = ctk.CTkButton(
            left_frame,
            text="Confirm & Issue Vehicle",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            font=FONT_BODY_BOLD,
            height=42,
            command=self._submit_rental
        )
        submit_btn.pack(fill="x", padx=20, pady=(5, 15))

        # Right Column - Available Vehicles Table for easy clicking
        right_frame = ctk.CTkFrame(container, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True)

        right_header = ctk.CTkFrame(right_frame, fg_color="transparent")
        right_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(right_header, text="Available Vehicles Fleet", font=FONT_SUBHEADING).pack(side="left")

        refresh_btn = ctk.CTkButton(right_header, text="🔄 Refresh", width=90, height=30, command=self.load_vehicles)
        refresh_btn.pack(side="right")

        columns = [
            ("id", "ID", 50),
            ("vehicle_type", "Type", 70),
            ("name", "Make", 110),
            ("model", "Model", 160),
            ("transmission", "Trans", 90),
            ("rate_per_hour", "Rate/Hr (₹)", 90),
            ("status", "Status", 80)
        ]

        self.table = DataTable(right_frame, columns, on_select=self._on_table_row_click)
        self.table.pack(fill="both", expand=True)

    def load_vehicles(self):
        """Loads all available vehicles and populates both dropdown and table."""
        self.available_vehicles = VehicleModel.get_available()
        self.table.populate(self.available_vehicles, tag_key="status")

        options = [f"#{v['id']} - {v['name']} {v['model']} (₹{v['rate_per_hour']}/hr)" for v in self.available_vehicles]
        self.vehicle_combo.configure(values=options)

        if options:
            if self.preselected_id:
                # Find matching option
                matched = [opt for opt in options if opt.startswith(f"#{self.preselected_id} ")]
                if matched:
                    self.vehicle_combo.set(matched[0])
                    self._on_vehicle_selected(matched[0])
                    return
            self.vehicle_combo.set(options[0])
            self._on_vehicle_selected(options[0])
        else:
            self.vehicle_combo.set("No available vehicles")
            self.veh_info_banner.configure(text="⚠ All vehicles are currently rented or in maintenance.")

    def _on_vehicle_selected(self, choice):
        if not choice or choice.startswith("No available"):
            return
        try:
            v_id = int(choice.split("#")[1].split(" ")[0])
            for v in self.available_vehicles:
                if v["id"] == v_id:
                    self.selected_vehicle = v
                    txt = f"Selected: {v['name']} {v['model']} | Type: {v['vehicle_type']} | Rate: ₹{v['rate_per_hour']:.2f}/hr | Trans: {v['transmission']}"
                    self.veh_info_banner.configure(text=txt)
                    break
        except Exception:
            pass

    def _on_table_row_click(self, row_values):
        if not row_values:
            return
        v_id = row_values[0]
        for opt in self.vehicle_combo.cget("values"):
            if opt.startswith(f"#{v_id} "):
                self.vehicle_combo.set(opt)
                self._on_vehicle_selected(opt)
                break

    def _submit_rental(self):
        if not hasattr(self, 'selected_vehicle') or not self.selected_vehicle:
            messagebox.showerror("Error", "Please choose a vehicle to rent.")
            return

        cust_name = self.name_entry.get().strip()
        aadhar = self.aadhar_entry.get().strip()
        phone = self.phone_entry.get().strip()
        addr = self.addr_entry.get().strip() or "Local"

        # Validation checks
        if not cust_name:
            messagebox.showerror("Validation Error", "Customer name is required.")
            return

        valid_aadhar, err_aadhar = validate_aadhar(aadhar)
        if not valid_aadhar:
            messagebox.showerror("Aadhar Validation Error", err_aadhar)
            return

        valid_phone, err_phone = validate_phone(phone)
        if not valid_phone:
            messagebox.showerror("Phone Validation Error", err_phone)
            return

        # Confirm Dialog
        confirm_msg = (
            f"Confirm Rental Booking:\n\n"
            f"Vehicle: {self.selected_vehicle['name']} {self.selected_vehicle['model']}\n"
            f"Rate: ₹{self.selected_vehicle['rate_per_hour']}/hour\n"
            f"Customer: {cust_name}\n"
            f"Phone: {phone}\n"
            f"Aadhar: {aadhar}\n"
            f"Handled by Staff: {self.current_user.get('full_name')}\n\n"
            f"Proceed with booking?"
        )
        if not messagebox.askyesno("Confirm Rental", confirm_msg):
            return

        staff_uname = self.current_user.get("username", "Staff")
        success, msg = RentalModel.create_rental(
            vehicle_id=self.selected_vehicle["id"],
            customer_name=cust_name,
            customer_aadhar=aadhar,
            customer_phone=phone,
            customer_address=addr,
            staff_username=staff_uname
        )

        if success:
            messagebox.showinfo("Rental Successful", msg)
            # Clear form
            self.name_entry.delete(0, "end")
            self.aadhar_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.addr_entry.delete(0, "end")
            self.load_vehicles()
        else:
            messagebox.showerror("Rental Failed", msg)
