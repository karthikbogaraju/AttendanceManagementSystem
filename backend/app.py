from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
import os
import datetime

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')


# ------------ Paths ------------
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "attendance.db")

# ------------ DB helper ------------
def get_db_connection():
    """Open a sqlite3 connection and set row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

# ------------ Home & Login ----
@app.route("/")
def home():
    """Serve the main login page."""
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logout and return to login page."""
    return redirect(url_for("home"))

# ================== TEACHER FLOWS ==================

@app.route("/teacher/signup", methods=["GET", "POST"])
def teacher_signup():
    """Teacher registration: select courses to teach."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == "GET":
        cur.execute("SELECT id, name FROM courses")
        courses = cur.fetchall()
        conn.close()
        return render_template("teacher_signup.html", courses=courses)

    # POST - create teacher
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    course_ids = request.form.getlist("course_ids")

    if not course_ids:
        conn.close()
        return render_template("message.html", 
                             title="Error", 
                             message="Please select at least one course.",
                             link_text="Back",
                             link_url=url_for("teacher_signup"))

    try:
        cur.execute("INSERT INTO teachers (name,email,password) VALUES (?,?,?)", (name, email, password))
        teacher_id = cur.lastrowid
        for cid in course_ids:
            try:
                cur.execute("INSERT INTO teacher_courses (teacher_id, course_id) VALUES (?, ?)", (teacher_id, cid))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        return render_template("message.html",
                             title="Success",
                             message="Teacher account created successfully! You can now login.",
                             link_text="Go to Login",
                             link_url=url_for("home"))
    except sqlite3.IntegrityError:
        conn.rollback()
        return render_template("message.html",
                             title="Error",
                             message="A teacher with this email already exists.",
                             link_text="Try Again",
                             link_url=url_for("teacher_signup"))
    finally:
        conn.close()

@app.route("/teacher/login", methods=["POST"])
def teacher_login():
    """Authenticate teacher and redirect to dashboard."""
    email = request.form.get("email")
    password = request.form.get("password")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM teachers WHERE email=? AND password=?", (email, password))
    teacher = cur.fetchone()
    conn.close()

    if not teacher:
        return render_template("message.html",
                             title="Login Failed",
                             message="Invalid teacher credentials. Please try again.",
                             link_text="Back to Login",
                             link_url=url_for("home"))

    return redirect(url_for("teacher_dashboard", teacher_id=teacher["id"]))

@app.route("/teacher/dashboard/<int:teacher_id>")
def teacher_dashboard(teacher_id):
    """Teacher dashboard showing profile and courses."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, email FROM teachers WHERE id=?", (teacher_id,))
    teacher = cur.fetchone()
    if not teacher:
        conn.close()
        return render_template("error.html", message="Teacher not found"), 404

    cur.execute("""
        SELECT c.id, c.name
        FROM courses c
        JOIN teacher_courses tc ON c.id = tc.course_id
        WHERE tc.teacher_id = ?
    """, (teacher_id,))
    courses = cur.fetchall()
    conn.close()

    return render_template("teacher_dashboard.html",
                         teacher_id=teacher_id,
                         teacher_name=teacher['name'],
                         teacher_email=teacher['email'],
                         courses=courses)

