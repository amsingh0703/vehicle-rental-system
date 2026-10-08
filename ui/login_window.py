import customtkinter as ctk
from tkinter import messagebox
from ui.theme import *
from models import UserModel
import config

class LoginWindow(ctk.CTkFrame):
    """Modern authentication screen with Admin / Staff role selection and validation."""
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.on_login_success = on_login_success

        self._build_ui()

    def _build_ui(self):
        # Outer center container
        center_box = ctk.CTkFrame(self, width=460, corner_radius=16, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER)
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        # Header Branding
        ctk.CTkLabel(center_box, text="🚗 DriveEase", font=(FONT_FAMILY, 26, "bold"), text_color=COLOR_PRIMARY[1]).pack(pady=(25, 4))
        ctk.CTkLabel(center_box, text="Vehicle Rental Management System", font=FONT_SMALL, text_color=("gray40", "gray60")).pack(pady=(0, 15))

        # Role Selector (Admin vs Staff)
        self.role_var = ctk.StringVar(value=config.ROLE_STAFF)
        self.role_seg = ctk.CTkSegmentedButton(
            center_box,
            values=["Staff Login", "Admin Login"],
            font=FONT_BODY_BOLD,
            height=38,
            command=self._on_role_toggle
        )
        self.role_seg.set("Staff Login")
        self.role_seg.pack(fill="x", padx=35, pady=(0, 20))

        # Username Field
        ctk.CTkLabel(center_box, text="Username:", font=FONT_BODY_BOLD).pack(anchor="w", padx=35, pady=(0, 2))
        self.user_entry = ctk.CTkEntry(center_box, placeholder_text="Enter your username", height=42, font=FONT_BODY)
        self.user_entry.pack(fill="x", padx=35, pady=(0, 15))
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())

        # Password Field
        ctk.CTkLabel(center_box, text="Password:", font=FONT_BODY_BOLD).pack(anchor="w", padx=35, pady=(0, 2))
        self.pass_entry = ctk.CTkEntry(center_box, placeholder_text="Enter your password", show="*", height=42, font=FONT_BODY)
        self.pass_entry.pack(fill="x", padx=35, pady=(0, 8))
        self.pass_entry.bind("<Return>", lambda e: self._attempt_login())

        # Show password toggle
        self.show_pass_var = ctk.BooleanVar(value=False)
        show_pass_cb = ctk.CTkCheckBox(
            center_box,
            text="Show Password",
            font=FONT_SMALL,
            variable=self.show_pass_var,
            command=self._toggle_password_visibility
        )
        show_pass_cb.pack(anchor="w", padx=35, pady=(0, 15))

        # Status / Error Label
        self.status_lbl = ctk.CTkLabel(center_box, text="", font=FONT_SMALL, text_color=COLOR_DANGER[1])
        self.status_lbl.pack(pady=(0, 5))

        # Login Button
        self.login_btn = ctk.CTkButton(
            center_box,
            text="Login to System",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=44,
            font=FONT_BODY_BOLD,
            command=self._attempt_login
        )
        self.login_btn.pack(fill="x", padx=35, pady=(5, 15))

        # Credentials Hint Box
        hint_frame = ctk.CTkFrame(center_box, fg_color=("gray90", "gray20"), corner_radius=8)
        hint_frame.pack(fill="x", padx=35, pady=(0, 25))

        self.hint_lbl = ctk.CTkLabel(
            hint_frame,
            text="Staff Login Hint: username: ritesh | pwd: Amit1234 (or dg / 2006)",
            font=(FONT_FAMILY, 10),
            text_color=("gray40", "gray65"),
            justify="center"
        )
        self.hint_lbl.pack(padx=10, pady=8)

        # Focus username initially
        self.user_entry.focus()

    def _on_role_toggle(self, value):
        if value == "Admin Login":
            self.role_var.set(config.ROLE_ADMIN)
            self.hint_lbl.configure(text="Admin Login Hint: username: Amit | pwd: Amit1234 (or admin / admin123)")
        else:
            self.role_var.set(config.ROLE_STAFF)
            self.hint_lbl.configure(text="Staff Login Hint: username: ritesh | pwd: Amit1234 (or dg / 2006)")

    def _toggle_password_visibility(self):
        if self.show_pass_var.get():
            self.pass_entry.configure(show="")
        else:
            self.pass_entry.configure(show="*")

    def _attempt_login(self):
        uname = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        selected_role = self.role_var.get()

        if not uname or not pwd:
            self.status_lbl.configure(text="⚠ Please enter both username and password.")
            return

        user_data, msg = UserModel.authenticate(uname, pwd, expected_role=selected_role)
        if not user_data:
            self.status_lbl.configure(text=f"❌ {msg}")
            return

        self.status_lbl.configure(text="")
        # Success callback
        self.on_login_success(user_data)
