import streamlit as st
import PyPDF2
import re
import sqlite3
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import io

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Resume Screener AI", page_icon="📄", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* MAIN PAGE */
    .stApp { background-color: #FFFDD0; }
    
    /* TEXT COLORS */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, li, div { color: #000000 !important; }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input { color: #000000 !important; background-color: #FFFFFF !important; border: 1px solid #ccc; }

    /* DRAG & DROP AREA */
    [data-testid="stFileUploader"] { background-color: #262730; border-radius: 10px; padding: 10px; }
    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] div { color: #FFFFFF !important; }
    
    /* BUTTONS */
    .stButton>button { background-color: #FF4B4B; color: white !important; border-radius: 8px; border: none; font-weight: bold; }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #E6D9B8; border-right: 1px solid #C4B490; }
    [data-testid="stSidebar"] * { color: #2C2C2C !important; }

    /* CARDS */
    .info-box { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .resume-box { background-color: #FFFFFF; border: 1px solid #CCCCCC; padding: 15px; border-radius: 5px; font-family: 'Courier New', Courier, monospace; font-size: 14px; color: #333333 !important; height: 250px; overflow-y: scroll; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); white-space: pre-wrap; }
    .candidate-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 8px solid #333; }

    /* --- CHAT BAR STYLING (Removing Form Border) --- */
    [data-testid="stForm"] {
        border: none;
        padding: 0;
        margin-top: 20px;
    }
    
    /* Chat Response Bubble */
    .chat-bubble {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        border-left: 5px solid #2196F3; /* Blue accent */
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []

# --- 3. LOGIN PAGE ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔒 HR Login Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter your credentials.</p>", unsafe_allow_html=True)
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

# --- 4. MAIN APP LOGIC ---
def main_tool():
    with st.sidebar:
        st.title("Admin Panel")
        st.write("Welcome, HR Admin")
        st.markdown("---")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['analysis_result'] = None
            st.session_state['chat_history'] = []
            st.rerun()
        st.markdown("---")
        st.info("ℹ️ Chatbot is active for analyzed resumes.")

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
        c.execute('''CREATE TABLE IF NOT EXISTS candidates (name TEXT, score INTEGER, education TEXT, skills TEXT, reason TEXT)''')
        conn.commit()
        conn.close()

    def save_candidate(name, score, education, skills, reason):
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        try:
            c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", (name, score, education, skills_str, reason))
            conn.commit()
        except:
            c.execute("DROP TABLE IF EXISTS candidates")
            init_db()
            c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", (name, score, education, skills_str, reason))
            conn.commit()
        conn.close()

    def delete_candidate(name):
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        c.execute("DELETE FROM candidates WHERE name=?", (name,))
        conn.commit()
        conn.close()

    # --- TEXT EXTRACTION ---
    def extract_text_from_pdf(uploaded_file):
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages[:3]:
                content = page.extract_text()
                if content: text += content + " "
            if len(text.strip()) < 50:
                with st.spinner("⚠️ Scanned PDF! Applying OCR..."):
                    uploaded_file.seek(0)
                    images = convert_from_bytes(uploaded_file.read())
                    for img in images[:2]: text += pytesseract.image_to_string(img)
            return re.sub(r'\s+', ' ', text).strip()
        except: return ""

    # --- ANALYSIS LOGIC ---
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

        match_10 = re.search(r'(?:10th|Class X|SSC|Matric)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if match_10: res["10th"] = match_10.group(1); res["score"] += 2
        match_12 = re.search(r'(?:12th|Class XII|HSC|Intermediate)[^0-9]*(\d{1,2}(?:\.\d+)?\s*%|\d(?:\.\d+)?\s*CGPA)', text, re.I)
        if match_12: res["12th"] = match_12.group(1); res["score"] += 2

        skill_list = ["Python", "Java", "C\+\+", "SQL", "MySQL", "JavaScript", "HTML", "CSS", "React", "Node", "AWS", "Git", "Excel"]
        found_skills = []
        for skill in skill_list:
            if re.search(r'\b' + skill.replace("+", "\+") + r'\b', text, re.I):
                found_skills.append(skill.replace("\+", "+")); res["score"] += 5
        
        res["skills"] = list(set(found_skills)); res["score"] = min(res["score"], 100)

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
            
            st.session_state['analysis_result'] = result
            st.session_state['resume_text'] = text
            st.session_state['file_name'] = uploaded_file.name
            st.session_state['chat_history'] = [] 
            
            edu_full = f"{result['education']} | 10th: {result['10th']} | 12th: {result['12th']}"
            save_candidate(uploaded_file.name, result['score'], edu_full, result['skills'], result['reason'])

    # --- RESULTS SECTION ---
    if st.session_state['analysis_result']:
        res = st.session_state['analysis_result']
        name = st.session_state['file_name']
        
        st.divider()
        st.subheader(f"Result for: {name}")
        
        col1, col2 = st.columns(2)
        col1.metric("Overall Score", f"{res['score']}/100")
        status_color = "green" if "Selected" in res['reason'] else "orange" if "Waitlist" in res['reason'] else "red"
        col2.markdown(f"### Status: :{status_color}[{res['reason']}]")
        
        st.divider()
        st.markdown("#### 🎓 Education & Marks")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='info-box'><b>Degree</b><br>{res['education']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='info-box'><b>10th</b><br>{res['10th']}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='info-box'><b>12th</b><br>{res['12th']}</div>", unsafe_allow_html=True)
        
        st.markdown("#### 🛠️ Skills")
        st.markdown(f"<div class='info-box'>{', '.join(res['skills']) if res['skills'] else 'None'}</div>", unsafe_allow_html=True)
        
        with st.expander("📄 View Raw Text"):
            st.markdown(f"<div class='resume-box'>{st.session_state['resume_text']}</div>", unsafe_allow_html=True)

        # --- HORIZONTAL CHAT BAR (NO GAPS, SAME LINE) ---
        st.divider()
        
        # Form Container that looks like a Toolbar
        with st.form(key='chat_form', clear_on_submit=True):
            # Layout: [Title (Small width)] [Input Box (Big width)] [Button (Small width)]
            c_label, c_input, c_btn = st.columns([3, 5, 1])
            
            with c_label:
                # Align text vertically with input box
                st.markdown("<h3 style='margin-top: 5px; margin-bottom: 0;'>💬 Chat with Data:</h3>", unsafe_allow_html=True)
                
            with c_input:
                user_input = st.text_input("Message", placeholder="Ask 'What are the skills?'...", label_visibility="collapsed")
                
            with c_btn:
                submit_btn = st.form_submit_button("Send ➤")
            
            if submit_btn and user_input:
                st.session_state['chat_history'].append({"role": "user", "content": user_input})
                
                # Logic
                prompt_lower = user_input.lower()
                bot_reply = "I didn't understand. Try asking about Score, Skills, or Education."
                if "score" in prompt_lower or "marks" in prompt_lower:
                    bot_reply = f"The candidate scored **{res['score']}/100**."
                elif "skill" in prompt_lower:
                    bot_reply = f"Skills found: **{', '.join(res['skills'])}**."
                elif "education" in prompt_lower or "degree" in prompt_lower:
                    bot_reply = f"Education: **{res['education']}** (10th: {res['10th']}, 12th: {res['12th']})."
                elif "reason" in prompt_lower or "status" in prompt_lower:
                    bot_reply = f"Status: **{res['reason']}**."
                elif "email" in prompt_lower:
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', st.session_state['resume_text'])
                    bot_reply = f"Email: **{email_match.group(0)}**" if email_match else "No email found."
                
                st.session_state['chat_history'].append({"role": "assistant", "content": bot_reply})
                st.rerun()

        # --- CHAT RESPONSES (Shown Below the Bar) ---
        # Show only the last exchange or full history
        if st.session_state['chat_history']:
            for msg in reversed(st.session_state['chat_history']): # Newest first
                bubble_color = "#E3F2FD" if msg["role"] == "assistant" else "#F5F5F5"
                border_color = "#2196F3" if msg["role"] == "assistant" else "#9E9E9E"
                align = "left" 
                
                st.markdown(f"""
                <div style='background-color: {bubble_color}; padding: 10px; border-radius: 10px; 
                            border-left: 5px solid {border_color}; margin-bottom: 10px;'>
                    <b>{'🤖 AI' if msg['role'] == 'assistant' else '👤 HR'}:</b> {msg['content']}
                </div>
                """, unsafe_allow_html=True)

    # --- DATABASE LIST ---
    st.divider()
    st.markdown("### 🗂️ Candidate Database")
    if st.checkbox("Show Candidate Management List"):
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if df.empty: st.info("No data yet.")
            else:
                for index, row in df.iterrows():
                    status_color = "#4CAF50" if "Selected" in row['reason'] else "#FF9800" if "Waitlist" in row['reason'] else "#F44336"
                    with st.container():
                        st.markdown(f"""<div class="candidate-card" style="border-left: 8px solid {status_color};"><h4 style="margin:0; color:black;">👤 {row['name']}</h4></div>""", unsafe_allow_html=True)
                        c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
                        with c1: st.write(f"**{row['score']}/100**")
                        with c2: st.write(f"{row['reason']}")
                        with c3:
                            with st.expander("Details"):
                                st.write(f"**Edu:** {row['education']}\n**Skills:** {row['skills']}")
                        with c4:
                            if st.button("🗑️", key=f"del_{index}"):
                                delete_candidate(row['name'])
                                st.rerun()
                st.download_button("📥 CSV", df.to_csv(index=False).encode('utf-8'), "candidates.csv", "text/csv")
        except Exception as e: st.error(str(e))
        finally: conn.close()

if not st.session_state['logged_in']: login_page()
else: main_tool()
