import customtkinter as ctk
from datetime import datetime
from ui.theme import *
from ui.widgets import StatCard, DataTable
from models import RentalModel, VehicleModel

class DashboardView(ctk.CTkFrame):
    """Admin and Staff Executive Dashboard with real-time stats and active rentals overview."""
    def __init__(self, parent, current_user: dict, navigate_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.navigate_callback = navigate_callback

        self._build_header()
        self._build_stats_section()
        self._build_quick_actions()
        self._build_recent_activity()

        self.refresh_data()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        welcome_text = f"Welcome back, {self.current_user.get('full_name', 'User')}!"
        role_badge = f"Role: {self.current_user.get('role', 'staff').upper()}"

        title_lbl = ctk.CTkLabel(header_frame, text=welcome_text, font=FONT_HEADING, anchor="w")
        title_lbl.pack(side="left")

        badge_lbl = ctk.CTkLabel(
            header_frame,
            text=f"  {role_badge}  ",
            font=FONT_SMALL,
            fg_color=COLOR_PRIMARY,
            corner_radius=6,
            text_color="white"
        )
        badge_lbl.pack(side="left", padx=15)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=32,
            font=FONT_SMALL,
            command=self.refresh_data
        )
        refresh_btn.pack(side="right")

        today_str = datetime.now().strftime("%A, %d %B %Y")
        date_lbl = ctk.CTkLabel(header_frame, text=today_str, font=FONT_BODY, text_color=("gray40", "gray60"))
        date_lbl.pack(side="right", padx=15)

    def _build_stats_section(self):
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=20, pady=5)

        # 5 Stat Cards in horizontal row
        self.card_total = StatCard(self.stats_container, "Total Fleet", "0", "Vehicles in System", accent_color=COLOR_PRIMARY)
        self.card_total.pack(side="left", fill="x", expand=True, padx=5)

        self.card_available = StatCard(self.stats_container, "Available Now", "0", "Ready to Rent", accent_color=COLOR_ACCENT)
        self.card_available.pack(side="left", fill="x", expand=True, padx=5)

        self.card_rented = StatCard(self.stats_container, "Currently Rented", "0", "On the Road", accent_color=COLOR_WARNING)
        self.card_rented.pack(side="left", fill="x", expand=True, padx=5)

        self.card_revenue = StatCard(self.stats_container, "Total Revenue", "₹0.00", "All-Time Completed", accent_color=COLOR_ACCENT)
        self.card_revenue.pack(side="left", fill="x", expand=True, padx=5)

        self.card_staff = StatCard(self.stats_container, "Active Staff", "0", "Staff Members", accent_color=COLOR_PRIMARY)
        self.card_staff.pack(side="left", fill="x", expand=True, padx=5)

    def _build_quick_actions(self):
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(15, 5))

        lbl = ctk.CTkLabel(actions_frame, text="Quick Operations:", font=FONT_BODY_BOLD)
        lbl.pack(side="left", padx=(5, 15))

        btn_rent = ctk.CTkButton(
            actions_frame,
            text="➕ Rent Vehicle",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            height=34,
            command=lambda: self.navigate_callback("rent") if self.navigate_callback else None
        )
        btn_rent.pack(side="left", padx=5)

        btn_return = ctk.CTkButton(
            actions_frame,
            text="↩️ Return & Calculate Bill",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=34,
            command=lambda: self.navigate_callback("return") if self.navigate_callback else None
        )
        btn_return.pack(side="left", padx=5)

        btn_inv = ctk.CTkButton(
            actions_frame,
            text="📋 View Fleet",
            height=34,
            command=lambda: self.navigate_callback("inventory") if self.navigate_callback else None
        )
        btn_inv.pack(side="left", padx=5)

        if self.current_user.get("role") == "admin":
            btn_staff = ctk.CTkButton(
                actions_frame,
                text="👥 Manage Staff",
                height=34,
                command=lambda: self.navigate_callback("staff") if self.navigate_callback else None
            )
            btn_staff.pack(side="left", padx=5)

    def _build_recent_activity(self):
        activity_frame = ctk.CTkFrame(self, fg_color="transparent")
        activity_frame.pack(fill="both", expand=True, padx=20, pady=(15, 15))

        section_title = ctk.CTkLabel(activity_frame, text="Active Rentals (Currently on Road)", font=FONT_SUBHEADING, anchor="w")
        section_title.pack(fill="x", pady=(0, 6))

        columns = [
            ("id", "Rental ID", 70),
            ("vehicle_name", "Vehicle Name & Model", 200),
            ("customer_name", "Customer Name", 140),
            ("customer_phone", "Contact No.", 110),
            ("rent_date", "Date", 90),
            ("rent_time", "Rent Time", 80),
            ("rate_per_hour", "Rate/Hr (₹)", 80),
            ("status", "Status", 80)
        ]

        self.table = DataTable(activity_frame, columns)
        self.table.pack(fill="both", expand=True)

    def refresh_data(self):
        """Fetches the latest metrics and table data."""
        stats = RentalModel.get_stats()
        self.card_total.update_value(str(stats["total_fleet"]), f"{stats['bikes_count']} Bikes, {stats['cars_count']} Cars")
        self.card_available.update_value(str(stats["available_fleet"]), "Ready to Rent")
        self.card_rented.update_value(str(stats["rented_fleet"]), "Currently Out")
        self.card_revenue.update_value(f"₹{stats['total_revenue']:,.2f}", "Total Earnings")
        self.card_staff.update_value(str(stats["staff_count"]), "Staff on Duty")

        active_rentals = RentalModel.get_active_rentals()
        self.table.populate(active_rentals, tag_key="status")
