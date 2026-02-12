# --- CLASSIC PASTEL UI CUSTOMIZATION ---
st.markdown("""
    <style>
    /* 1. Global Background & Classical Font */
    .main {
        background: linear-gradient(135deg, #f0f4f1 0%, #d9e4dd 100%);
        font-family: 'Times New Roman', Times, serif;
    }

    /* 2. Professional Pastel Cards */
    .stmarkdown, .card, [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(46, 125, 50, 0.1);
        border: 1px solid #c8d6cc;
        margin-bottom: 20px;
    }

    /* 3. Typography: Times New Roman */
    h1, h2, h3, p, span, div, label {
        font-family: 'Times New Roman', Times, serif !important;
        color: #2d3e33 !important;
    }

    h1 { font-weight: bold; color: #1b3022 !important; }

    /* 4. Sidebar Styling (Light Mint) */
    section[data-testid="stSidebar"] {
        background-color: #eef2ef;
        border-right: 1px solid #c8d6cc;
    }

    /* 5. Elegant Button Styling (Deep Forest Green) */
    .stButton>button {
        background-color: #4f6d5a;
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-family: 'Times New Roman', Times, serif;
        font-weight: bold;
        letter-spacing: 0.5px;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #3a5142;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        color: #ffffff !important;
    }

    /* 6. Metrics Design */
    [data-testid="stMetricValue"] {
        color: #4f6d5a !important;
        font-family: 'Times New Roman', Times, serif;
    }
    </style>
    """, unsafe_allow_html=True)
