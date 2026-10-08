import hashlib
import re

def hash_password(password: str) -> str:
    """Hashes a plain text password using SHA-256."""
    if not password:
        return ""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored SHA-256 hash."""
    return hash_password(password) == hashed_password

def validate_aadhar(aadhar: str) -> tuple[bool, str]:
    """Validates 12-digit Indian Aadhar number."""
    cleaned = aadhar.strip().replace(" ", "").replace("-", "")
    if not cleaned:
        return False, "Aadhar number cannot be empty."
    if not cleaned.isdigit() or len(cleaned) != 12:
        return False, "Aadhar must be exactly 12 digits."
    return True, ""

def validate_phone(phone: str) -> tuple[bool, str]:
    """Validates 10-digit phone number."""
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    if not cleaned:
        return False, "Phone number cannot be empty."
    if not cleaned.isdigit() or len(cleaned) != 10:
        return False, "Phone number must be exactly 10 digits."
    return True, ""

def validate_rate(rate_str: str) -> tuple[bool, str, float]:
    """Validates hourly rate to be a positive number."""
    try:
        val = float(rate_str)
        if val <= 0:
            return False, "Rate per hour must be greater than 0.", 0.0
        return True, "", val
    except ValueError:
        return False, "Rate per hour must be a valid numeric value.", 0.0

def validate_year(year_str: str) -> tuple[bool, str, int]:
    """Validates model year to be a 4-digit reasonable year."""
    try:
        val = int(year_str)
        if val < 1980 or val > 2030:
            return False, "Year must be between 1980 and 2030.", 0
        return True, "", val
    except ValueError:
        return False, "Year must be a valid 4-digit number.", 0
