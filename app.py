import customtkinter as ctk
import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from database import init_db
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class VehicleRentalApp(ctk.CTk):
    """Main Application Controller."""
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title(config.APP_TITLE)
        self.geometry(config.WINDOW_SIZE)
        self.minsize(*config.MIN_WINDOW_SIZE)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Initialize SQLite Database & Data Migration
        init_db()

        self.current_user = None
        self.current_screen = None

        # Start with Login Screen
        self.show_login_screen()

    def show_login_screen(self):
        """Displays the login window."""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_user = None
        self.current_screen = LoginWindow(self, on_login_success=self.on_login_success)
        self.current_screen.pack(fill="both", expand=True)

    def on_login_success(self, user_data: dict):
        """Callback invoked when user successfully logs in."""
        self.current_user = user_data
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = MainWindow(self, current_user=self.current_user, on_logout=self.show_login_screen)
        self.current_screen.pack(fill="both", expand=True)

def main():
    app = VehicleRentalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
