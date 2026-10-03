import re


TRIAGE_RULES = [
    {
        "category": "Payment / Enrollment",
        "department": "Accounts / Admissions",
        "terms": (
            "payment", "paid", "fee", "refund", "transaction", "billing",
            "enrollment", "enrolment", "enroll", "admission", "charge",
        ),
        "response": "I’ll check the payment and enrollment details. Keep your transaction reference available for the accounts team.",
    },
    {
        "category": "Course / Technical Support",
        "department": "Technical / Course Support",
        "terms": (
            "access", "recording", "login", "password", "error", "video",
            "course", "class", "platform", "lesson", "resource", "link",
        ),
        "response": "I’ll route this to course support. Include the course name and class date so the team can investigate quickly.",
    },
    {
        "category": "Certificate / Internship",
        "department": "Career Services",
        "terms": (
            "certificate", "certification", "internship", "placement", "career",
        ),
        "response": "I’ll route this to Career Services to review your certificate or opportunity request.",
    },
    {
        "category": "Schedule / Attendance",
        "department": "Academic Operations",
        "terms": (
            "schedule", "timetable", "attendance", "absent", "session", "timing",
        ),
        "response": "I’ll route this to Academic Operations. Share the course and session date if they are not in your request.",
    },
]


URGENT_TERMS = (
    "urgent", "asap", "immediately", "today", "tomorrow", "charged twice",
    "locked out", "cannot attend", "can't attend", "deadline",
)


def classify_request(text):
    normalized = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    words = set(normalized.split())

    scores = []
    for rule in TRIAGE_RULES:
        score = sum(
            2 if " " in term and term in normalized else 1 if term in words else 0
            for term in rule["terms"]
        )
        scores.append((score, rule))

    score, match = max(scores, key=lambda item: item[0])
    if score == 0:
        match = {
            "category": "General Student Support",
            "department": "Student Support",
            "response": "Your request is logged for the student support team. They’ll follow up with you through this ticket.",
        }

    high_priority = any(term in normalized for term in URGENT_TERMS)
    if match["category"] == "Payment / Enrollment" and any(
        phrase in normalized
        for phrase in ("not showing", "not reflected", "not enrolled", "still missing")
    ):
        high_priority = True

    return {
        "category": match["category"],
        "priority": "High" if high_priority else "Medium",
        "department": match["department"],
        "response": match["response"],
    }
