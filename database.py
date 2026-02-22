import sqlite3

def create_tables():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    # Admin Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # Doctor Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctor(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    availability TEXT,
    status TEXT,
    password TEXT
    )
    """)

    # Patient Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        phone TEXT
    )
    """)

    # Appointment Table
    cursor.execute("""
    SELECT patient.name,
           appointment.date,
           appointment.time,
           appointment.status,
           appointment.id
    FROM appointment
    JOIN patient ON appointment.patient_id = patient.id
""")


    # Treatment Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treatment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        diagnosis TEXT,
        prescription TEXT,
        notes TEXT
    )
    """)

    # Insert default admin (very important as per doc)
    cursor.execute("SELECT * FROM admin")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", 
                       ("admin", "admin123"))

    conn.commit()
    conn.close()
