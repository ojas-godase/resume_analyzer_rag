from typing import Dict, TypedDict, List


class ResumeState(TypedDict, total=False):

    pdf_path: str
    resume_name: str

    resume_text: str

    skills: List[str]

    ats_score: int
    sections: Dict[str, bool]

    rag_context: List[str]

    analysis: str

    # JD extraction fields
    job_description: str
    jd_skills: List[str]
    jd_qualifications: List[str]
    jd_responsibilities: List[str]

    # Matching results
    matched_skills: List[str]
    missing_skills: List[str]
    skill_match_score: float
    resume_jd_similarity: float

    # LLM output
    summary: str
    suggestions: List[str]
    job_role: str

    improved_bullets: List[Dict[str, str]]   # [{"original": "...", "improved": "..."}]
    rewritten_resume: str
    generated_resume: str
    section_improvements: dict
    improvement_comparisons: list