import streamlit as st
from utils import configure_gemini, extract_text, rank_candidates
import re

st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="📊",
    layout="wide"
)


# Load Gemini model
model = configure_gemini()

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("AI Recruiter Dashboard")
st.sidebar.markdown("Upload JD and resumes to rank candidates.")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit + Gemini")

# ---------------------------
# Header
# ---------------------------
st.title("📊 AI Recruiter Dashboard")
st.markdown("Automatically rank candidates based on Job Description")

st.divider()

# ---------------------------
# Upload Section
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    jd_file = st.file_uploader(
        "Upload Job Description",
        type=["txt"]
    )

with col2:
    resume_files = st.file_uploader(
        "Upload Candidate Resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

st.divider()

# ---------------------------
# Analyze Button
# ---------------------------
if st.button("🚀 Analyze Candidates", use_container_width=True):

    if jd_file is None or not resume_files:
        st.warning("Please upload JD and resumes")

    else:

        with st.spinner("AI analyzing candidates..."):

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

        st.success("Analysis Complete")

        st.divider()

        st.header("🏆 Candidate Rankings")

        # Split candidates
        candidates = re.split(r"Rank\s*\d+", result)

        rank = 1

        for candidate in candidates:

            if len(candidate.strip()) < 20:
                continue

            # Extract score
            score_match = re.search(r"Score:\s*(\d+)", candidate)

            score = int(score_match.group(1)) if score_match else 70

            with st.container():

                st.markdown(
                    f"""
                    ### 🥇 Rank {rank}
                    """,
                )

                # Score progress bar
                st.progress(score / 100)

                # Candidate details
                clean_text = candidate.replace("**", "")
                st.markdown(clean_text)

                st.divider()

            rank += 1