import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from graph.workflow import graph
from agents.ranking_agent import ranking_agent
from agents.jd_agent import jd_agent


jd = """
Machine Learning Engineer

Requirements:
Python, PyTorch, Docker

Qualifications:
Masters in Computer Science
2+ years experience in machine learning

Responsibilities:
Build ML pipelines
Deploy models
Work with data engineering teams
"""


resume_folder = "resumes"


# ----- RUN JD AGENT ONCE -----

jd_state = {"job_description": jd}

jd_result = jd_agent(jd_state)

jd_skills = jd_result["jd_skills"]
jd_qualifications = jd_result["jd_qualifications"]
jd_responsibilities = jd_result["jd_responsibilities"]

print("JD Extraction Completed:")

# ----- PROCESS RESUMES -----

def process_resume(file):
    print(f"Processing {file}...")
    path = os.path.join(resume_folder, file)
    print(f"Invoking graph for {file} with path {path}...")
    result = graph.invoke({
        "pdf_path": path,
        "job_description": jd,
        "jd_skills": jd_skills,
        "jd_qualifications": jd_qualifications,
        "jd_responsibilities": jd_responsibilities
    })

    result["resume_name"] = file
    print(f"Completed processing {file}. ATS Score: {result['ats_score']}, Skill Match Score: {result['skill_match_score']}")
    return result


files = [f for f in os.listdir(resume_folder) if f.endswith(".pdf")]

results = []

print("\nProcessing resumes in parallel...\n")

with ThreadPoolExecutor(max_workers=6) as executor:

    futures = {executor.submit(process_resume, f): f for f in files}

    print("All resumes submitted for processing. Waiting for results...\n")

    for future in as_completed(futures):

        file = futures[future]

        try:
            res = future.result()
            results.append(res)

            print(f"Finished processing {file}")

        except Exception as e:
            print(f"Error processing {file}: {e}")


# ----- RANK CANDIDATES -----

ranked = ranking_agent(results)


print("\n=========== FINAL CANDIDATE RANKING ===========\n")

for i, r in enumerate(ranked, 1):

    print(f"Rank {i}: {r['resume']}")
    print(f"Skill Match: {r['skill_match']}")
    print(f"Semantic Similarity: {r['semantic_similarity']}")
    print(f"ATS Score: {r['ats_score']}")
    print(f"Final Score: {r['final_score']}\n")