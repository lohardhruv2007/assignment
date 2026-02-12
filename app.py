import streamlit as st
import sqlite3
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Recruiter Portal",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Completely disable sidebar
st.sidebar.empty()

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- CLEAN CSS ----------------
st.markdown("""
<style>

/* Remove top padding */
.block-container {
    padding-top: 3rem;
}

/* Background */
.stApp {
    background-color: #f3f7f0;
}

/* Title style */
.title {
    text-align: center;
    font-size: 50px;
    font-weight: bold;
    margin-bottom: 40px;
    color: #1b3022;
}

/* Remove blue background */
div[data-baseweb="input"] {
    background-color: white !important;
    border-radius: 10px !important;
}

/* Remove default blue focus glow */
input {
    background-color: white !important;
    box-shadow: none !important;
    border: none !important;
}

/* Custom input border */
[data-testid="stTextInput"] > div {
    border: 2px solid #c8d6cc !important;
    border-radius: 10px !important;
}

/* On focus border */
[data-testid="stTextInput"] > div:focus-within {
    border: 2px solid #4f6d5a !important;
}

/* Button style */
.stButton > button {
    width: 100%;
    height: 50px;
    background-color: #4f6d5a;
    color: white;
    font-size: 18px;
    border-radius: 8px;
    border: none;
    margin-top: 15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="title">Recruiter Portal</div>', unsafe_allow_html=True)

    username = st.text_input("Username")

    # 🔴 NOT using type="password" → so NO eye icon
    password = st.text_input("Password")

    if st.button("Login"):
        if username == "admin" and password == "hr123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- DASHBOARD ----------------
else:

    st.markdown('<div class="title">Dashboard</div>', unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.success("Welcome to Recruiter Dashboard ✅")

    conn = sqlite3.connect("candidates.db")
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    conn.close()

    if df.empty:
        st.info("No candidates found.")
    else:
        st.dataframe(df, use_container_width=True)
