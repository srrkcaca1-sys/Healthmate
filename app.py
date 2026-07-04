from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import sqlite3

app = Flask(__name__)

app.secret_key = "healthmate123"

# Home
@app.route('/')
def home():
    return render_template('index.html')
# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        print(request.form)

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        print(name)
        print(email)
        print(password)

        conn = sqlite3.connect("healthmate.db")

        conn.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template("register.html")


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect("healthmate.db")

        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session['user_id'] = user[0]
            session['user_name'] = user[1]

            return redirect(url_for('dashboard'))

        return "Invalid Email or Password"

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
def dashboard():

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    # Total Health Records
    total_records = conn.execute(
        "SELECT COUNT(*) FROM health_records WHERE user_id=?",
        (user_id,)
    ).fetchone()[0]

    # Latest Health Record
    health = conn.execute("""
        SELECT heart_rate, blood_pressure, blood_sugar, weight, height
        FROM health_records
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    # Latest Prediction
    prediction = conn.execute("""
        SELECT result
        FROM predictions
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    # Heart Rate History
    heart_history = conn.execute("""
        SELECT heart_rate
        FROM health_records
        WHERE user_id=?
        ORDER BY id
    """, (user_id,)).fetchall()

    # Blood Sugar History
    sugar_history = conn.execute("""
        SELECT blood_sugar
        FROM health_records
        WHERE user_id=?
        ORDER BY id
    """, (user_id,)).fetchall()

    # BMI History
    bmi_history = conn.execute("""
        SELECT weight, height
        FROM health_records
        WHERE user_id=?
        ORDER BY id
    """, (user_id,)).fetchall()

    # Pending Medicines
    pending_medicines = conn.execute("""
        SELECT COUNT(*)
        FROM medicines
        WHERE user_id=? AND status='Pending'
    """, (user_id,)).fetchone()[0]

    # Booked Appointments
    upcoming_appointments = conn.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE user_id=? AND status='Booked'
    """, (user_id,)).fetchone()[0]

    conn.close()

    # Default Values
    heart_rate = "--"
    blood_pressure = "--"
    blood_sugar = "--"
    bmi = "--"

    if health:
        heart_rate = health[0]
        blood_pressure = health[1]
        blood_sugar = health[2]

        weight = health[3]
        height = health[4] / 100

        bmi = round(weight / (height * height), 2)

    prediction_result = prediction[0] if prediction else "No Prediction"

    # Graph Data
    heart_data = [row[0] for row in heart_history]
    sugar_data = [row[0] for row in sugar_history]

    bmi_data = []

    for row in bmi_history:
        weight = row[0]
        height = row[1] / 100
        bmi_data.append(round(weight / (height * height), 2))

    # Notifications
    notifications = []

    if pending_medicines > 0:
        notifications.append(
            f"💊 You have {pending_medicines} pending medicine reminder(s)."
        )

    if upcoming_appointments > 0:
        notifications.append(
            f"📅 You have {upcoming_appointments} upcoming appointment(s)."
        )

    if bmi != "--" and bmi > 25:
        notifications.append(
            "⚠️ Your BMI is above the healthy range."
        )

    if blood_sugar != "--" and float(blood_sugar) > 140:
        notifications.append(
            "🍬 Your blood sugar level is high."
        )

    if len(notifications) == 0:
        notifications.append(
            "✅ No new notifications."
        )

    return render_template(
        "dashboard.html",
        total_records=total_records,
        heart_rate=heart_rate,
        blood_pressure=blood_pressure,
        blood_sugar=blood_sugar,
        bmi=bmi,
        prediction=prediction_result,
        username=session['user_name'],
        heart_data=heart_data,
        sugar_data=sugar_data,
        bmi_data=bmi_data,
        notifications=notifications
    )


# Add Health Record
@app.route('/add_health', methods=['GET', 'POST'])
def add_health():

    if request.method == 'POST':

        user_id = session['user_id']

        heart_rate = request.form['heart_rate']
        blood_pressure = request.form['blood_pressure']
        blood_sugar = request.form['blood_sugar']
        weight = request.form['weight']
        height = request.form['height']

        conn = sqlite3.connect("healthmate.db")

        conn.execute("""
        INSERT INTO health_records
        (user_id,heart_rate,blood_pressure,blood_sugar,weight,height)
        VALUES(?,?,?,?,?,?)
        """,
        (
            user_id,
            heart_rate,
            blood_pressure,
            blood_sugar,
            weight,
            height
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_health.html')


# Health History
@app.route('/history')
def history():

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    records = conn.execute(
        "SELECT * FROM health_records WHERE user_id=?",
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template(
        'history.html',
        records=records
    )
@app.route('/delete_record/<int:id>')
def delete_record(id):

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    conn.execute(
        "DELETE FROM health_records WHERE id=? AND user_id=?",
        (id, user_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('history'))


# BMI Calculator
@app.route('/bmi')
def bmi():

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    record = conn.execute("""
        SELECT weight,height
        FROM health_records
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    conn.close()

    if record:

        weight = record[0]
        height = record[1] / 100

        bmi = round(weight / (height * height), 2)

    else:

        bmi = 0

    return render_template("bmi.html", bmi=bmi)


# Upload Skin Image
@app.route('/upload_skin', methods=['GET', 'POST'])
def upload_skin():

    if request.method == 'POST':

        print("FILES:", request.files)

        image = request.files.get('image')

        if image is None:
            return "No image selected"

        if image.filename == "":
            return "No image selected"

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, image.filename)

        image.save(filepath)

        print("Saved:", filepath)

        conn = sqlite3.connect("healthmate.db")

        user_id = session['user_id']
        conn.execute(
    "INSERT INTO skin_images(user_id, image_name) VALUES(?, ?)",
    (user_id, image.filename)
)

        conn.commit()
        conn.close()

        return redirect(url_for('symptoms'))

    return render_template('upload_skin.html')


