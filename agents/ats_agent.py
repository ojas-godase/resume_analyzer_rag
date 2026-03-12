from services.ats_service import compute_ats_score


def ats_agent(state):

    text = state["resume_text"]

    score, sections = compute_ats_score(text)

    return {
        "ats_score": score,
        "sections": sections
    }