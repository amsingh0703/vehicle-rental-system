# 🚗 DriveEase — Vehicle Rental Management System

A desktop application built with Python and CustomTkinter for managing vehicle rentals (Bikes & Cars), automated hourly billing, customer records, and fleet inventory.

---

## 🌟 Key Highlights & Upgrades

- **Role-Based Access Control**:
  - 👑 **Admin**: Full business oversight — dashboard metrics, fleet CRUD (add/edit/delete), staff account management, all rental audit logs.
  - 👷 **Staff**: Customer service operations — dispatch rentals, process returns with automatic bill calculation, search inventory, view customer booking history.
- **SQLite Database**: Replaced error-prone CSV files with a relational SQLite database (`data/vehicle_rental.db`) supporting ACID transactions.
- **Automated Hourly Rent Calculation**: Automatically computes elapsed rental duration from pickup time to return time (with minimum 1-hour charge and hourly rate).
- **Security & Data Integrity**:
  - Passwords hashed using **SHA-256**.
  - Strict input validation for **12-digit Indian Aadhar**, **10-digit Phone numbers**, and positive hourly rates.
- **Modern Responsive GUI**: Built with CustomTkinter supporting **Light, Dark, and System Theme** toggling on the fly.
- **Preserved Fleet Data**: Migrated and deduplicated 88 vehicles (62 bikes + 26 cars) from legacy datasets.

---

## 🚀 How to Run

1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd D:\Project
   ```

2. (Optional) Activate your Python virtual environment if using one.

3. Run the application:
   ```powershell
   python app.py
   ```

---

## 🔑 Login Credentials

### 👑 Administrator Accounts
| Username | Password | Role | Access Level |
|---|---|---|---|
| `Amit` | `Amit1234` | Admin | Full Access (Dashboard, Fleet, Staff, History) |
| `admin` | `admin123` | Admin | Full Access |
| `r` | `r` | Admin | Full Access |

### 👷 Staff Accounts
| Username | Password | Role | Access Level |
|---|---|---|---|
| `ritesh` | `Amit1234` | Staff | Frontline Desk (Rent, Return/Bill, Fleet Search) |
| `dg` | `2006` | Staff | Frontline Desk |

*(Admins can create additional staff accounts anytime via the **Staff Management** tab).*

---

## 📁 Project Architecture

```
D:\Project\
├── app.py                  # Main application launcher
├── config.py               # Paths, appearance modes, and constants
├── database.py             # SQLite database initialization & migration
├── auth.py                 # SHA-256 hashing and input validators (Aadhar, Phone, Rate)
├── models.py               # Data Access Object (DAO) for Vehicles, Rentals, Users
├── test_app.py             # Automated unit and integration test suite
├── requirements.txt        # Python package dependencies
├── README.md               # Project guide and documentation
│
├── ui/                     # UI Views and Components
│   ├── theme.py            # Fonts, colors, and design system
│   ├── widgets.py          # Custom DataTable and StatCard widgets
│   ├── login_window.py     # Login screen with Admin / Staff switch
│   ├── main_window.py      # App shell with responsive sidebar navigation
│   ├── dashboard_view.py   # Executive dashboard with stat cards & active fleet
│   ├── inventory_view.py   # Fleet management (Search, Filter, Add, Edit, Delete)
│   ├── rent_view.py        # Rental booking form with customer validation
│   ├── return_view.py      # Return processing & automated bill receipt popup
│   ├── history_view.py     # Rental transaction audit log
│   └── staff_view.py       # Admin staff accounts management
│
└── data/
    └── vehicle_rental.db   # SQLite database
```

---

## 🧪 Testing

To run the automated verification suite:
```powershell
python test_app.py
```
