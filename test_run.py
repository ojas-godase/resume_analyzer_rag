from graph.workflow import graph


result = graph.invoke({
    "pdf_path": "sample_resume.pdf"
})

print("\nATS Score:\n")
print(result["ats_score"])

print("\nSections:\n")
print(result["sections"])

print("\nSkills:\n")
print(result["skills"])