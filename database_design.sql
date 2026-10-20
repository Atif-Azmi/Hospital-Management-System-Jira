-- Hospital Management System: Database Design (SCRUM-5)
-- Tables: Patient, Doctor, Appointment, Bill

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- 1. Patient table
CREATE TABLE Patient (
    patient_id      INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    age             INT NOT NULL,
    gender          VARCHAR(10) NOT NULL,
    contact         VARCHAR(15) NOT NULL,
    address         VARCHAR(255),
    medical_history TEXT
);

-- 2. Doctor table
CREATE TABLE Doctor (
    doctor_id       INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    specialization  VARCHAR(100) NOT NULL,
    contact         VARCHAR(15) NOT NULL,
    availability    VARCHAR(100)
);

-- 3. Appointment table (links Patient and Doctor)
CREATE TABLE Appointment (
    appointment_id  INT PRIMARY KEY AUTO_INCREMENT,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    appt_date       DATE NOT NULL,
    appt_time       TIME NOT NULL,
    status          VARCHAR(20) DEFAULT 'Booked',
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES Doctor(doctor_id)
);

-- 4. Bill table (links to Patient)
CREATE TABLE Bill (
    bill_id         INT PRIMARY KEY AUTO_INCREMENT,
    patient_id      INT NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    payment_status  VARCHAR(20) DEFAULT 'Pending',
    bill_date       DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
);
