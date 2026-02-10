# ... (Baaki code same rahega, sirf Database wale part mein ye change karein)

elif st.session_state['page'] == "Database":
    st.header("📂 Candidate Pool & Intelligent Insights")
    conn = sqlite3.connect('candidates.db')
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    
    if not df.empty:
        # Ranking ke saath reason column bhi dikhayenge
        st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
        
        # Ek sundar summary card
        st.subheader("Decision Breakdown")
        for index, row in df.iterrows():
            with st.expander(f"Details for {row['name']} (Score: {row['score']})"):
                st.write(f"**Status:** {row['reason']}")
                st.write(f"**Skills Found:** {row['skills']}")
    
    # ... (Delete button wala code same rahega)
