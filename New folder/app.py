from flask import Flask, render_template, request, redirect
import sqlite3
import bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from email_alert import send_email_alert
from sms_alert import send_sms_alert
from whatsapp_alert import send_whatsapp_alert

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Database connection
def get_db():
    return sqlite3.connect("database.db")

# Create tables
def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        phone TEXT,
        password BLOB
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        username TEXT,
        timestamp TEXT,
        status TEXT
    )
    """)

    db.commit()
    db.close()

init_db()

# Track failed attempts
failed_attempts = {}
BLOCK_TIME = 2  # minutes
MAX_ATTEMPTS = 3

def is_blocked(username):
    if username in failed_attempts:
        attempts, last_time = failed_attempts[username]
        if attempts >= MAX_ATTEMPTS:
            if datetime.now() - last_time < timedelta(minutes=BLOCK_TIME):
                return True
            else:
                failed_attempts[username] = (0, datetime.now())
    return False

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            msg = "Please enter both username and password"
            return render_template("login.html", msg=msg)

        if is_blocked(username):
            msg = "Account temporarily blocked due to multiple failed attempts!"
            return render_template("login.html", msg=msg)

        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute("SELECT password, email, phone FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode(), user[0]):
                failed_attempts[username] = (0, datetime.now())
                cursor.execute("INSERT INTO logs VALUES (?,?,?)",
                               (username, str(datetime.now()), "Login Success"))
                db.commit()
                return redirect('/dashboard')
            else:
                count, _ = failed_attempts.get(username, (0, datetime.now()))
                new_count = count + 1
                failed_attempts[username] = (new_count, datetime.now())
                cursor.execute("INSERT INTO logs VALUES (?,?,?)",
                               (username, str(datetime.now()), "Failed Login"))
                db.commit()
                if new_count == MAX_ATTEMPTS:
                    ip = request.remote_addr
                    user_email = user[1] if user else None
                    user_phone = user[2] if user else None
                    if user_email and user_phone:
                        send_email_alert(username, ip, user_email)
                        send_sms_alert(username, ip, user_phone)
                        send_whatsapp_alert(username, ip, user_phone)
                    else:
                        print(f"Alert skipped: User '{username}' does not exist or lacks contact info.")
                msg = "Invalid credentials!"
        finally:
            db.close()
    return render_template("login.html", msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password_input = request.form.get('password')

        if username and email and phone and password_input:
            password = bcrypt.hashpw(password_input.encode(), bcrypt.gensalt())
            db = get_db()
            try:
                cursor = db.cursor()
                cursor.execute("INSERT INTO users(username, email, phone, password) VALUES (?,?,?,?)",
                               (username, email, phone, password))
                db.commit()
                msg = "Registration successful!"
            except sqlite3.IntegrityError:
                msg = "Username already exists!"
            except Exception as e:
                msg = f"An error occurred: {e}"
            finally:
                db.close()
        else:
            msg = "Please fill in all fields!"
    return render_template("register.html", msg=msg)

@app.route('/dashboard')
def dashboard():
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM logs")
        logs = cursor.fetchall()
    finally:
        db.close()
    return render_template("dashboard.html", logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
