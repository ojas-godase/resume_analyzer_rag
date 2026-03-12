import re
import pandas as pd
from sentence_transformers import SentenceTransformer, util

skills_df = pd.read_csv("knowledge/skills_dataset.csv")

SKILLS = (
    skills_df["Skill"]
    .dropna()
    .astype(str)
    .str.lower()
    .str.strip()
    .unique()
    .tolist()
)

SKILLS = sorted(SKILLS, key=len, reverse=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

skill_embeddings = model.encode(SKILLS, convert_to_tensor=True)


def extract_skills_dictionary(text):

    text = text.lower()

    found = set()

    for skill in SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.add(skill)

    return list(found)


def extract_skills_semantic(text, threshold=0.45):

    text_embedding = model.encode(text, convert_to_tensor=True)

    scores = util.cos_sim(text_embedding, skill_embeddings)[0]

    found = []

    for i, score in enumerate(scores):
        if score >= threshold:
            found.append(SKILLS[i])

    return found


def extract_skills(text):

    dict_skills = extract_skills_dictionary(text)

    semantic_skills = extract_skills_semantic(text)

    return sorted(list(set(dict_skills + semantic_skills)))