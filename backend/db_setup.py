import sqlite3
import os

# Path to database file (project layout: backend/<this file>, database folder sibling)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "attendance.db")

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -------------------------
    # TEACHERS
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

   
    # STUDENTS

    # Students table stores profile info. Courses are managed via student_courses mapping
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    
    # COURSES
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # -------------------------
    # teacher_courses (mapping teacher -> course)
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        UNIQUE(teacher_id, course_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
    """)

    # -------------------------
    # student_courses (mapping student -> course)  (students can join multiple)
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        UNIQUE(student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id) 

    );
    """)

    # -------------------------
    # ATTENDANCE
    # -------------------------
    # Each row is a record of a student's status for a course on a date
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)     
    );
    """)



    # -------------------------
    # Seed: sample courses and accounts
    # (INSERT OR IGNORE used so re-running won't duplicate)
    # -------------------------
    cur.execute("INSERT OR IGNORE INTO courses (id, name) VALUES (1, 'Python 101')")
    cur.execute("INSERT OR IGNORE INTO courses (id, name) VALUES (2, 'Data Structures')")
    cur.execute("INSERT OR IGNORE INTO courses (id, name) VALUES (3, 'Java')")
    cur.execute("INSERT OR IGNORE INTO courses (id, name) VALUES (4, 'AI Basics')")


    # Sample teacher (will not duplicate because of OR IGNORE on unique email)
    cur.execute("""
    INSERT OR IGNORE INTO teachers (id, name, email, password)
    VALUES (1, 'Test Teacher', 'teacher@example.com', 'password123')
    """)

    # Sample student
    cur.execute("""
    INSERT OR IGNORE INTO students (id, name, email, password)
    VALUES (1, 'Student One', 'student1@example.com', 'studpass1')
    """)

    # Map teacher to course(s)
    cur.execute("INSERT OR IGNORE INTO teacher_courses (id, teacher_id, course_id) VALUES (1, 1, 1)")
    cur.execute("INSERT OR IGNORE INTO teacher_courses (id, teacher_id, course_id) VALUES (2, 1, 2)")

    # Map sample student to a course
    cur.execute("INSERT OR IGNORE INTO student_courses (id, student_id, course_id) VALUES (1, 1, 1)")

    conn.commit()
    conn.close()
    print("✅ Database & tables created (attendance.db). Sample data inserted.")

if __name__ == "__main__":
    main()
