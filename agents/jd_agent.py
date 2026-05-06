import json
import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)


prompt = PromptTemplate.from_template("""
You are an expert recruiter.

Extract structured information from the following job description.

Job Description:
{jd}

Return ONLY valid JSON in the format:

{{
 "skills": [
   {{"name": "...", "weight": 1}},
   {{"name": "...", "weight": 2}},
   {{"name": "...", "weight": 3}}
 ],
 "qualifications": [],
 "responsibilities": []
}}

Skill weight meaning:
3 = critical skill
2 = important skill
1 = optional or nice-to-have skill

Rules:
- Extract ONLY concrete technical skills (e.g., Python, Docker, XGBoost, NLP)
- DO NOT return phrases like "experience with", "knowledge of"
- Split combined skills into atomic ones
- Keep skill names SHORT (1–3 words max)
- Do not include explanations
""")


def normalize_and_split(skill_text):

    skill_text = skill_text.lower()

    # remove noise phrases
    skill_text = re.sub(
        r"experience with|hands[- ]on experience with|experience in|familiarity with|understanding of|knowledge of",
        "",
        skill_text
    )

    # remove "such as ..."
    skill_text = re.sub(r"such as.*", "", skill_text)

    # split into parts
    parts = re.split(r",|and|or", skill_text)

    cleaned = []

    for p in parts:
        p = p.strip()

        if not p or len(p) < 2:
            continue

        if len(p.split()) > 4:
            continue

        cleaned.append(p)

    return cleaned


def jd_agent(state):

    if state.get("jd_skills"):
        return {}

    jd_text = state.get("job_description", "")

    prompt_value = prompt.invoke({"jd": jd_text})

    response = llm.invoke(prompt_value)

    raw = response.content.strip()
    cleaned = raw.replace("```json", "").replace("```", "").strip()

    data = {}

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            data = json.loads(match.group(0))
        except:
            data = {}

    skills = data.get("skills", [])
    qualifications = data.get("qualifications", [])
    responsibilities = data.get("responsibilities", [])

    jd_skills = []
    jd_weights = {}

    for s in skills:

        raw_name = s.get("name", "")
        weight = s.get("weight", 1)

        if not raw_name:
            continue

        # 🔥 CLEAN + SPLIT HERE
        split_skills = normalize_and_split(raw_name)

        for skill in split_skills:

            if skill not in jd_skills:
                jd_skills.append(skill)
                jd_weights[skill] = weight

    return {
        "jd_skills": jd_skills,
        "jd_skill_weights": jd_weights,
        "jd_qualifications": qualifications,
        "jd_responsibilities": responsibilities
    }