"""
White-box tests for the Hospital Management System (SCRUM-10).
Each test targets a specific branch / path in the source code.
Every test uses a temporary database, so hospital.db is never touched.

Run all tests:           python test_whitebox.py -v
Run with coverage:       pip install coverage
                         coverage run test_whitebox.py
                         coverage report -m
                         coverage html          (open htmlcov/index.html)
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import billing_module
import doctor_appointment_module as appt
import hospital_app
import login_module
import patient_module

ALL_MODULES = (patient_module, appt, billing_module, login_module)


class BaseTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        for module in ALL_MODULES:
            module.DB_NAME = self.db_path
        hospital_app.init_all()

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def make_patient(self, name="Rahul"):
        return patient_module.add_patient(name, 30, "Male", "9999999999", "Nagpur", "None")

    def make_doctor(self):
        return appt.add_doctor("Dr Mehta", "Cardiology", "9000000001", "Mon-Fri")


def run_menu(menu_function, inputs):
    """Run an interactive menu with scripted input and return what it printed."""
    buffer = io.StringIO()
    with patch("builtins.input", side_effect=inputs), redirect_stdout(buffer):
        menu_function()
    return buffer.getvalue()


# ---------------------------------------------------------------- Patient
class TestPatient(BaseTest):
    def test_wb01_add_patient_returns_id(self):
        """Path: INSERT executes, lastrowid returned."""
        self.assertEqual(self.make_patient(), 1)

    def test_wb02_view_patients_empty_and_filled(self):
        """Branch: no rows vs rows."""
        self.assertEqual(patient_module.view_patients(), [])
        self.make_patient()
        self.assertEqual(len(patient_module.view_patients()), 1)

    def test_wb03_search_by_numeric_keyword_uses_id_branch(self):
        """Branch: keyword.isdigit() == True."""
        self.make_patient("Amit")
        self.assertEqual(len(patient_module.search_patient("1")), 1)

    def test_wb04_search_by_name_uses_name_branch(self):
        """Branch: keyword.isdigit() == False (partial, case-insensitive)."""
        self.make_patient("Priya Verma")
        self.assertEqual(len(patient_module.search_patient("priya")), 1)

    def test_wb05_search_no_match(self):
        """Branch: query returns no rows."""
        self.assertEqual(patient_module.search_patient("zzz"), [])

    def test_wb06_edit_existing_and_missing(self):
        """Branch: rowcount > 0 (True) and rowcount == 0 (False)."""
        pid = self.make_patient()
        self.assertTrue(patient_module.edit_patient(pid, "New", 31, "Male", "1", "A", "B"))
        self.assertFalse(patient_module.edit_patient(99, "X", 1, "M", "1", "A", "B"))

    def test_wb07_delete_existing_and_missing(self):
        """Branch: rowcount > 0 (True) and rowcount == 0 (False)."""
        pid = self.make_patient()
        self.assertTrue(patient_module.delete_patient(pid))
        self.assertFalse(patient_module.delete_patient(pid))

    def test_wb08_print_patients_empty_and_filled(self):
        """Branch: print_patients with no rows and with rows."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            patient_module.print_patients([])
            self.make_patient("Sita")
            patient_module.print_patients(patient_module.view_patients())
        self.assertIn("No patient found.", buffer.getvalue())
        self.assertIn("Sita", buffer.getvalue())

    def test_wb09_menu_register_view_search_edit_delete_exit(self):
        """Path: menu loop through options 1,2,3,4,5,6."""
        inputs = [
            "1", "Amit", "abc", "40", "Male", "9999999999", "Pune", "None",  # register (bad age first)
            "2",
            "3", "Amit",
            "4", "1", "Amit K", "", "", "", "", "",
            "5", "1", "y",
            "6",
        ]
        output = run_menu(patient_module.menu, inputs)
        self.assertIn("Please enter a number.", output)
        self.assertIn("Patient registered. ID = 1", output)
        self.assertIn("Patient updated.", output)
        self.assertIn("Patient deleted.", output)
        self.assertIn("Goodbye.", output)

    def test_wb10_menu_validation_branches(self):
        """Branches: missing required field, edit missing id, delete cancelled, invalid choice."""
        inputs = [
            "1", "", "20", "", "", "", "",   # name/gender/contact missing
            "4", "99",                       # edit non-existent
            "5", "99", "n",                  # delete cancelled
            "5", "99", "y",                  # delete not found
            "9",                             # invalid choice
            "6",
        ]
        output = run_menu(patient_module.menu, inputs)
        self.assertIn("required", output)
        self.assertIn("Patient not found.", output)
        self.assertIn("Cancelled.", output)
        self.assertIn("Invalid choice.", output)


