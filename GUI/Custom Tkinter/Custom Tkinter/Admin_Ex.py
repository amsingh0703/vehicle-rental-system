import customtkinter as ctk
from tkinter import messagebox

# ------------------ LOGIN WINDOW ------------------ #

def open_admin_dashboard():
    login_window.destroy()  # Close login window
    admin_dashboard()       # Open dashboard

def login():
    username = username_entry.get()
    password = password_entry.get()

    # Example credentials
    if username == "admin" and password == "admin123":
        open_admin_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

# ------------------ ADMIN DASHBOARD ------------------ #

def admin_dashboard():
    root = ctk.CTk()
    root.geometry("900x600")
    root.title("Admin Dashboard")

    # Left Sidebar
    sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    # Main Content Area
    content = ctk.CTkFrame(root)
    content.pack(side="right", expand=True, fill="both")

    # Function to update content area
    def show_content(text):
        for widget in content.winfo_children():
            widget.destroy()
        ctk.CTkLabel(content, text=text, font=ctk.CTkFont(size=24, weight="bold")).pack(pady=50)

    # Sidebar Buttons
    ctk.CTkButton(sidebar, text="Home", command=lambda: show_content("Welcome to Admin Home")).pack(pady=20, padx=20)
    ctk.CTkButton(sidebar, text="Manage Users", command=lambda: show_content("User Management Section")).pack(pady=20, padx=20)
    ctk.CTkButton(sidebar, text="Settings", command=lambda: show_content("Settings Section")).pack(pady=20, padx=20)

    def logout():
        root.destroy()
        main_login_screen()  # Return to login page

    ctk.CTkButton(sidebar, text="Logout", fg_color="red", command=logout).pack(side="bottom", pady=20, padx=20)

    show_content("Welcome to Admin Dashboard")  # Default content
    root.mainloop()

# ------------------ LOGIN SCREEN UI ------------------ #

def main_login_screen():
    global login_window, username_entry, password_entry

    login_window = ctk.CTk()
    login_window.geometry("400x350")
    login_window.title("Admin Login")

    frame = ctk.CTkFrame(login_window, corner_radius=15)
    frame.pack(pady=50, padx=50, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Admin Login", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

    username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=250, height=40)
    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250, height=40)
    password_entry.pack(pady=10)

    login_btn = ctk.CTkButton(frame, text="Login", width=200, height=40, command=login)
    login_btn.pack(pady=20)

    login_window.mainloop()

# Run Login Screen
if __name__ == "__main__":
    main_login_screen()
