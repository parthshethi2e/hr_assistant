import streamlit as st
import json
from utils import configure_gemini, extract_text, rank_candidates


st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

.card {
    padding:20px;
    border-radius:12px;
    background-color:#f8f9fa;
    margin-bottom:20px;
    border:1px solid #e6e6e6;
}

.card-title {
    font-size:20px;
    font-weight:600;
}

.skill-green {
    color:green;
    font-weight:500;
}

.skill-red {
    color:red;
    font-weight:500;
}

</style>
""", unsafe_allow_html=True)

def get_rank_icon(rank):
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    return "🏅"

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

            try:
                data = json.loads(result)
            except:
                st.error("AI response parsing failed")
                st.code(result)
                st.stop()

        st.success("Analysis Complete")
        st.divider()
        st.header("🏆 Candidate Rankings")

        # ✅ NOW safe because data exists
        for candidate in data:
            rank = candidate["rank"]
            name = candidate["candidate"]
            score = candidate["score"]

            strengths = candidate["strengths"]
            missing = candidate["missing"]
            summary = candidate["summary"]

            icon = get_rank_icon(rank)

            with st.container():

                st.markdown(
                    f"<div class='card'><div class='card-title'>{icon} {name}</div>",
                    unsafe_allow_html=True
                )

                st.progress(score / 100)
                st.write(f"Score: **{score}%**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("🟢 **Strengths**")
                    for s in strengths:
                        st.write(f"• {s}")

                with col2:
                    st.markdown("🔴 **Missing Skills**")
                    for m in missing:
                        st.write(f"• {m}")

                st.info(summary)

                st.markdown("</div>", unsafe_allow_html=True)