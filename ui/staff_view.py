import customtkinter as ctk
from tkinter import messagebox
from ui.theme import *
from ui.widgets import DataTable
from models import UserModel
from auth import validate_phone

class StaffView(ctk.CTkFrame):
    """Admin Staff Management View: Add, update, and manage staff credentials."""
    def __init__(self, parent, current_user: dict, navigate_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.navigate_callback = navigate_callback

        self._build_header()
        self._build_table()
        self._build_actions()

        self.refresh_users()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="Staff & Employee Accounts Management", font=FONT_SUBHEADING)
        title.pack(side="left", padx=15, pady=12)

        desc = ctk.CTkLabel(header, text="Control system access for frontline staff and managers", font=FONT_SMALL, text_color=("gray40", "gray60"))
        desc.pack(side="left", padx=5)

    def _build_table(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=5)

        columns = [
            ("id", "User ID", 60),
            ("username", "Login Username", 130),
            ("full_name", "Full Name / Title", 180),
            ("role", "System Role", 90),
            ("phone", "Contact Phone", 120),
            ("created_at", "Date Created", 150)
        ]

        self.table = DataTable(container, columns)
        self.table.pack(fill="both", expand=True)

    def _build_actions(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(10, 15))

        add_btn = ctk.CTkButton(
            bar,
            text="➕ Create New Staff Account",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            height=36,
            font=FONT_BODY_BOLD,
            command=self._open_add_user_modal
        )
        add_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(
            bar,
            text="🔑 Reset Password",
            height=36,
            command=self._open_reset_password_modal
        )
        reset_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(
            bar,
            text="🗑️ Remove Account",
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=36,
            command=self._delete_selected_user
        )
        delete_btn.pack(side="left", padx=5)

        refresh_btn = ctk.CTkButton(
            bar,
            text="🔄 Refresh",
            width=90,
            height=36,
            fg_color="gray50",
            command=self.refresh_users
        )
        refresh_btn.pack(side="right", padx=5)

    def refresh_users(self):
        users = UserModel.get_all_users()
        self.table.populate(users)

    def _open_add_user_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Create Staff / Admin Account")
        modal.geometry("450x520")
        modal.grab_set()
        modal.resizable(False, False)

        frame = ctk.CTkFrame(modal, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Create Employee Account", font=FONT_SUBHEADING).pack(pady=(10, 15))

        role_var = ctk.StringVar(value="staff")
        ctk.CTkLabel(frame, text="Role Designation:", font=FONT_SMALL).pack(anchor="w", padx=25)
        role_seg = ctk.CTkSegmentedButton(frame, values=["staff", "admin"], variable=role_var)
        role_seg.pack(fill="x", padx=25, pady=(0, 10))

        full_name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name (e.g. Ramesh Kumar)", height=36)
        full_name_entry.pack(fill="x", padx=25, pady=8)

        username_entry = ctk.CTkEntry(frame, placeholder_text="Username (Login ID)", height=36)
        username_entry.pack(fill="x", padx=25, pady=8)

        password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", height=36)
        password_entry.pack(fill="x", padx=25, pady=8)

        phone_entry = ctk.CTkEntry(frame, placeholder_text="Contact Phone (Optional 10-digit)", height=36)
        phone_entry.pack(fill="x", padx=25, pady=8)

        def save_user():
            fname = full_name_entry.get().strip()
            uname = username_entry.get().strip()
            pwd = password_entry.get().strip()
            ph = phone_entry.get().strip()

            if not fname or not uname or not pwd:
                messagebox.showerror("Validation Error", "Full Name, Username, and Password are all required.")
                return

            if len(pwd) < 3:
                messagebox.showerror("Validation Error", "Password must be at least 3 characters.")
                return

            if ph:
                valid_ph, err_ph = validate_phone(ph)
                if not valid_ph:
                    messagebox.showerror("Phone Error", err_ph)
                    return

            success, msg = UserModel.add_user(
                username=uname,
                password=pwd,
                full_name=fname,
                role=role_var.get(),
                phone=ph
            )

            if success:
                messagebox.showinfo("Success", msg)
                modal.destroy()
                self.refresh_users()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(frame, text="Create Account", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, height=40, font=FONT_BODY_BOLD, command=save_user).pack(fill="x", padx=25, pady=(20, 10))

    def _open_reset_password_modal(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a user account to reset password.")
            return

        u_id = int(sel["id"])
        uname = sel["username"]

        modal = ctk.CTkToplevel(self)
        modal.title(f"Reset Password for '{uname}'")
        modal.geometry("420x350")
        modal.grab_set()
        modal.resizable(False, False)

        frame = ctk.CTkFrame(modal, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=f"Change Password for {uname}", font=FONT_SUBHEADING).pack(pady=(10, 15))

        new_pwd_entry = ctk.CTkEntry(frame, placeholder_text="Enter New Password", show="*", height=36)
        new_pwd_entry.pack(fill="x", padx=25, pady=10)

        confirm_pwd_entry = ctk.CTkEntry(frame, placeholder_text="Confirm New Password", show="*", height=36)
        confirm_pwd_entry.pack(fill="x", padx=25, pady=10)

        def save_pwd():
            p1 = new_pwd_entry.get().strip()
            p2 = confirm_pwd_entry.get().strip()

            if not p1:
                messagebox.showerror("Error", "Password cannot be empty.")
                return
            if p1 != p2:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            success, msg = UserModel.update_user(
                user_id=u_id,
                full_name=sel["full_name"],
                role=sel["role"],
                phone=sel["phone"],
                new_password=p1
            )

            if success:
                messagebox.showinfo("Success", "Password updated successfully!")
                modal.destroy()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(frame, text="Update Password", fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, height=40, font=FONT_BODY_BOLD, command=save_pwd).pack(fill="x", padx=25, pady=(20, 10))

    def _delete_selected_user(self):
        sel = self.table.get_selected_dict()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an account to remove.")
            return

        u_id = int(sel["id"])
        uname = sel["username"]

        if uname == self.current_user.get("username"):
            messagebox.showerror("Cannot Delete", "You cannot delete your own logged-in account.")
            return

        if not messagebox.askyesno("Confirm Removal", f"Are you sure you want to delete user '{uname}'?"):
            return

        success, msg = UserModel.delete_user(u_id)
        if success:
            messagebox.showinfo("Deleted", msg)
            self.refresh_users()
        else:
            messagebox.showerror("Cannot Delete", msg)
