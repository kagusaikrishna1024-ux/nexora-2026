
import sqlite3
import hashlib
import secrets
from pathlib import Path

DB_PATH = Path(__file__).parent / "nexora.db"

DEMO_STUDENTS = [
    ("Aarav Sharma", "student01"),
    ("Ananya Patel", "student02"),
    ("Vivaan Reddy", "student03"),
    ("Diya Nair", "student04"),
    ("Arjun Kumar", "student05"),
    ("Meera Iyer", "student06"),
    ("Reyansh Gupta", "student07"),
    ("Aadhya Singh", "student08"),
    ("Advik Joshi", "student09"),
    ("Saanvi Rao", "student10"),
    ("Kabir Verma", "student11"),
    ("Ishita Das", "student12"),
    ("Vihaan Malhotra", "student13"),
    ("Pari Shah", "student14"),
    ("Arnav Kapoor", "student15"),
    ("Anaya Menon", "student16"),
    ("Krishna Bhat", "student17"),
    ("Myra Kulkarni", "student18"),
    ("Dhruv Choudhary", "student19"),
    ("Sara Fernandes", "student20"),
    ("Rohan Mishra", "student21"),
    ("Tara Banerjee", "student22"),
    ("Atharv Sinha", "student23"),
    ("Kiara Thomas", "student24"),
    ("Ishaan Ghosh", "student25"),
    ("Navya Pillai", "student26"),
    ("Yash Agarwal", "student27"),
    ("Riya Chawla", "student28"),
    ("Omkar Desai", "student29"),
    ("Zoya Khan", "student30"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000
    ).hex()
    return salt, hashed


def verify_password(password, salt, saved_hash):
    _, entered_hash = hash_password(password, salt)
    return secrets.compare_digest(entered_hash, saved_hash)


def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                duration TEXT DEFAULT '',
                fee REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TEXT DEFAULT CURRENT_DATE,
                progress REAL DEFAULT 0,
                attendance_percent REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                UNIQUE(user_id, course_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            );

            CREATE TABLE IF NOT EXISTS complaints (
                complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT 'Other',
                priority TEXT DEFAULT 'Medium',
                department TEXT DEFAULT 'Student Support',
                ai_response TEXT DEFAULT '',
                status TEXT DEFAULT 'Open',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_status TEXT DEFAULT 'Pending',
                payment_date TEXT DEFAULT CURRENT_DATE,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            );

            CREATE TABLE IF NOT EXISTS announcements (
                announcement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS class_schedule (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                starts_at TEXT NOT NULL,
                instructor TEXT NOT NULL,
                meeting_mode TEXT DEFAULT 'Online',
                UNIQUE(course_id, title),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            );

            CREATE TABLE IF NOT EXISTS learning_resources (
                resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                url TEXT NOT NULL,
                UNIQUE(course_id, title),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            );

            CREATE TABLE IF NOT EXISTS certificates (
                certificate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                certificate_code TEXT NOT NULL UNIQUE,
                issued_at TEXT DEFAULT CURRENT_DATE,
                UNIQUE(user_id, course_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            );

            CREATE TABLE IF NOT EXISTS internships (
                internship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_title TEXT NOT NULL UNIQUE,
                company TEXT NOT NULL,
                work_mode TEXT NOT NULL,
                deadline TEXT NOT NULL,
                description TEXT NOT NULL
            );
        """)

        enrollment_columns = {
            column["name"]
            for column in conn.execute("PRAGMA table_info(enrollments)")
        }
        if "attendance_percent" not in enrollment_columns:
            conn.execute(
                "ALTER TABLE enrollments ADD COLUMN attendance_percent REAL DEFAULT 0"
            )

        default_courses = [
            ("Python", "Python programming fundamentals", "3 months", 8000),
            ("SQL", "Database and SQL training", "2 months", 6000),
            ("Data Analytics", "Analytics with Excel, SQL and Power BI", "4 months", 15000),
            ("Power BI", "Interactive dashboard development", "2 months", 7000),
            ("Excel", "Excel and data analysis", "1 month", 4000),
            ("Java", "Java programming and object-oriented development", "3 months", 10000),
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO courses
            (course_name, description, duration, fee)
            VALUES (?, ?, ?, ?)
        """, default_courses)

        demo_accounts = [
            (name, username, f"{username}@nexora.local", "Student@123", "student")
            for name, username in DEMO_STUDENTS
        ]
        demo_accounts.extend([
            ("Krishna", "admin", "admin@nexora.local", "Admin@123", "admin"),
            ("Arsha", "admin2", "admin2@nexora.local", "Admin@123", "admin"),
        ])

        for full_name, username, email, password, role in demo_accounts:
            account_exists = conn.execute(
                "SELECT user_id FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if account_exists is None:
                salt, password_hash = hash_password(password)
                conn.execute("""
                    INSERT INTO users
                    (full_name, username, email, salt, password_hash, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (full_name, username, email, salt, password_hash, role))

        for full_name, username in (("Krishna", "admin"), ("Arsha", "admin2")):
            conn.execute("""
                UPDATE users SET full_name = ?
                WHERE username = ? AND role = 'admin'
            """, (full_name, username))

        course_rows = conn.execute(
            "SELECT course_id, course_name, fee FROM courses ORDER BY course_name"
        ).fetchall()
        course_ids = {row["course_name"]: row["course_id"] for row in course_rows}
        course_names = ["Data Analytics", "Excel", "Power BI", "Python", "SQL"]

        schedule_seeds = [
            ("Python", "Python lab: functions and modules", "2026-10-05 16:00", "Ananya Rao"),
            ("SQL", "SQL clinic: joins and reporting", "2026-10-06 17:00", "Rohan Das"),
            ("Data Analytics", "Analytics workshop: build a dashboard", "2026-10-07 16:30", "Meera Nair"),
            ("Power BI", "Power BI studio: publish your report", "2026-10-08 17:00", "Kabir Shah"),
            ("Excel", "Excel practice: formulas and pivots", "2026-10-09 16:00", "Diya Menon"),
            ("Java", "Java lab: classes and object-oriented design", "2026-10-10 16:00", "Arjun Nair"),
        ]
        for course_name, title, starts_at, instructor in schedule_seeds:
            conn.execute("""
                INSERT OR IGNORE INTO class_schedule
                (course_id, title, starts_at, instructor)
                VALUES (?, ?, ?, ?)
            """, (course_ids[course_name], title, starts_at, instructor))

        resource_seeds = [
            ("Python", "Python language tutorial", "Documentation", "https://docs.python.org/3/tutorial/"),
            ("SQL", "SQLite SQL language reference", "Documentation", "https://www.sqlite.org/lang.html"),
            ("Data Analytics", "Data analysis with pandas", "Documentation", "https://pandas.pydata.org/docs/getting_started/intro_tutorials/"),
            ("Power BI", "Power BI learning paths", "Learning path", "https://learn.microsoft.com/power-bi/"),
            ("Excel", "Excel help and learning", "Learning path", "https://support.microsoft.com/excel"),
            ("Java", "Java tutorials", "Documentation", "https://dev.java/learn/"),
        ]
        for course_name, title, resource_type, url in resource_seeds:
            conn.execute("""
                INSERT OR IGNORE INTO learning_resources
                (course_id, title, resource_type, url)
                VALUES (?, ?, ?, ?)
            """, (course_ids[course_name], title, resource_type, url))

        demo_users = conn.execute("""
            SELECT user_id, username FROM users
            WHERE role = 'student' AND username GLOB 'student[0-9][0-9]'
            ORDER BY username
        """).fetchall()
        payment_statuses = ["Paid", "Paid", "Pending", "Paid", "Paid"]
        progress_values = [18, 42, 68, 100, 0]
        attendance_values = [86, 92, 74, 100, 65]
        for index, student in enumerate(demo_users):
            course_name = course_names[index % len(course_names)]
            course_id = course_ids[course_name]
            enrollment = conn.execute("""
                SELECT enrollment_id FROM enrollments
                WHERE user_id = ? AND course_id = ?
            """, (student["user_id"], course_id)).fetchone()
            if enrollment is None:
                conn.execute("""
                    INSERT INTO enrollments
                    (user_id, course_id, progress, attendance_percent, status)
                    VALUES (?, ?, ?, ?, 'Active')
                """, (student["user_id"], course_id,
                      progress_values[index % 5], attendance_values[index % 5]))
            else:
                conn.execute("""
                    UPDATE enrollments SET attendance_percent = ?
                    WHERE user_id = ? AND course_id = ? AND attendance_percent = 0
                """, (attendance_values[index % 5], student["user_id"], course_id))

            payment_exists = conn.execute("""
                SELECT payment_id FROM payments
                WHERE user_id = ? AND course_id = ?
            """, (student["user_id"], course_id)).fetchone()
            if payment_exists is None:
                status = payment_statuses[index % 5]
                conn.execute("""
                    INSERT INTO payments
                    (user_id, course_id, amount, payment_status)
                    VALUES (?, ?, ?, ?)
                """, (student["user_id"], course_id,
                      next(row["fee"] for row in conn.execute(
                          "SELECT course_id, fee FROM courses WHERE course_id = ?",
                          (course_id,)
                      )), status))

            if progress_values[index % 5] == 100:
                conn.execute("""
                    INSERT OR IGNORE INTO certificates
                    (user_id, course_id, certificate_code)
                    VALUES (?, ?, ?)
                """, (student["user_id"], course_id,
                      f"NX-{student['username'].upper()}-{course_id:02d}"))

        java_course_id = course_ids["Java"]
        java_fee = next(row["fee"] for row in course_rows
                        if row["course_name"] == "Java")
        for index, student in enumerate(demo_users):
            java_enrollment = conn.execute("""
                SELECT enrollment_id FROM enrollments
                WHERE user_id = ? AND course_id = ?
            """, (student["user_id"], java_course_id)).fetchone()
            if java_enrollment is None:
                conn.execute("""
                    INSERT INTO enrollments
                    (user_id, course_id, progress, attendance_percent, status)
                    VALUES (?, ?, ?, ?, 'Active')
                """, (
                    student["user_id"],
                    java_course_id,
                    progress_values[(index + 1) % 5],
                    attendance_values[(index + 2) % 5],
                ))

            java_payment = conn.execute("""
                SELECT payment_id FROM payments
                WHERE user_id = ? AND course_id = ?
            """, (student["user_id"], java_course_id)).fetchone()
            if java_payment is None:
                conn.execute("""
                    INSERT INTO payments
                    (user_id, course_id, amount, payment_status)
                    VALUES (?, ?, ?, ?)
                """, (
                    student["user_id"], java_course_id, java_fee,
                    payment_statuses[(index + 1) % 5],
                ))

        announcement_count = conn.execute(
            "SELECT COUNT(*) FROM announcements"
        ).fetchone()[0]
        if announcement_count == 0:
            conn.executemany("""
                INSERT INTO announcements (title, message)
                VALUES (?, ?)
            """, [
                ("Welcome to NEXORA 2026", "Your student portal is ready. Check your course dashboard for learning resources and upcoming sessions."),
                ("Support desk hours", "The student support team reviews new requests on weekdays. High-priority payment and access issues are routed first."),
                ("Career clinic", "Bring your resume and project portfolio to the online career clinic this Friday at 4:00 PM."),
            ])

        internship_count = conn.execute(
            "SELECT COUNT(*) FROM internships"
        ).fetchone()[0]
        if internship_count == 0:
            conn.executemany("""
                INSERT INTO internships
                (role_title, company, work_mode, deadline, description)
                VALUES (?, ?, ?, ?, ?)
            """, [
                ("Junior Data Analyst Intern", "Northstar Labs", "Hybrid", "2026-10-24", "Build reports, validate datasets and share weekly insights with the analytics team."),
                ("Python Automation Intern", "Brightpath Systems", "Remote", "2026-10-30", "Create small Python tools and document repeatable operations workflows."),
                ("Business Intelligence Intern", "Cedarline Digital", "On-site", "2026-11-05", "Support dashboard development and convert stakeholder questions into metrics."),
            ])

        complaint_count = conn.execute(
            "SELECT COUNT(*) FROM complaints"
        ).fetchone()[0]
        if complaint_count == 0 and demo_users:
            conn.executemany("""
                INSERT INTO complaints
                (user_id, description, category, priority, department, ai_response, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (demo_users[0]["user_id"], "I paid for Data Analytics yesterday, but my enrollment is still not showing.", "Payment / Enrollment", "High", "Accounts / Admissions", "Payment and enrollment request routed to Accounts / Admissions.", "Open"),
                (demo_users[1]["user_id"], "I cannot access yesterday's class recording.", "Course / Technical Support", "Medium", "Technical / Course Support", "Recording access request routed to course support.", "In Progress"),
                (demo_users[2]["user_id"], "When will my course certificate be available?", "Certificate / Internship", "Medium", "Career Services", "Certificate request routed to Career Services.", "Resolved"),
                (demo_users[3]["user_id"], "Please confirm the schedule for the next class.", "Schedule / Attendance", "Medium", "Academic Operations", "Schedule request routed to Academic Operations.", "Open"),
            ])


def register_student(full_name, username, email, password, course_id):
    salt, password_hash = hash_password(password)

    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO users
                (full_name, username, email, salt, password_hash, role)
                VALUES (?, ?, ?, ?, ?, 'student')
            """, (
                full_name.strip(),
                username.strip(),
                email.strip(),
                salt,
                password_hash
            ))

            user_id = cursor.lastrowid

            if course_id is not None:
                conn.execute("""
                    INSERT INTO enrollments (user_id, course_id)
                    VALUES (?, ?)
                """, (user_id, course_id))
                course = conn.execute(
                    "SELECT fee FROM courses WHERE course_id = ?",
                    (course_id,)
                ).fetchone()
                conn.execute("""
                    INSERT INTO payments
                    (user_id, course_id, amount, payment_status)
                    VALUES (?, ?, ?, 'Pending')
                """, (user_id, course_id, course["fee"]))

        return True, "Registration successful. Please log in."

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."


def authenticate_user(username, password):
    with get_connection() as conn:
        user = conn.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username.strip(),)).fetchone()

    if user is None:
        return None

    if verify_password(
        password,
        user["salt"],
        user["password_hash"]
    ):
        return dict(user)

    return None


def get_courses():
    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM courses ORDER BY course_name
        """).fetchall()


def add_course(course_name, description, duration, fee):
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO courses (course_name, description, duration, fee)
                VALUES (?, ?, ?, ?)
            """, (course_name.strip(), description.strip(), duration.strip(), fee))
        return True, "Course added to the catalogue."
    except sqlite3.IntegrityError:
        return False, "A course with that name already exists."


def get_student_courses(user_id):
    with get_connection() as conn:
        return conn.execute("""
                 SELECT c.course_id, c.course_name, c.description, c.duration,
                     c.fee, e.enrollment_date, e.progress,
                     e.attendance_percent, e.status
            FROM enrollments e
            JOIN courses c ON c.course_id = e.course_id
            WHERE e.user_id = ?
            ORDER BY c.course_name
        """, (user_id,)).fetchall()


def get_student_schedule(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT s.title, s.starts_at, s.instructor, s.meeting_mode,
                   c.course_name
            FROM class_schedule s
            JOIN courses c ON c.course_id = s.course_id
            JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.user_id = ? AND e.status = 'Active'
            ORDER BY s.starts_at
        """, (user_id,)).fetchall()


def get_student_resources(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT r.title, r.resource_type, r.url, c.course_name
            FROM learning_resources r
            JOIN courses c ON c.course_id = r.course_id
            JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.user_id = ? AND e.status = 'Active'
            ORDER BY c.course_name
        """, (user_id,)).fetchall()


def get_student_payments(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT c.course_name, p.amount, p.payment_status, p.payment_date
            FROM payments p
            JOIN courses c ON c.course_id = p.course_id
            WHERE p.user_id = ?
            ORDER BY p.payment_date DESC
        """, (user_id,)).fetchall()


def get_student_certificates(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT c.course_name, cert.certificate_code, cert.issued_at
            FROM certificates cert
            JOIN courses c ON c.course_id = cert.course_id
            WHERE cert.user_id = ?
            ORDER BY cert.issued_at DESC
        """, (user_id,)).fetchall()


def get_student_tickets(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT complaint_id, description, category, priority,
                   department, ai_response, status, created_at, resolved_at
            FROM complaints
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()


def create_support_ticket(user_id, description, triage):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO complaints
            (user_id, description, category, priority, department, ai_response)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            description.strip(),
            triage["category"],
            triage["priority"],
            triage["department"],
            triage["response"],
        ))
        return cursor.lastrowid


def get_all_tickets():
    with get_connection() as conn:
        return conn.execute("""
            SELECT c.complaint_id, c.description, c.category, c.priority,
                   c.department, c.ai_response, c.status, c.created_at,
                   c.resolved_at, u.full_name, u.username
            FROM complaints c
            JOIN users u ON u.user_id = c.user_id
            ORDER BY CASE c.priority WHEN 'High' THEN 0 ELSE 1 END,
                     CASE c.status WHEN 'Open' THEN 0 WHEN 'In Progress' THEN 1 ELSE 2 END,
                     c.created_at DESC
        """).fetchall()


def update_ticket_status(complaint_id, status):
    resolved_at = "CURRENT_TIMESTAMP" if status == "Resolved" else "NULL"
    with get_connection() as conn:
        conn.execute(f"""
            UPDATE complaints
            SET status = ?, resolved_at = {resolved_at}
            WHERE complaint_id = ?
        """, (status, complaint_id))


def enroll_student(user_id, course_id):
    try:
        with get_connection() as conn:
            course = conn.execute(
                "SELECT fee FROM courses WHERE course_id = ?",
                (course_id,)
            ).fetchone()
            if course is None:
                return False, "Course not found."

            conn.execute("""
                INSERT INTO enrollments (user_id, course_id)
                VALUES (?, ?)
            """, (user_id, course_id))
            conn.execute("""
                INSERT INTO payments (user_id, course_id, amount, payment_status)
                VALUES (?, ?, ?, 'Pending')
            """, (user_id, course_id, course["fee"]))
        return True, "Enrollment request submitted. Payment status is pending."
    except sqlite3.IntegrityError:
        return False, "You are already enrolled in this course."


def get_announcements():
    with get_connection() as conn:
        return conn.execute("""
            SELECT title, message, created_at
            FROM announcements
            ORDER BY created_at DESC, announcement_id DESC
        """).fetchall()


def add_announcement(title, message):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO announcements (title, message)
            VALUES (?, ?)
        """, (title.strip(), message.strip()))


def get_internships():
    with get_connection() as conn:
        return conn.execute("""
            SELECT role_title, company, work_mode, deadline, description
            FROM internships
            ORDER BY deadline
        """).fetchall()


def get_admin_course_stats():
    with get_connection() as conn:
        return conn.execute("""
            SELECT c.course_id, c.course_name, c.duration, c.fee,
                   COUNT(e.enrollment_id) AS enrollments,
                   SUM(CASE WHEN e.status = 'Active' THEN 1 ELSE 0 END) AS active
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.course_id
            GROUP BY c.course_id
            ORDER BY enrollments DESC, c.course_name
        """).fetchall()


def get_admin_student_roster():
    with get_connection() as conn:
        return conn.execute("""
            SELECT u.full_name, u.username, u.email,
                   COUNT(DISTINCT e.enrollment_id) AS courses,
                   COALESCE(ROUND(AVG(e.progress)), 0) AS avg_progress,
                   u.created_at
            FROM users u
            LEFT JOIN enrollments e ON e.user_id = u.user_id
            WHERE u.role = 'student'
            GROUP BY u.user_id
            ORDER BY u.full_name
        """).fetchall()


def get_admin_metrics():
    with get_connection() as conn:
        metrics = conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM users WHERE role = 'student') AS total_students,
                (SELECT COUNT(DISTINCT user_id) FROM enrollments WHERE status = 'Active') AS active_students,
                (SELECT COUNT(*) FROM enrollments) AS total_enrollments,
                (SELECT COUNT(*) FROM complaints WHERE status NOT IN ('Resolved', 'Closed')) AS pending_tickets,
                (SELECT COUNT(*) FROM complaints WHERE status = 'Resolved') AS resolved_tickets,
                (SELECT COUNT(*) FROM complaints WHERE priority = 'High' AND status NOT IN ('Resolved', 'Closed')) AS high_priority,
                (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status = 'Paid') AS paid_revenue,
                (SELECT COUNT(*) FROM payments WHERE payment_status = 'Pending') AS pending_payments,
                (SELECT COALESCE(AVG(julianday(resolved_at) - julianday(created_at)), 0)
                 FROM complaints WHERE resolved_at IS NOT NULL) AS avg_resolution_days
        """).fetchone()
        common_issues = conn.execute("""
            SELECT category, COUNT(*) AS total
            FROM complaints
            GROUP BY category
            ORDER BY total DESC, category
            LIMIT 5
        """).fetchall()
    return dict(metrics), common_issues
