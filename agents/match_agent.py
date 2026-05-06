from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def normalize_skill(skill):

    skill = skill.lower().strip()

    # remove noisy phrases
    for phrase in [
        "experience with",
        "hands-on experience with",
        "experience in",
        "familiarity with",
        "understanding of"
    ]:
        skill = skill.replace(phrase, "")

    # remove trailing junk like "such as ..."
    if "such as" in skill:
        skill = skill.split("such as")[0]

    return skill.strip()


def match_agent(state):

    resume_skills = state.get("skills", [])
    jd_skills = state.get("jd_skills", [])
    weights = state.get("jd_skill_weights", {})

    resume_text = state.get("resume_text", "")
    jd_text = state.get("job_description", "")


    resume_skills = list(set([normalize_skill(s) for s in resume_skills if s]))
    jd_skills = list(set([normalize_skill(s) for s in jd_skills if s]))

    # normalize weights keys
    weights = {normalize_skill(k): v for k, v in weights.items()}

    matched = []
    missing = []


    if resume_skills and jd_skills:

        resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
        jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

        cosine_scores = util.cos_sim(jd_embeddings, resume_embeddings)

        threshold = 0.6

        for i, jd_skill in enumerate(jd_skills):

            best_score = cosine_scores[i].max().item()

            if best_score >= threshold:
                matched.append(jd_skill)
            else:
                missing.append(jd_skill)


        if weights:
            total_weight = sum(weights.values())
        else:
            total_weight = len(jd_skills)

        matched_weight = 0

        for skill in matched:
            matched_weight += weights.get(skill, 1)

        skill_score = round((matched_weight / total_weight) * 100, 2)

    else:

        missing = jd_skills
        skill_score = 0


    if resume_text and jd_text:

        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = model.encode(jd_text, convert_to_tensor=True)

        similarity = util.cos_sim(resume_embedding, jd_embedding).item()
        similarity_score = round(similarity * 100, 2)

    else:

        similarity_score = 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_score": skill_score,
        "resume_jd_similarity": similarity_score
    }