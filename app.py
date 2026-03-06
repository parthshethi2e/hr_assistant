import streamlit as st
from utils import configure_gemini, extract_text, rank_candidates

# Load Gemini model
model = configure_gemini()

st.title("AI Recruiter Ranking System")

jd_file = st.file_uploader(
    "Upload Job Description",
    type=["txt"]
)

resume_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if st.button("Analyze Candidates"):

    if jd_file is None or not resume_files:
        st.warning("Please upload JD and resumes")

    else:

        jd_text = extract_text(jd_file)

        resume_data = ""

        for resume in resume_files:

            resume_text = extract_text(resume)

            resume_data += f"""

Candidate Name: {resume.name}

Resume:
{resume_text}

"""

        result = rank_candidates(model, jd_text, resume_data)

        st.subheader("Candidate Ranking")

        st.write(result)