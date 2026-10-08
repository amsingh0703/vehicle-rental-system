import sqlite3
import os
import json
import pandas as pd
from datetime import datetime
import config
from auth import hash_password

def get_connection():
    """Returns a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and performs legacy data migration if needed."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users table (Admin & Staff)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'staff')),
        phone TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. Vehicles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        vehicle_type TEXT NOT NULL DEFAULT 'Bike',
        fuel_type TEXT DEFAULT 'Petrol',
        transmission TEXT DEFAULT 'Manual',
        engine TEXT DEFAULT 'N/A',
        model_year INTEGER DEFAULT 2023,
        rate_per_hour REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available' CHECK(status IN ('Available', 'Rented', 'Maintenance')),
        created_at TEXT NOT NULL
    );
    """)

    # 3. Rentals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        vehicle_name TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        customer_aadhar TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_address TEXT,
        rent_date TEXT NOT NULL,
        rent_time TEXT NOT NULL,
        return_date TEXT,
        return_time TEXT,
        hours_used REAL DEFAULT 0.0,
        rate_per_hour REAL NOT NULL,
        total_rent REAL DEFAULT 0.0,
        staff_username TEXT,
        status TEXT NOT NULL DEFAULT 'Rented' CHECK(status IN ('Rented', 'Returned')),
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
    );
    """)

    conn.commit()
    conn.close()

    # Check and run migration if vehicles or users are empty
    check_and_migrate()

def check_and_migrate():
    """Migrates existing CSV and JSON data into SQLite if tables are empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check users count
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    # Check vehicles count
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    vehicle_count = cursor.fetchone()[0]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Migrate Users / Staff
    if user_count == 0:
        print("[MIGRATION] Migrating users and staff accounts...")
        migrated_users = set()

        # Default fallback admin if none found
        default_accounts = [
            ("admin", "admin123", "System Administrator", "admin"),
            ("r", "r", "Administrator (R)", "admin"),
            ("Amit", "Amit1234", "Amit Kumar", "admin"),
            ("ritesh", "Amit1234", "Ritesh Staff", "staff"),
            ("dg", "2006", "Deemanth Staff", "staff")
        ]

        # Check JSON data in GUI folder
        gui_json_path = os.path.join(config.BASE_DIR, "GUI", "Custom Tkinter", "Custom Tkinter", "data.json")
        if os.path.exists(gui_json_path):
            try:
                with open(gui_json_path, "r", encoding="utf-8") as f:
                    jdata = json.load(f)
                    for a in jdata.get("admin", []):
                        uname = a.get("username", "").strip()
                        pwd = a.get("password", "").strip()
                        if uname and uname not in migrated_users:
                            cursor.execute("""
                                INSERT INTO users (username, password_hash, full_name, role, created_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (uname, hash_password(pwd), f"Admin {uname.capitalize()}", "admin", now_str))
                            migrated_users.add(uname)

                    for u in jdata.get("user", []):
                        uname = u.get("username", "").strip()
                        pwd = u.get("password", "").strip()
                        name = u.get("name", f"Staff {uname}").strip()
                        if uname and uname not in migrated_users:
                            cursor.execute("""
                                INSERT INTO users (username, password_hash, full_name, role, created_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (uname, hash_password(pwd), name, "staff", now_str))
                            migrated_users.add(uname)
            except Exception as e:
                print(f"[MIGRATION WARNING] Failed reading data.json: {e}")

        # Check accounts.csv
        accounts_csv = os.path.join(config.BASE_DIR, "accounts.csv")
        if os.path.exists(accounts_csv):
            try:
                df_acc = pd.read_csv(accounts_csv)
                for _, row in df_acc.iterrows():
                    uname = str(row.get("Username", "")).strip()
                    pwd = str(row.get("Password", "")).strip()
                    role_raw = str(row.get("Role", "staff")).strip().lower()
                    role = "admin" if role_raw == "admin" else "staff"
                    if uname and uname not in migrated_users:
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, full_name, role, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (uname, hash_password(pwd), f"{role.capitalize()} {uname.capitalize()}", role, now_str))
                        migrated_users.add(uname)
            except Exception as e:
                print(f"[MIGRATION WARNING] Failed reading accounts.csv: {e}")

        # Insert defaults if still empty
        for uname, pwd, name, role in default_accounts:
            if uname not in migrated_users:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (uname, hash_password(pwd), name, role, now_str))
                migrated_users.add(uname)

        conn.commit()

    # Migrate Vehicles
    if vehicle_count == 0:
        print("[MIGRATION] Migrating vehicles from inventory.csv and bikes.csv...")
        inserted_models = set()

        # 1. First, import detailed bikes from GUI bikes.csv if present
        bikes_csv = os.path.join(config.BASE_DIR, "GUI", "Custom Tkinter", "Custom Tkinter", "bikes.csv")
        if os.path.exists(bikes_csv):
            try:
                df_bikes = pd.read_csv(bikes_csv)
                for _, row in df_bikes.iterrows():
                    name = str(row.get("name", "")).strip()
                    model = str(row.get("model", "")).strip()
                    engine = str(row.get("engine", "N/A")).strip()
                    gear = str(row.get("gear_type", "Manual")).strip()
                    year = int(row.get("model_year", 2023)) if pd.notna(row.get("model_year")) else 2023
                    rate = float(row.get("rate_per_hour", 25.0)) if pd.notna(row.get("rate_per_hour")) else 25.0

                    key = f"{name.lower()}_{model.lower()}"
                    if key not in inserted_models:
                        cursor.execute("""
                            INSERT INTO vehicles (name, model, vehicle_type, fuel_type, transmission, engine, model_year, rate_per_hour, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (name, model, "Bike", "Petrol", gear, engine, year, rate, "Available", now_str))
                        inserted_models.add(key)
            except Exception as e:
                print(f"[MIGRATION WARNING] Failed reading bikes.csv: {e}")

        # 2. Next, import from inventory.csv (bikes + cars)
        inv_csv = os.path.join(config.BASE_DIR, "inventory.csv")
        if os.path.exists(inv_csv):
            try:
                df_inv = pd.read_csv(inv_csv)
                for _, row in df_inv.iterrows():
                    model_full = str(row.get("Model Name", "")).strip()
                    fuel = str(row.get("Fuel Type", "Petrol")).strip()
                    gear = str(row.get("Transmission", "Manual")).strip()
                    rate = float(row.get("Rate/Hr", 30.0)) if pd.notna(row.get("Rate/Hr")) else 30.0
                    status = str(row.get("Status", "Available")).strip()
                    if status not in ["Available", "Rented", "Maintenance"]:
                        status = "Available"

                    # Classify Car vs Bike
                    car_brands = ["Maruti", "Tata", "Hyundai", "Kia", "Toyota", "Mahindra", "MG", "Honda Amaze", "Honda City"]
                    is_car = any(cb.lower() in model_full.lower() for cb in car_brands)
                    v_type = "Car" if is_car else "Bike"

                    parts = model_full.split(" ", 1)
                    name = parts[0]
                    model = parts[1] if len(parts) > 1 else model_full

                    key = f"{name.lower()}_{model.lower()}"
                    if key not in inserted_models:
                        cursor.execute("""
                            INSERT INTO vehicles (name, model, vehicle_type, fuel_type, transmission, engine, model_year, rate_per_hour, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (name, model, v_type, fuel, gear, "Standard", 2023, rate, status, now_str))
                        inserted_models.add(key)
            except Exception as e:
                print(f"[MIGRATION WARNING] Failed reading inventory.csv: {e}")

        conn.commit()

    # Migrate Rentals if rentals table is empty
    cursor.execute("SELECT COUNT(*) FROM rentals")
    rental_count = cursor.fetchone()[0]

    if rental_count == 0:
        print("[MIGRATION] Migrating existing rental records...")
        rented_csv = os.path.join(config.BASE_DIR, "GUI", "Custom Tkinter", "Custom Tkinter", "rented_vehicle.csv")
        if os.path.exists(rented_csv):
            try:
                df_rent = pd.read_csv(rented_csv)
                for _, row in df_rent.iterrows():
                    v_name = f"{row.get('bike_name', '')} {row.get('model', '')}".strip()
                    c_name = str(row.get("user_name", "Walk-in Customer")).strip()
                    aadhar = str(row.get("aadhar", "111122223333")).split(".")[0].strip()
                    phone = str(row.get("phone_number", "9999988888")).split(".")[0].strip()
                    addr = str(row.get("address", "Local")).strip()
                    r_date = str(row.get("date", "2025-10-10")).strip()
                    r_time = str(row.get("time", "10:00:00")).split(".")[0].strip()
                    ret_date = str(row.get("return", "")).strip()
                    ret_time = str(row.get("ret_time", "")).strip()
                    status = str(row.get("status", "Returned")).strip()
                    rate = float(row.get("rate_per_hour", 20.0)) if pd.notna(row.get("rate_per_hour")) else 20.0

                    if ret_date in ["NAN", "nan", ""]:
                        ret_date = None
                        ret_time = None
                        status = "Rented"
                    else:
                        status = "Returned"

                    # Find vehicle ID
                    cursor.execute("SELECT id FROM vehicles WHERE name LIKE ? LIMIT 1", (f"%{row.get('bike_name', '')}%",))
                    v_res = cursor.fetchone()
                    v_id = v_res[0] if v_res else 1

                    cursor.execute("""
                        INSERT INTO rentals (
                            vehicle_id, vehicle_name, customer_name, customer_aadhar, customer_phone, customer_address,
                            rent_date, rent_time, return_date, return_time, hours_used, rate_per_hour, total_rent, staff_username, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        v_id, v_name, c_name, aadhar, phone, addr,
                        r_date, r_time, ret_date, ret_time, 2.0, rate, rate * 2.0, "Amit", status
                    ))
            except Exception as e:
                print(f"[MIGRATION WARNING] Failed reading rented_vehicle.csv: {e}")

        conn.commit()

    conn.close()
    print("[MIGRATION COMPLETE] SQLite database ready at", config.DB_PATH)
