from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
import json
import re

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.2
)

prompt = PromptTemplate.from_template("""
You MUST return ONLY valid JSON.
If you include anything else, the output will be rejected.

FORMAT:
{{
"summary": "...",
"suggestions": ["...", "..."],
"section_improvements": {{
    "summary_section": "...",
    "skills_section": "...",
    "projects_section": "..."
}}
}}

Resume:
{resume}

ATS Score:
{ats}

Skill Match Score:
{match_score}

Retrieved ATS / Resume Context:
{rag_context}

Tasks:
1. Write a professional summary (100 words)

2. Give exactly 10 actionable improvements

3. Give section-wise improvements:
   - Summary → clarity and positioning
   - Skills → missing or weak skills
   - Projects → bullet strength and impact

Rules:
- NO generic advice like "do courses"
- MUST refer to the actual resume
- MUST use the retrieved context when relevant
""")

def critic_agent(state):

    rag_context = state.get("rag_context", [])

    if isinstance(rag_context, list):
        rag_context = "\n".join(rag_context)

    formatted_prompt = prompt.format(
        resume=state.get("generated_resume") or state.get("resume_text"),
        ats=state.get("ats_score", 0),
        match_score=state.get("skill_match_score", 0),
        rag_context=rag_context
    )

    response = llm.invoke(formatted_prompt)

    raw = response.content.strip()

    cleaned = (
        raw.replace("```json", "")
           .replace("```", "")
           .strip()
    )

    data = {}

    try:
        data = json.loads(cleaned)

    except Exception:

        match = re.search(r"\{[\s\S]*\}", cleaned)

        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                data = {}

    if not data:
        return {
            "summary": raw,
            "suggestions": [],
            "section_improvements": {
                "summary_section": "Improve clarity and make it more role-specific.",
                "skills_section": "Add missing skills like Docker and prioritize relevant ones.",
                "projects_section": "Strengthen bullet points with clearer impact and keywords."
            }
        }

    section_data = data.get("section_improvements")

    if not section_data:
        section_data = {
            "summary_section": "Improve clarity and make it more role-specific.",
            "skills_section": "Add missing skills like Docker and prioritize relevant ones.",
            "projects_section": "Strengthen bullet points with clearer impact and keywords."
        }

    return {
        "summary": data.get("summary"),
        "suggestions": data.get("suggestions", []),
        "section_improvements": section_data
    }