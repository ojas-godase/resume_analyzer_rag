from services.pdf_service import extract_text

def parser_agent(state):

    pdf_path = state["pdf_path"]

    text = extract_text(pdf_path)

    return {"resume_text": text}