@app.route("/teacher/<int:teacher_id>/courses/<int:course_id>/students")
def teacher_course_students(teacher_id, course_id):
    """Show students in a course."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM teacher_courses WHERE teacher_id=? AND course_id=?", (teacher_id, course_id))
    if not cur.fetchone():
        conn.close()
        return render_template("error.html", message="You are not assigned to this course"), 403

    cur.execute("""
        SELECT s.id, s.name, s.email
        FROM students s
        JOIN student_courses sc ON s.id = sc.student_id
        WHERE sc.course_id = ?
    """, (course_id,))
    students = cur.fetchall()

    cur.execute("SELECT name FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()
    conn.close()

    return render_template("teacher_students.html",
                         teacher_id=teacher_id,
                         course_id=course_id,
                         course_name=course['name'],
                         students=students)

@app.route("/teacher/add_student/<int:teacher_id>", methods=["GET", "POST"])
def teacher_add_student(teacher_id):
    """Add a new student and enroll in courses."""
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "GET":
        cur.execute("""
            SELECT c.id, c.name
            FROM courses c
            JOIN teacher_courses tc ON c.id = tc.course_id
            WHERE tc.teacher_id = ?
        """, (teacher_id,))
        courses = cur.fetchall()
        conn.close()
        return render_template("teacher_add_student.html", teacher_id=teacher_id, courses=courses)

    # POST
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    course_ids = request.form.getlist("course_ids")

    try:
        cur.execute("INSERT INTO students (name,email,password) VALUES (?,?,?)", (name, email, password))
        student_id = cur.lastrowid
        for cid in course_ids:
            try:
                cur.execute("INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)", (student_id, cid))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        return render_template("message.html",
                             title="Success",
                             message="Student added and enrolled successfully.",
                             link_text="Back to Dashboard",
                             link_url=url_for("teacher_dashboard", teacher_id=teacher_id))
    except sqlite3.IntegrityError:
        conn.rollback()
        return render_template("message.html",
                             title="Error",
                             message="A student with this email already exists.",
                             link_text="Try Again",
                             link_url=url_for("teacher_add_student", teacher_id=teacher_id))
    finally:
        conn.close()

@app.route("/teacher/edit_student/<int:student_id>/<int:teacher_id>", methods=["GET", "POST"])
def edit_student_form(student_id, teacher_id):
    """Edit student form with course enrollment management."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, name, email FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()
    if not student:
        conn.close()
        return render_template("error.html", message="Student not found"), 404

    cur.execute("""
        SELECT c.id, c.name
        FROM courses c
        JOIN teacher_courses tc ON c.id = tc.course_id
        WHERE tc.teacher_id = ?
    """, (teacher_id,))
    teacher_courses = cur.fetchall()

    cur.execute("SELECT course_id FROM student_courses WHERE student_id=?", (student_id,))
    enrolled = {row["course_id"] for row in cur.fetchall()}
    conn.close()

    return render_template("teacher_edit_student.html",
                         student_id=student_id,
                         teacher_id=teacher_id,
                         student_name=student['name'],
                         student_email=student['email'],
                         courses=teacher_courses,
                         enrolled=enrolled)

@app.route("/teacher/update_student", methods=["POST"])
def update_student():
    """Update student profile and course enrollment."""
    student_id = int(request.form.get("student_id"))
    teacher_id = int(request.form.get("teacher_id"))
    name = request.form.get("name")
    email = request.form.get("email")
    selected_course_ids = set(map(int, request.form.getlist("course_ids")))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE students SET name=?, email=? WHERE id=?", (name, email, student_id))

    cur.execute("SELECT course_id FROM teacher_courses WHERE teacher_id = ?", (teacher_id,))
    teacher_course_ids = {r["course_id"] for r in cur.fetchall()}

    cur.execute("SELECT course_id FROM student_courses WHERE student_id=?", (student_id,))
    existing = {r["course_id"] for r in cur.fetchall()}

    for cid in (selected_course_ids & teacher_course_ids) - existing:
        try:
            cur.execute("INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)", (student_id, cid))
        except sqlite3.IntegrityError:
            pass

    for cid in (existing & teacher_course_ids) - selected_course_ids:
        cur.execute("DELETE FROM student_courses WHERE student_id=? AND course_id=?", (student_id, cid))

    conn.commit()
    conn.close()
    return redirect(url_for("teacher_dashboard", teacher_id=teacher_id))

