import streamlit as st
import PyPDF2
import re
import sqlite3
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import io

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Mufat ka AI naam mera, par kaam bada hi tight,
Resume agar strong hua, to job lagwa du overnight.", page_icon="🫡", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFDD0; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, li, div { color: #000000 !important; }
    
    /* Input & Forms */
    .stTextInput > div > div > input { color: #000000 !important; background-color: #FFFFFF !important; border: 1px solid #ccc; }
    [data-testid="stForm"] { background-color: transparent !important; border: none !important; padding: 0px !important; }

    /* File Uploader */
    [data-testid="stFileUploader"] { background-color: #262730; border-radius: 10px; padding: 10px; }
    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] div { color: #FFFFFF !important; }
    
    /* Buttons - Uniform Theme */
    .stButton>button, .stDownloadButton>button { 
        background-color: #FF4B4B !important; 
        color: white !important; 
        border-radius: 8px !important; 
        border: none !important; 
        font-weight: bold !important;
        width: 100%;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #E6D9B8; border-right: 1px solid #C4B490; }
    [data-testid="stSidebar"] * { color: #2C2C2C !important; }

    /* Info Boxes */
    .info-box { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }
    
    /* CANDIDATE CARD DESIGN */
    .candidate-card { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
    }
    .candidate-header {
        font-size: 20px;
        font-weight: bold;
        border-bottom: 2px solid #FF4B4B;
        padding-bottom: 5px;
        margin-bottom: 10px;
        color: #000000;
    }
    .detail-item { margin-bottom: 5px; font-size: 14px; }
    
    .chat-msg { background-color: #FFFFFF; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #2196F3; margin-bottom: 10px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []

# --- 3. LOGIN PAGE ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔒 HR Login Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Invalid Credentials")

# --- 4. MAIN TOOL ---
def main_tool():
    with st.sidebar:
        st.title("Admin Panel")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    def init_db():
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS candidates (name TEXT, score INTEGER, education TEXT, skills TEXT, reason TEXT)''')
        conn.commit()
        conn.close()

    def save_candidate(name, score, education, skills, reason):
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", (name, score, education, skills_str, reason))
        conn.commit()
        conn.close()

    def delete_candidate(name):
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        c.execute("DELETE FROM candidates WHERE name=?", (name,))
        conn.commit()
        conn.close()

    def extract_text_from_pdf(uploaded_file):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([p.extract_text() for p in pdf_reader.pages[:3] if p.extract_text()])
            if len(text.strip()) < 50:
                uploaded_file.seek(0)
                images = convert_from_bytes(uploaded_file.read())
                text = "".join([pytesseract.image_to_string(img) for img in images[:2]])
            return re.sub(r'\s+', ' ', text).strip()
        except: return ""

    def analyze_resume(text):
        res = {"education": "Other", "skills": [], "score": 25, "reason": "", "10th": "N/A", "12th": "N/A"}
        if re.search(r'B\.?T\s*e\s*c\s*h|Engineering|MCA|BCA|Techno India', text, re.I):
            res["education"] = "Technical Degree"; res["score"] += 45
        m10 = re.search(r'(?:10th|SSC|Matric)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if m10: res["10th"] = m10.group(1); res["score"] += 5
        m12 = re.search(r'(?:12th|HSC|Inter)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if m12: res["12th"] = m12.group(1); res["score"] += 5
        skill_list = ["Python", "Java", "SQL", "JavaScript", "React", "Node", "AWS", "Git", "Excel", "PHP", "MySQL", "HTML", "CSS"]
        res["skills"] = [s for s in skill_list if re.search(r'\b' + s.replace("+", "\+") + r'\b', text, re.I)]
        res["score"] = min(res["score"] + (len(res["skills"]) * 5), 100)
        res["reason"] = "Selected: Strong Profile" if res["score"] >= 70 else "Waitlist" if res["score"] >= 40 else "Rejected"
        return res

    init_db()
    st.title("📄 AI Resume Screener")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    if uploaded_file and st.button("Analyze Resume Now"):
        text = extract_text_from_pdf(uploaded_file)
        result = analyze_resume(text)
        st.session_state['analysis_result'], st.session_state['resume_text'], st.session_state['file_name'] = result, text, uploaded_file.name
        save_candidate(uploaded_file.name, result['score'], f"{result['education']} (10th:{result['10th']}, 12th:{result['12th']})", result['skills'], result['reason'])

    if st.session_state['analysis_result']:
        res = st.session_state['analysis_result']
        st.divider()
        st.subheader(f"Analysis: {st.session_state['file_name']}")
        c1, c2 = st.columns(2); c1.metric("Score", f"{res['score']}/100"); c2.markdown(f"### Status: {res['reason']}")
        st.markdown(f"<div class='info-box'><b>Degree:</b> {res['education']} | <b>10th:</b> {res['10th']} | <b>12th:</b> {res['12th']}<br><b>Skills:</b> {', '.join(res['skills'])}</div>", unsafe_allow_html=True)

        # --- SMART CHATBOT LOGIC ---
        st.markdown("### 💬 Chat with AI Assistant")
        for msg in st.session_state['chat_history']:
            st.markdown(f"<div class='chat-msg'><b>{'🤖 AI' if msg['role'] == 'assistant' else '👤 HR'}:</b> {msg['content']}</div>", unsafe_allow_html=True)
        
        with st.form(key='chat_f', clear_on_submit=True):
            ci, cb = st.columns([5, 1])
            u_in = ci.text_input("Message", label_visibility="collapsed")
            if cb.form_submit_button("Send") and u_in:
                st.session_state['chat_history'].append({"role": "user", "content": u_in})
                
                # Smart Filtering
                q = u_in.lower()
                if "skill" in q or "tech" in q:
                    reply = f"The candidate has the following skills: **{', '.join(res['skills'])}**."
                elif "score" in q or "mark" in q:
                    reply = f"The overall candidate score is **{res['score']}/100**."
                elif "education" in q or "degree" in q or "study" in q:
                    reply = f"Education Details: **{res['education']}**. Marks - 10th: {res['10th']}, 12th: {res['12th']}."
                elif "name" in q:
                    reply = f"The candidate's name (filename) is **{st.session_state['file_name']}**."
                elif "reason" in q or "status" in q:
                    reply = f"Status: **{res['reason']}**."
                elif "email" in q:
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', st.session_state['resume_text'])
                    reply = f"Found Email: **{email_match.group(0)}**" if email_match else "No email address found."
                else:
                    reply = "I can specifically tell you about the candidate's **Skills, Score, Education, Name, or Status**. What would you like to know?"
                
                st.session_state['chat_history'].append({"role": "assistant", "content": reply})
                st.rerun()

    # --- DATABASE VIEW ---
    st.divider()
    st.markdown("### 🗂️ Candidate Database")
    if st.checkbox("Show Candidate Management List"):
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        if df.empty:
            st.info("No data yet.")
        else:
            for i, r in df.iterrows():
                st.markdown(f"""
                <div class='candidate-card'>
                    <div class='candidate-header'>👤 {r['name']}</div>
                    <div class='detail-item'><b>🛠️ Skills:</b> {r['skills']}</div>
                    <div class='detail-item'><b>🎓 Education:</b> {r['education']}</div>
                    <div class='detail-item'><b>📊 Status:</b> {r['reason']} (Score: {r['score']})</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Delete Profile", key=f"del_{i}"):
                    delete_candidate(r['name']); st.rerun()
            st.markdown("---")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Full CSV Report", csv, "candidates_report.csv", "text/csv")
        conn.close()

if not st.session_state['logged_in']: login_page()
else: main_tool()
