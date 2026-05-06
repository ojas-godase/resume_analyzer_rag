from graph.workflow import graph

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

result = graph.invoke({
    "pdf_path": "sample_resume.pdf",
    "job_description": jd
})


print("\nATS Score:\n", result.get("ats_score"))

print("\nResume Skills:\n", result.get("skills"))

print("\nJD Skills:\n", result.get("jd_skills"))
print("\nJD Qualifications:\n", result.get("jd_qualifications"))
print("\nJD Responsibilities:\n", result.get("jd_responsibilities"))

print("\nMatched Skills:\n", result.get("matched_skills"))
print("\nMissing Skills:\n", result.get("missing_skills"))
print("\nSkill Match Score:\n", result.get("skill_match_score"))


print("\n================= IMPROVEMENTS =================\n")

for item in result.get("improved_bullets", []):
    print("ORIGINAL:", item.get("original"))
    print("IMPROVED:", item.get("improved"))
    print("-" * 50)


print("\n================= GENERATED RESUME =================\n")

print(result.get("generated_resume"))


print("\n================= FINAL ANALYSIS =================\n")

print("Summary:\n", result.get("summary"))
print("\nSuggestions:\n")

for s in result.get("suggestions", []):
    print("-", s)

print("\n=========== SECTION IMPROVEMENTS ===========\n")

sections = result.get("section_improvements", {})

for k, v in sections.items():
    print(k.upper(), ":\n", v, "\n")


print("\n=========== BEFORE vs AFTER ===========\n")

for item in result.get("improvement_comparisons", []):
    print("ORIGINAL:", item["original"])
    print("IMPROVED:", item["improved"])
    print("REASON:", item["reason"])
    print("-" * 50)