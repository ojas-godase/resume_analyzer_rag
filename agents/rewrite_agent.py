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
Do NOT include explanations or markdown.

FORMAT:
{{
"improvements": [
    {{
        "original": "...",
        "improved": "..."
    }}
]
}}

Resume:
{resume}

Missing Skills:
{missing_skills}

Retrieved ATS / Resume Context:
{rag_context}

Tasks:

1. Identify 5–8 weak or generic bullet points

2. Rewrite them using:
   - Strong action verbs
   - Better clarity
   - Industry-relevant keywords

3. Align improvements with missing skills where possible

4. Use retrieved ATS/resume context when relevant

Rules:
- Do NOT invent unrealistic metrics
- Keep improvements realistic
- Focus on ATS optimization and stronger impact
""")

def rewrite_agent(state):

    resume = state.get("resume_text", "")

    missing = ", ".join(
        state.get("missing_skills", [])
    )

    rag_context = state.get("rag_context", [])

    # convert list -> readable string
    if isinstance(rag_context, list):
        rag_context = "\n".join(rag_context)

    formatted_prompt = prompt.format(
        resume=resume,
        missing_skills=missing,
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

    improvements = data.get("improvements", [])

    structured = []

    for item in improvements:

        if not item:
            continue

        original = item.get("original")
        improved = item.get("improved")

        # skip incomplete entries
        if not original or not improved:
            continue

        structured.append({
            "original": original.strip(),
            "improved": improved.strip(),
            "reason": (
                "Stronger action verbs, clearer impact, "
                "better ATS optimization, and alignment "
                "with job requirements"
            )
        })

    return {
        "improved_bullets": improvements if improvements else [],
        "improvement_comparisons": structured if structured else []
    }