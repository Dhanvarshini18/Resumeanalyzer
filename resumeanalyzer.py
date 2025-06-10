import streamlit as st
import PyPDF2
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
import google.generativeai as genai

# Configure Gemini API key from Streamlit secrets
genai.configure(api_key="AIzaSyBYTDmlXHHg9SGYDBA-mimwffrYuSruLZc")

# Custom CSS for colorful styling
st.markdown("""
<style>
body {
    background-color: #f0f8ff;
}
.stButton>button {
    background-color: #FF4500;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}
.stButton>button:hover {
    background-color: #1E90FF;
}
.stSelectbox, .stTextArea {
    background-color: #e6f3ff;
    border-radius: 5px;
}
h1, h2, h3 {
    color: #32CD32;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "job_role" not in st.session_state:
    st.session_state.job_role = "Software Engineer"
if "requirements" not in st.session_state:
    st.session_state.requirements = ""
if "report" not in st.session_state:
    st.session_state.report = None

# Function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

# Function to generate analysis using Gemini API
def generate_resume_analysis(resume_text, job_role, requirements):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Analyze the following resume for the job role: {job_role}.
    Resume: {resume_text}
    Additional Requirements: {requirements}
    Provide a structured report in markdown format with:
    - Key Skills: List extracted skills (technical and soft skills).
    - Work Experience Summary: Summarize roles, duration, and responsibilities.
    - Alignment Rating: Rate alignment with the job role (0-100) based on industry standards.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return None

# Function to create colorful PDF report
def create_pdf_report(report_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles["Title"].textColor = HexColor("#32CD32")
    styles["Heading2"].textColor = HexColor("#1E90FF")
    story = []
    story.append(Paragraph("SNS Square Resume Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))
    for line in report_text.split("\n"):
        if line.startswith("##"):
            story.append(Paragraph(line[2:], styles["Heading2"]))
        else:
            story.append(Paragraph(line, styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit app
st.title("🌟 SNS Square Resume Analyzer 🌟")
st.markdown("""
Upload a resume (PDF or text) to analyze key skills, summarize work experience, and rate alignment with a selected job role. 
Download the colorful report as a PDF!
""")

# Resume upload
uploaded_file = st.file_uploader("Upload Resume (PDF or Text)", type=["pdf", "txt"])
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
    else:
        st.session_state.resume_text = uploaded_file.read().decode("utf-8")
    if st.session_state.resume_text:
        st.success("Resume uploaded successfully!")

# Job role and requirements input
st.subheader("Job Role and Requirements")
st.session_state.job_role = st.selectbox(
    "Select Job Role",
    ["Software Engineer", "Data Scientist", "Project Manager", "UX Designer", "Marketing Manager", "Other"],
    index=["Software Engineer", "Data Scientist", "Project Manager", "UX Designer", "Marketing Manager", "Other"].index(st.session_state.job_role)
)
if st.session_state.job_role == "Other":
    st.session_state.job_role = st.text_input("Enter Custom Job Role", value=st.session_state.job_role if st.session_state.job_role != "Other" else "")
st.session_state.requirements = st.text_area("Additional Requirements (e.g., specific skills, experience)", value=st.session_state.requirements)

# Generate analysis
if st.button("Analyze Resume") and st.session_state.resume_text:
    with st.spinner("Analyzing resume..."):
        st.session_state.report = generate_resume_analysis(
            st.session_state.resume_text, st.session_state.job_role, st.session_state.requirements
        )
        if st.session_state.report:
            st.markdown(st.session_state.report)

# Regenerate analysis
if st.button("Regenerate Analysis") and st.session_state.resume_text and st.session_state.report:
    with st.spinner("Regenerating analysis..."):
        st.session_state.report = generate_resume_analysis(
            st.session_state.resume_text, st.session_state.job_role, st.session_state.requirements
        )
        if st.session_state.report:
            st.markdown(st.session_state.report)

# Download report as PDF
if st.session_state.report:
    pdf_buffer = create_pdf_report(st.session_state.report)
    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="sns_resume_analysis_report.pdf",
        mime="application/pdf"
    )