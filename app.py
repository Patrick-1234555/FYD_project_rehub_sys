import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rehabilitation_app')

# Database initialization
def create_table():
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)
    
    # Create patients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            condition_description TEXT,
            release_date TEXT,
            assigned_caregiver TEXT,
            doctor_id INTEGER,
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    """)
    
    # Create feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            caregiver_id INTEGER,
            behavior_rating INTEGER,
            recovery_progress INTEGER,
            mobility_status TEXT,
            medication_compliance TEXT,
            mood_status TEXT,
            additional_notes TEXT,
            submission_date TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (caregiver_id) REFERENCES users (id)
        )
    """)
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Sample users
        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                      ('dr_smith', 'doctor123', 'doctor', 'Dr. John Smith'))
        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                      ('caregiver1', 'care123', 'caregiver', 'Mary Johnson'))
        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                      ('caregiver2', 'care123', 'caregiver', 'Robert Wilson'))
        
        # Sample patients
        cursor.execute("""INSERT INTO patients (name, age, condition_description, release_date, assigned_caregiver, doctor_id) 
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      ('Alice Brown', 65, 'Hip replacement recovery', '2024-01-15', 'Mary Johnson', 1))
        cursor.execute("""INSERT INTO patients (name, age, condition_description, release_date, assigned_caregiver, doctor_id) 
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      ('James Davis', 58, 'Stroke rehabilitation', '2024-01-20', 'Robert Wilson', 1))
    
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif session['role'] == 'caregiver':
            return redirect(url_for('caregiver_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form.get('role')
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    if role:
        # If role is specified, only check users with that role
        cursor.execute("SELECT id, password, role, name FROM users WHERE username = ? AND role = ?", (username, role))
    else:
        # Otherwise check all users
        cursor.execute("SELECT id, password, role, name FROM users WHERE username = ?", (username,))
        
    user = cursor.fetchone()
    conn.close()
    
    if user and user[1] == password:
        session['user_id'] = user[0]
        session['username'] = username
        session['role'] = user[2]
        session['name'] = user[3]
        flash(f'Welcome, {user[3]}!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid credentials!', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('name', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    # Get all patients assigned to this doctor
    cursor.execute("""
        SELECT p.id, p.name, p.age, p.condition_description, p.release_date, p.assigned_caregiver,
               COUNT(f.id) as feedback_count,
               AVG(f.behavior_rating) as avg_behavior,
               AVG(f.recovery_progress) as avg_recovery
        FROM patients p
        LEFT JOIN feedback f ON p.id = f.patient_id
        WHERE p.doctor_id = ?
        GROUP BY p.id
    """, (session['user_id'],))
    
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('doctor_dashboard.html', patients=patients)

@app.route('/patient_details/<int:patient_id>')
def patient_details(patient_id):
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    # Get patient info
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    
    # Get all feedback for this patient
    cursor.execute("""
        SELECT f.*, u.name as caregiver_name
        FROM feedback f
        JOIN users u ON f.caregiver_id = u.id
        WHERE f.patient_id = ?
        ORDER BY f.submission_date DESC
    """, (patient_id,))
    
    feedback_list = cursor.fetchall()
    conn.close()
    
    return render_template('patient_details.html', patient=patient, feedback_list=feedback_list)

@app.route('/caregiver_dashboard')
def caregiver_dashboard():
    if 'user_id' not in session or session['role'] != 'caregiver':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    # Get patients assigned to this caregiver
    cursor.execute("SELECT * FROM patients WHERE assigned_caregiver = ?", (session['name'],))
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('caregiver_dashboard.html', patients=patients)

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, condition_description, release_date, assigned_caregiver FROM patients WHERE id = ?", (session['user_id'],))
    patient = cursor.fetchone()
    
    cursor.execute("SELECT feedback_text, date FROM feedback WHERE patient_id = ?", (session['user_id'],))
    feedback = cursor.fetchall()
    
    conn.close()
    
    return render_template('patient_dashboard.html', username=session['username'], patient=patient, feedback=feedback)

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    # Get all doctors
    cursor.execute("SELECT id, username, name FROM users WHERE role = 'doctor'")
    doctors = cursor.fetchall()
    
    # Get all caregivers
    cursor.execute("SELECT id, username, name FROM users WHERE role = 'caregiver'")
    caregivers = cursor.fetchall()
    
    # Get all patients
    cursor.execute("""
        SELECT p.id, p.name, p.age, p.condition_description, p.assigned_caregiver, u.name as doctor_name
        FROM patients p
        LEFT JOIN users u ON p.doctor_id = u.id
    """)
    patients = cursor.fetchall()
    
    conn.close()
    
    return render_template('manage_users.html', doctors=doctors, caregivers=caregivers, patients=patients)

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        condition = request.form['condition']
        release_date = request.form['release_date']
        assigned_caregiver = request.form['assigned_caregiver']
        
        conn = sqlite3.connect('rehabilitation.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO patients (name, age, condition_description, release_date, assigned_caregiver, doctor_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, age, condition, release_date, assigned_caregiver, session['user_id']))
        
        conn.commit()
        conn.close()
        
        flash('Patient registered successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    # Get list of caregivers for dropdown
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE role = 'caregiver'")
    caregivers = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('register_patient.html', caregivers=caregivers)

@app.route('/register_caregiver', methods=['GET', 'POST'])
def register_caregiver():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        conn = sqlite3.connect('rehabilitation.db')
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash('Username already exists!', 'error')
            return redirect(url_for('register_caregiver'))
        
        cursor.execute("""
            INSERT INTO users (username, password, role, name)
            VALUES (?, ?, ?, ?)
        """, (username, password, 'caregiver', name))
        
        conn.commit()
        conn.close()
        
        flash('Caregiver registered successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('register_caregiver.html')

@app.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        conn = sqlite3.connect('rehabilitation.db')
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash('Username already exists!', 'error')
            return redirect(url_for('register_doctor'))
        
        cursor.execute("""
            INSERT INTO users (username, password, role, name)
            VALUES (?, ?, ?, ?)
        """, (username, password, 'doctor', name))
        
        conn.commit()
        conn.close()
        
        flash('Doctor registered successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('register_doctor.html')

@app.route('/delete_user/<user_type>/<int:user_id>', methods=['POST'])
def delete_user(user_type, user_id):
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('index'))
    
    # Prevent self-deletion
    if user_type == 'doctor' and user_id == session['user_id']:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('manage_users'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    if user_type == 'patient':
        # Delete patient's feedback first
        cursor.execute("DELETE FROM feedback WHERE patient_id = ?", (user_id,))
        # Then delete the patient
        cursor.execute("DELETE FROM patients WHERE id = ?", (user_id,))
    else:
        # For doctor or caregiver
        cursor.execute("DELETE FROM users WHERE id = ? AND role = ?", (user_id, user_type))
    
    conn.commit()
    conn.close()
    
    flash(f'{user_type.capitalize()} deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/submit_feedback_form/<int:patient_id>')
def submit_feedback_form(patient_id):
    if 'user_id' not in session or session['role'] != 'caregiver':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    return render_template('feedback_form.html', patient=patient)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session or session['role'] != 'caregiver':
        return redirect(url_for('index'))
    
    patient_id = request.form['patient_id']
    behavior_rating = request.form['behavior_rating']
    recovery_progress = request.form['recovery_progress']
    mobility_status = request.form['mobility_status']
    medication_compliance = request.form['medication_compliance']
    mood_status = request.form['mood_status']
    additional_notes = request.form['additional_notes']
    
    from datetime import datetime
    
    conn = sqlite3.connect('rehabilitation.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO feedback (patient_id, caregiver_id, behavior_rating, recovery_progress, 
                            mobility_status, medication_compliance, mood_status, additional_notes, submission_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, session['user_id'], behavior_rating, recovery_progress, 
          mobility_status, medication_compliance, mood_status, additional_notes, 
          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()
    
    flash('Feedback submitted successfully!', 'success')
    return redirect(url_for('caregiver_dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)