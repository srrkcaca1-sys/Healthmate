import sqlite3
import os

print(os.path.abspath("healthmate.db"))

conn = sqlite3.connect("healthmate.db")

# Users Table
conn.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# Health Records Table
conn.execute("""
CREATE TABLE IF NOT EXISTS health_records(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    heart_rate INTEGER,
    blood_pressure TEXT,
    blood_sugar INTEGER,
    weight REAL,
    height REAL
)
""")

# Skin Images Table
conn.execute("""
CREATE TABLE IF NOT EXISTS skin_images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    image_name TEXT
)
""")

# Symptoms Table
conn.execute("""
CREATE TABLE IF NOT EXISTS symptoms(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    fever TEXT,
    itching TEXT,
    redness TEXT,
    swelling TEXT,
    pain TEXT
)
""")

# Predictions Table
conn.execute("""
CREATE TABLE IF NOT EXISTS predictions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    result TEXT
)
""")

# Profile Table
conn.execute("""
CREATE TABLE IF NOT EXISTS profile(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    phone TEXT,
    age INTEGER,
    gender TEXT,
    address TEXT,
    blood_group TEXT
)
""")
# Medicine Reminder Table
conn.execute("""
CREATE TABLE IF NOT EXISTS medicines(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    medicine_name TEXT,
    dosage TEXT,
    reminder_time TEXT,
    status TEXT
)
""")
# Appointment Table
conn.execute("""
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    doctor_name TEXT,
    hospital_name TEXT,
    appointment_date TEXT,
    appointment_time TEXT,
    reason TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")