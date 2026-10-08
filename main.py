import pandas as pd
import os
from datetime import datetime

# ===============================
# File paths
# ===============================
INVENTORY_FILE = "inventory.csv"
ACCOUNTS_FILE = "accounts.csv"
USERS_FILE = "users.csv"

# ===============================
# Helper Functions
# ===============================
def load_csv(filename, columns=None):
    """Load a CSV file into a pandas DataFrame"""
    if not os.path.exists(filename):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(filename)

def save_csv(df, filename):
    """Save DataFrame back to CSV"""
    df.to_csv(filename, index=False)

# ===============================
# Account Management
# ===============================
def add_account(role):
    df = load_csv(ACCOUNTS_FILE, ["AccountID", "Role", "Username", "Password"])
    account_id = len(df) + 1
    uname = input("Enter new username: ")
    pwd = input("Enter new password: ")

    df.loc[len(df)] = [account_id, role, uname, pwd]
    save_csv(df, ACCOUNTS_FILE)
    print(f"✅ {role.capitalize()} account added successfully!")

def login():
    df = load_csv(ACCOUNTS_FILE, ["AccountID", "Role", "Username", "Password"])
    uname = input("Enter username: ")
    pwd = input("Enter password: ")

    match = df[(df["Username"] == uname) & (df["Password"] == pwd)]
    if not match.empty:
        print(f"✅ Welcome {uname} !")
        return uname
    else:
        print("❌ Invalid credentials!")
        return None

# ===============================
# Admin Functions
# ===============================
def add_vehicle():
    df = load_csv(INVENTORY_FILE, ["VEHICLE-ID", "Model Name", "Fuel Type", "Transmission", "Rate/Hr", "Status"])
    vid = len(df) + 1
    model = input("Enter Vehicle Model: ")
    fuel = input("Enter Fuel Type (Petrol/Diesel): ")
    gear = input("Enter Transmission (Manual/Automatic): ")
    rate = input("Enter Rate per Hour: ")

    new_row = {
        "VEHICLE-ID": vid,
        "Model Name": model,
        "Fuel Type": fuel,
        "Transmission": gear,
        "Rate/Hr": rate,
        "Status": "Available"
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_csv(df, INVENTORY_FILE)
    print("✅ Vehicle added successfully!")

def view_inventory():
    df = load_csv(INVENTORY_FILE)
    if df.empty:
        print("⚠ No vehicles in inventory.")
        return
    print("\n--- Vehicle Inventory ---")
    print(df.to_string(index=False))

def search_vehicle():
    df = load_csv(INVENTORY_FILE)
    name = input("Enter vehicle model to search: ").lower()
    results = df[df["Model Name"].str.lower() == name]
    if results.empty:
        print("❌ Vehicle not found!")
    else:
        print("\n--- Search Result ---")
        print(results.to_string(index=False))

# ===============================
# User Functions
# ===============================
def rent_vehicle():
    inv = load_csv(INVENTORY_FILE)
    users = load_csv(USERS_FILE, ["UserID", "Name", "Mobile", "Aadhar", "VEHICLE-ID", "StartTime", "EndTime", "2"
                                                                                                              ""])

    print("\n--- Available Vehicles ---")
    print(inv[inv["Status"] == "Available"].to_string(index=False))

    vid = input("Enter VEHICLE-ID to rent: ")

    if vid not in inv["VEHICLE-ID"].astype(str).values:
        print("❌ Invalid Vehicle ID!")
        return

    vehicle = inv.loc[inv["VEHICLE-ID"].astype(str) == vid]
    if vehicle.iloc[0]["Status"] != "Available":
        print("❌ Vehicle is already rented!")
        return
    name = input("Enter Name: ")
    mobile = input("Enter Mobile Number: ")
    aadhar = input("Enter Aadhar Number: ")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_user = {
        "UserID": len(users) + 1,
        "Name": name,
        "Mobile": mobile,
        "Aadhar": aadhar,
        "VEHICLE-ID": vid,
        "StartTime": start_time,
        "EndTime": "",
        "TotalRent": ""
    }

    users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
    inv.loc[inv["VEHICLE-ID"].astype(str) == vid, "Status"] = "Rented"

    save_csv(users, USERS_FILE)
    save_csv(inv, INVENTORY_FILE)
    print(f"✅ {name}, you rented {vehicle.iloc[0]['Model Name']} at {start_time}")

def calculate_rent():
    users = load_csv(USERS_FILE)
    inv = load_csv(INVENTORY_FILE)
    name = input("Enter name: ")
    active = users[(users["Name"] == name) & (users["EndTime"].isna())]
    if active.empty:
        print("⚠ No active rentals found.")
        return

    hours = int(input("Enter number of hours used: "))
    vid = str(active.iloc[0]["VEHICLE-ID"])
    vehicle = inv[inv["VEHICLE-ID"].astype(str) == vid]
    rate = int(vehicle.iloc[0]["Rate/Hr"])

    users["EndTime"] = users["EndTime"].astype(str)
    users["TotalRent"] = users["TotalRent"].astype(str)

    rent = hours * rate
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    users.loc[(users["Name"] == name) & (users["VEHICLE-ID"].astype(str) == vid), "EndTime"] = end_time
    users.loc[(users["Name"] == name) & (users["VEHICLE-ID"].astype(str) == vid), "TotalRent"] = rent
    inv.loc[inv["VEHICLE-ID"].astype(str) == vid, "Status"] = "Available"

    save_csv(users, USERS_FILE)
    save_csv(inv, INVENTORY_FILE)
    print(f"✅ Rent calculated: ₹{rent}")

# ===============================
# Menus
# ===============================
def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Add New Vehicle")
        print("2. View Inventory")
        print("3. Search Vehicle")
        print("4. Add New Admin")
        print("5. Add New User")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            add_vehicle()
        elif choice == "2":
            view_inventory()
        elif choice == "3":
            search_vehicle()
        elif choice == "4":
            add_account("admin")
        elif choice == "5":
            add_account("user")
        elif choice == "6":
            break
        else:
            print("⚠ Invalid choice!")

def user_menu():
    while True:
        print("\n--- User Menu ---")
        print("1. Rent Vehicle")
        print("2. Calculate Rent")
        print("3. Search Vehicle")
        print("4. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            rent_vehicle()
        elif choice == "2":
            calculate_rent()
        elif choice == "3":
            search_vehicle()
        elif choice == "4":
            break
        else:
            print("⚠ Invalid choice!")

def main():
    while True:
        print("\n=== Vehicle Rental Management System ===")
        print("1. Admin Login")
        print("2. User Login")
        print("3. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            uname = login()
            if uname:
                admin_menu()
        elif choice == "2":
            uname = login()
            if uname:
                user_menu()
        elif choice == "3":
            print("👋 Exiting... Thank you!")
            break
        else:
            print("⚠ Invalid choice!")

if __name__ == "__main__":
    main()
