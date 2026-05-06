import streamlit as st
import tempfile
import json
import re
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

from graph.workflow import full_graph, ranking_graph
from agents.ranking_agent import ranking_agent

from docx import Document
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="Resume App")
st.title("Resume System")


def clean_text(value):

    if not value:
        return ""

    if isinstance(value, (list, dict)):
        return value

    text = str(value).strip()

    text = (
        text.replace("```json", "")
            .replace("```", "")
            .strip()
    )

    match = re.search(r"\{[\s\S]*\}", text)

    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    return text


def clean_label(text):

    text = text.lower()

    text = re.sub(
        r"experience with|hands[- ]on experience with|experience in|familiarity with|understanding of|knowledge of|experience building|experience",
        "",
        text
    )

    return text.strip().capitalize()


def create_docx(text):

    doc = Document()

    for line in text.split("\n"):
        doc.add_paragraph(line)

    buffer = BytesIO()

    doc.save(buffer)

    buffer.seek(0)

    return buffer


def create_pdf(text):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    for line in text.split("\n"):

        content.append(
            Paragraph(line, styles["Normal"])
        )

        content.append(
            Spacer(1, 8)
        )

    doc.build(content)

    buffer.seek(0)

    return buffer


mode = st.radio(
    "",
    ["Analyze Resume", "Rank Resumes"]
)


if mode == "Analyze Resume":

    file = st.file_uploader(
        "Resume (PDF)",
        type=["pdf"]
    )

    jd = st.text_area(
        "Job Description"
    )

    if st.button("Run"):

        if not file or not jd:
            st.stop()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(file.read())

            path = tmp.name

        result = full_graph.invoke({
            "pdf_path": path,
            "job_description": jd
        })

        col1, col2 = st.columns(2)

        col1.markdown(
            f"## ATS Score: {result.get('ats_score', 0)}"
        )

        col2.markdown(
            f"## Match Score: {result.get('skill_match_score', 0)}"
        )

        st.subheader("Summary")

        st.write(
            clean_text(
                result.get("summary")
            )
        )

        st.subheader("Missing Skills")

        for skill in result.get("missing_skills", []) or []:

            st.write(
                f"- {clean_label(skill)}"
            )

        st.subheader("Improvements")

        for i in result.get(
            "improvement_comparisons",
            []
        ):

            st.write(
                "Original:",
                i.get("original")
            )

            st.write(
                "Improved:",
                i.get("improved")
            )

            st.write(
                "Reason:",
                i.get("reason")
            )

            st.write("---")

        st.subheader("Suggestions")

        suggestions = clean_text(
            result.get("suggestions")
        ) or []

        for s in suggestions:

            st.write(f"- {s}")

        st.subheader("Section Improvements")

        section_improvements = clean_text(
            result.get("section_improvements")
        ) or {}

        for k, v in section_improvements.items():

            st.write(f"{k.upper()}:")

            st.write(v)

        st.subheader("Resume")

        resume_text = clean_text(
            result.get("generated_resume")
        )

        if isinstance(resume_text, dict):

            resume_text = json.dumps(
                resume_text,
                indent=2
            )

        st.text_area(
            "Generated Resume",
            resume_text,
            height=400
        )

        col1, col2 = st.columns(2)

        col1.download_button(
            "Download DOCX",
            create_docx(resume_text),
            "resume.docx"
        )

        col2.download_button(
            "Download PDF",
            create_pdf(resume_text),
            "resume.pdf"
        )

else:

    files = st.file_uploader(
        "Upload Resumes",
        type=["pdf"],
        accept_multiple_files=True
    )

    jd = st.text_area(
        "Job Description"
    )

    if st.button("Rank"):

        if not files or not jd:
            st.stop()

        def process_resume(f):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(f.read())

                path = tmp.name

            r = ranking_graph.invoke({
                "pdf_path": path,
                "job_description": jd
            })

            r["resume_name"] = f.name

            return r

        with ThreadPoolExecutor(
            max_workers=4
        ) as executor:

            results = list(
                executor.map(
                    process_resume,
                    files
                )
            )

        ranked = ranking_agent(results)

        st.subheader("Ranking")

        for i, r in enumerate(ranked, 1):

            st.markdown(
                f"### {i}. {r.get('resume')}"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Final Score",
                r.get("final_score", 0)
            )

            col2.metric(
                "Skill Match",
                r.get("skill_match", 0)
            )

            col3.metric(
                "ATS",
                r.get("ats_score", 0)
            )

            st.markdown("---")