# ------------------------------------------------- Doctor & Appointment
class TestDoctorAppointment(BaseTest):
    def test_wb11_add_view_get_edit_doctor(self):
        """Paths: add, view, get (found/not found), edit (found/not found)."""
        did = self.make_doctor()
        self.assertEqual(len(appt.view_doctors()), 1)
        self.assertIsNotNone(appt.get_doctor(did))
        self.assertIsNone(appt.get_doctor(99))
        self.assertTrue(appt.edit_doctor(did, "Dr M", "ENT", "1", "Sat"))
        self.assertFalse(appt.edit_doctor(99, "X", "Y", "1", "Z"))

    def test_wb12_book_success(self):
        """Path: patient exists, doctor exists, slot free."""
        pid, did = self.make_patient(), self.make_doctor()
        appt_id, msg = appt.book_appointment(pid, did, "2026-10-30", "10:00")
        self.assertEqual(appt_id, 1)
        self.assertEqual(msg, "Appointment booked.")

    def test_wb13_book_unknown_patient(self):
        """Branch: patient not found."""
        did = self.make_doctor()
        appt_id, msg = appt.book_appointment(99, did, "2026-10-30", "10:00")
        self.assertIsNone(appt_id)
        self.assertIn("Patient ID not found", msg)

    def test_wb14_book_unknown_doctor(self):
        """Branch: doctor not found."""
        pid = self.make_patient()
        appt_id, msg = appt.book_appointment(pid, 99, "2026-10-30", "10:00")
        self.assertIsNone(appt_id)
        self.assertIn("Doctor ID not found", msg)

    def test_wb15_double_booking_rejected(self):
        """Branch: slot_is_free() == False."""
        pid, did = self.make_patient(), self.make_doctor()
        appt.book_appointment(pid, did, "2026-10-30", "10:00")
        appt_id, msg = appt.book_appointment(pid, did, "2026-10-30", "10:00")
        self.assertIsNone(appt_id)
        self.assertIn("already booked", msg)

    def test_wb16_cancel_then_cancel_again(self):
        """Branch: cancel booked (True) then already cancelled (False)."""
        pid, did = self.make_patient(), self.make_doctor()
        aid, _ = appt.book_appointment(pid, did, "2026-10-30", "10:00")
        self.assertTrue(appt.cancel_appointment(aid))
        self.assertFalse(appt.cancel_appointment(aid))

    def test_wb17_cancelled_slot_can_be_rebooked(self):
        """Branch: slot_is_free ignores Cancelled appointments."""
        pid, did = self.make_patient(), self.make_doctor()
        aid, _ = appt.book_appointment(pid, did, "2026-10-30", "10:00")
        appt.cancel_appointment(aid)
        new_id, _ = appt.book_appointment(pid, did, "2026-10-30", "10:00")
        self.assertIsNotNone(new_id)

    def test_wb18_reschedule_all_branches(self):
        """Branches: not found, not Booked, slot taken, success, same slot."""
        pid, did = self.make_patient(), self.make_doctor()
        a1, _ = appt.book_appointment(pid, did, "2026-10-30", "10:00")
        a2, _ = appt.book_appointment(pid, did, "2026-10-30", "11:00")
        self.assertEqual(appt.reschedule_appointment(99, "2026-11-01", "09:00")[1], "Appointment not found.")
        self.assertFalse(appt.reschedule_appointment(a1, "2026-10-30", "11:00")[0])  # slot taken by a2
        self.assertTrue(appt.reschedule_appointment(a1, "2026-10-30", "10:00")[0])   # same slot, ignore_id
        self.assertTrue(appt.reschedule_appointment(a1, "2026-11-02", "09:00")[0])   # success
        appt.cancel_appointment(a2)
        self.assertIn("Only booked", appt.reschedule_appointment(a2, "2026-11-03", "09:00")[1])

    def test_wb19_view_appointments_joins_names(self):
        """Path: JOIN returns patient and doctor names."""
        pid, did = self.make_patient("Rahul"), self.make_doctor()
        appt.book_appointment(pid, did, "2026-10-30", "10:00")
        rows = appt.view_appointments()
        self.assertEqual(rows[0][1], "Rahul")
        self.assertEqual(rows[0][2], "Dr Mehta")

    def test_wb20_print_functions_empty(self):
        """Branch: print with no rows."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            appt.print_doctors([])
            appt.print_appointments([])
        self.assertIn("No doctor found.", buffer.getvalue())
        self.assertIn("No appointment found.", buffer.getvalue())

    def test_wb21_menu_full_flow(self):
        """Path: menu options 1-8 including booking and a failed booking."""
        self.make_patient()
        inputs = [
            "1", "Dr A", "ENT", "111", "Mon",
            "2",
            "3", "1", "Dr AA", "", "", "",
            "4", "1", "1", "2026-10-30", "10:00",
            "4", "1", "1", "2026-10-30", "10:00",   # double booking
            "5",
            "7", "1", "2026-10-31", "11:00",
            "6", "1",
            "8",
        ]
        output = run_menu(appt.menu, inputs)
        self.assertIn("Doctor added. ID = 1", output)
        self.assertIn("Appointment booked.", output)
        self.assertIn("already booked", output)
        self.assertIn("Appointment rescheduled.", output)
        self.assertIn("Appointment cancelled.", output)

    def test_wb22_menu_validation_branches(self):
        """Branches: missing doctor fields, edit missing doctor, cancel missing, invalid choice."""
        inputs = ["1", "", "", "", "", "3", "99", "6", "99", "0", "8"]
        output = run_menu(appt.menu, inputs)
        self.assertIn("required", output)
        self.assertIn("Doctor not found.", output)
        self.assertIn("Not found or already cancelled.", output)
        self.assertIn("Invalid choice.", output)


# ---------------------------------------------------------------- Billing
class TestBilling(BaseTest):
    def test_wb23_generate_bill_total(self):
        """Path: success. total = consultation + medicine + other."""
        pid = self.make_patient()
        bill_id, total, msg = billing_module.generate_bill(pid, 500, 300, 50)
        self.assertEqual((bill_id, total), (1, 850))
        self.assertEqual(msg, "Bill generated.")

    def test_wb24_generate_bill_negative_charge(self):
        """Branch: value < 0."""
        pid = self.make_patient()
        bill_id, _, msg = billing_module.generate_bill(pid, -5, 1)
        self.assertIsNone(bill_id)
        self.assertIn("negative", msg)

    def test_wb25_generate_bill_unknown_patient(self):
        """Branch: patient not found."""
        bill_id, _, msg = billing_module.generate_bill(99, 1, 1)
        self.assertIsNone(bill_id)
        self.assertIn("Patient ID not found", msg)

    def test_wb26_view_bills_all_and_by_patient(self):
        """Branches: patient_id is None vs not None."""
        p1, p2 = self.make_patient("A"), self.make_patient("B")
        billing_module.generate_bill(p1, 100, 0)
        billing_module.generate_bill(p2, 200, 0)
        self.assertEqual(len(billing_module.view_bills()), 2)
        self.assertEqual(len(billing_module.view_bills(p1)), 1)

    def test_wb27_update_payment_status_branches(self):
        """Branches: invalid status, bill not found, success."""
        pid = self.make_patient()
        billing_module.generate_bill(pid, 100, 0)
        self.assertFalse(billing_module.update_payment_status(1, "Maybe"))
        self.assertFalse(billing_module.update_payment_status(99, "Paid"))
        self.assertTrue(billing_module.update_payment_status(1, "Paid"))

    def test_wb28_totals(self):
        """Path: SUM for Paid and Pending, COALESCE 0 when empty."""
        self.assertEqual(billing_module.totals(), (0, 0))
        pid = self.make_patient()
        billing_module.generate_bill(pid, 100, 0)
        billing_module.generate_bill(pid, 50, 0)
        billing_module.update_payment_status(1, "Paid")
        self.assertEqual(billing_module.totals(), (100, 50))

    def test_wb29_print_bills_empty(self):
        """Branch: no bills."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            billing_module.print_bills([])
        self.assertIn("No bill found.", buffer.getvalue())

    def test_wb30_menu_full_flow(self):
        """Path: menu options 1-6 with a bad amount first."""
        self.make_patient()
        inputs = [
            "1", "1", "abc", "500", "300", "0",
            "2",
            "3", "1",
            "4", "1", "paid",
            "4", "9", "paid",
            "5",
            "9",
            "6",
        ]
        output = run_menu(billing_module.menu, inputs)
        self.assertIn("Please enter an amount", output)
        self.assertIn("Total = 800.00", output)
        self.assertIn("Payment status updated to Paid", output)
        self.assertIn("Bill not found or status invalid.", output)
        self.assertIn("Total paid: 800.00", output)
        self.assertIn("Invalid choice.", output)


