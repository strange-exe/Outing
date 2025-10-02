# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from datetime import datetime, timedelta
import mysql.connector
import json
import pytz

app = Flask(__name__)

# Load config
with open("config.json") as f:
    config = json.load(f)

app.secret_key = config.get("SECRET_KEY", "a-default-fallback-secret-key")
app.permanent_session_lifetime = timedelta(days=7)

# Timezone
TZ = pytz.timezone('Asia/Kolkata')

# ---------- Database Management ----------
def get_db():
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------- Helpers ----------
def get_ordinal_suffix(num):
    if num is None:
        return ""  # return empty string if no value
    try:
        j = int(num) % 10
        k = int(num) % 100
        if j == 1 and k != 11:
            return "st"
        elif j == 2 and k != 12:
            return "nd"
        elif j == 3 and k != 13:
            return "rd"
        else:
            return "th"
    except (ValueError, TypeError):
        return ""  # fallback in case num is invalid

app.jinja_env.filters['ordinal'] = get_ordinal_suffix

def format_duration(start, end):
    if not start or not end:
        return "N/A"
    delta = end - start
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(_)}s"

app.jinja_env.filters['duration'] = format_duration


def get_student(sid):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id=%s", (sid,))
    student = cursor.fetchone()
    cursor.close()
    return student

def add_student_to_db(sid, name, course, branch, semester, year, hostel, room, mobile, password_hash):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO students (id, name, course, branch, semester, year, hostel, room, mobile, password)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (sid, name, course, branch, semester, year, hostel, room, mobile, password_hash)
    )
    db.commit()
    cursor.close()

# ---------- Outing Helpers ----------
def _format_duration(delta):
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts) if parts else "0s"

def add_outing(sid, reason):
    db = get_db()
    time_out = datetime.now(TZ)  # aware datetime
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO outings (student_id, reason, time_out) VALUES (%s,%s,%s)",
        (sid, reason, time_out)
    )
    db.commit()
    cursor.close()
    return time_out

def mark_return(sid):
    db = get_db()
    time_in = datetime.now(TZ)  # aware datetime

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, time_out FROM outings WHERE student_id=%s AND time_in IS NULL ORDER BY id DESC LIMIT 1",
        (sid,)
    )
    outing = cursor.fetchone()
    if not outing:
        cursor.close()
        return None, None

    # Ensure time_out is aware
    time_out = outing["time_out"]
    if isinstance(time_out, str):
        try:
            time_out = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            time_out = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S.%f")

    if time_out.tzinfo is None:
        time_out = TZ.localize(time_out)

    cursor.execute("UPDATE outings SET time_in=%s WHERE id=%s", (time_in, outing['id']))
    db.commit()
    cursor.close()

    duration = time_in - time_out
    return time_in, _format_duration(duration)

def is_on_outing(sid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM outings WHERE student_id=%s AND time_in IS NULL", (sid,))
    res = cursor.fetchone()
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

# ---------- Routes ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        sid = request.form["sid"].strip()
        password = request.form["password"]
        student = get_student(sid)
        if student and check_password_hash(student["password"], password):
            session.permanent = True
            session["sid"] = str(sid)
            flash("✅ Login successful!", "success")
            return redirect(url_for("student_page"))
        flash("❌ Invalid Student ID or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("sid", None)
    flash("👋 You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])

def index():
    if request.method == "POST":
        sid = request.form["sid"].strip()
        password = request.form["password"]
        student = get_student(sid)
        if student and check_password_hash(student["password"], password):
            session.permanent = True
            session["sid"] = str(sid)
            flash("Login successful!", "success")
            return redirect(url_for("student_page", sid=sid))
        flash("Invalid Student ID or password.", "danger")
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        sid = request.form["id"].strip()
        password = request.form["password"]
        confirm = request.form.get("confirm_password", "")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        try:
            pw_hash = generate_password_hash(password)
            add_student_to_db(
                sid,
                request.form["name"].strip(),
                request.form["course"].strip(),
                request.form["branch"].strip(),
                request.form["semester"].strip(),
                request.form["year"].strip(),
                request.form["hostel"].strip(),
                request.form.get("room", "").strip(),  # Optional field
                request.form["mobile"].strip(),
                pw_hash
            )
            flash("Student registered successfully! Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            if err.errno == 1062:
                flash(f"Student ID '{sid}' is already registered.", "danger")
            else:
                flash(f"A database error occurred: {err}", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/student", methods=["GET", "POST"])
def student_page():
    sid = session.get("sid")
    if not sid:
        flash("⚠️ Please log in to access this page.", "warning")
        return redirect(url_for("login"))

    student = get_student(sid)
    if not student:
        flash("Student not found!", "danger")
        session.pop("sid", None)
        return redirect(url_for("index"))

    if request.method == "POST":
        if "outing" in request.form:
            reason = request.form["reason"].strip()
            if reason:
                t_out = add_outing(sid, reason)
                flash(f"🫡 Outing started at {t_out.strftime('%I:%M %p')}", "info")
            else:
                flash("⚠️ Reason required.", "warning")
        elif "return" in request.form:
            t_in, duration = mark_return(sid)
            if t_in:
                flash(f"Returned at {t_in.strftime('%I:%M %p')}. Total duration: {duration}", "success")
            else:
                flash("⚠️ No active outing found.", "warning")
        return redirect(url_for("student_page"))

    return render_template("student.html", student=student, on_outing=is_on_outing(sid))


@app.route("/history", methods=["GET", "POST"])
def history():
    sid = session.get("sid")
    if not sid:
        flash("⚠️ Please log in to view outing history.", "warning")
        return redirect(url_for("login"))

    student = get_student(sid)
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for("index"))

    outings = get_outing_history(sid)
    return render_template("history.html", student=student, outings=outings)

if __name__ == "__main__":
    app.run(debug=True)
