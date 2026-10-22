"""
Hospital Management System - Doctor & Appointment Module (SCRUM-7)
Features: add/view/edit doctor, book appointment, view, cancel, reschedule.
Uses the same hospital.db as patient_module.py (register patients there first).
Run:  python doctor_appointment_module.py
"""

import sqlite3

DB_NAME = "hospital.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS Patient (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, age INTEGER NOT NULL, gender TEXT NOT NULL,
            contact TEXT NOT NULL, address TEXT, medical_history TEXT)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS Doctor (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, specialization TEXT NOT NULL,
            contact TEXT NOT NULL, availability TEXT)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS Appointment (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL, doctor_id INTEGER NOT NULL,
            appt_date TEXT NOT NULL, appt_time TEXT NOT NULL,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id))"""
    )
    conn.commit()
    conn.close()


# ---------------- Doctor ----------------
def add_doctor(name, specialization, contact, availability=""):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO Doctor (name, specialization, contact, availability) VALUES (?,?,?,?)",
        (name, specialization, contact, availability),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def view_doctors():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Doctor ORDER BY doctor_id").fetchall()
    conn.close()
    return rows


def get_doctor(doctor_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM Doctor WHERE doctor_id=?", (doctor_id,)).fetchone()
    conn.close()
    return row


def edit_doctor(doctor_id, name, specialization, contact, availability):
    conn = get_connection()
    cur = conn.execute(
        "UPDATE Doctor SET name=?, specialization=?, contact=?, availability=? WHERE doctor_id=?",
        (name, specialization, contact, availability, doctor_id),
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


# ---------------- Appointment ----------------
def slot_is_free(doctor_id, appt_date, appt_time, ignore_id=None):
    """A doctor cannot have two active appointments at the same date and time."""
    conn = get_connection()
    row = conn.execute(
        "SELECT appointment_id FROM Appointment WHERE doctor_id=? AND appt_date=? "
        "AND appt_time=? AND status='Booked' AND appointment_id IS NOT ?",
        (doctor_id, appt_date, appt_time, ignore_id),
    ).fetchone()
    conn.close()
    return row is None


def book_appointment(patient_id, doctor_id, appt_date, appt_time):
    """Returns (appointment_id, message). appointment_id is None on failure."""
    conn = get_connection()
    patient = conn.execute("SELECT 1 FROM Patient WHERE patient_id=?", (patient_id,)).fetchone()
    doctor = conn.execute("SELECT 1 FROM Doctor WHERE doctor_id=?", (doctor_id,)).fetchone()
    conn.close()
    if not patient:
        return None, "Patient ID not found. Register the patient first."
    if not doctor:
        return None, "Doctor ID not found."
    if not slot_is_free(doctor_id, appt_date, appt_time):
        return None, "Doctor is already booked at that date and time."
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO Appointment (patient_id, doctor_id, appt_date, appt_time, status) "
        "VALUES (?,?,?,?, 'Booked')",
        (patient_id, doctor_id, appt_date, appt_time),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id, "Appointment booked."


def view_appointments():
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.appointment_id, p.name, d.name, a.appt_date, a.appt_time, a.status
           FROM Appointment a
           JOIN Patient p ON a.patient_id = p.patient_id
           JOIN Doctor d ON a.doctor_id = d.doctor_id
           ORDER BY a.appt_date, a.appt_time"""
    ).fetchall()
    conn.close()
    return rows


def cancel_appointment(appointment_id):
    conn = get_connection()
    cur = conn.execute(
        "UPDATE Appointment SET status='Cancelled' WHERE appointment_id=? AND status='Booked'",
        (appointment_id,),
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def reschedule_appointment(appointment_id, new_date, new_time):
    """Returns (ok, message)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT doctor_id, status FROM Appointment WHERE appointment_id=?", (appointment_id,)
    ).fetchone()
    conn.close()
    if not row:
        return False, "Appointment not found."
    if row[1] != "Booked":
        return False, "Only booked appointments can be rescheduled."
    if not slot_is_free(row[0], new_date, new_time, ignore_id=appointment_id):
        return False, "Doctor is already booked at that date and time."
    conn = get_connection()
    conn.execute(
        "UPDATE Appointment SET appt_date=?, appt_time=? WHERE appointment_id=?",
        (new_date, new_time, appointment_id),
    )
    conn.commit()
    conn.close()
    return True, "Appointment rescheduled."


# ---------------- Menu ----------------
def print_doctors(rows):
    if not rows:
        print("No doctor found.")
        return
    print("\n{:<5} {:<20} {:<18} {:<14} {}".format("ID", "Name", "Specialization", "Contact", "Availability"))
    print("-" * 80)
    for r in rows:
        print("{:<5} {:<20} {:<18} {:<14} {}".format(r[0], r[1], r[2], r[3], r[4] or "-"))


def print_appointments(rows):
    if not rows:
        print("No appointment found.")
        return
    print("\n{:<5} {:<20} {:<20} {:<12} {:<7} {}".format("ID", "Patient", "Doctor", "Date", "Time", "Status"))
    print("-" * 80)
    for r in rows:
        print("{:<5} {:<20} {:<20} {:<12} {:<7} {}".format(*r))


def ask_int(prompt):
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a number.")


def menu():
    init_db()
    while True:
        print("\n===== DOCTOR & APPOINTMENT MODULE =====")
        print("1. Add doctor")
        print("2. View doctors")
        print("3. Edit doctor")
        print("4. Book appointment")
        print("5. View appointments")
        print("6. Cancel appointment")
        print("7. Reschedule appointment")
        print("8. Exit")
        choice = input("Choose (1-8): ").strip()

        if choice == "1":
            name = input("Doctor name: ").strip()
            spec = input("Specialization: ").strip()
            contact = input("Contact: ").strip()
            avail = input("Availability (e.g. Mon-Fri 10am-4pm): ").strip()
            if not name or not spec or not contact:
                print("Name, specialization and contact are required.")
                continue
            print("Doctor added. ID =", add_doctor(name, spec, contact, avail))

        elif choice == "2":
            print_doctors(view_doctors())

        elif choice == "3":
            did = ask_int("Doctor ID to edit: ")
            old = get_doctor(did)
            if not old:
                print("Doctor not found.")
                continue
            print("Press Enter to keep the old value.")
            name = input("Name [{}]: ".format(old[1])).strip() or old[1]
            spec = input("Specialization [{}]: ".format(old[2])).strip() or old[2]
            contact = input("Contact [{}]: ".format(old[3])).strip() or old[3]
            avail = input("Availability [{}]: ".format(old[4] or "")).strip() or old[4]
            edit_doctor(did, name, spec, contact, avail)
            print("Doctor updated.")

        elif choice == "4":
            pid = ask_int("Patient ID: ")
            did = ask_int("Doctor ID: ")
            date = input("Date (YYYY-MM-DD): ").strip()
            time = input("Time (HH:MM): ").strip()
            appt_id, msg = book_appointment(pid, did, date, time)
            print(msg + (" ID = {}".format(appt_id) if appt_id else ""))

        elif choice == "5":
            print_appointments(view_appointments())

        elif choice == "6":
            aid = ask_int("Appointment ID to cancel: ")
            print("Appointment cancelled." if cancel_appointment(aid)
                  else "Not found or already cancelled.")

        elif choice == "7":
            aid = ask_int("Appointment ID to reschedule: ")
            date = input("New date (YYYY-MM-DD): ").strip()
            time = input("New time (HH:MM): ").strip()
            print(reschedule_appointment(aid, date, time)[1])

        elif choice == "8":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()