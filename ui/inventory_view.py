import customtkinter as ctk
from tkinter import messagebox
from ui.theme import *
from ui.widgets import DataTable
from models import VehicleModel
from auth import validate_rate, validate_year
import config

class InventoryView(ctk.CTkFrame):
    """Inventory Management View with live search, filters, CRUD operations, and quick rent."""
    def __init__(self, parent, current_user: dict, navigate_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.navigate_callback = navigate_callback
        self.is_admin = current_user.get("role") == "admin"

        self._build_header_and_filters()
        self._build_table()
        self._build_action_bar()

        self.refresh_table()

    def _build_header_and_filters(self):
        filter_box = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        filter_box.pack(fill="x", padx=20, pady=(15, 10))

        # Title & Subtitle inside filter box
        title_lbl = ctk.CTkLabel(filter_box, text="Vehicle Fleet & Inventory", font=FONT_SUBHEADING)
        title_lbl.pack(side="left", padx=15, pady=12)

        # Search Bar
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filter_box,
            placeholder_text="Search by name, model, fuel...",
            textvariable=self.search_var,
            width=230,
            height=32
        )
        search_entry.pack(side="left", padx=8, pady=10)
        search_entry.bind("<Return>", lambda e: self.refresh_table())

        search_btn = ctk.CTkButton(filter_box, text="Search", width=75, height=32, command=self.refresh_table)
        search_btn.pack(side="left", padx=4)

        clear_btn = ctk.CTkButton(filter_box, text="Reset", width=65, height=32, fg_color="gray50", hover_color="gray40", command=self._reset_filters)
        clear_btn.pack(side="left", padx=4)

        # Type Filter
        ctk.CTkLabel(filter_box, text="Type:", font=FONT_SMALL).pack(side="left", padx=(15, 4))
        self.type_filter = ctk.CTkOptionMenu(
            filter_box,
            values=["All", "Bike", "Car"],
            width=90,
            height=32,
            command=lambda v: self.refresh_table()
        )
        self.type_filter.set("All")
        self.type_filter.pack(side="left", padx=4)

        # Status Filter
        ctk.CTkLabel(filter_box, text="Status:", font=FONT_SMALL).pack(side="left", padx=(10, 4))
        self.status_filter = ctk.CTkOptionMenu(
            filter_box,
            values=["All", "Available", "Rented"],
            width=100,
            height=32,
            command=lambda v: self.refresh_table()
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=4)

    def _build_table(self):
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=5)

        columns = [
            ("id", "ID", 50),
            ("vehicle_type", "Type", 70),
            ("name", "Make / Brand", 120),
            ("model", "Model Details", 170),
            ("fuel_type", "Fuel", 90),
            ("transmission", "Gear / Trans", 100),
            ("engine", "Engine / Power", 110),
            ("model_year", "Year", 70),
            ("rate_per_hour", "Rate/Hr (₹)", 90),
            ("status", "Status", 95)
        ]

        self.table = DataTable(table_container, columns)
        self.table.pack(fill="both", expand=True)

    def _build_action_bar(self):
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(10, 15))

        # Rent Button (Available for both Admin & Staff)
        rent_btn = ctk.CTkButton(
            action_bar,
            text="⚡ Rent Selected Vehicle",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            height=36,
            font=FONT_BODY_BOLD,
            command=self._rent_selected
        )
        rent_btn.pack(side="left", padx=5)

        # Admin-only operations
        if self.is_admin:
            add_btn = ctk.CTkButton(
                action_bar,
                text="➕ Add New Vehicle",
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                height=36,
                command=self._open_add_modal
            )
            add_btn.pack(side="left", padx=5)

            edit_btn = ctk.CTkButton(
                action_bar,
                text="✏️ Edit Selected",
                height=36,
                command=self._open_edit_modal
            )
            edit_btn.pack(side="left", padx=5)

            delete_btn = ctk.CTkButton(
                action_bar,
                text="🗑️ Delete Vehicle",
                fg_color=COLOR_DANGER,
                hover_color=COLOR_DANGER_HOVER,
                height=36,
                command=self._delete_selected
            )
            delete_btn.pack(side="left", padx=5)

        # Total count indicator
        self.count_lbl = ctk.CTkLabel(action_bar, text="", font=FONT_SMALL, text_color=("gray40", "gray60"))
        self.count_lbl.pack(side="right", padx=10)

    def _reset_filters(self):
        self.search_var.set("")
        self.type_filter.set("All")
        self.status_filter.set("All")
        self.refresh_table()

    def refresh_table(self):
        search_q = self.search_var.get()
        v_type = self.type_filter.get()
        v_status = self.status_filter.get()

        data = VehicleModel.get_all(search_query=search_q, vehicle_type=v_type, status_filter=v_status)
        self.table.populate(data, tag_key="status")
        self.count_lbl.configure(text=f"Showing {len(data)} vehicles")

    def _rent_selected(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an Available vehicle from the table first.")
            return

        if sel.get("status") != config.STATUS_AVAILABLE:
            messagebox.showerror("Not Available", f"This vehicle is currently '{sel.get('status')}'. Only 'Available' vehicles can be rented.")
            return

        if self.navigate_callback:
            self.navigate_callback("rent", preselected_vehicle_id=int(sel["id"]))

    def _open_add_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add New Vehicle to Fleet")
        modal.geometry("500x580")
        modal.grab_set()
        modal.resizable(False, False)

        frame = ctk.CTkFrame(modal, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Add New Vehicle", font=FONT_SUBHEADING).pack(pady=(10, 15))

        # Fields
        vtype_var = ctk.StringVar(value="Bike")
        ctk.CTkLabel(frame, text="Vehicle Type:", font=FONT_SMALL).pack(anchor="w", padx=25)
        type_seg = ctk.CTkSegmentedButton(frame, values=["Bike", "Car"], variable=vtype_var)
        type_seg.pack(fill="x", padx=25, pady=(0, 8))

        name_entry = ctk.CTkEntry(frame, placeholder_text="Brand / Make (e.g. Honda, Hero, Tata)", height=35)
        name_entry.pack(fill="x", padx=25, pady=6)

        model_entry = ctk.CTkEntry(frame, placeholder_text="Model (e.g. Activa 6G, Nexon, Splendor)", height=35)
        model_entry.pack(fill="x", padx=25, pady=6)

        engine_entry = ctk.CTkEntry(frame, placeholder_text="Engine Capacity (e.g. 125cc, 1.2L Turbo)", height=35)
        engine_entry.pack(fill="x", padx=25, pady=6)

        fuel_var = ctk.StringVar(value="Petrol")
        ctk.CTkLabel(frame, text="Fuel Type:", font=FONT_SMALL).pack(anchor="w", padx=25)
        fuel_menu = ctk.CTkOptionMenu(frame, values=["Petrol", "Diesel", "Electric", "CNG", "Hybrid"], variable=fuel_var)
        fuel_menu.pack(fill="x", padx=25, pady=(0, 6))

        trans_var = ctk.StringVar(value="Manual")
        ctk.CTkLabel(frame, text="Transmission:", font=FONT_SMALL).pack(anchor="w", padx=25)
        trans_menu = ctk.CTkOptionMenu(frame, values=["Manual", "Automatic", "AMT", "CVT"], variable=trans_var)
        trans_menu.pack(fill="x", padx=25, pady=(0, 6))

        year_entry = ctk.CTkEntry(frame, placeholder_text="Model Year (e.g. 2023)", height=35)
        year_entry.insert(0, "2023")
        year_entry.pack(fill="x", padx=25, pady=6)

        rate_entry = ctk.CTkEntry(frame, placeholder_text="Rate per Hour in ₹ (e.g. 35.00)", height=35)
        rate_entry.pack(fill="x", padx=25, pady=6)

        def save_vehicle():
            name = name_entry.get().strip()
            model_val = model_entry.get().strip()
            if not name or not model_val:
                messagebox.showerror("Validation Error", "Brand Name and Model cannot be empty.")
                return

            valid_yr, err_yr, year_val = validate_year(year_entry.get())
            if not valid_yr:
                messagebox.showerror("Validation Error", err_yr)
                return

            valid_rt, err_rt, rate_val = validate_rate(rate_entry.get())
            if not valid_rt:
                messagebox.showerror("Validation Error", err_rt)
                return

            success, msg = VehicleModel.add_vehicle(
                name=name,
                model=model_val,
                vehicle_type=vtype_var.get(),
                fuel_type=fuel_var.get(),
                transmission=trans_var.get(),
                engine=engine_entry.get().strip() or "Standard",
                model_year=year_val,
                rate_per_hour=rate_val
            )

            if success:
                messagebox.showinfo("Success", msg)
                modal.destroy()
                self.refresh_table()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(frame, text="Save Vehicle", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, height=40, font=FONT_BODY_BOLD, command=save_vehicle).pack(fill="x", padx=25, pady=(15, 10))

    def _open_edit_modal(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a vehicle to edit.")
            return

        v_id = int(sel["id"])
        vehicle = VehicleModel.get_by_id(v_id)
        if not vehicle:
            messagebox.showerror("Error", "Vehicle not found.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Edit Vehicle #{v_id}")
        modal.geometry("500x600")
        modal.grab_set()
        modal.resizable(False, False)

        frame = ctk.CTkFrame(modal, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=f"Edit Vehicle #{v_id}", font=FONT_SUBHEADING).pack(pady=(10, 15))

        vtype_var = ctk.StringVar(value=vehicle["vehicle_type"])
        type_seg = ctk.CTkSegmentedButton(frame, values=["Bike", "Car"], variable=vtype_var)
        type_seg.pack(fill="x", padx=25, pady=(0, 8))

        name_entry = ctk.CTkEntry(frame, placeholder_text="Brand", height=35)
        name_entry.insert(0, vehicle["name"])
        name_entry.pack(fill="x", padx=25, pady=6)

        model_entry = ctk.CTkEntry(frame, placeholder_text="Model", height=35)
        model_entry.insert(0, vehicle["model"])
        model_entry.pack(fill="x", padx=25, pady=6)

        engine_entry = ctk.CTkEntry(frame, placeholder_text="Engine Capacity", height=35)
        engine_entry.insert(0, vehicle["engine"] or "Standard")
        engine_entry.pack(fill="x", padx=25, pady=6)

        fuel_var = ctk.StringVar(value=vehicle["fuel_type"] or "Petrol")
        ctk.CTkLabel(frame, text="Fuel Type:", font=FONT_SMALL).pack(anchor="w", padx=25)
        fuel_menu = ctk.CTkOptionMenu(frame, values=["Petrol", "Diesel", "Electric", "CNG", "Hybrid"], variable=fuel_var)
        fuel_menu.pack(fill="x", padx=25, pady=(0, 6))

        trans_var = ctk.StringVar(value=vehicle["transmission"] or "Manual")
        ctk.CTkLabel(frame, text="Transmission:", font=FONT_SMALL).pack(anchor="w", padx=25)
        trans_menu = ctk.CTkOptionMenu(frame, values=["Manual", "Automatic", "AMT", "CVT"], variable=trans_var)
        trans_menu.pack(fill="x", padx=25, pady=(0, 6))

        year_entry = ctk.CTkEntry(frame, placeholder_text="Year", height=35)
        year_entry.insert(0, str(vehicle["model_year"]))
        year_entry.pack(fill="x", padx=25, pady=6)

        rate_entry = ctk.CTkEntry(frame, placeholder_text="Rate per Hour (₹)", height=35)
        rate_entry.insert(0, str(vehicle["rate_per_hour"]))
        rate_entry.pack(fill="x", padx=25, pady=6)

        status_var = ctk.StringVar(value=vehicle["status"])
        ctk.CTkLabel(frame, text="Status:", font=FONT_SMALL).pack(anchor="w", padx=25)
        status_menu = ctk.CTkOptionMenu(frame, values=["Available", "Rented", "Maintenance"], variable=status_var)
        status_menu.pack(fill="x", padx=25, pady=(0, 6))

        def update_vehicle():
            name = name_entry.get().strip()
            model_val = model_entry.get().strip()
            if not name or not model_val:
                messagebox.showerror("Validation Error", "Name and Model cannot be empty.")
                return

            valid_yr, err_yr, year_val = validate_year(year_entry.get())
            if not valid_yr:
                messagebox.showerror("Validation Error", err_yr)
                return

            valid_rt, err_rt, rate_val = validate_rate(rate_entry.get())
            if not valid_rt:
                messagebox.showerror("Validation Error", err_rt)
                return

            success, msg = VehicleModel.update_vehicle(
                vehicle_id=v_id,
                name=name,
                model=model_val,
                vehicle_type=vtype_var.get(),
                fuel_type=fuel_var.get(),
                transmission=trans_var.get(),
                engine=engine_entry.get().strip(),
                model_year=year_val,
                rate_per_hour=rate_val,
                status=status_var.get()
            )

            if success:
                messagebox.showinfo("Success", msg)
                modal.destroy()
                self.refresh_table()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(frame, text="Update Vehicle", fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, height=40, font=FONT_BODY_BOLD, command=update_vehicle).pack(fill="x", padx=25, pady=(15, 10))

    def _delete_selected(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a vehicle to delete.")
            return

        v_id = int(sel["id"])
        name = f"{sel['name']} {sel['model']}"

        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete vehicle #{v_id} ({name}) permanently?"):
            return

        success, msg = VehicleModel.delete_vehicle(v_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_table()
        else:
            messagebox.showerror("Cannot Delete", msg)
