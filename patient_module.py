"""
Hospital Management System - Patient Module (SCRUM-6)
Features: register, view all, search, edit, delete patient.
Database: SQLite (file: hospital.db). No installation needed.
Run:  python patient_module.py
"""

import sqlite3

DB_NAME = "hospital.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create the Patient table (same columns as database_design.sql)."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Patient (
            patient_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            age             INTEGER NOT NULL,
            gender          TEXT NOT NULL,
            contact         TEXT NOT NULL,
            address         TEXT,
            medical_history TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def print_patients(rows):
    if not rows:
        print("No patient found.")
        return
    print("\n{:<5} {:<20} {:<5} {:<8} {:<14} {:<20} {}".format(
        "ID", "Name", "Age", "Gender", "Contact", "Address", "Medical History"))
    print("-" * 95)
    for r in rows:
        print("{:<5} {:<20} {:<5} {:<8} {:<14} {:<20} {}".format(
            r[0], r[1], r[2], r[3], r[4], r[5] or "-", r[6] or "-"))


def add_patient(name, age, gender, contact, address="", medical_history=""):
    """1. Register a new patient. Returns new patient_id."""
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO Patient (name, age, gender, contact, address, medical_history) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (name, age, gender, contact, address, medical_history),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def view_patients():
    """2. View all patients."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Patient ORDER BY patient_id").fetchall()
    conn.close()
    return rows


def search_patient(keyword):
    """3. Search by patient ID or by name (partial match)."""
    conn = get_connection()
    if keyword.isdigit():
        rows = conn.execute(
            "SELECT * FROM Patient WHERE patient_id = ? OR name LIKE ?",
            (int(keyword), "%" + keyword + "%"),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM Patient WHERE name LIKE ?", ("%" + keyword + "%",)
        ).fetchall()
    conn.close()
    return rows


def edit_patient(patient_id, name, age, gender, contact, address, medical_history):
    """4. Edit patient details. Returns True if a record was updated."""
    conn = get_connection()
    cur = conn.execute(
        "UPDATE Patient SET name=?, age=?, gender=?, contact=?, address=?, "
        "medical_history=? WHERE patient_id=?",
        (name, age, gender, contact, address, medical_history, patient_id),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def delete_patient(patient_id):
    """5. Delete a patient. Returns True if a record was deleted."""
    conn = get_connection()
    cur = conn.execute("DELETE FROM Patient WHERE patient_id = ?", (patient_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def ask_int(prompt):
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a number.")


def menu():
    init_db()
    while True:
        print("\n===== PATIENT MODULE =====")
        print("1. Register new patient")
        print("2. View all patients")
        print("3. Search patient (name / ID)")
        print("4. Edit patient")
        print("5. Delete patient")
        print("6. Exit")
        choice = input("Choose (1-6): ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            age = ask_int("Age: ")
            gender = input("Gender (Male/Female/Other): ").strip()
            contact = input("Contact: ").strip()
            address = input("Address: ").strip()
            history = input("Medical history: ").strip()
            if not name or not gender or not contact:
                print("Name, gender and contact are required.")
                continue
            pid = add_patient(name, age, gender, contact, address, history)
            print("Patient registered. ID =", pid)

        elif choice == "2":
            print_patients(view_patients())

        elif choice == "3":
            keyword = input("Enter name or ID: ").strip()
            print_patients(search_patient(keyword))

        elif choice == "4":
            pid = ask_int("Patient ID to edit: ")
            existing = search_patient(str(pid))
            existing = [r for r in existing if r[0] == pid]
            if not existing:
                print("Patient not found.")
                continue
            old = existing[0]
            print("Press Enter to keep the old value.")
            name = input("Name [{}]: ".format(old[1])).strip() or old[1]
            age_in = input("Age [{}]: ".format(old[2])).strip()
            age = int(age_in) if age_in.isdigit() else old[2]
            gender = input("Gender [{}]: ".format(old[3])).strip() or old[3]
            contact = input("Contact [{}]: ".format(old[4])).strip() or old[4]
            address = input("Address [{}]: ".format(old[5] or "")).strip() or old[5]
            history = input("Medical history [{}]: ".format(old[6] or "")).strip() or old[6]
            edit_patient(pid, name, age, gender, contact, address, history)
            print("Patient updated.")

        elif choice == "5":
            pid = ask_int("Patient ID to delete: ")
            confirm = input("Delete patient {}? (y/n): ".format(pid)).strip().lower()
            if confirm == "y":
                print("Patient deleted." if delete_patient(pid) else "Patient not found.")
            else:
                print("Cancelled.")

        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()