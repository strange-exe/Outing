# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection  # Import the function
from datetime import datetime, timedelta
import mysql.connector
import json

app = Flask(__name__)

# Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)

# Set the secret key from the config file for better security
app.secret_key = config.get("SECRET_KEY", "a-default-fallback-secret-key")
app.permanent_session_lifetime = timedelta(days=7)

# --- Database Connection Management ---
def get_db():
    """Get a database connection for the current request."""
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------- Helpers ----------
def get_student(sid):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id=%s", (sid,))
    student = cursor.fetchone()
    cursor.close()
    return student

def add_student_to_db(sid, name, course, branch, semester, hostel, mobile, password_hash):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO students (id, name, course, branch, semester, hostel, mobile, password)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (sid, name, course, branch, semester, hostel, mobile, password_hash)
    )
    db.commit()
    cursor.close()

def add_outing(sid, reason, client_time_str=None):
    db = get_db()
    if client_time_str:
        # Convert ISO string from client to datetime
        time_out = datetime.fromisoformat(client_time_str)
    else:
        time_out = datetime.now()  # fallback if JS fails

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO outings (student_id, reason, time_out) VALUES (%s,%s,%s)",
        (sid, reason, time_out)
    )
    db.commit()
    cursor.close()
    return time_out

def _format_duration(delta):
    if not isinstance(delta, timedelta):
        raise TypeError(f"_format_duration expected timedelta, got {type(delta)}")

    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts) if parts else "0s"


def mark_return(sid, client_time_str=None):
    db = get_db()
    if client_time_str:
        time_in = datetime.fromisoformat(client_time_str)
    else:
        time_in = datetime.now()

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, time_out FROM outings WHERE student_id=%s AND time_in IS NULL ORDER BY id DESC LIMIT 1",
        (sid,)
    )
    outing = cursor.fetchone()
    if not outing:
        cursor.close()
        return None, None

    cursor.execute("UPDATE outings SET time_in=%s WHERE id=%s", (time_in, outing["id"]))
    db.commit()
    cursor.close()

    time_out = outing["time_out"]

    # Convert if string from DB
    if isinstance(time_out, str):
        try:
            time_out = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            time_out = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S.%f")

    duration = time_in - time_out
    return time_in, _format_duration(duration)


def is_on_outing(sid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id FROM outings WHERE student_id=%s AND time_in IS NULL", (sid,)
    )
    res = cursor.fetchone()
    # Consume any unread results to avoid "Unread result found"
    cursor.fetchall()
    cursor.close()
    return bool(res)

def get_outing_history(sid):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT reason, time_out, time_in FROM outings WHERE student_id=%s ORDER BY id DESC", (sid,)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows

# ---------- Auth Routes ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        sid = request.form["sid"].strip()
        password = request.form["password"]
        student = get_student(sid)
        if student and "password" in student and check_password_hash(student["password"], password):
            session.permanent = True
            session["sid"] = str(sid)
            flash("✅ Login successful!", "success")
            return redirect(url_for("student_page", sid=sid))
        else:
            flash("❌ Invalid Student ID or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("sid", None)
    flash("👋 You have been logged out.", "info")
    return redirect(url_for("login"))

# ---------- Public Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        sid = request.form["sid"].strip()
        if not sid:
            flash("⚠️ Please enter a Student ID.", "warning")
            return redirect(url_for("index"))
        
        student = get_student(sid)
        if student:
            if session.get("sid") == str(sid):
                return redirect(url_for("student_page", sid=sid))
            return redirect(url_for("login"))
        else:
            flash(f"Student ID '{sid}' not found. Please register.", "danger")
            return redirect(url_for("register", sid=sid))
    return render_template("index.html")

@app.route("/register/", defaults={'sid': '0'}, methods=["GET", "POST"])
@app.route("/register/<sid>", methods=["GET", "POST"])
def register(sid):
    if request.method == "POST":
        sid = request.form["id"].strip()
        password = request.form["password"]
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("❌ Passwords do not match.", "danger")
            return redirect(url_for("register", sid=sid))

        try:
            pw_hash = generate_password_hash(password)
            add_student_to_db(
                sid,
                request.form["name"].strip(),
                request.form["course"].strip(),
                request.form["branch"].strip(),
                request.form["semester"].strip(),
                request.form["hostel"].strip(),
                request.form["mobile"].strip(),
                pw_hash
            )
            flash("✅ Student registered successfully! Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            if err.errno == 1062: # Duplicate entry
                flash(f"❌ Student ID '{sid}' is already registered.", "danger")
            else:
                flash(f"❌ A database error occurred: {err}", "danger")
            return redirect(url_for("register", sid=sid))

    return render_template("register.html", sid=sid)

# ---------- Protected Routes ----------
@app.route("/student/<sid>", methods=["GET", "POST"])
def student_page(sid):
    if "sid" not in session or session["sid"] != str(sid):
        flash("⚠️ Please log in to access this page.", "warning")
        return redirect(url_for("login"))

    student = get_student(sid)
    if not student:
        flash("❌ Student not found!", "danger")
        session.pop("sid", None)  # Log out user if their ID disappears
        return redirect(url_for("index"))

    if request.method == "POST":
        if "outing" in request.form:
            reason = request.form["reason"].strip()
            client_time_str = request.form.get("client_time")
            t_out = add_outing(sid, reason, client_time_str)
            flash(f"🫡 Outing started at {t_out.strftime('%I:%M %p')}", "info")

        elif "return" in request.form:
            client_time_str = request.form.get("client_time")
            t_in, duration = mark_return(sid, client_time_str)
            if t_in:
                flash(f"✅ Returned at {t_in.strftime('%I:%M %p')}. Total duration: {duration}", "success")
            else:
                flash("⚠️ No active outing found to mark as returned.", "warning")
        return redirect(url_for("student_page", sid=sid))


    return render_template("student.html", student=student, on_outing=is_on_outing(sid))

@app.route("/history/<sid>")
def history(sid):
    if "sid" not in session or session["sid"] != str(sid):
        flash("⚠️ Please log in to view outing history.", "warning")
        return redirect(url_for("login"))

    student = get_student(sid)
    if not student:
        flash("❌ Student not found!", "danger")
        return redirect(url_for("index"))

    outings = get_outing_history(sid)
    return render_template("history.html", student=student, outings=outings)

if __name__ == "__main__":
    app.run(debug=True)
