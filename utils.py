import os
import google.generativeai as genai
from dotenv import load_dotenv
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
import tempfile

load_dotenv()

# 
# -----------------------------
# Configure Gemini
# -----------------------------
def configure_gemini():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        "gemini-3-flash-preview",
        generation_config={"temperature": 0.2}
    )

    return model


# -----------------------------
# Extract text from uploaded file
# -----------------------------
def extract_text(uploaded_file):

    file_type = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        path = tmp.name

    if file_type == "pdf":
        return extract_pdf_text(path)

    elif file_type == "docx":
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file_type == "txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return ""


# -----------------------------
# Rank Candidates
# -----------------------------
def rank_candidates(model, jd_text, resumes):

    prompt = f"""
You are an expert AI recruiter.

Compare the Job Description with candidate resumes.

Rank candidates from BEST to WORST.

For each candidate provide:

Rank
Candidate Name
Score (0-100)

Selected Reasons (strengths)
Rejected Reasons (missing skills)

Provide a short justification.

Job Description:
{jd_text}

Candidate Resumes:
{resumes}
"""

    response = model.generate_content(prompt)

    return response.text