# ------------------------------------------------------------------ Login
class TestLogin(BaseTest):
    def test_wb31_hash_is_salted_and_repeatable(self):
        """Path: salt generated vs salt supplied."""
        salt1, hash1 = login_module.hash_password("secret1")
        salt2, hash2 = login_module.hash_password("secret1")
        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)
        self.assertEqual(login_module.hash_password("secret1", salt1)[1], hash1)

    def test_wb32_register_validation_branches(self):
        """Branches: empty username, short password, bad role, success, duplicate."""
        self.assertFalse(login_module.register_user("", "secret1", "Admin")[0])
        self.assertFalse(login_module.register_user("a", "123", "Admin")[0])
        self.assertFalse(login_module.register_user("a", "secret1", "Janitor")[0])
        self.assertTrue(login_module.register_user("a", "secret1", "Admin")[0])
        self.assertEqual(login_module.register_user("a", "secret1", "Admin")[1], "Username already exists.")

    def test_wb33_password_is_not_stored_in_plain_text(self):
        """Security: database holds only salt and hash."""
        login_module.register_user("a", "secret1", "Admin")
        conn = login_module.get_connection()
        stored = conn.execute("SELECT password_hash, salt FROM Users").fetchone()
        conn.close()
        self.assertNotIn("secret1", stored[0] + stored[1])

    def test_wb34_login_branches(self):
        """Branches: unknown user, wrong password, correct password."""
        login_module.register_user("doc", "secret1", "Doctor")
        self.assertEqual(login_module.login("nobody", "x"), (False, "Invalid username or password."))
        self.assertEqual(login_module.login("doc", "wrong"), (False, "Invalid username or password."))
        self.assertEqual(login_module.login("doc", "secret1"), (True, "Doctor"))

    def test_wb35_role_permissions(self):
        """Path: can_access for each role."""
        self.assertTrue(login_module.can_access("Admin", "users"))
        self.assertTrue(login_module.can_access("Doctor", "appointments"))
        self.assertFalse(login_module.can_access("Doctor", "billing"))
        self.assertTrue(login_module.can_access("Receptionist", "patients"))
        self.assertFalse(login_module.can_access("Receptionist", "appointments"))
        self.assertFalse(login_module.can_access("Unknown", "patients"))

    def test_wb36_delete_user_branches(self):
        """Branches: not found, last admin protected, normal user, admin when 2 admins."""
        login_module.register_user("admin1", "secret1", "Admin")
        login_module.register_user("doc", "secret1", "Doctor")
        self.assertEqual(login_module.delete_user(99), (False, "User not found."))
        self.assertEqual(login_module.delete_user(1), (False, "Cannot delete the last Admin."))
        self.assertTrue(login_module.delete_user(2)[0])
        login_module.register_user("admin2", "secret1", "Admin")
        self.assertTrue(login_module.delete_user(1)[0])

    def test_wb37_user_count_and_list(self):
        """Path: counts and lists."""
        self.assertEqual(login_module.user_count(), 0)
        login_module.register_user("a", "secret1", "Admin")
        self.assertEqual(login_module.user_count(), 1)
        self.assertEqual(login_module.list_users()[0][1], "a")

    def test_wb38_users_menu(self):
        """Path: users_menu options 1,2,3,4 and invalid input."""
        login_module.register_user("boss", "secret1", "Admin")
        inputs = [
            "1", "nurse", "secret1", "receptionist",
            "2",
            "3", "abc",
            "3", "2",
            "9",
            "4",
        ]
        output = run_menu(login_module.users_menu, inputs)
        self.assertIn("User created.", output)
        self.assertIn("nurse", output)
        self.assertIn("Please enter a number.", output)
        self.assertIn("User deleted.", output)
        self.assertIn("Invalid choice.", output)


