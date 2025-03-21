import io
import os
import zipfile
import pdfplumber
import psycopg2
import streamlit as st
import google.generativeai as genai
import re
from dotenv import load_dotenv
from time import sleep
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# ----------------- Database Connection ----------------- #
def get_db_connection():
    URL = os.getenv("DATABASE_URL")
    try:
        return psycopg2.connect(URL)
    except psycopg2.Error as e:
        st.error(f"❌ Error connecting to the database: {e}")
        return None

# ----------------- Save to Database ----------------- #
def save_to_database(candidate_name, skills, experience, resume_file, match_percentage, phone_number):
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO shortlisted (candidate_name, skills, experience, resume_file, match_percentage, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (candidate_name, skills, experience, resume_file, match_percentage, phone_number))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"❌ Error saving data for {candidate_name}: {e}")

# ----------------- Send Email Function ----------------- #
def send_email_to_candidate(candidate_email, candidate_name, match_percentage):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    subject = "Congratulations! You're shortlisted for the next round - Company ABC"
    body = f"""
    Dear {candidate_name},

    Congratulations! Based on your resume screening, you have been shortlisted for the next round of the selection process at Company ABC.

    Your profile matched {match_percentage}% with the job description provided by our hiring team.

    Our HR team will reach out to you soon for further steps.

    Best wishes,
    Recruitment Team,
    Company ABC
    """
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = candidate_email
        message['Subject'] = subject
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        st.info(f"📩 Email sent to {candidate_name} at {candidate_email}")
    except Exception as e:
        st.warning(f"⚠️ Failed to send email to {candidate_name}: {e}")

# ----------------- Configure Gemini API ----------------- #
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ----------------- PDF Text Extraction ----------------- #
def extract_text_from_pdf(pdf_bytes):
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# ----------------- Gemini AI Response ----------------- #
def get_gemini_response(resume_text, job_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f'''
    You are an ATS AI extracting details from resumes. Extract:
    - Candidate's full name
    - Key skills (max 10, comma-separated)
    - Total years of experience
    - Match percentage against job description
    - Phone number (if available)
    - Email address (if available)

    Format:
    ```
    Name: [Candidate Name]
    Skills: [Skill1, Skill2, ...]
    Experience: [X Years]
    Match Percentage: [XX%]
    Phone Number: [Phone Number]
    Email: [Email Address]
    ```

    Resume Text: {resume_text}
    Job Description: {job_description}
    ''')
    return response.text

# ----------------- Resume Analyzer ----------------- #
def analyze_resumes(job_description, resumes):
    shortlisted = {}
    total_resumes = len(resumes)

    progress_bar = st.progress(0)

    for idx, (file_name, pdf_content) in enumerate(resumes.items(), start=1):
        with st.spinner(f"Analyzing {file_name}..."):
            resume_text = extract_text_from_pdf(pdf_content)
            response = get_gemini_response(resume_text, job_description)

            name_match = re.search(r'Name: (.+)', response)
            skills_match = re.search(r'Skills: (.+)', response)
            experience_match = re.search(r'Experience: (\d+)', response)
            match_percent_match = re.search(r'Match Percentage: (\d+)%', response)
            phone_number_match = re.search(r'Phone Number: ([\d\s\-\+\(\)]+)', response)
            email_match = re.search(r'Email: ([\w\.-]+@[\w\.-]+\.\w+)', response)

            if name_match and skills_match and experience_match and match_percent_match:
                candidate_name = name_match.group(1).strip()
                skills = skills_match.group(1).strip()
                experience = int(experience_match.group(1))
                match_percentage = int(match_percent_match.group(1))
                phone_number = phone_number_match.group(1).strip() if phone_number_match else "Not Available"
                candidate_email = email_match.group(1).strip() if email_match else None

                if match_percentage >= 70:
                    shortlisted[file_name] = (pdf_content, match_percentage)
                    save_to_database(candidate_name, skills, experience, file_name, match_percentage, phone_number)

                    if candidate_email:
                        send_email_to_candidate(candidate_email, candidate_name, match_percentage)

            progress_bar.progress(int((idx / total_resumes) * 100))
            sleep(0.5)

    return shortlisted

# ----------------- Streamlit UI Setup ----------------- #
st.set_page_config(page_title="RecruitEaze Resume Screener", page_icon="📄", layout="wide")

with st.sidebar:
    st.image("assets/logo.gif", use_column_width=True)
    st.title("RecruitEaze Resume Screener")
    nav_choice = st.radio("📂 Navigation", ["Resume Screening", "View Shortlisted Candidates"])

# ----------------- Page 1: Resume Screening ----------------- #
if nav_choice == "Resume Screening":
    st.markdown('<h1 style="text-align: center;">Bulk ATS Resume Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Upload resumes and enter job description to shortlist candidates.</p>', unsafe_allow_html=True)

    job_description = st.text_area("Enter Job Description:", key="job_description", height=150,
                                   placeholder="Paste the job description here...")

    uploaded_file = st.file_uploader("Upload a ZIP file of Resumes (PDF Only)", type=["zip"],
                                     help="Ensure the ZIP file contains only PDF resumes.")

    if uploaded_file and job_description:
        st.success("✅ File uploaded and job description provided!")

        with st.spinner("Analyzing resumes..."):
            try:
                with zipfile.ZipFile(uploaded_file) as z:
                    resumes = {name: z.read(name) for name in z.namelist() if name.endswith(".pdf")}

                st.info(f"📂 Found {len(resumes)} resumes in the ZIP file.")
                shortlisted_resumes = analyze_resumes(job_description, resumes)

                if shortlisted_resumes:
                    st.success(f"✅ {len(shortlisted_resumes)} resumes shortlisted!")
                    for name, (content, match_percentage) in shortlisted_resumes.items():
                        st.write(f"**{name}** (Match: {match_percentage}%)")
                        st.download_button(label=f"⬇ Download {name}", data=content, file_name=name, mime="application/pdf")
                else:
                    st.warning("❌ No resumes matched with a percentage above 70%.")
            except Exception as e:
                st.error(f"⚠️ Error processing the ZIP file: {e}")
    else:
        st.warning("❗ Please upload a ZIP file and enter a job description.")

# ----------------- Page 2: View Shortlisted Candidates ----------------- #
elif nav_choice == "View Shortlisted Candidates":
    st.markdown("<h2>📋 Shortlisted Candidates</h2>", unsafe_allow_html=True)
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT candidate_name, skills, experience, resume_file, match_percentage, phone_number FROM shortlisted ORDER BY match_percentage DESC;")
            rows = cur.fetchall()
            if rows:
                st.dataframe(rows, use_container_width=True)
            else:
                st.info("No shortlisted candidates found yet.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"⚠️ Error fetching data: {e}")

