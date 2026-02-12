import streamlit as st
import PyPDF2
import re
import sqlite3
import pytesseract
from pdf2image import convert_from_bytes
import io
from PIL import Image

# --- PAGE CONFIGURATION (Title & Icon) ---
st.set_page_config(page_title="Resume Screener AI", page_icon="📄")

# --- CUSTOM CSS FOR CREAM BACKGROUND ---
# Streamlit me background color direct option nahi hota, CSS inject krna padta hai
cream_css = """
<style>
    .stApp {
        background-color: #FFFDD0;
    }
    /* Text color fix for contrast */
    h1, h2, h3, h4, h5, h6, p, div, label {
        color: #333333 !important;
    }
    /* Button style */
    .stButton>button {
        background-color: #4CAF50;
        color: white !important;
        border-radius: 10px;
    }
</style>
"""
st.markdown(cream_css, unsafe_allow_html=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
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
    except Exception as e:
        st.error(f"Database Error: {e}")
    conn.close()

# --- TEXT EXTRACTION LOGIC ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        # Streamlit file object ko direct read kar sakte hain
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        
        # Read First 3 Pages
        for page in pdf_reader.pages[:3]:
            content = page.extract_text()
            if content:
                text += content + " "
        
        # OCR Fallback (Agar text kam hai)
        if len(text.strip()) < 50:
            st.warning("⚠️ Scanned PDF detected! Applying OCR (this might take a few seconds)...")
            uploaded_file.seek(0)  # File pointer reset
            # Bytes me convert karke OCR lagayenge
            images = convert_from_bytes(uploaded_file.read())
            for img in images[:2]: # Sirf pehle 2 page OCR ke liye (speed ke liye)
                text += pytesseract.image_to_string(img)
                
        return re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# --- SCORING LOGIC ---
def analyze_resume(text):
    res = {"education": "Other", "skills": [], "score": 25, "reason": ""}
    
    if not text:
        res["reason"] = "Rejected: Document unreadable."
        return res

    # Education
    has_degree = False
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering|Techno India|B\.E\.|M\.C\.A', text, re.I):
        res["education"] = "Technical Degree"
        res["score"] += 45
        has_degree = True

    # Skills
    skill_list = ["Python", "Java", "PHP", "MySQL", "JavaScript", "HTML", "CSS", "Node", "Git", "React", "AWS", "Machine Learning"]
    found_skills = []
    for skill in skill_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.I):
            found_skills.append(skill)
            res["score"] += 5
    
    res["skills"] = list(set(found_skills)) # Remove duplicates
    res["score"] = min(res["score"], 100)

    # Decision
    if res["score"] >= 70:
        res["reason"] = "Selected: Strong Profile"
    elif res["score"] >= 40:
        res["reason"] = "Waitlist: Average Profile"
    else:
        res["reason"] = "Rejected: Low Match"
    
    return res

# --- MAIN APP UI ---
init_db()

st.title("📄 AI Resume Screener")
st.markdown("**Upload a Resume (PDF) to check eligibility instantly.**")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing... Please wait..."):
            # Process
            text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume(text)
            
            # Save to DB
            save_candidate(uploaded_file.name, result['score'], result['education'], result['skills'], result['reason'])
            
            # Display Result
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Score", value=f"{result['score']}/100")
            with col2:
                status_color = "green" if result['score'] >= 70 else "orange" if result['score'] >= 40 else "red"
                st.markdown(f"### Status: :{status_color}[{result['reason']}]")
            
            st.subheader("Details Found:")
            st.write(f"**Education:** {result['education']}")
            st.write(f"**Skills:** {', '.join(result['skills']) if result['skills'] else 'None detected'}")
            
            st.success("✅ Candidate saved to database successfully!")

# Optional: Show Database Data
if st.checkbox("Show All Candidates Data"):
    conn = sqlite3.connect('candidates.db')
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    st.dataframe(df)
    conn.close()