# ---------------------------------------------------------- Main application
class TestApp(BaseTest):
    def test_wb39_first_run_creates_admin_once(self):
        """Branches: no users (setup runs) and users exist (setup skipped)."""
        output = run_menu(hospital_app.first_run_setup, ["admin", "abc", "admin", "secret1"])
        self.assertIn("Password must be at least 6 characters.", output)
        self.assertEqual(login_module.user_count(), 1)
        self.assertEqual(run_menu(hospital_app.first_run_setup, []), "")

    def test_wb40_login_success_and_lockout(self):
        """Branches: success on 1st try; 3 failed attempts returns (None, None)."""
        login_module.register_user("admin", "secret1", "Admin")
        buffer = io.StringIO()
        with patch("builtins.input", side_effect=["admin", "secret1"]), redirect_stdout(buffer):
            self.assertEqual(hospital_app.do_login(), ("admin", "Admin"))
        with patch("builtins.input", side_effect=["admin", "x"] * 3), redirect_stdout(buffer):
            self.assertEqual(hospital_app.do_login(), (None, None))
        self.assertIn("Too many failed attempts.", buffer.getvalue())

    def test_wb41_main_menu_shows_only_allowed_modules(self):
        """Path: Doctor sees 1 module, Receptionist sees 2, Admin sees 4."""
        doctor = run_menu(lambda: hospital_app.main_menu("d", "Doctor"), ["9", "2"])
        self.assertIn("Doctor & Appointment Module", doctor)
        self.assertNotIn("Billing Module", doctor)
        receptionist = run_menu(lambda: hospital_app.main_menu("r", "Receptionist"), ["3"])
        self.assertIn("Patient Module", receptionist)
        self.assertIn("Billing Module", receptionist)
        self.assertNotIn("Doctor & Appointment Module", receptionist)
        admin = run_menu(lambda: hospital_app.main_menu("a", "Admin"), ["5"])
        self.assertIn("User Management", admin)
        self.assertIn("Logged out.", admin)

    def test_wb42_main_menu_opens_a_module(self):
        """Path: choosing option 1 opens the first allowed module, then logout."""
        output = run_menu(lambda: hospital_app.main_menu("d", "Doctor"), ["1", "8", "2"])
        self.assertIn("DOCTOR & APPOINTMENT MODULE", output)
        self.assertIn("Logged out.", output)

    def test_wb43_main_end_to_end(self):
        """Path: main() -> setup -> login -> menu -> logout."""
        output = run_menu(hospital_app.main, ["admin", "secret1", "admin", "secret1", "5"])
        self.assertIn("Login successful. Role: Admin", output)
        self.assertIn("Logged out.", output)

    def test_wb44_main_login_failure_skips_menu(self):
        """Branch: login fails 3 times, menu is never shown."""
        login_module.register_user("admin", "secret1", "Admin")
        output = run_menu(hospital_app.main, ["admin", "x", "admin", "x", "admin", "x"])
        self.assertNotIn("HOSPITAL MANAGEMENT SYSTEM", output)


if __name__ == "__main__":
    unittest.main()