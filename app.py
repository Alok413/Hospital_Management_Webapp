from flask import Flask, render_template, request, redirect, url_for
from database import create_tables
import sqlite3

app = Flask(__name__)

# ------------------ ADMIN LOGIN ---------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('hms.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )
        admin = cursor.fetchone()
        conn.close()

        if admin:
            return redirect(url_for('admin_dashboard'))
        else:
            message = "Invalid Credentials ❌"

    return render_template('admin/admin_login.html', message=message)

# ------------------ ADMIN DASHBOARD ------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM doctor")
    doctor_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patient")
    patient_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointment")
    appointment_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin/admin_dashboard.html',
        doctor_count=doctor_count,
        patient_count=patient_count,
        appointment_count=appointment_count
    )
#---------------------ADD DOCTOR ------------------------
@app.route('/admin/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    message = ""

    if request.method == 'POST':
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        availability = request.form.get('availability')

        # -------- Validation part (Step A) yahi par aata hai --------
        if not name or not specialization or not availability:
            message = "All fields are required ❌"
        else:
            conn = sqlite3.connect('hms.db')
            cursor = conn.cursor()
         
            password = request.form.get('password')

            cursor.execute(
            "INSERT INTO doctor (name, specialization, availability, status, password) VALUES (?, ?, ?, ?, ?)",
                    (name, specialization, availability, "Active", password)
                )


            conn.commit()
            conn.close()

            message = "Doctor Added Successfully ✅"

    return render_template('admin/add_doctor.html', message=message)
# ------------------------ VIEW DOCTORS -----------------------------
@app.route('/admin/view_doctors')
def view_doctors():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctor")
    doctors = cursor.fetchall()

    conn.close()

    return render_template('admin/view_doctors.html', doctors=doctors)
# -------- DELETE DOCTOR --------
@app.route('/admin/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM doctor WHERE id=?", (doctor_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_doctors'))
# -------- EDIT DOCTOR --------
@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        availability = request.form.get('availability')
        status = request.form.get('status')
        password = request.form.get('password')

        cursor.execute("""
            UPDATE doctor
            SET name=?,
                specialization=?,
                availability=?,
                status=?,
                password=?
            WHERE id=?
        """, (name, specialization, availability, status, password, id))

        conn.commit()
        conn.close()

        return redirect(url_for('view_doctors'))

    cursor.execute("SELECT * FROM doctor WHERE id=?", (id,))
    doctor = cursor.fetchone()
    conn.close()

    return render_template('admin/edit_doctor.html', doctor=doctor)

# -------- PATIENT VIEW DOCTORS --------
@app.route('/patient/view_doctors')
def patient_view_doctors():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctor WHERE status='Active'")
    doctors = cursor.fetchall()

    conn.close()

    return render_template('patient/patient_view_doctors.html', doctors=doctors)
# -------- BOOK APPOINTMENT --------
@app.route('/patient/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    message = ""

    if request.method == 'POST':
        date = request.form.get('date')

        hour = request.form.get('hour')
        minute = request.form.get('minute')
        ampm = request.form.get('ampm')

        time = f"{hour}:{minute} {ampm}"
        hour_int = int(hour)

        patient_id = 1  # temporary

        conn = sqlite3.connect('hms.db')
        cursor = conn.cursor()

        # -------- CHECK DOCTOR AVAILABILITY --------
        cursor.execute("SELECT availability FROM doctor WHERE id=?", (doctor_id,))
        availability = cursor.fetchone()[0]

        if availability.lower() == "morning":
            if not (9 <= hour_int <= 12):
                message = "Doctor available only in Morning (9AM-12PM) ❌"
                conn.close()
                return render_template('book_appointment.html', message=message)

        elif availability.lower() == "evening":
            if not (2 <= hour_int <= 7):
                message = "Doctor available only in Evening (2PM-7PM) ❌"
                conn.close()
                return render_template('patient/book_appointment.html', message=message)

        # -------- CHECK DOUBLE BOOKING --------
        cursor.execute("""
            SELECT * FROM appointment
            WHERE doctor_id=? AND date=? AND time=? AND status='Booked'
        """, (doctor_id, date, time))

        existing = cursor.fetchone()

        if existing:
            message = "This slot is already booked ❌ Please choose another time."
        else:
            cursor.execute("""
                INSERT INTO appointment (patient_id, doctor_id, date, time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, doctor_id, date, time, "Booked"))

            conn.commit()
            message = "Appointment Booked Successfully ✅"

        conn.close()

    return render_template('patient/book_appointment.html', message=message)
# -------- DOCTOR LOGIN --------
@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    message = ""

    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        conn = sqlite3.connect('hms.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM doctor WHERE name=? AND password=?",
            (name, password)
        )
        doctor = cursor.fetchone()
        conn.close()

        if doctor:
            return redirect(url_for('doctor_dashboard'))
        else:
            message = "Invalid Credentials ❌"

    return render_template('doctor/doctor_login.html', message=message)
#--------------------Doctor Dashboard-------------------------------
@app.route('/doctor/dashboard')
def doctor_dashboard():
    return render_template('doctor/doctor_dashboard.html')
# -------- DOCTOR APPOINTMENTS --------
@app.route("/doctor/appointments", methods=["GET"])
def doctor_appointments():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient.name,
               appointment.date,
               appointment.time,
               appointment.status,
               appointment.id
        FROM appointment
        JOIN patient ON appointment.patient_id = patient.id
    """)

    appointments = cursor.fetchall()
    conn.close()

    return render_template("doctor/doctor_appointments.html", appointments=appointments)


# -------- DOCTOR DIAGNOSE --------
@app.route("/doctor/diagnose/<int:appointment_id>", methods=["GET", "POST"])
def doctor_diagnose(appointment_id):
    if request.method == "POST":
        visit_type = request.form.get("visit_type")
        test_done = request.form.get("test_done")
        diagnosis = request.form.get("diagnosis")
        prescription = request.form.get("prescription")

        conn = sqlite3.connect('hms.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE appointment
            SET visit_type=?,
                test_done=?,
                diagnosis=?,
                prescription=?,
                status='Completed'
            WHERE id=?
        """, (visit_type, test_done, diagnosis, prescription, appointment_id))

        conn.commit()
        conn.close()

        return redirect(url_for("doctor_appointments"))

    return render_template("doctor/doctor_diagnose.html")


# -------- PATIENT HISTORY --------
@app.route("/patient/history", methods=["GET"])
def patient_history():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    patient_id = 1

    cursor.execute("""
        SELECT appointment.date,
               appointment.time,
               doctor.name,
               appointment.diagnosis,
               appointment.prescription
        FROM appointment
        JOIN doctor ON appointment.doctor_id = doctor.id
        WHERE appointment.patient_id=? AND appointment.status='Completed'
    """, (patient_id,))

    history = cursor.fetchall()
    conn.close()

    return render_template("patient/patient_history.html", history=history)

# ------------------ HOME ROUTE (optional) ------------------

@app.route('/')
def home():
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