@app.route("/teacher/<int:teacher_id>/courses/<int:course_id>/attendance", methods=["GET", "POST"])
def teacher_attendance(teacher_id, course_id):
    """Mark and view attendance."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM teacher_courses WHERE teacher_id=? AND course_id=?", (teacher_id, course_id))
    if not cur.fetchone():
        conn.close()
        return render_template("error.html", message="You are not assigned to this course"), 403

    if request.method == "GET":
        cur.execute("""
            SELECT s.id, s.name
            FROM students s
            JOIN student_courses sc ON s.id = sc.student_id
            WHERE sc.course_id = ?
        """, (course_id,))
        students = cur.fetchall()

        cur.execute("""
            SELECT date, COUNT(*) as total
            FROM attendance
            WHERE course_id = ?
            GROUP BY date
            ORDER BY date DESC
        """, (course_id,))
        attendance_dates = cur.fetchall()

        cur.execute("SELECT name FROM courses WHERE id=?", (course_id,))
        course = cur.fetchone()
        conn.close()

        return render_template("teacher_attendance.html",
                             teacher_id=teacher_id,
                             course_id=course_id,
                             course_name=course['name'],
                             students=students,
                             attendance_dates=attendance_dates)

    # POST - save attendance
    date = request.form.get("date") or datetime.date.today().isoformat()
    
    cur.execute("SELECT student_id FROM student_courses WHERE course_id=?", (course_id,))
    students = cur.fetchall()
    for s in students:
        sid = s["student_id"]
        status = request.form.get(f"status_{sid}")
        if status:
            cur.execute("""
                SELECT id FROM attendance WHERE student_id=? AND course_id=? AND date=?
            """, (sid, course_id, date))
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE attendance SET status=? WHERE id=?", (status, existing["id"]))
            else:
                cur.execute("INSERT INTO attendance (student_id, course_id, date, status) VALUES (?,?,?,?)",
                            (sid, course_id, date, status))

    conn.commit()
    conn.close()
    return render_template("message.html",
                         title="Success",
                         message=f"Attendance saved for {date}",
                         link_text="Back",
                         link_url=url_for("teacher_attendance", teacher_id=teacher_id, course_id=course_id))

@app.route("/teacher/<int:teacher_id>/courses/<int:course_id>/attendance/edit", methods=["GET", "POST"])
def edit_attendance(teacher_id, course_id):
    """Edit attendance records for a specific date."""
    date = request.args.get("date") if request.method == "GET" else request.form.get("date")
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM teacher_courses WHERE teacher_id=? AND course_id=?", (teacher_id, course_id))
    if not cur.fetchone():
        conn.close()
        return render_template("error.html", message="You are not assigned to this course"), 403

    if request.method == "GET":
        cur.execute("""
            SELECT a.id, a.student_id, s.name, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.course_id=? AND a.date=?
        """, (course_id, date))
        rows = cur.fetchall()
        conn.close()
        return render_template("teacher_edit_attendance.html",
                             teacher_id=teacher_id,
                             course_id=course_id,
                             date=date,
                             attendance_records=rows)

    # POST - save edits
    keys = [k for k in request.form.keys() if k.startswith("att_")]
    for key in keys:
        att_id = int(key.split("_", 1)[1])
        status = request.form.get(key)
        cur.execute("UPDATE attendance SET status=? WHERE id=?", (status, att_id))
    conn.commit()
    conn.close()
    return redirect(url_for("teacher_attendance", teacher_id=teacher_id, course_id=course_id))

@app.route("/teacher/edit_profile/<int:teacher_id>", methods=["GET", "POST"])
def edit_teacher_profile(teacher_id):
    """Edit teacher profile and course assignments."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == "GET":
        cur.execute("SELECT id, name, email FROM teachers WHERE id=?", (teacher_id,))
        t = cur.fetchone()
        cur.execute("""
            SELECT c.id, c.name,
                   CASE WHEN tc.course_id IS NULL THEN 0 ELSE 1 END AS assigned
            FROM courses c LEFT JOIN (
                SELECT course_id FROM teacher_courses WHERE teacher_id=?
            ) tc ON c.id = tc.course_id
        """, (teacher_id,))
        courses = cur.fetchall()
        conn.close()
        return render_template("teacher_profile.html",
                             teacher_id=teacher_id,
                             teacher_name=t['name'],
                             teacher_email=t['email'],
                             courses=courses)

    # POST - save changes
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    selected = set(map(int, request.form.getlist("course_ids")))

    if password:
        cur.execute("UPDATE teachers SET name=?, email=?, password=? WHERE id=?", (name, email, password, teacher_id))
    else:
        cur.execute("UPDATE teachers SET name=?, email=? WHERE id=?", (name, email, teacher_id))

    cur.execute("SELECT course_id FROM teacher_courses WHERE teacher_id=?", (teacher_id,))
    existing = {r["course_id"] for r in cur.fetchall()}

    for cid in selected - existing:
        try:
            cur.execute("INSERT INTO teacher_courses (teacher_id, course_id) VALUES (?, ?)", (teacher_id, cid))
        except sqlite3.IntegrityError:
            pass

    for cid in existing - selected:
        cur.execute("DELETE FROM teacher_courses WHERE teacher_id=? AND course_id=?", (teacher_id, cid))

    conn.commit()
    conn.close()
    return redirect(url_for("teacher_dashboard", teacher_id=teacher_id))

# ================== STUDENT FLOWS ==================

