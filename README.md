ATS Resume Expert(RECRUITEASE) 📄🤖

A Streamlit-based application that analyzes resumes against job descriptions using Generative AI and stores/uploaded resumes in a PostgreSQL database.

Description
This project helps users evaluate their resumes against job descriptions by leveraging the power of AI and an ATS-like analysis. Users can upload their resumes in PDF format and receive actionable insights, improvement suggestions, percentage match, and tailored job recommendations.

Key Features:

📄 Resume Upload: Upload resumes in PDF format.
💡 AI-Powered Analysis: Utilizes Generative AI (Gemini) for evaluation and keyword matching.
📊 Percentage Match: Get the percentage alignment between your resume and a job description.
📝 Improvement Suggestions: Identify missing keywords and areas of improvement.
👔 Job Recommendations: Suggests fields or job posts based on your resume.
🗄️ Database Integration: Resumes are stored in a PostgreSQL database as binary data for secure storage and retrieval.
Technologies Used
Python: Core programming language.
Streamlit: Interactive web app for the user interface.
PostgreSQL: Database for storing and retrieving resumes.
Generative AI (Gemini): For resume evaluation and generating insights.
PDF2Image: Converts PDF to image for analysis.
Psycopg2: PostgreSQL database adapter for Python.
Pillow (PIL): Image processing.
dotenv: For managing environment variables securely.
Installation and Setup
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/ats-resume-expert.git
cd ats-resume-expert
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the .env file with your environment variables:

GOOGLE_API_KEY for Generative AI.
PostgreSQL credentials.
Run the application:

bash
Copy code
streamlit run main.py
How It Works
Upload a PDF resume.
Paste a job description in the provided text area.
Select from the available features:
Analyze Resume
Improvement Tips
Percentage Match
Job Suggestions
View AI-generated insights and download your analysis if needed.
Screenshots
Upload Resume and Input Job Description
AI-Powered Resume Analysis
Percentage Match Results
(Add screenshots or GIFs here to demonstrate functionality.)

Future Enhancements
Support for multiple file formats (e.g., DOCX).
Additional job analysis models.
Enhanced AI insights using more sophisticated language models.
Export analysis as a downloadable PDF report.

