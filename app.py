import streamlit as st
import json
import plotly.express as px
from utils import (
    configure_gemini,
    extract_text,
    rank_candidates,
    generate_interview_questions
)

st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="📊",
    layout="wide"
)

# ---------------------------
# Styling
# ---------------------------
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

</style>
""", unsafe_allow_html=True)

# ---------------------------
# Rank Icon
# ---------------------------
def get_rank_icon(rank):
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    return "🏅"


# ---------------------------
# Load Gemini
# ---------------------------
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
# Upload Inputs
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
if st.button("🚀 Analyze Candidates", width="stretch"):

    if jd_file is None or not resume_files:
        st.warning("Please upload JD and resumes")

    else:

        with st.spinner("AI analyzing candidates..."):

            jd_text = extract_text(jd_file)

            resume_data = ""
            resume_map = {}

            for resume in resume_files:

                resume_text = extract_text(resume)

                resume_map[resume.name] = resume_text

                resume_data += f"""

Candidate Name: {resume.name}

Resume:
{resume_text}

"""

            result = rank_candidates(model, jd_text, resume_data)

            try:
                data = json.loads(result)

                st.session_state["analysis_data"] = data
                st.session_state["resume_map"] = resume_map
                st.session_state["jd_text"] = jd_text

            except:
                st.error("AI response parsing failed")
                st.code(result)
                st.stop()

        st.success("Analysis Complete")


# ---------------------------
# Dashboard Rendering
# ---------------------------
if "analysis_data" in st.session_state:

    data = st.session_state["analysis_data"]
    resume_map = st.session_state["resume_map"]
    jd_text = st.session_state["jd_text"]

    # sort by score
    data = sorted(data, key=lambda x: x["score"], reverse=True)

    names = [c["candidate"] for c in data]
    scores = [c["score"] for c in data]

    st.divider()

    # ---------------------------
    # Score Chart
    # ---------------------------
    st.subheader("📊 Candidate Score Comparison")

    fig = px.bar(
        x=names,
        y=scores,
        labels={"x": "Candidate", "y": "Score"},
        text=scores,
        color=scores,
        color_continuous_scale="Blues"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, width="stretch")

    st.divider()

    # ---------------------------
    # Candidate Cards
    # ---------------------------
    st.header("🏆 Candidate Rankings")

    for candidate in data:

        rank = candidate["rank"]
        name = candidate["candidate"]
        score = candidate["score"]

        strengths = candidate["strengths"]
        missing = candidate["missing"]
        summary = candidate["summary"]

        icon = get_rank_icon(rank)
        display_name = name.replace("_", " ").replace(".pdf", "")
        with st.container():

            st.markdown(
                f"<div class='card'><div class='card-title'>{icon} {display_name}</div>",
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

            # ---------------------------
            # Interview Question Button
            # ---------------------------
            if st.button(
                f"Generate Interview Questions for {name}",
                key=f"question_btn_{rank}"
            ):

                with st.spinner("Generating interview questions..."):

                    resume_text = resume_map[name]

                    questions = generate_interview_questions(
                        model,
                        jd_text,
                        resume_text
                    )

                    try:
                        clean_questions = questions.strip()
                        clean_questions = clean_questions.replace("```json", "").replace("```", "").strip()
                        questions_list = json.loads(questions)

                        st.session_state[f"questions_{name}"] = questions_list

                    except:
                        st.error("Failed to parse questions")
                        st.code(questions)
                        st.stop()

            # ---------------------------
            # Show Questions
            # ---------------------------
            if f"questions_{name}" in st.session_state:

                with st.expander("🤖 Suggested Interview Questions"):

                    for i, q in enumerate(st.session_state[f"questions_{name}"], 1):
                        st.write(f"{i}. {q}")