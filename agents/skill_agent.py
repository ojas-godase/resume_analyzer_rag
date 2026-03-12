from services.skill_service import extract_skills

def skill_agent(state):

    text = state["resume_text"]

    skills = extract_skills(text)

    return {"skills": skills}