# Symptoms Checker
@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():

    if request.method == 'POST':

        fever = request.form['fever']
        itching = request.form['itching']
        redness = request.form['redness']
        swelling = request.form['swelling']
        pain = request.form['pain']

        conn = sqlite3.connect("healthmate.db")
        user_id = session['user_id']

        conn.execute("""
        INSERT INTO symptoms
        (user_id, fever, itching, redness, swelling, pain)
VALUES(?,?,?,?,?,?)
""",
(
    user_id,
    fever,
    itching,
    redness,
    swelling,
    pain
))

        conn.commit()
        conn.close()

        # Disease Prediction Logic
        if swelling == "yes" or pain == "yes":
            result = "ALERT"

        elif itching == "yes" or redness == "yes":
            result = "CAUTION"

        else:
            result = "NORMAL"

        conn = sqlite3.connect("healthmate.db")
        user_id = session['user_id']

        conn.execute(
            "INSERT INTO predictions(user_id, result) VALUES(?, ?)", 
             (user_id, result)
        )

        conn.commit()
        conn.close()

        return render_template(
            'result.html',
            result=result
        )

    return render_template('symptoms.html')
@app.route('/users')
def users():

    conn = sqlite3.connect("healthmate.db")

    data = conn.execute(
        "SELECT * FROM users"
    ).fetchall()

    conn.close()

    return str(data)
# ==========================
# User Profile
# ==========================

@app.route('/profile')
def profile():

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    profile = conn.execute(
        "SELECT * FROM profile WHERE user_id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        profile=profile
    )
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    if request.method == 'POST':

        phone = request.form['phone']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        blood_group = request.form['blood_group']

        profile = conn.execute(
            "SELECT * FROM profile WHERE user_id=?",
            (user_id,)
        ).fetchone()

        if profile:

            conn.execute("""
            UPDATE profile
            SET phone=?,
                age=?,
                gender=?,
                address=?,
                blood_group=?
            WHERE user_id=?
            """,
            (
                phone,
                age,
                gender,
                address,
                blood_group,
                user_id
            ))

        else:

            conn.execute("""
            INSERT INTO profile
            (user_id,phone,age,gender,address,blood_group)
            VALUES(?,?,?,?,?,?)
            """,
            (
                user_id,
                phone,
                age,
                gender,
                address,
                blood_group
            ))

        conn.commit()
        conn.close()

        return redirect(url_for("profile"))

    profile = conn.execute(
        "SELECT * FROM profile WHERE user_id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_profile.html",
        profile=profile
    )
@app.route('/tables')
def tables():

    conn = sqlite3.connect("healthmate.db")

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    conn.close()

    return str(tables)


import os

@app.route('/dbpath')
def dbpath():
    return os.path.abspath("healthmate.db")
