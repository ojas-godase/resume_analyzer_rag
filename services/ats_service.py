import re


SECTION_PATTERNS = {
    "education": r"^\s*(education|academic background)",
    "experience": r"^\s*(work experience|professional experience|employment history|experience)",
    "projects": r"^\s*(projects|personal projects)",
    "skills": r"^\s*(skills|technical skills|key skills)",
    "certifications": r"^\s*(certifications|licenses)",
    "summary": r"^\s*(summary|objective|professional summary|career objective)"
}


def detect_sections(text):

    sections = {}

    for section, pattern in SECTION_PATTERNS.items():
        sections[section] = bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))

    return sections


def detect_contact_info(text):

    email = bool(re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text))
    phone = bool(re.search(r"\b\+?\d{10,13}\b", text))
    linkedin = bool(re.search(r"linkedin\.com", text.lower()))

    return email, phone, linkedin


def bullet_count(text):

    bullets = re.findall(r"(?m)^\s*[\-\•\▪\▶\●]\s+", text)
    return len(bullets)


def keyword_match_score(resume_text, jd_skills):

    if not jd_skills:
        return 0

    resume_text = resume_text.lower()

    matched = 0

    for skill in jd_skills:
        if skill.lower() in resume_text:
            matched += 1

    return matched / len(jd_skills)


def compute_ats_score(text, jd_skills=None):

    sections = detect_sections(text)

    score = 0

    # Section scoring
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

    # Contact info
    email, phone, linkedin = detect_contact_info(text)

    if email:
        score += 1

    if phone:
        score += 1

    if linkedin:
        score += 0.5

    if bullet_count(text) >= 5:
        score += 0.5

    keyword_score = keyword_match_score(text, jd_skills)
    score += keyword_score * 2  # weight

    max_score = 13  # updated

    ats_score = int((score / max_score) * 100)
    ats_score = min(ats_score, 100)

    return ats_score, sections