@app.route("/student/signup", methods=["GET", "POST"])
def student_signup():
    """Student registration: select courses to join."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == "GET":
        cur.execute("SELECT id, name FROM courses")
        courses = cur.fetchall()
        conn.close()
        return render_template("student_signup.html", courses=courses)

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    course_ids = request.form.getlist("course_ids")

    try:
        cur.execute("INSERT INTO students (name, email, password) VALUES (?,?,?)", (name, email, password))
        student_id = cur.lastrowid
        for cid in course_ids:
            try:
                cur.execute("INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)", (student_id, cid))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        return render_template("message.html",
                             title="Success",
                             message="Student account created successfully! You can now login.",
                             link_text="Go to Login",
                             link_url=url_for("home"))
    except sqlite3.IntegrityError:
        conn.rollback()
        return render_template("message.html",
                             title="Error",
                             message="A student with this email already exists.",
                             link_text="Try Again",
                             link_url=url_for("student_signup"))
    finally:
        conn.close()

@app.route("/student/login", methods=["POST"])
def student_login():
    """Student login: redirect to dashboard."""
    email = request.form.get("email")
    password = request.form.get("password")
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM students WHERE email=? AND password=?", (email, password))
    student = cur.fetchone()
    if not student:
        conn.close()
        return render_template("message.html",
                             title="Login Failed",
                             message="Invalid student credentials. Please try again.",
                             link_text="Back to Login",
                             link_url=url_for("home"))

    student_id = student["id"]
    conn.close()
    return redirect(url_for("student_dashboard", student_id=student_id))

@app.route("/student/dashboard/<int:student_id>")
def student_dashboard(student_id):
    """Student dashboard showing profile and courses."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()
    if not student:
        conn.close()
        return render_template("error.html", message="Student not found"), 404

    cur.execute("""
        SELECT c.id, c.name
        FROM courses c
        JOIN student_courses sc ON c.id = sc.course_id
        WHERE sc.student_id = ?
    """, (student_id,))
    courses = cur.fetchall()
    conn.close()

    return render_template("student_dashboard.html",
                         student_id=student_id,
                         student_name=student['name'],
                         courses=courses)

@app.route("/student/<int:student_id>/courses/<int:course_id>/attendance")
def student_view_attendance(student_id, course_id):
    """Student view attendance records."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM student_courses WHERE student_id=? AND course_id=?", (student_id, course_id))
    if not cur.fetchone():
        conn.close()
        return render_template("error.html", message="You are not enrolled in this course"), 403

    cur.execute("SELECT date, status FROM attendance WHERE student_id=? AND course_id=? ORDER BY date DESC", 
                (student_id, course_id))
    records = cur.fetchall()
    
    cur.execute("SELECT name FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()
    conn.close()

    return render_template("student_attendance.html",
                         student_id=student_id,
                         course_id=course_id,
                         course_name=course['name'],
                         records=records)

@app.route("/student/edit_profile/<int:student_id>", methods=["GET", "POST"])
def edit_student_profile(student_id):
    """Edit student profile and course enrollment."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == "GET":
        cur.execute("SELECT id, name, email FROM students WHERE id=?", (student_id,))
        s = cur.fetchone()
        cur.execute("SELECT id, name FROM courses")
        courses = cur.fetchall()
        cur.execute("SELECT course_id FROM student_courses WHERE student_id=?", (student_id,))
        enrolled = {r["course_id"] for r in cur.fetchall()}
        conn.close()
        return render_template("student_profile.html",
                             student_id=student_id,
                             student_name=s['name'],
                             student_email=s['email'],
                             courses=courses,
                             enrolled=enrolled)

    # POST
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    selected = set(map(int, request.form.getlist("course_ids")))

    if password:
        cur.execute("UPDATE students SET name=?, email=?, password=? WHERE id=?", (name, email, password, student_id))
    else:
        cur.execute("UPDATE students SET name=?, email=? WHERE id=?", (name, email, student_id))

    cur.execute("SELECT course_id FROM student_courses WHERE student_id=?", (student_id,))
    existing = {r["course_id"] for r in cur.fetchall()}

    for cid in selected - existing:
        try:
            cur.execute("INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)", (student_id, cid))
        except sqlite3.IntegrityError:
            pass

    for cid in existing - selected:
        cur.execute("DELETE FROM student_courses WHERE student_id=? AND course_id=?", (student_id, cid))

    conn.commit()
    conn.close()
    return render_template("message.html",
                         title="Success",
                         message="Profile and enrollments updated successfully!",
                         link_text="Go to Dashboard",
                         link_url=url_for("student_dashboard", student_id=student_id))

# ================== ERROR HANDLERS ==================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", message="Page not found (404)"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", message="Server error (500)"), 500

# ================== MAIN ==================
if __name__ == "__main__":
    app.run(debug=True)
