# NEXORA 2026

AI-powered student support, academy management, and complaint resolution prototype for the NEXORA 2026 Tech Innovation Hackathon.

## Problem

Students use different channels for enrollment, course access, payments, schedules, certificates, and technical issues. Support teams then manually categorize, prioritize, route, and track those requests. NEXORA brings student services and academy support into one portal.

## Solution

NEXORA provides separate student and admin sign-in, an individual student dashboard, course enrollment, learning progress and resources, payment status, class schedules, certificate and internship listings, academy announcements, and a trackable support-request workflow. Student requests are classified by topic and urgency, routed to a suggested department, and assigned a suggested response. Admins can review and update request status and see operational metrics.

## Features

- Student registration and role-specific student/admin login.
- Student profile, enrolled courses, learning progress and attendance, schedule, resources, payments, certificates, internships, announcements, and support history in one dashboard.
- Course catalogue and enrollment requests; fees are recorded as pending payments.
- Natural-language support request submission with category, priority, department, and suggested response.
- Ticket status tracking: Open, In Progress, Resolved, and Closed.
- Admin metrics for students, active enrollments, payments, ticket status, priority, resolution time, course enrollment, and common issues.
- Admin ticket management, student roster, course creation, and announcement publishing.
- Demo records are created idempotently when the SQLite database is initialized.

## Architecture

- `app.py`: Streamlit UI, role-specific navigation, student workflows, and academy/admin views.
- `database.py`: SQLite schema, demo seed data, authentication, and persistence/query functions.
- `support_ai.py`: local request classification, urgency detection, routing, and suggested responses.
- `.streamlit/config.toml`: dark, high-contrast theme for readable course and dashboard panels.
- `nexora.db`: generated local SQLite data store; it is not included in the source ZIP.

## Modules

- Authentication and roles: student registration, password verification, and separate student/admin access.
- Student academy portal: profile, course enrollment, progress and attendance, schedule, resources, payments, certificates, internships, announcements, and support history.
- AI student support: request intake, category and urgency classification, department routing, suggested response, and ticket creation.
- Admin operations: academy metrics, course and student overviews, ticket status management, course creation, and announcement publishing.
- Persistence: SQLite tables and query functions for users, courses, enrollments, payments, services, announcements, and complaints.

## Implementation details

- Streamlit reruns render the role-appropriate navigation and dashboard from the authenticated session state.
- SQLite initialization creates missing tables, migrates the enrollment table to include attendance, and inserts demo content idempotently.
- Passwords are salted and derived using PBKDF2-HMAC-SHA256; only the salt and derived hash are stored.
- Course enrollment writes the enrollment and corresponding pending payment in one database transaction.
- Support triage runs locally using intent-term scoring and urgency rules; ticket analysis and status are persisted in SQLite.
- Admin metrics are calculated from live student, enrollment, payment, and complaint records.

## Technology stack

- Python 3.13 (Python 3.10 or newer recommended)
- Streamlit
- SQLite
- PBKDF2-HMAC-SHA256 password hashing with per-account salts
- Python standard library for local support-intent classification

## AI approach and limitations

The current hackathon prototype uses a deterministic local intent classifier. It scores terms for payment/enrollment, course/technical support, certificate/internship, and schedule/attendance topics; it separately detects urgency phrases and routes each request to a department. This makes the demo self-contained and avoids sending student information to an external service. It is not a trained language model and may misclassify ambiguous wording. Human admins should review triage and make final decisions. A hosted language model, multilingual support, sentiment analysis, duplicate detection, and automatic escalation are future improvements.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The app creates `nexora.db` beside `app.py` on first run and seeds demo accounts and sample academy records. Keep the SQLite file backed up if you want to preserve local changes.

## Demo accounts

- Student: `student01` / `Student@123`
- Admin Krishna: `admin` / `Admin@123`
- Admin Arsha: `admin2` / `Admin@123`
- The student login page shows the seeded roster and usernames.

These are demonstration credentials. Replace them and configure proper secrets and account provisioning before any real deployment.

## Usage

1. Open the app and sign in through the Student Login or Admin Login tab.
2. A student can enroll in a course, review services, or submit a natural-language request from Support center.
3. The support result includes a ticket ID, triage category, priority, department, and suggested response.
4. An admin can review tickets, change their status, inspect academy metrics and student/course data, add courses, and publish announcements.

## Verification

The two problem-statement examples are supported by the local classifier:

- Payment made but enrollment missing -> Payment / Enrollment, High, Accounts / Admissions.
- Cannot access a class recording -> Course / Technical Support, Medium, Technical / Course Support.

Run syntax checks with:

```powershell
python -m py_compile app.py database.py support_ai.py
```

## Deployment

The prototype currently runs locally at the Streamlit URL printed by `streamlit run app.py`. To publish it, push the source files to a GitHub repository and create a Streamlit Community Cloud app with `app.py` as the entry point and `requirements.txt` as dependencies. This workspace does not have deployment credentials or a connected repository, so a public deployed URL has not been created. SQLite storage on hosted/container platforms may be ephemeral; use a managed persistent database before relying on hosted data.

## Future scope

- Connect a hosted AI model with privacy controls and human-review safeguards.
- Add persistent hosted storage, role/permission administration, and password reset.
- Add attendance records, payment reconciliation, certificate downloads, and verified internship application links.
- Add sentiment and duplicate detection, escalation policies, multilingual requests, satisfaction feedback, and trend forecasting.
- Add automated deployment and end-to-end tests.