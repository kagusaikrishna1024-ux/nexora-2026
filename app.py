
import re
import streamlit as st

from database import (
    DEMO_STUDENTS,
    add_announcement,
    add_course,
    create_support_ticket,
    enroll_student,
    get_admin_course_stats,
    get_admin_metrics,
    get_admin_student_roster,
    get_all_tickets,
    get_announcements,
    initialize_database,
    get_courses,
    get_internships,
    register_student,
    authenticate_user,
    get_student_certificates,
    get_student_courses,
    get_student_payments,
    get_student_resources,
    get_student_schedule,
    get_student_tickets,
    update_ticket_status,
)
from support_ai import classify_request

st.set_page_config(
    page_title="NEXORA AI",
    page_icon="🎓",
    layout="wide"
)

initialize_database()

st.markdown("""
<style>
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #182427;
    border-color: #405458;
    border-radius: 8px;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-testid="stRadioOption"] {
    width: 100%;
    box-sizing: border-box;
    min-height: 2.6rem;
    margin: 0.25rem 0;
    padding: 0.4rem 0.7rem;
    border: 1px solid #31474a;
    border-radius: 11px;
    background: #182427;
    transition: background-color 140ms ease, border-color 140ms ease;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stRadio"]) {
    width: 100%;
}
[data-testid="stSidebar"] [data-testid="stRadio"] {
    width: 100%;
}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
    width: 100%;
    align-items: stretch;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-testid="stRadioOption"]:hover {
    border-color: #65d9c8;
    background: #203235;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-testid="stRadioOption"]:has(input:checked) {
    border-color: #65d9c8;
    background: #075f57;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-testid="stRadioOption"] > div > div:first-child {
    display: none;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-testid="stRadioOption"] p {
    color: #dce8e6;
    font-weight: 550;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-testid="stRadioOption"][data-selected="true"] p {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


if "user" not in st.session_state:
    st.session_state.user = None


def logout():
    st.session_state.user = None
    st.rerun()


def show_login_form(role):
    role_label = role.title()
    st.subheader(f"{role_label} sign in")

    with st.form(f"{role}_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_clicked = st.form_submit_button(
            f"Sign in as {role_label}",
            use_container_width=True
        )

    if login_clicked:
        if not username.strip() or not password:
            st.error("Enter both username and password.")
        else:
            user = authenticate_user(username, password)

            if user and user["role"] == role:
                st.session_state.user = user
                st.rerun()
            else:
                st.error(f"Invalid {role} username or password.")

    if role == "student":
        with st.expander("Seeded student accounts", expanded=True):
            st.caption("Password for all seeded students: Student@123")
            st.table([
                {"Name": name, "Username": username}
                for name, username in DEMO_STUDENTS
            ])
    else:
        st.caption(
            "Krishna: admin / Admin@123 · Arsha: admin2 / Admin@123"
        )


def show_registration_form():
    st.subheader("Create student account")

    courses = get_courses()
    course_names = ["No course selected"] + [
        course["course_name"] for course in courses
    ]

    with st.form("registration_form"):
        full_name = st.text_input("Full name")
        new_username = st.text_input("Choose username")
        email = st.text_input("Email address")
        new_password = st.text_input("Create password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        selected_course = st.selectbox("Select course", course_names)
        register_clicked = st.form_submit_button("Register")

    if register_clicked:
        if not all([
            full_name.strip(), new_username.strip(), email.strip(),
            new_password, confirm_password
        ]):
            st.error("Please fill in all required fields.")
        elif not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", new_username.strip()):
            st.error("Username must be 3–30 characters using letters, numbers, underscores, dots or hyphens.")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            st.error("Enter a valid email address.")
        elif len(new_password) < 8:
            st.error("Password must contain at least 8 characters.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            course_id = next(
                (course["course_id"] for course in courses
                 if course["course_name"] == selected_course),
                None,
            )
            success, message = register_student(
                full_name, new_username, email, new_password, course_id
            )
            if success:
                st.success(message)
                st.info("Open the Student Login tab to sign in.")
            else:
                st.error(message)


def show_login():
    st.title("🎓 NEXORA AI")
    st.subheader("Student Support & Academy Management")
    st.write("One platform for students, courses and support.")

    student_tab, admin_tab, register_tab = st.tabs(
        ["Student Login", "Admin Login", "Student Registration"]
    )

    with student_tab:
        show_login_form("student")

    with admin_tab:
        show_login_form("admin")

    with register_tab:
        show_registration_form()


def show_student_dashboard(user):
    st.title("Student dashboard")
    st.write(f"Welcome, **{user['full_name']}**!")
    courses = get_student_courses(user["user_id"])
    tickets = get_student_tickets(user["user_id"])
    open_tickets = sum(ticket["status"] not in ("Resolved", "Closed") for ticket in tickets)
    average_progress = round(
        sum(course["progress"] for course in courses) / len(courses)
    ) if courses else 0
    average_attendance = round(
        sum(course["attendance_percent"] for course in courses) / len(courses)
    ) if courses else 0

    first_row = st.columns(4)
    first_row[0].metric("Enrolled courses", len(courses))
    first_row[1].metric("Average progress", f"{average_progress}%")
    first_row[2].metric("Attendance", f"{average_attendance}%")
    first_row[3].metric("Open support requests", open_tickets)

    profile_tab, learning_tab, services_tab, support_tab = st.tabs([
        "Profile & overview", "Learning", "Academy services", "AI support"
    ])

    with profile_tab:
        st.subheader("Student profile")
        profile = st.columns(3)
        profile[0].metric("Full name", user["full_name"])
        profile[1].metric("Username", user["username"])
        profile[2].metric("Student ID", user["user_id"])
        st.caption(f"Email: {user['email']} · Account type: {user['role'].title()}")

        st.subheader("Course and progress snapshot")
        if not courses:
            st.info("You are not enrolled in a course yet. Open Learning to browse the catalogue.")
        else:
            for course in courses:
                with st.container(border=True):
                    st.markdown(f"**{course['course_name']}** · {course['duration']}")
                    st.progress(min(100, max(0, int(course["progress"]))) / 100)
                    st.caption(
                        f"Progress {course['progress']}% · Attendance "
                        f"{course['attendance_percent']}% · {course['status']} enrollment · "
                        f"Enrolled {course['enrollment_date']}"
                    )

        st.subheader("Upcoming classes and announcements")
        left, right = st.columns(2)
        with left:
            schedule = get_student_schedule(user["user_id"])
            if schedule:
                for meeting in schedule[:3]:
                    st.write(f"**{meeting['course_name']}** · {meeting['title']}")
                    st.caption(f"{meeting['starts_at']} · {meeting['instructor']} · {meeting['meeting_mode']}")
            else:
                st.info("No upcoming classes for your courses.")
        with right:
            for announcement in get_announcements()[:3]:
                st.write(f"**{announcement['title']}**")
                st.caption(announcement["message"])

    with learning_tab:
        show_student_learning(user)

    with services_tab:
        show_student_services(user)

    with support_tab:
        show_student_support(user)


def show_student_learning(user):
    st.title("My learning")
    courses_tab, catalogue_tab = st.tabs(["My courses", "Course catalogue"])

    with courses_tab:
        enrolled = get_student_courses(user["user_id"])
        if not enrolled:
            st.info("You are not enrolled in a course yet.")
        for course in enrolled:
            with st.container(border=True):
                st.subheader(course["course_name"])
                st.write(course["description"])
                st.caption(f"{course['duration']} · Enrollment: {course['enrollment_date']} · {course['status']}")
                st.progress(min(100, max(0, int(course["progress"]))) / 100)
                st.caption(
                    f"Learning progress: {course['progress']}% · "
                    f"Attendance: {course['attendance_percent']}%"
                )

    with catalogue_tab:
        st.write("Choose a course to create an enrollment. The course fee will appear as pending in Payments.")
        enrolled_ids = {course["course_id"] for course in get_student_courses(user["user_id"])}
        for course in get_courses():
            with st.container(border=True):
                st.subheader(course["course_name"])
                st.write(course["description"])
                st.caption(f"{course['duration']} · ₹{course['fee']:,.0f}")
                if course["course_id"] in enrolled_ids:
                    st.button("Enrolled", key=f"enrolled_{course['course_id']}", disabled=True)
                elif st.button("Enroll", key=f"enroll_{course['course_id']}"):
                    success, message = enroll_student(user["user_id"], course["course_id"])
                    st.success(message) if success else st.warning(message)
                    if success:
                        st.rerun()


def show_student_support(user):
    st.title("AI student support")
    st.write("Describe the issue in your own words. The assistant classifies it, suggests next steps, and creates a trackable request.")
    st.caption("Prototype triage runs locally using intent and urgency rules; it does not send student information to an external AI service.")

    with st.form("support_request_form"):
        description = st.text_area(
            "What do you need help with?",
            placeholder="For example: I paid for Data Analytics yesterday, but my enrollment is still not showing.",
            max_chars=1200,
        )
        submitted = st.form_submit_button("Analyze and submit request")

    if submitted:
        if len(description.strip()) < 10:
            st.error("Please describe the issue in at least 10 characters.")
        else:
            triage = classify_request(description)
            ticket_id = create_support_ticket(user["user_id"], description, triage)
            st.success(f"Request NX-{ticket_id:04d} submitted")
            analysis = st.columns(3)
            analysis[0].metric("Category", triage["category"])
            analysis[1].metric("Priority", triage["priority"])
            analysis[2].metric("Routed to", triage["department"])
            st.info(triage["response"])

    st.divider()
    st.subheader("My support history")
    tickets = get_student_tickets(user["user_id"])
    if not tickets:
        st.info("Your support requests will appear here.")
    for ticket in tickets:
        with st.container(border=True):
            st.markdown(f"**Request NX-{ticket['complaint_id']:04d} · {ticket['status']}**")
            st.caption(f"{ticket['category']} · {ticket['priority']} priority · {ticket['department']} · {ticket['created_at']}")
            st.write(ticket["description"])
            if ticket["ai_response"]:
                st.info(ticket["ai_response"])


def show_student_services(user):
    st.title("Academy services")
    schedule_tab, payments_tab, certificates_tab, internships_tab, updates_tab = st.tabs(
        ["Classes and resources", "Payments", "Certificates", "Internships", "Announcements"]
    )

    with schedule_tab:
        st.subheader("Class schedule")
        schedule = get_student_schedule(user["user_id"])
        if schedule:
            st.table([{
                "Course": item["course_name"], "Class": item["title"],
                "Starts": item["starts_at"], "Instructor": item["instructor"],
                "Mode": item["meeting_mode"],
            } for item in schedule])
        else:
            st.info("No scheduled classes for your active enrollments.")
        st.subheader("Learning resources")
        resources = get_student_resources(user["user_id"])
        if resources:
            for resource in resources:
                st.markdown(f"[{resource['title']}]({resource['url']}) · {resource['course_name']} · {resource['resource_type']}")
        else:
            st.info("Enroll in a course to see its learning resources.")

    with payments_tab:
        payments = get_student_payments(user["user_id"])
        if payments:
            st.table([{
                "Course": item["course_name"], "Amount": f"₹{item['amount']:,.0f}",
                "Status": item["payment_status"], "Date": item["payment_date"],
            } for item in payments])
        else:
            st.info("No payment records yet.")

    with certificates_tab:
        certificates = get_student_certificates(user["user_id"])
        if certificates:
            st.table([{
                "Course": item["course_name"], "Certificate code": item["certificate_code"],
                "Issued": item["issued_at"],
            } for item in certificates])
        else:
            st.info("Certificates are listed here when a course is completed.")

    with internships_tab:
        for internship in get_internships():
            with st.container(border=True):
                st.markdown(f"**{internship['role_title']} · {internship['company']}**")
                st.caption(f"{internship['work_mode']} · Apply by {internship['deadline']}")
                st.write(internship["description"])

    with updates_tab:
        for announcement in get_announcements():
            with st.container(border=True):
                st.markdown(f"**{announcement['title']}**")
                st.write(announcement["message"])
                st.caption(announcement["created_at"])

def show_admin_dashboard(user):
    st.title("Academy operations")
    st.write(f"Welcome, **{user['full_name']}**!")
    metrics, issues = get_admin_metrics()

    first_row = st.columns(4)
    first_row[0].metric("Total students", metrics["total_students"])
    first_row[1].metric("Active students", metrics["active_students"])
    first_row[2].metric("Course enrollments", metrics["total_enrollments"])
    first_row[3].metric("Pending requests", metrics["pending_tickets"])
    second_row = st.columns(4)
    second_row[0].metric("Resolved requests", metrics["resolved_tickets"])
    second_row[1].metric("High priority", metrics["high_priority"])
    second_row[2].metric("Paid revenue", f"₹{metrics['paid_revenue']:,.0f}")
    second_row[3].metric("Pending payments", metrics["pending_payments"])
    st.caption(f"Average resolution time: {metrics['avg_resolution_days']:.1f} days")

    course_stats = get_admin_course_stats()
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.subheader("Course-wise enrollments")
        st.bar_chart({row["course_name"]: row["enrollments"] for row in course_stats})
    with chart_right:
        st.subheader("Common student issues")
        if issues:
            st.bar_chart({row["category"]: row["total"] for row in issues})
        else:
            st.info("Issue trends appear after students submit support requests.")

    if metrics["high_priority"]:
        st.warning(f"Management insight: {metrics['high_priority']} high-priority request(s) need attention.")
    elif metrics["pending_tickets"]:
        st.info("Management insight: No high-priority tickets are waiting; review the pending queue for routine follow-up.")
    else:
        st.success("Management insight: The support queue is clear.")


def show_admin_tickets():
    st.title("Support request queue")
    tickets = get_all_tickets()
    if not tickets:
        st.success("No support requests are waiting.")
        return

    for ticket in tickets:
        with st.container(border=True):
            st.markdown(f"**NX-{ticket['complaint_id']:04d} · {ticket['priority']} priority · {ticket['category']}**")
            st.caption(f"{ticket['full_name']} (@{ticket['username']}) · {ticket['department']} · {ticket['created_at']}")
            st.write(ticket["description"])
            if ticket["ai_response"]:
                st.info(ticket["ai_response"])
            with st.form(f"ticket_update_{ticket['complaint_id']}"):
                status_options = ["Open", "In Progress", "Resolved", "Closed"]
                current_status = ticket["status"] if ticket["status"] in status_options else "Open"
                selected_status = st.selectbox(
                    "Request status", status_options,
                    index=status_options.index(current_status),
                    key=f"ticket_status_{ticket['complaint_id']}",
                )
                save_status = st.form_submit_button("Save status")
            if save_status:
                update_ticket_status(ticket["complaint_id"], selected_status)
                st.success("Request status updated.")
                st.rerun()


def show_admin_students():
    st.title("Students and courses")
    roster = get_admin_student_roster()
    st.subheader("Student roster")
    st.table([{
        "Student": row["full_name"], "Username": row["username"],
        "Email": row["email"], "Courses": row["courses"],
        "Avg. progress": f"{row['avg_progress']}%", "Joined": row["created_at"],
    } for row in roster])

    st.subheader("Course performance")
    course_stats = get_admin_course_stats()
    st.table([{
        "Course": row["course_name"], "Enrollments": row["enrollments"],
        "Active": row["active"], "Duration": row["duration"],
        "Fee": f"₹{row['fee']:,.0f}",
    } for row in course_stats])

    with st.expander("Add a course"):
        with st.form("add_course_form"):
            name = st.text_input("Course name")
            description = st.text_area("Description")
            duration = st.text_input("Duration", placeholder="e.g. 8 weeks")
            fee = st.number_input("Fee (₹)", min_value=0.0, step=500.0)
            submitted = st.form_submit_button("Add course")
        if submitted:
            if not name.strip() or not duration.strip():
                st.error("Course name and duration are required.")
            else:
                success, message = add_course(name, description, duration, fee)
                st.success(message) if success else st.warning(message)
                if success:
                    st.rerun()


def show_admin_announcements():
    st.title("Academy announcements")
    with st.form("announcement_form"):
        title = st.text_input("Announcement title")
        message = st.text_area("Message")
        publish = st.form_submit_button("Publish announcement")
    if publish:
        if not title.strip() or not message.strip():
            st.error("Enter both a title and a message.")
        else:
            add_announcement(title, message)
            st.success("Announcement published.")
            st.rerun()

    st.subheader("Published announcements")
    for announcement in get_announcements():
        with st.container(border=True):
            st.markdown(f"**{announcement['title']}**")
            st.write(announcement["message"])
            st.caption(announcement["created_at"])


# ---------------- MAIN APP ----------------
if st.session_state.user is None:
    show_login()

else:
    user = st.session_state.user

    st.sidebar.title("🎓 NEXORA AI")
    st.sidebar.write(f"**{user['full_name']}**")
    st.sidebar.caption(f"Role: {user['role'].title()}")

    if user["role"] == "admin":
        page = st.sidebar.radio(
            "Navigation",
            ["Overview", "Support tickets", "Students & courses", "Announcements"]
        )
    else:
        page = st.sidebar.radio(
            "Navigation",
            ["Overview", "My learning", "Support center", "Academy services"]
        )

    if st.sidebar.button("Logout", use_container_width=True):
        logout()

    if page == "Overview" and user["role"] == "student":
        show_student_dashboard(user)
    elif page == "Overview" and user["role"] == "admin":
        show_admin_dashboard(user)
    elif page == "My learning":
        show_student_learning(user)
    elif page == "Support center":
        show_student_support(user)
    elif page == "Academy services":
        show_student_services(user)
    elif page == "Support tickets":
        show_admin_tickets()
    elif page == "Students & courses":
        show_admin_students()
    elif page == "Announcements":
        show_admin_announcements()
