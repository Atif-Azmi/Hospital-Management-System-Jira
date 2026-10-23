"""
Hospital Management System - Login & Roles Module (SCRUM-9)
Roles: Admin, Doctor, Receptionist.
Passwords are stored as salted PBKDF2 hashes (never as plain text).
Uses the same hospital.db as the other modules.
Run:  python login_module.py      (stand-alone check)
      python hospital_app.py      (full app with role-based menu)
"""

import hashlib
import hmac
import os
import sqlite3

DB_NAME = "hospital.db"
ROLES = ("Admin", "Doctor", "Receptionist")

# Which modules each role may open (used by hospital_app.py)
PERMISSIONS = {
    "Admin": ["patients", "appointments", "billing", "users"],
    "Doctor": ["appointments"],
    "Receptionist": ["patients", "billing"],
}


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS Users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            role          TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


def hash_password(password, salt_hex=None):
    """Returns (salt_hex, hash_hex)."""
    salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex(), digest.hex()


def user_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
    conn.close()
    return count


def register_user(username, password, role):
    """Returns (ok, message)."""
    username = username.strip()
    if not username:
        return False, "Username is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if role not in ROLES:
        return False, "Role must be one of: " + ", ".join(ROLES)
    salt, pw_hash = hash_password(password)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Users (username, password_hash, salt, role) VALUES (?,?,?,?)",
            (username, pw_hash, salt, role),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()
    return True, "User created."


def login(username, password):
    """Returns (ok, role_or_message)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT password_hash, salt, role FROM Users WHERE username=?", (username.strip(),)
    ).fetchone()
    conn.close()
    if not row:
        return False, "Invalid username or password."
    _, attempt = hash_password(password, row[1])
    if hmac.compare_digest(attempt, row[0]):
        return True, row[2]
    return False, "Invalid username or password."


def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT user_id, username, role FROM Users ORDER BY user_id").fetchall()
    conn.close()
    return rows


def delete_user(user_id):
    """Refuses to delete the last Admin. Returns (ok, message)."""
    conn = get_connection()
    row = conn.execute("SELECT role FROM Users WHERE user_id=?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return False, "User not found."
    if row[0] == "Admin":
        admins = conn.execute("SELECT COUNT(*) FROM Users WHERE role='Admin'").fetchone()[0]
        if admins <= 1:
            conn.close()
            return False, "Cannot delete the last Admin."
    conn.execute("DELETE FROM Users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return True, "User deleted."


def can_access(role, module_name):
    return module_name in PERMISSIONS.get(role, [])


def users_menu():
    """Admin only: manage users."""
    while True:
        print("\n===== USER MANAGEMENT (Admin) =====")
        print("1. Add user\n2. View users\n3. Delete user\n4. Back")
        choice = input("Choose (1-4): ").strip()
        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password (min 6 chars): ")
            role = input("Role ({}): ".format("/".join(ROLES))).strip().capitalize()
            print(register_user(username, password, role)[1])
        elif choice == "2":
            print("\n{:<5} {:<20} {}".format("ID", "Username", "Role"))
            for r in list_users():
                print("{:<5} {:<20} {}".format(*r))
        elif choice == "3":
            uid = input("User ID to delete: ").strip()
            if uid.isdigit():
                print(delete_user(int(uid))[1])
            else:
                print("Please enter a number.")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    init_db()
    print("Users in database:", user_count())