@app.route('/edit_record/<int:id>', methods=['GET', 'POST'])
def edit_record(id):

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    if request.method == "POST":

        heart_rate = request.form['heart_rate']
        blood_pressure = request.form['blood_pressure']
        blood_sugar = request.form['blood_sugar']
        weight = request.form['weight']
        height = request.form['height']

        conn.execute("""
        UPDATE health_records
        SET heart_rate=?,
            blood_pressure=?,
            blood_sugar=?,
            weight=?,
            height=?
        WHERE id=? AND user_id=?
        """,
        (
            heart_rate,
            blood_pressure,
            blood_sugar,
            weight,
            height,
            id,
            user_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('history'))

    record = conn.execute(
        "SELECT * FROM health_records WHERE id=? AND user_id=?",
        (id, user_id)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_health.html",
        record=record
    )
@app.route('/health_tips')
def health_tips():

    user_id = session['user_id']

    conn = sqlite3.connect("healthmate.db")

    health = conn.execute("""
        SELECT heart_rate, blood_pressure, blood_sugar, weight, height
        FROM health_records
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    conn.close()

    if not health:
        return "No Health Records Found"

    heart_rate = health[0]
    blood_pressure = health[1]
    blood_sugar = health[2]
    weight = health[3]
    height = health[4] / 100

    bmi = round(weight / (height * height), 2)

    tips = []

    # Heart Rate
    if heart_rate < 60:
        tips.append("❤️ Your heart rate is low. Consult a doctor if you feel dizzy.")
    elif heart_rate > 100:
        tips.append("❤️ Your heart rate is high. Avoid stress and drink enough water.")
    else:
        tips.append("❤️ Your heart rate is normal. Keep exercising regularly.")

    # Blood Sugar
    if blood_sugar > 140:
        tips.append("🍬 Blood sugar is high. Reduce sugary foods and exercise daily.")
    else:
        tips.append("🍬 Blood sugar is normal. Maintain a balanced diet.")

    # BMI
    if bmi < 18.5:
        tips.append("⚖️ You are underweight. Eat nutritious meals.")
    elif bmi > 25:
        tips.append("⚖️ Your BMI is high. Walk 30 minutes every day.")
    else:
        tips.append("⚖️ Your BMI is healthy. Keep up the good work.")

    return render_template(
        "health_tips.html",
        tips=tips,
        bmi=bmi,
        heart_rate=heart_rate,
        blood_sugar=blood_sugar
    )
@app.route('/medicine', methods=['GET', 'POST'])
def medicine():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("healthmate.db")

    if request.method == 'POST':

        medicine_name = request.form['medicine_name']
        dosage = request.form['dosage']
        reminder_time = request.form['reminder_time']

        conn.execute("""
            INSERT INTO medicines
            (user_id, medicine_name, dosage, reminder_time, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session['user_id'],
            medicine_name,
            dosage,
            reminder_time,
            "Pending"
        ))

        conn.commit()

    medicines = conn.execute("""
        SELECT *
        FROM medicines
        WHERE user_id=?
        ORDER BY reminder_time
    """, (session['user_id'],)).fetchall()

    conn.close()

    return render_template(
        "medicine.html",
        medicines=medicines
    )
@app.route('/taken/<int:id>')
def taken(id):

    conn = sqlite3.connect("healthmate.db")

    conn.execute("""

        UPDATE medicines

        SET status='Taken'

        WHERE id=?

    """, (id,))

    conn.commit()

    conn.close()

    return redirect('/medicine')
@app.route('/delete_medicine/<int:id>')
def delete_medicine(id):

    conn = sqlite3.connect("healthmate.db")

    conn.execute("""

        DELETE FROM medicines

        WHERE id=?

    """, (id,))

    conn.commit()

    conn.close()

    return redirect('/medicine')
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("healthmate.db")

    if request.method == 'POST':

        doctor_name = request.form['doctor_name']
        hospital_name = request.form['hospital_name']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        reason = request.form['reason']

        conn.execute("""
        INSERT INTO appointments
        (
            user_id,
            doctor_name,
            hospital_name,
            appointment_date,
            appointment_time,
            reason,
            status
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            session['user_id'],
            doctor_name,
            hospital_name,
            appointment_date,
            appointment_time,
            reason,
            "Booked"
        ))

        conn.commit()

    appointments = conn.execute("""
    SELECT *
    FROM appointments
    WHERE user_id=?
    ORDER BY appointment_date
    """,
    (session['user_id'],)).fetchall()

    conn.close()

    return render_template(
        "appointment.html",
        appointments=appointments
    )
@app.route('/cancel_appointment/<int:id>')
def cancel_appointment(id):

    conn = sqlite3.connect("healthmate.db")

    conn.execute("""

    UPDATE appointments

    SET status='Cancelled'

    WHERE id=?

    """,(id,))

    conn.commit()

    conn.close()

    return redirect('/appointment')
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))
@app.route('/delete_health/<int:id>')
def delete_health(id):

    conn = sqlite3.connect("healthmate.db")

    conn.execute(
        "DELETE FROM health_records WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('history'))


if __name__ == '__main__':
    app.run(debug=True)