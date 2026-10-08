import os
import sys

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database path
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "vehicle_rental.db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Application Information
APP_TITLE = "DriveEase - Vehicle Rental Management System"
APP_VERSION = "2.0.0"
WINDOW_SIZE = "1150x750"
MIN_WINDOW_SIZE = (1000, 650)

# Role Constants
ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"

# Status Constants
STATUS_AVAILABLE = "Available"
STATUS_RENTED = "Rented"
STATUS_RETURNED = "Returned"
STATUS_MAINTENANCE = "Maintenance"

# Vehicle Types
TYPE_BIKE = "Bike"
TYPE_CAR = "Car"
