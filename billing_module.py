"""
Hospital Management System - Billing Module (SCRUM-8)
Features: generate bill, view bills, update payment status (Paid/Pending),
view bills of one patient.
Uses the same hospital.db as the other modules (register patients first).
Run:  python billing_module.py
"""

import sqlite3
from datetime import date

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
        """CREATE TABLE IF NOT EXISTS Bill (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'Pending',
            bill_date TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES Patient(patient_id))"""
    )
    conn.commit()
    conn.close()


def generate_bill(patient_id, consultation, medicine, other=0.0):
    """Total = consultation + medicine + other. Returns (bill_id, total, message)."""
    for value in (consultation, medicine, other):
        if value < 0:
            return None, 0, "Charges cannot be negative."
    conn = get_connection()
    patient = conn.execute("SELECT 1 FROM Patient WHERE patient_id=?", (patient_id,)).fetchone()
    if not patient:
        conn.close()
        return None, 0, "Patient ID not found. Register the patient first."
    total = consultation + medicine + other
    cur = conn.execute(
        "INSERT INTO Bill (patient_id, amount, payment_status, bill_date) VALUES (?,?,?,?)",
        (patient_id, total, "Pending", date.today().isoformat()),
    )
    conn.commit()
    bill_id = cur.lastrowid
    conn.close()
    return bill_id, total, "Bill generated."


def view_bills(patient_id=None):
    conn = get_connection()
    query = (
        "SELECT b.bill_id, p.name, b.amount, b.payment_status, b.bill_date "
        "FROM Bill b JOIN Patient p ON b.patient_id = p.patient_id "
    )
    if patient_id is None:
        rows = conn.execute(query + "ORDER BY b.bill_id").fetchall()
    else:
        rows = conn.execute(query + "WHERE b.patient_id=? ORDER BY b.bill_id", (patient_id,)).fetchall()
    conn.close()
    return rows


def update_payment_status(bill_id, status):
    """status must be 'Paid' or 'Pending'. Returns True if a bill was updated."""
    if status not in ("Paid", "Pending"):
        return False
    conn = get_connection()
    cur = conn.execute("UPDATE Bill SET payment_status=? WHERE bill_id=?", (status, bill_id))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def totals():
    """Returns (total_paid, total_pending)."""
    conn = get_connection()
    paid = conn.execute("SELECT COALESCE(SUM(amount),0) FROM Bill WHERE payment_status='Paid'").fetchone()[0]
    pending = conn.execute("SELECT COALESCE(SUM(amount),0) FROM Bill WHERE payment_status='Pending'").fetchone()[0]
    conn.close()
    return paid, pending


def print_bills(rows):
    if not rows:
        print("No bill found.")
        return
    print("\n{:<6} {:<20} {:<12} {:<10} {}".format("Bill", "Patient", "Amount", "Status", "Date"))
    print("-" * 65)
    for r in rows:
        print("{:<6} {:<20} {:<12.2f} {:<10} {}".format(*r))


def ask_int(prompt):
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a number.")


def ask_amount(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("Please enter an amount (number).")


def menu():
    init_db()
    while True:
        print("\n===== BILLING MODULE =====")
        print("1. Generate bill")
        print("2. View all bills")
        print("3. View bills of a patient")
        print("4. Update payment status")
        print("5. Show totals (paid / pending)")
        print("6. Exit")
        choice = input("Choose (1-6): ").strip()

        if choice == "1":
            pid = ask_int("Patient ID: ")
            consultation = ask_amount("Consultation fee: ")
            medicine = ask_amount("Medicine charges: ")
            other = ask_amount("Other charges (0 if none): ")
            bill_id, total, msg = generate_bill(pid, consultation, medicine, other)
            print(msg + (" Bill ID = {}, Total = {:.2f}".format(bill_id, total) if bill_id else ""))

        elif choice == "2":
            print_bills(view_bills())

        elif choice == "3":
            pid = ask_int("Patient ID: ")
            print_bills(view_bills(pid))

        elif choice == "4":
            bid = ask_int("Bill ID: ")
            status = input("New status (Paid/Pending): ").strip().capitalize()
            if update_payment_status(bid, status):
                print("Payment status updated to", status)
            else:
                print("Bill not found or status invalid.")

        elif choice == "5":
            paid, pending = totals()
            print("Total paid: {:.2f}\nTotal pending: {:.2f}".format(paid, pending))

        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()