from datetime import datetime
import math
from database import get_connection
from auth import hash_password, verify_password
import config

class UserModel:
    @staticmethod
    def authenticate(username, password, expected_role=None):
        """Authenticates user with username and password, verifying SHA-256 hash."""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM users WHERE LOWER(username) = LOWER(?)"
        params = [username.strip()]
        if expected_role:
            query += " AND role = ?"
            params.append(expected_role)
            
        cursor.execute(query, params)
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return None, "Invalid username or account not found."
            
        if not verify_password(password, user["password_hash"]):
            return None, "Incorrect password."
            
        return dict(user), "Login successful"

    @staticmethod
    def get_staff_list():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, phone, created_at FROM users WHERE role = 'staff' ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_all_users():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, phone, created_at FROM users ORDER BY role ASC, id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def username_exists(username):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    @staticmethod
    def add_user(username, password, full_name, role="staff", phone=""):
        if UserModel.username_exists(username):
            return False, f"Username '{username}' already exists."
            
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role, phone, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username.strip(), hash_password(password), full_name.strip(), role, phone.strip(), now_str))
            conn.commit()
            return True, f"{role.capitalize()} '{username}' added successfully."
        except Exception as e:
            return False, f"Database error: {e}"
        finally:
            conn.close()

    @staticmethod
    def update_user(user_id, full_name, role, phone="", new_password=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if new_password and new_password.strip():
                cursor.execute("""
                    UPDATE users SET full_name = ?, role = ?, phone = ?, password_hash = ?
                    WHERE id = ?
                """, (full_name.strip(), role, phone.strip(), hash_password(new_password.strip()), user_id))
            else:
                cursor.execute("""
                    UPDATE users SET full_name = ?, role = ?, phone = ?
                    WHERE id = ?
                """, (full_name.strip(), role, phone.strip(), user_id))
            conn.commit()
            return True, "User updated successfully."
        except Exception as e:
            return False, f"Update failed: {e}"
        finally:
            conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Prevent deleting the last admin
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False, "User not found."
            if row["role"] == "admin":
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
                if cursor.fetchone()[0] <= 1:
                    return False, "Cannot delete the only admin account."
            
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True, "User deleted successfully."
        except Exception as e:
            return False, f"Delete failed: {e}"
        finally:
            conn.close()


class VehicleModel:
    @staticmethod
    def get_all(search_query="", vehicle_type=None, status_filter=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM vehicles WHERE 1=1"
        params = []
        
        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (name LIKE ? OR model LIKE ? OR fuel_type LIKE ? OR transmission LIKE ?)"
            params.extend([sq, sq, sq, sq])
            
        if vehicle_type and vehicle_type != "All":
            query += " AND vehicle_type = ?"
            params.append(vehicle_type)
            
        if status_filter and status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)
            
        query += " ORDER BY id ASC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_by_id(vehicle_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_available(vehicle_type=None):
        return VehicleModel.get_all(vehicle_type=vehicle_type, status_filter=config.STATUS_AVAILABLE)

    @staticmethod
    def add_vehicle(name, model, vehicle_type="Bike", fuel_type="Petrol", transmission="Manual", engine="N/A", model_year=2023, rate_per_hour=30.0):
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute("""
                INSERT INTO vehicles (name, model, vehicle_type, fuel_type, transmission, engine, model_year, rate_per_hour, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?)
            """, (name.strip(), model.strip(), vehicle_type, fuel_type, transmission, engine.strip(), model_year, rate_per_hour, now_str))
            conn.commit()
            new_id = cursor.lastrowid
            return True, f"Vehicle '{name} {model}' added with ID #{new_id}."
        except Exception as e:
            return False, f"Failed to add vehicle: {e}"
        finally:
            conn.close()

    @staticmethod
    def update_vehicle(vehicle_id, name, model, vehicle_type, fuel_type, transmission, engine, model_year, rate_per_hour, status):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE vehicles SET name = ?, model = ?, vehicle_type = ?, fuel_type = ?, transmission = ?, engine = ?, model_year = ?, rate_per_hour = ?, status = ?
                WHERE id = ?
            """, (name.strip(), model.strip(), vehicle_type, fuel_type, transmission, engine.strip(), model_year, rate_per_hour, status, vehicle_id))
            conn.commit()
            return True, "Vehicle details updated successfully."
        except Exception as e:
            return False, f"Failed to update vehicle: {e}"
        finally:
            conn.close()

    @staticmethod
    def delete_vehicle(vehicle_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Check if currently rented
            cursor.execute("SELECT status, name, model FROM vehicles WHERE id = ?", (vehicle_id,))
            veh = cursor.fetchone()
            if not veh:
                return False, "Vehicle not found."
            if veh["status"] == config.STATUS_RENTED:
                return False, f"Cannot delete '{veh['name']} {veh['model']}' because it is currently rented."
                
            cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
            conn.commit()
            return True, "Vehicle deleted from inventory."
        except Exception as e:
            return False, f"Failed to delete vehicle: {e}"
        finally:
            conn.close()

    @staticmethod
    def update_status(vehicle_id, new_status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE vehicles SET status = ? WHERE id = ?", (new_status, vehicle_id))
        conn.commit()
        conn.close()


class RentalModel:
    @staticmethod
    def create_rental(vehicle_id, customer_name, customer_aadhar, customer_phone, customer_address, staff_username="Staff"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
            veh = cursor.fetchone()
            if not veh:
                return False, "Vehicle not found."
            if veh["status"] != config.STATUS_AVAILABLE:
                return False, f"Vehicle '{veh['name']}' is not available (Status: {veh['status']})."

            now = datetime.now()
            rent_date = now.strftime("%Y-%m-%d")
            rent_time = now.strftime("%H:%M:%S")
            v_name = f"{veh['name']} {veh['model']}".strip()

            # Insert rental record
            cursor.execute("""
                INSERT INTO rentals (
                    vehicle_id, vehicle_name, customer_name, customer_aadhar, customer_phone, customer_address,
                    rent_date, rent_time, rate_per_hour, staff_username, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Rented')
            """, (
                vehicle_id, v_name, customer_name.strip(), customer_aadhar.strip(), customer_phone.strip(), customer_address.strip(),
                rent_date, rent_time, veh["rate_per_hour"], staff_username
            ))
            rental_id = cursor.lastrowid

            # Update vehicle status to Rented
            cursor.execute("UPDATE vehicles SET status = 'Rented' WHERE id = ?", (vehicle_id,))
            conn.commit()
            return True, f"Successfully rented {v_name} to {customer_name}. Rental #{rental_id}"
        except Exception as e:
            conn.rollback()
            return False, f"Failed to process rental: {e}"
        finally:
            conn.close()

    @staticmethod
    def preview_return_calculation(rental_id):
        """Calculates elapsed time and rent amount without saving to DB yet."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rentals WHERE id = ?", (rental_id,))
        rental = cursor.fetchone()
        conn.close()
        
        if not rental:
            return None, "Rental record not found."
        if rental["status"] == config.STATUS_RETURNED:
            return None, "Vehicle has already been returned."

        now = datetime.now()
        rent_dt_str = f"{rental['rent_date']} {rental['rent_time']}"
        try:
            # Handle microsecond if present
            clean_str = rent_dt_str.split(".")[0]
            rent_dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            rent_dt = datetime.strptime(rental['rent_date'], "%Y-%m-%d")

        seconds_diff = max(60, (now - rent_dt).total_seconds())
        # Convert to hours. If rented for less than 1 hour, standard rental policy charges for minimum 1 hour, or exact fraction.
        # Here we charge exact fractional hours with a minimum of 1.0 hour.
        exact_hours = seconds_diff / 3600.0
        billable_hours = max(1.0, round(exact_hours, 2))
        rate = float(rental["rate_per_hour"])
        total_rent = round(billable_hours * rate, 2)

        return {
            "rental_id": rental["id"],
            "vehicle_name": rental["vehicle_name"],
            "customer_name": rental["customer_name"],
            "rent_date": rental["rent_date"],
            "rent_time": rental["rent_time"],
            "return_date": now.strftime("%Y-%m-%d"),
            "return_time": now.strftime("%H:%M:%S"),
            "rate_per_hour": rate,
            "hours_used": billable_hours,
            "total_rent": total_rent,
            "vehicle_id": rental["vehicle_id"]
        }, "Calculation successful"

    @staticmethod
    def process_return(rental_id):
        calc_data, err = RentalModel.preview_return_calculation(rental_id)
        if not calc_data:
            return False, err, None

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Update rental record
            cursor.execute("""
                UPDATE rentals SET
                    return_date = ?,
                    return_time = ?,
                    hours_used = ?,
                    total_rent = ?,
                    status = 'Returned'
                WHERE id = ?
            """, (
                calc_data["return_date"],
                calc_data["return_time"],
                calc_data["hours_used"],
                calc_data["total_rent"],
                rental_id
            ))

            # Update vehicle status back to Available
            cursor.execute("UPDATE vehicles SET status = 'Available' WHERE id = ?", (calc_data["vehicle_id"],))
            conn.commit()
            return True, f"Vehicle returned successfully! Total Rent: ₹{calc_data['total_rent']:.2f}", calc_data
        except Exception as e:
            conn.rollback()
            return False, f"Failed to complete return: {e}", None
        finally:
            conn.close()

    @staticmethod
    def get_active_rentals(search_query=""):
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM rentals WHERE status = 'Rented'"
        params = []
        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (customer_name LIKE ? OR vehicle_name LIKE ? OR customer_phone LIKE ? OR customer_aadhar LIKE ?)"
            params.extend([sq, sq, sq, sq])
        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_rental_history(search_query="", status_filter=None, staff_filter=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM rentals WHERE 1=1"
        params = []

        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (customer_name LIKE ? OR vehicle_name LIKE ? OR customer_phone LIKE ? OR customer_aadhar LIKE ?)"
            params.extend([sq, sq, sq, sq])

        if status_filter and status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)

        if staff_filter and staff_filter != "All":
            query += " AND staff_username = ?"
            params.append(staff_filter)

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_stats():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total_fleet = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'Available'")
        available_fleet = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'Rented'")
        rented_fleet = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(total_rent), 0) FROM rentals WHERE status = 'Returned'")
        total_revenue = cursor.fetchone()[0]

        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM rentals WHERE rent_date = ?", (today_str,))
        rented_today = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'staff'")
        staff_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE vehicle_type = 'Bike'")
        bikes_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE vehicle_type = 'Car'")
        cars_count = cursor.fetchone()[0]

        conn.close()
        return {
            "total_fleet": total_fleet,
            "available_fleet": available_fleet,
            "rented_fleet": rented_fleet,
            "total_revenue": total_revenue,
            "rented_today": rented_today,
            "staff_count": staff_count,
            "bikes_count": bikes_count,
            "cars_count": cars_count
        }
