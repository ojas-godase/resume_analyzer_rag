import re


SECTION_PATTERNS = {
    "education": r"\b(education|academic background)\b",
    "experience": r"\b(work experience|professional experience|employment history|experience)\b",
    "projects": r"\b(projects|personal projects)\b",
    "skills": r"\b(skills|technical skills|key skills)\b",
    "certifications": r"\b(certifications|licenses)\b",
    "summary": r"\b(summary|objective|professional summary|career objective)\b"
}


def detect_sections(text):

    text = text.lower()

    sections = {}

    for section, pattern in SECTION_PATTERNS.items():
        sections[section] = bool(re.search(pattern, text))

    return sections


def detect_contact_info(text):

    text = text.lower()

    email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text))
    phone = bool(re.search(r"\+?\d[\d\-\s]{8,}\d", text))
    linkedin = "linkedin" in text

    return email, phone, linkedin


def bullet_count(text):

    bullets = re.findall(r"[\n•\-▪▶●]\s*", text)

    return len(bullets)


def compute_ats_score(text):

    sections = detect_sections(text)

    score = 0

    if sections["education"]:
        score += 1

    if sections["experience"]:
        score += 2

    if sections["skills"]:
        score += 2

    if sections["projects"]:
        score += 1

    if sections["certifications"]:
        score += 1

    if sections["summary"]:
        score += 1

    email, phone, linkedin = detect_contact_info(text)

    if email:
        score += 1

    if phone:
        score += 1

    if linkedin:
        score += 0.5

    if bullet_count(text) >= 5:
        score += 0.5

    max_score = 11

    ats_score = int((score / max_score) * 100)

    ats_score = min(ats_score, 100)

    return ats_score, sections