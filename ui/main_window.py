import customtkinter as ctk
from tkinter import messagebox
from ui.theme import *
from ui.dashboard_view import DashboardView
from ui.inventory_view import InventoryView
from ui.rent_view import RentView
from ui.return_view import ReturnView
from ui.history_view import HistoryView
from ui.staff_view import StaffView
import config

class MainWindow(ctk.CTkFrame):
    """Main application shell with sidebar navigation and role-based page switcher."""
    def __init__(self, parent, current_user: dict, on_logout):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.current_user = current_user
        self.on_logout = on_logout
        self.is_admin = current_user.get("role") == config.ROLE_ADMIN

        self.current_view_name = None
        self.current_view_widget = None
        self.nav_buttons = {}

        self._build_sidebar()
        self._build_content_area()

        # Load default view (Dashboard)
        self.navigate_to("dashboard")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLOR_SIDEBAR_BG)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=15, pady=(20, 15))

        logo_lbl = ctk.CTkLabel(brand_frame, text="🚗 DriveEase", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_PRIMARY[1], anchor="w")
        logo_lbl.pack(fill="x")

        sub_lbl = ctk.CTkLabel(brand_frame, text="Vehicle Rental System", font=FONT_SMALL, text_color=("gray40", "gray60"), anchor="w")
        sub_lbl.pack(fill="x")

        # Divider
        div = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLOR_CARD_BORDER)
        div.pack(fill="x", padx=15, pady=(0, 12))

        # Nav Buttons Container
        self.nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_container.pack(fill="both", expand=True, padx=10)

        # Define navigation items based on role
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("inventory", "📋 Fleet Inventory"),
            ("rent", "⚡ Rent Vehicle"),
            ("return", "↩️ Return & Bill"),
            ("history", "📜 Rental History")
        ]

        if self.is_admin:
            nav_items.append(("staff", "👥 Staff Management"))

        for key, text in nav_items:
            btn = ctk.CTkButton(
                self.nav_container,
                text=f"  {text}",
                anchor="w",
                font=FONT_BODY,
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray20", "gray85"),
                hover_color=("gray85", "gray30"),
                command=lambda k=key: self.navigate_to(k)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[key] = btn

        # Bottom Section (User Badge, Theme Switcher, Logout)
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=12, pady=15)

        # User profile badge
        user_badge = ctk.CTkFrame(bottom_frame, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        user_badge.pack(fill="x", pady=(0, 10))

        u_name = self.current_user.get("full_name") or self.current_user.get("username")
        u_role = self.current_user.get("role", "staff").capitalize()

        ctk.CTkLabel(user_badge, text=f"👤 {u_name}", font=FONT_BODY_BOLD, anchor="w").pack(fill="x", padx=10, pady=(6, 1))
        ctk.CTkLabel(user_badge, text=f"Designation: {u_role}", font=FONT_SMALL, text_color=("gray40", "gray60"), anchor="w").pack(fill="x", padx=10, pady=(0, 6))

        # Appearance mode segmented switch
        theme_lbl = ctk.CTkLabel(bottom_frame, text="Appearance:", font=FONT_SMALL, text_color=("gray40", "gray60"))
        theme_lbl.pack(anchor="w", padx=4, pady=(0, 2))

        self.theme_seg = ctk.CTkSegmentedButton(
            bottom_frame,
            values=["Light", "System", "Dark"],
            height=28,
            font=FONT_SMALL,
            command=self._change_theme
        )
        self.theme_seg.set("System")
        self.theme_seg.pack(fill="x", pady=(0, 12))

        # Logout Button
        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="🚪 Logout",
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=34,
            font=FONT_BODY_BOLD,
            command=self._confirm_logout
        )
        logout_btn.pack(fill="x")

    def _build_content_area(self):
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)

    def navigate_to(self, view_name: str, **kwargs):
        """Swaps content frame to requested view."""
        if self.current_view_widget:
            self.current_view_widget.destroy()

        # Update button states
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.configure(fg_color=COLOR_ACTIVE_NAV, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray20", "gray85"))

        self.current_view_name = view_name

        if view_name == "dashboard":
            self.current_view_widget = DashboardView(self.content_area, self.current_user, self.navigate_to)
        elif view_name == "inventory":
            self.current_view_widget = InventoryView(self.content_area, self.current_user, self.navigate_to)
        elif view_name == "rent":
            pre_id = kwargs.get("preselected_vehicle_id")
            self.current_view_widget = RentView(self.content_area, self.current_user, self.navigate_to, preselected_vehicle_id=pre_id)
        elif view_name == "return":
            self.current_view_widget = ReturnView(self.content_area, self.current_user, self.navigate_to)
        elif view_name == "history":
            self.current_view_widget = HistoryView(self.content_area, self.current_user, self.navigate_to)
        elif view_name == "staff" and self.is_admin:
            self.current_view_widget = StaffView(self.content_area, self.current_user, self.navigate_to)
        else:
            self.current_view_widget = DashboardView(self.content_area, self.current_user, self.navigate_to)

        self.current_view_widget.pack(fill="both", expand=True)

    def _change_theme(self, mode: str):
        ctk.set_appearance_mode(mode.lower())

    def _confirm_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?"):
            self.on_logout()
