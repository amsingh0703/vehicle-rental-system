"""Automated verification suite for DriveEase Vehicle Rental System."""
import unittest
from datetime import datetime
import config
from database import init_db, get_connection
from models import UserModel, VehicleModel, RentalModel
from auth import hash_password, verify_password, validate_aadhar, validate_phone, validate_rate, validate_year

class TestDriveEaseSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_authentication_admin(self):
        # Test Admin login
        user, msg = UserModel.authenticate("Amit", "Amit1234", expected_role="admin")
        self.assertIsNotNone(user, f"Admin login failed: {msg}")
        self.assertEqual(user["role"], "admin")

    def test_02_authentication_staff(self):
        # Test Staff login
        user, msg = UserModel.authenticate("ritesh", "Amit1234", expected_role="staff")
        self.assertIsNotNone(user, f"Staff login failed: {msg}")
        self.assertEqual(user["role"], "staff")

    def test_03_validation(self):
        # Aadhar validation
        ok, _ = validate_aadhar("123456789012")
        self.assertTrue(ok)
        bad, _ = validate_aadhar("1234")
        self.assertFalse(bad)

        # Phone validation
        ok_p, _ = validate_phone("9876543210")
        self.assertTrue(ok_p)
        bad_p, _ = validate_phone("123")
        self.assertFalse(bad_p)

        # Rate validation
        ok_r, _, val = validate_rate("50.0")
        self.assertTrue(ok_r)
        self.assertEqual(val, 50.0)

    def test_04_fleet_operations(self):
        # Test adding vehicle
        ok, msg = VehicleModel.add_vehicle(
            name="TestMake",
            model="TestModelX",
            vehicle_type="Bike",
            fuel_type="Electric",
            transmission="Automatic",
            rate_per_hour=45.0
        )
        self.assertTrue(ok)

        # Search for it
        results = VehicleModel.get_all(search_query="TestModelX")
        self.assertGreater(len(results), 0)
        test_veh_id = results[0]["id"]

        # Clean up
        del_ok, _ = VehicleModel.delete_vehicle(test_veh_id)
        self.assertTrue(del_ok)

    def test_05_rental_lifecycle(self):
        # Find an available vehicle
        avail = VehicleModel.get_available()
        self.assertGreater(len(avail), 0, "Need at least one available vehicle")
        v = avail[0]

        # Rent it
        rent_ok, rent_msg = RentalModel.create_rental(
            vehicle_id=v["id"],
            customer_name="Test Customer",
            customer_aadhar="999988887777",
            customer_phone="9876543210",
            customer_address="Test City",
            staff_username="ritesh"
        )
        self.assertTrue(rent_ok, rent_msg)

        # Verify active rentals
        active = RentalModel.get_active_rentals(search_query="Test Customer")
        self.assertGreater(len(active), 0)
        rental_id = active[0]["id"]

        # Calculate & Return
        ret_ok, ret_msg, calc = RentalModel.process_return(rental_id)
        self.assertTrue(ret_ok, ret_msg)
        self.assertGreater(calc["total_rent"], 0)

    def test_06_dashboard_stats(self):
        stats = RentalModel.get_stats()
        self.assertIn("total_fleet", stats)
        self.assertIn("total_revenue", stats)
        self.assertIn("available_fleet", stats)
        self.assertGreater(stats["total_fleet"], 0)

if __name__ == "__main__":
    unittest.main()
