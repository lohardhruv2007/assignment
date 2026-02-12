import streamlit as st
import sqlite3
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Recruiter Portal",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Remove sidebar completely
st.sidebar.empty()

# ---------------- DATABASE ----------------
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

# ---------------- CSS ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #f3f7f0;
}

/* Title */
.title {
    text-align: center;
    font-size: 50px;
    font-weight: bold;
    margin-bottom: 40px;
    color: #1b3022;
}

/* Input container */
div[data-baseweb="input"] {
    background-color: white !important;
    border-radius: 12px !important;
}

/* Input field styling */
[data-testid="stTextInput"] > div {
    border: 2px solid #b7d8c0 !important;
    border-radius: 12px !important;
}

/* Pastel green text */
[data-testid="stTextInput"] input {
    color: #8fc7a5 !important;   /* Light pastel green */
    font-size: 18px !important;
}

/* Remove blue focus */
[data-testid="stTextInput"] > div:focus-within {
    border: 2px solid #6fbf8f !important;
    box-shadow: none !important;
}

/* Button */
.stButton > button {
    width: 100%;
    height: 50px;
    background-color: #6fbf8f;
    color: white;
    font-size: 18px;
    border-radius: 10px;
    border: none;
    margin-top: 15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="title">Recruiter Portal</div>', unsafe_allow_html=True)

    username = st.text_input("Username")

    # No type="password" so no eye icon
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
