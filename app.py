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

# --- CUSTOM CSS (Global Styling) ---
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
    
    /* 3. INPUT FIELDS & LOGIN BOX */
    .stTextInput > div > div > input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* 4. DRAG & DROP AREA (Dark + White Text) */
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
    
    /* 6. INFO CARDS */
    .info-box {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }

    /* 7. RAW TEXT BOX */
    .resume-box {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        color: #333333 !important;
        height: 250px;
        overflow-y: scroll;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE FOR LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 3. LOGIN FUNCTION ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔒 HR Login Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter your credentials to access the Resume Screener.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # --- SET PASSWORD HERE ---
            if username == "admin" and password == "admin123":
                st.session_state['logged_in'] = True
                st.rerun() # Refresh app to show main tool
            else:
                st.error("❌ Invalid Username or Password")

# --- 4. MAIN APP LOGIC (Only accessible after login) ---
def main_tool():
    # Logout Button in Sidebar
    with st.sidebar:
        st.write(f"Logged in as: **HR Admin**")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- DATABASE FUNCTIONS ---
    def init_db():
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
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

    # --- TEXT EXTRACTION ---
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

    # --- SCORING & PARSING LOGIC ---
    def analyze_resume(text):
        res = {"education": "Unknown", "skills": [], "score": 25, "reason": "", "10th": "Not Found", "12th": "Not Found"}
        if not text:
            res["reason"] = "Rejected: File unreadable."
            return res

        # Education Check
        has_degree = False
        if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering|B\.E\.|M\.C\.A|B\.C\.A', text, re.I):
            res["education"] = "B.Tech/BE/MCA"
            res["score"] += 45
            has_degree = True
        elif re.search(r'B\.Sc|M\.Sc|Bachelor\s*of\s*Science', text, re.I):
            res["education"] = "B.Sc/M.Sc"
            res["score"] += 30

        # Marks Check (10th/12th)
        match_10 = re.search(r'(?:10th|Class X|SSC|Matric|High School)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if match_10:
            res["10th"] = match_10.group(1)
            res["score"] += 2

        match_12 = re.search(r'(?:12th|Class XII|HSC|Intermediate|Senior School)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if match_12:
            res["12th"] = match_12.group(1)
            res["score"] += 2

        # Skills Check
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

    # --- UI EXECUTION ---
    init_db()

    st.title("📄 AI Resume Screener")
    st.markdown("### Upload Resume to Check Eligibility")

    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Analyze Resume Now"):
            
            text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume(text)
            
            # Save to DB
            edu_full_text = f"{result['education']} | 10th: {result['10th']} | 12th: {result['12th']}"
            save_candidate(uploaded_file.name, result['score'], edu_full_text, result['skills'], result['reason'])
            
            st.divider()
            st.subheader(f"Result for: {uploaded_file.name}")
            
            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("Overall Score", f"{result['score']}/100")
            status_color = "green" if "Selected" in result['reason'] else "orange" if "Waitlist" in result['reason'] else "red"
            col2.markdown(f"### Status: :{status_color}[{result['reason']}]")
            
            st.divider()

            # Education Boxes
            st.markdown("#### 🎓 Education & Marks Details")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='info-box'><b>Highest Degree</b><br>{result['education']}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='info-box'><b>10th / SSC</b><br>{result['10th']}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='info-box'><b>12th / HSC</b><br>{result['12th']}</div>", unsafe_allow_html=True)

            # Skills
            st.markdown("#### 🛠️ Technical Skills Detected")
            st.markdown(f"<div class='info-box'>{', '.join(result['skills']) if result['skills'] else 'No specific skills detected.'}</div>", unsafe_allow_html=True)

            # Raw Text
            with st.expander("📄 View Extracted Content (Raw Text)"):
                st.markdown(f"<div class='resume-box'>{text}</div>", unsafe_allow_html=True)

    # Database
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

# --- 5. CONTROL FLOW ---
if not st.session_state['logged_in']:
    login_page()
else:
    main_tool()
