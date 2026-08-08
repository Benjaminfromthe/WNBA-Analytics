import os
import threading
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from google import genai

# ==========================================
# 1. BACKGROUND SCHEDULER INITIALIZATION
# ==========================================
@st.cache_resource
def start_background_scheduler():
    """
    Launches scheduler.py in a background thread so the ETL pipeline 
    runs continuously without blocking or restarting during Streamlit interactions.
    """
    def run_scheduler():
        try:
            print("🚀 [Streamlit Thread] Starting background ETL scheduler...")
            import scheduler
        except Exception as e:
            print(f"❌ [Streamlit Thread] Error running background scheduler: {e}")

    # Create and start a daemon thread
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread

# Start the background scheduler once
start_background_scheduler()


# ==========================================
# 2. STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="WNBA Analytics AI", page_icon="🏀", layout="wide")

st.title("🏀 WNBA Analytics & AI Insights")
st.caption("Live ETL Pipeline Monitoring & AI Assistant")

st.divider()

# ==========================================
# 3. DATABASE PREVIEW SECTION
# ==========================================
st.subheader("📊 Live ETL Data Preview")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")
DB_NAME = os.getenv("DB_NAME", "postgres")

if DB_HOST and DB_USER and DB_PASSWORD:
    try:
        # Construct PostgreSQL / Supabase connection URL
        db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_url)
        
        # Pull latest rows from your raw table
        df = pd.read_sql("SELECT * FROM wnba_games_raw ORDER BY created_at DESC LIMIT 5", engine)
        st.dataframe(df, use_container_width=True)
        st.success("Connected to database successfully!")
    except Exception as e:
        st.warning(f"Could not load live database preview: {e}")
else:
    st.info("Database connection environment variables are missing or incomplete.")

st.divider()

# ==========================================
# 4. INTERACTIVE GEMINI AI ASSISTANT
# ==========================================
st.subheader("💬 Ask WNBA AI Assistant")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY environment variable. Please configure it in Railway.")
else:
    client = genai.Client(api_key=api_key)

    # Maintain chat history state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle user prompt
    if prompt := st.chat_input("Ask about recent WNBA player stats, ETL pipeline status, or predictions..."):
        # Display user input
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Gemini response
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a WNBA sports analytics expert. Answer this query based on player data: {prompt}"
            )
            reply = response.text
        except Exception as err:
            reply = f"Error generating response: {err}"

        # Display AI output
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})