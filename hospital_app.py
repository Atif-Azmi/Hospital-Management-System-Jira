"""
Hospital Management System - Main Application
Login first, then each role sees only the modules it is allowed to use.

  Admin         -> Patients, Appointments, Billing, User management
  Doctor        -> Appointments
  Receptionist  -> Patients, Billing

Run:  python hospital_app.py
"""

import login_module
import patient_module
import doctor_appointment_module
import billing_module


def init_all():
    patient_module.init_db()
    doctor_appointment_module.init_db()
    billing_module.init_db()
    login_module.init_db()


def first_run_setup():
    """If no user exists yet, create the first Admin account."""
    if login_module.user_count() > 0:
        return
    print("No users found. Create the first Admin account.")
    while True:
        username = input("Admin username: ").strip()
        password = input("Admin password (min 6 chars): ")
        ok, msg = login_module.register_user(username, password, "Admin")
        print(msg)
        if ok:
            break


def do_login():
    for attempt in range(3):
        username = input("Username: ").strip()
        password = input("Password: ")
        ok, result = login_module.login(username, password)
        if ok:
            print("Login successful. Role: {}".format(result))
            return username, result
        print(result)
    print("Too many failed attempts.")
    return None, None


MODULES = {
    "patients": ("Patient Module", patient_module.menu),
    "appointments": ("Doctor & Appointment Module", doctor_appointment_module.menu),
    "billing": ("Billing Module", billing_module.menu),
    "users": ("User Management", login_module.users_menu),
}


def main_menu(username, role):
    allowed = login_module.PERMISSIONS[role]
    while True:
        print("\n===== HOSPITAL MANAGEMENT SYSTEM =====")
        print("User: {}  |  Role: {}".format(username, role))
        for number, key in enumerate(allowed, start=1):
            print("{}. {}".format(number, MODULES[key][0]))
        print("{}. Logout".format(len(allowed) + 1))
        choice = input("Choose: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(allowed):
            MODULES[allowed[int(choice) - 1]][1]()
        elif choice == str(len(allowed) + 1):
            print("Logged out.")
            return
        else:
            print("Invalid choice.")


def main():
    init_all()
    first_run_setup()
    username, role = do_login()
    if role:
        main_menu(username, role)


if __name__ == "__main__":
    main()