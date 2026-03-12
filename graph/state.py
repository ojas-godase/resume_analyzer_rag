from typing import Dict, TypedDict, List

class ResumeState(TypedDict, total=False):

    pdf_path: str

    resume_text: str

    skills: List[str]

    
    ats_score: int
    sections: Dict[str, bool]

    rag_context: str

    summary: str

    suggestions: List[str]

    job_role: str