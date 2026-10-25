# Hospital Management System

**Course:** Software Engineering Lab (PBL - Project-Based Learning)
**Team:** Atif Azmi, Mo Atif Azmi
**Project management:** Jira (space "Hospital Management System", key SCRUM, sprint 19 Oct - 26 Oct 2026)

---

## 1. Project Title
Hospital Management System (Python console application with SQLite database)

## 2. Problem Statement and Objectives

**Problem statement:** Small clinics and hospitals often keep patient records, doctor schedules and bills on paper or in separate files. This causes duplicate data, double-booked appointments, billing mistakes and no control over who can see what.

**Objectives**
- Keep patient, doctor, appointment and billing data in one database.
- Prevent two appointments for the same doctor at the same date and time.
- Calculate bills automatically and track payment status.
- Give each staff role access only to the modules it needs (role-based access).
- Store passwords safely (salted hash, never plain text).
- Test every module with black-box and white-box test cases.

## 3. Proposed Solution and Key Features

| Module | Jira task | Key features |
|---|---|---|
| Database design | SCRUM-5 | Tables: Patient, Doctor, Appointment, Bill (+ Users); foreign keys between them |
| Patient | SCRUM-6 | Register, view all, search by name or ID, edit, delete (with confirmation) |
| Doctor and Appointment | SCRUM-7 | Add/view/edit doctor, book, view, cancel, reschedule; double-booking blocked |
| Billing | SCRUM-8 | Generate bill (consultation + medicine + other), view, Paid/Pending status, totals |
| Login and roles | SCRUM-9 | Register/login, PBKDF2 password hashing, roles Admin / Doctor / Receptionist |
| Testing | SCRUM-10 | 48 black-box cases (Excel), 44 white-box tests (unittest) |
| Documentation | SCRUM-11 | This README, Jira screenshots, test reports |

**Role permissions**

| Role | Can open |
|---|---|
| Admin | Patients, Appointments, Billing, User management |
| Doctor | Appointments |
| Receptionist | Patients, Billing |

## 4. Technologies Used
- Python 3 (standard library only: sqlite3, hashlib, hmac, unittest)
- SQLite database (file `hospital.db`, created automatically)
- Git and GitHub (version control)
- Jira (Scrum board, epic, tasks, sprint)
- Excel (black-box test cases), coverage.py (white-box coverage report)

## 5. How the Project Works

1. Run `python hospital_app.py`.
2. First run only: the program asks you to create the first Admin account.
3. Log in with username and password (3 attempts allowed).
4. The main menu shows only the modules allowed for your role.
5. Each module reads and writes the shared SQLite database:
   - A **patient** is registered and gets an ID.
   - An **appointment** links a patient ID and a doctor ID with a date and time. The program checks that the patient and doctor exist and that the slot is free.
   - A **bill** is created for a patient ID. Total = consultation + medicine + other charges. Status starts as Pending and can be changed to Paid.
6. Logout returns to the end of the program.

### Database (summary)
```
Patient(patient_id, name, age, gender, contact, address, medical_history)
Doctor(doctor_id, name, specialization, contact, availability)
Appointment(appointment_id, patient_id -> Patient, doctor_id -> Doctor, appt_date, appt_time, status)
Bill(bill_id, patient_id -> Patient, amount, payment_status, bill_date)
Users(user_id, username, password_hash, salt, role)
```
The full SQL is in `database_design.sql`.

## 6. Files

| File | Purpose |
|---|---|
| `hospital_app.py` | Main program: login and role-based menu |
| `login_module.py` | Users, password hashing, roles |
| `patient_module.py` | Patient module |
| `doctor_appointment_module.py` | Doctor and appointment module |
| `billing_module.py` | Billing module |
| `test_whitebox.py` | White-box unit tests (44 tests) |
| `Black_Box_Test_Cases.xlsx` | Black-box test cases (48 cases) |
| `database_design.sql` | Database design |

## 7. How to Run

```
python hospital_app.py
```
Each module can also be run on its own, for example `python patient_module.py`.

## 8. Testing

**White-box tests** (source-code level, branch and path coverage):
```
python test_whitebox.py -v

pip install coverage
coverage run test_whitebox.py
coverage report -m
coverage html
```
Tests use a temporary database, so `hospital.db` is not changed.

**Black-box tests:** see `Black_Box_Test_Cases.xlsx` (Test Case ID, scenario, input, expected output, actual output, status).

## 9. Team Work in Jira
- Every module is a Jira task with an assignee, due date and priority, grouped under one epic.
- The person who builds a module does not test it. The other team member tests it and writes the result as a comment, then the task is moved to Done.
- Commit messages start with the Jira key, for example `SCRUM-6 Add patient module`.
