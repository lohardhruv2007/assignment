import streamlit as st
import PyPDF2
import re
import sqlite3
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import io

# --- 1. PAGE CONFIG & DESIGN SETTINGS ---
st.set_page_config(page_title="Resume Screener AI", page_icon="📄", layout="centered")

# --- CUSTOM CSS (SMART COLOR ADJUSTMENT) ---
st.markdown("""
    <style>
    /* 1. Main Background Cream */
    .stApp {
        background-color: #FFFDD0;
    }
    
    /* 2. General Page Text -> BLACK */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, li, div {
        color: #000000 !important;
    }
    
    /* 3. METRICS & TABLES -> BLACK */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    .dataframe {
        color: #000000 !important;
    }

    /* 4. FIX: FILE UPLOADER (Drag & Drop Area) */
    [data-testid="stFileUploader"] {
        background-color: #262730; 
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] small, 
    [data-testid="stFileUploader"] div {
        color: #FFFFFF !important;
    }
    
    /* 5. BUTTONS */
    .stButton>button {
        background-color: #FF4B4B;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    
    /* 6. STATUS MESSAGES */
    .stAlert div {
        color: #000000 !important;
    }

    /* 7. NEW: PROFESSIONAL RAW TEXT BOX STYLE */
    .resume-box {
        background-color: #FFFFFF; /* White Paper look */
        border: 1px solid #CCCCCC;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace; /* Typewriter font */
        font-size: 14px;
        color: #333333 !important;
        height: 300px; /* Fixed height */
        overflow-y: scroll; /* Scrollbar */
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); /* Soft Shadow */
        white-space: pre-wrap; /* Keeps formatting */
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # Check table schema
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='candidates' ''')
    if c.fetchone()[0] == 1:
        c.execute('PRAGMA table_info(candidates)')
        columns = c.fetchall()
        if len(columns) != 5:
            c.execute('DROP TABLE candidates')
            conn.commit()
            
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (name TEXT, score INTEGER, education TEXT, skills TEXT, reason TEXT)''')
    conn.commit()
    conn.close()

def save_candidate(name, score, education, skills, reason):
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
    
    try:
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", 
                  (name, score, education, skills_str, reason))
        conn.commit()
    except sqlite3.OperationalError:
        c.execute("DROP TABLE IF EXISTS candidates")
        init_db()
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", 
                  (name, score, education, skills_str, reason))
        conn.commit()
    conn.close()

# --- 3. TEXT EXTRACTION ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages[:3]:
            content = page.extract_text()
            if content:
                text += content + " "
        
        if len(text.strip()) < 50:
            with st.spinner("⚠️ Scanned Image Detected! Extracting text via OCR..."):
                uploaded_file.seek(0)
                images = convert_from_bytes(uploaded_file.read())
                for img in images[:2]:
                    text += pytesseract.image_to_string(img)
                    
        return re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return ""

# --- 4. SCORING LOGIC ---
def analyze_resume(text):
    res = {"education": "Unknown", "skills": [], "score": 25, "reason": ""}
    
    if not text:
        res["reason"] = "Rejected: File unreadable."
        return res

    # Education
    has_degree = False
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering|B\.E\.|M\.C\.A|B\.C\.A|Techno India', text, re.I):
        res["education"] = "Technical Degree (B.Tech/BE/MCA)"
        res["score"] += 45
        has_degree = True
    elif re.search(r'B\.Sc|M\.Sc|Bachelor\s*of\s*Science', text, re.I):
        res["education"] = "Science Degree (B.Sc/M.Sc)"
        res["score"] += 30

    # Skills
    skill_list = ["Python", "Java", "C\+\+", "SQL", "MySQL", "JavaScript", "HTML", "CSS", "React", "Node", "AWS", "Git", "Machine Learning", "Excel"]
    found_skills = []
    for skill in skill_list:
        pattern = r'\b' + skill.replace("+", "\+") + r'\b'
        if re.search(pattern, text, re.I):
            found_skills.append(skill.replace("\+", "+"))
            res["score"] += 5
    
    res["skills"] = list(set(found_skills))
    res["score"] = min(res["score"], 100)

    # Decision
    if res["score"] >= 70:
        res["reason"] = "Selected: Strong Profile"
    elif res["score"] >= 40:
        res["reason"] = "Waitlist: Average Profile"
    else:
        reason_list = []
        if not has_degree: reason_list.append("No Tech Degree")
        if len(found_skills) < 2: reason_list.append("Low Skills")
        res["reason"] = "Rejected: " + ", ".join(reason_list)
    
    return res

# --- 5. MAIN UI ---
init_db()

st.title("📄 AI Resume Screener")
st.markdown("### Upload Resume to Check Eligibility")

uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

if uploaded_file is not None:
    if st.button("Analyze Resume Now"):
        
        text = extract_text_from_pdf(uploaded_file)
        result = analyze_resume(text)
        save_candidate(uploaded_file.name, result['score'], result['education'], result['skills'], result['reason'])
        
        st.divider()
        st.subheader(f"Result for: {uploaded_file.name}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Score", f"{result['score']}/100")
        col2.metric("Education", "Tech" if "Tech" in result['education'] else "Other")
        col3.metric("Skills Found", len(result['skills']))
        
        # Status Box
        if "Selected" in result['reason']:
            st.success(f"🎉 {result['reason']}")
        elif "Waitlist" in result['reason']:
            st.warning(f"⚠️ {result['reason']}")
        else:
            st.error(f"❌ {result['reason']}")
            
        # --- NEW PROFESSIONAL TEXT DESIGN ---
        with st.expander("📄 View Extracted Content (Raw Text)"):
            st.markdown(f"""
                <div class="resume-box">
                {text}
                </div>
            """, unsafe_allow_html=True)

# Database View
st.divider()
if st.checkbox("Show All Candidates Database"):
    conn = sqlite3.connect('candidates.db')
    try:
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        st.dataframe(df)
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "candidates.csv", "text/csv")
    except:
        st.write("Database is empty.")
    conn.close()
