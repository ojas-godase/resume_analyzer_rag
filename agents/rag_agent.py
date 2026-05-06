from services.rag_service import retrieve_context


def rag_agent(state):

    resume_text = state["resume_text"]
    skills = state["skills"]
    ats = state["ats_score"]

    query = f"""
    Resume: {resume_text}

    Skills: {' '.join(skills)}

    ATS Score: {ats}
    """

    context = retrieve_context(query)

    return {"rag_context": context}