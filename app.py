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

# --- CUSTOM CSS (Global + Sidebar + Candidate Card Styling) ---
st.markdown("""
    <style>
    /* --- MAIN PAGE STYLING --- */
    .stApp {
        background-color: #FFFDD0;
    }
    
    /* Text Elements -> BLACK */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, li, div {
        color: #000000 !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* File Uploader */
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
    
    /* Buttons */
    .stButton>button {
        background-color: #FF4B4B;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    
    /* --- SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #E6D9B8;
        border-right: 1px solid #C4B490;
    }
    [data-testid="stSidebar"] * {
        color: #2C2C2C !important;
    }

    /* --- RESULT BOX STYLING --- */
    .info-box {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
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
    
    /* --- NEW: CANDIDATE LIST CARD STYLING --- */
    .candidate-card {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 8px solid #333; /* Default Border */
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 3. LOGIN PAGE ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔒 HR Login Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter your credentials to access the Resume Screener.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password")

# --- 4. MAIN APP LOGIC ---
def main_tool():
    # Sidebar
    with st.sidebar:
        st.title("Admin Panel")
        st.write("Welcome, HR Admin")
        st.markdown("---")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.markdown("---")
        st.info("ℹ️ Use 'Delete' to remove candidates permanently.")

    # --- DB FUNCTIONS ---
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
            c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", (name, score, education, skills_str, reason))
            conn.commit()
        except sqlite3.OperationalError:
            c.execute("DROP TABLE IF EXISTS candidates")
            init_db()
            c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", (name, score, education, skills_str, reason))
            conn.commit()
        conn.close()

    # --- NEW: DELETE FUNCTION ---
    def delete_candidate(name):
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        c.execute("DELETE FROM candidates WHERE name=?", (name,))
        conn.commit()
        conn.close()

    # --- PDF & ANALYZE FUNCTIONS (SAME AS BEFORE) ---
    def extract_text_from_pdf(uploaded_file):
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages[:3]:
                content = page.extract_text()
                if content: text += content + " "
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

    def analyze_resume(text):
        res = {"education": "Unknown", "skills": [], "score": 25, "reason": "", "10th": "Not Found", "12th": "Not Found"}
        if not text:
            res["reason"] = "Rejected: File unreadable."
            return res
        
        has_degree = False
        if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering|B\.E\.|M\.C\.A|B\.C\.A', text, re.I):
            res["education"] = "B.Tech/BE/MCA"
            res["score"] += 45
            has_degree = True
        elif re.search(r'B\.Sc|M\.Sc|Bachelor\s*of\s*Science', text, re.I):
            res["education"] = "B.Sc/M.Sc"
            res["score"] += 30

        match_10 = re.search(r'(?:10th|Class X|SSC|Matric|High School)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if match_10:
            res["10th"] = match_10.group(1)
            res["score"] += 2
        match_12 = re.search(r'(?:12th|Class XII|HSC|Intermediate|Senior School)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if match_12:
            res["12th"] = match_12.group(1)
            res["score"] += 2

        skill_list = ["Python", "Java", "C\+\+", "SQL", "MySQL", "JavaScript", "HTML", "CSS", "React", "Node", "AWS", "Git", "Machine Learning", "Excel"]
        found_skills = []
        for skill in skill_list:
            if re.search(r'\b' + skill.replace("+", "\+") + r'\b', text, re.I):
                found_skills.append(skill.replace("\+", "+"))
                res["score"] += 5
        
        res["skills"] = list(set(found_skills))
        res["score"] = min(res["score"], 100)

        if res["score"] >= 70: res["reason"] = "Selected: Strong Profile"
        elif res["score"] >= 40: res["reason"] = "Waitlist: Average Profile"
        else:
            reason_list = []
            if not has_degree: reason_list.append("No Tech Degree")
            if len(found_skills) < 2: reason_list.append("Low Skills")
            res["reason"] = "Rejected: " + ", ".join(reason_list)
        return res

    # --- UI LAYOUT ---
    init_db()

    st.title("📄 AI Resume Screener")
    st.markdown("### Upload Resume to Check Eligibility")

    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Analyze Resume Now"):
            text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume(text)
            
            edu_full_text = f"{result['education']} | 10th: {result['10th']} | 12th: {result['12th']}"
            save_candidate(uploaded_file.name, result['score'], edu_full_text, result['skills'], result['reason'])
            
            st.divider()
            st.subheader(f"Result for: {uploaded_file.name}")
            
            col1, col2 = st.columns(2)
            col1.metric("Overall Score", f"{result['score']}/100")
            status_color = "green" if "Selected" in result['reason'] else "orange" if "Waitlist" in result['reason'] else "red"
            col2.markdown(f"### Status: :{status_color}[{result['reason']}]")
            
            st.divider()
            st.markdown("#### 🎓 Education & Marks")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='info-box'><b>Degree</b><br>{result['education']}</div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='info-box'><b>10th</b><br>{result['10th']}</div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='info-box'><b>12th</b><br>{result['12th']}</div>", unsafe_allow_html=True)
            
            st.markdown("#### 🛠️ Skills")
            st.markdown(f"<div class='info-box'>{', '.join(result['skills']) if result['skills'] else 'None'}</div>", unsafe_allow_html=True)
            
            with st.expander("📄 View Raw Text"):
                st.markdown(f"<div class='resume-box'>{text}</div>", unsafe_allow_html=True)

    # --- PROFESSIONAL CANDIDATE LIST (REPLACES OLD TABLE) ---
    st.divider()
    st.markdown("### 🗂️ Candidate Database (HR Only)")

    if st.checkbox("Show Candidate Management List"):
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            
            if df.empty:
                st.info("Database is empty. No candidates analyzed yet.")
            else:
                # Loop through each candidate and create a CARD
                for index, row in df.iterrows():
                    
                    # Color Coding for Border based on Status
                    status_color = "#4CAF50" if "Selected" in row['reason'] else "#FF9800" if "Waitlist" in row['reason'] else "#F44336"
                    
                    # Card Container
                    with st.container():
                        # Custom HTML for Card Look
                        st.markdown(f"""
                        <div class="candidate-card" style="border-left: 8px solid {status_color};">
                            <h4 style="margin:0; color:black;">👤 {row['name']}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Data Columns inside the Card
                        c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
                        
                        with c1:
                            st.caption("Score")
                            st.write(f"**{row['score']}/100**")
                        
                        with c2:
                            st.caption("Status")
                            st.write(f"{row['reason']}")
                        
                        with c3:
                            with st.expander("View Details"):
                                st.write(f"**Edu:** {row['education']}")
                                st.write(f"**Skills:** {row['skills']}")
                        
                        with c4:
                            # Delete Button for this specific row
                            if st.button("🗑️ Delete", key=f"del_{index}"):
                                delete_candidate(row['name'])
                                st.rerun() # Refresh page immediately
                                
                # Download CSV Option (at the bottom)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Full CSV", csv, "candidates.csv", "text/csv")
                
        except Exception as e:
            st.error(f"Error loading database: {e}")
        finally:
            conn.close()

# --- 5. CONTROL FLOW ---
if not st.session_state['logged_in']:
    login_page()
else:
    main_tool()
