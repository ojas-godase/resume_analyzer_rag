from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
import json
import re

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)

prompt = PromptTemplate.from_template("""
You MUST return ONLY valid JSON.
If you include anything else, the output will be rejected.

FORMAT:
{{"resume": "..." }}

Candidate Data:
{resume}

Skills:
{skills}

Job Description:
{jd}

Missing Skills:
{missing_skills}

Improved Bullet Points:
{improved_bullets}

Retrieved ATS / Resume Context:
{rag_context}

Rules:

- Use clean sections in this EXACT order:
  1. Summary
  2. Skills
  3. Projects
  4. Education
  5. Certifications

- DO NOT merge sections
- DO NOT repeat sections
- Keep formatting clean and separated

- Replace weak bullets with improved ones wherever applicable

- MUST include missing skills explicitly
  (especially from JD)

- Use retrieved ATS/resume context where relevant

- Include missing skills naturally
  Example: include "Docker"
  naturally in Skills or Projects

- Use bullet points

- DO NOT invent fake metrics

- If metrics are unknown,
  use qualitative impact

- MUST include missing skills explicitly in BOTH:
  1. Skills section
  2. At least one Project or Experience bullet

- Optimize for ATS readability
- Use strong action verbs
- Keep wording concise and professional

Return ONLY the resume text inside JSON.
Do NOT include explanations or extra text.
""")

def resume_draft_agent(state):

    improved = state.get("improved_bullets", [])

    improved_text = "\n".join([
        f"Original: {b.get('original')} -> Improved: {b.get('improved')}"
        for b in improved
    ])

    rag_context = state.get("rag_context", [])

    # convert list -> string
    if isinstance(rag_context, list):
        rag_context = "\n".join(rag_context)

    formatted_prompt = prompt.format(
        resume=state.get("resume_text", ""),
        skills=", ".join(state.get("skills", [])),
        jd=state.get("job_description", ""),
        missing_skills=", ".join(state.get("missing_skills", [])),
        improved_bullets=improved_text,
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

    resume_text = ""

    if isinstance(data, dict) and data.get("resume"):
        resume_text = data["resume"]

    else:

        match = re.search(
            r'"resume"\s*:\s*"([\s\S]*?)"',
            cleaned
        )

        if match:
            resume_text = match.group(1)

    if not resume_text:
        resume_text = raw

    return {
        "generated_resume": resume_text.strip()
    }