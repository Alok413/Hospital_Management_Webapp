# -------- DOCTOR APPOINTMENTS --------
@app.route('/doctor/appointments')
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

    return render_template('doctor/doctor_appointments.html', appointments=appointments)

# -------- DOCTOR DIAGNOSE --------
@app.route('/doctor/diagnose/<int:appointment_id>', methods=['GET', 'POST'])
def doctor_diagnose(appointment_id):

    if request.method == 'POST':
        visit_type = request.form.get('visit_type')
        test_done = request.form.get('test_done')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')

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

        return redirect(url_for('doctor_appointments'))

    return render_template('doctor/diagnose.html')

# -------- PATIENT HISTORY --------
@app.route('/patient/history')
def patient_history():
    conn = sqlite3.connect('hms.db')
    cursor = conn.cursor()

    patient_id = 1  # temporary

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

    return render_template('patient/patient_history.html', history=history)
@app.route('/debug/routes')
def debug_routes():
    return str(app.url_map)
