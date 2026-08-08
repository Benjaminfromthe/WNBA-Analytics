import os
import threading
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import google.generativeai as genai

# ==========================================
# 1. BACKGROUND SCHEDULER INITIALIZATION
# ==========================================
@st.cache_resource
def start_background_scheduler():
    """
    Launches scheduler.py in a background thread so the ETL pipeline 
    runs continuously in the cloud alongside Streamlit.
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

# Start the background ETL job once
start_background_scheduler()


# ==========================================
# 2. STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="WNBA Analytics AI", 
    page_icon="🏀", 
    layout="wide"
)

st.title("🏀 WNBA Analytics & AI Insights")
st.caption("Live Cloud ETL Pipeline Monitoring & AI Analytics Assistant")

st.divider()

# ==========================================
# 3. LIVE DATABASE PREVIEW SECTION
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
        
        # Safely fetch recent 5 rows from raw staging table
        df = pd.read_sql("SELECT * FROM wnba_games_raw LIMIT 5", engine)
        
        st.dataframe(df, use_container_width=True)
        st.success("Connected to database successfully!")
    except Exception as e:
        st.warning(f"Could not load live database preview: {e}")
else:
    st.info("Database credentials missing or incomplete in environment variables.")

st.divider()

# ==========================================
# 4. INTERACTIVE AI ASSISTANT SECTION
# ==========================================
st.subheader("💬 Ask WNBA AI Assistant")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY environment variable. Please check Railway settings.")
else:
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Maintain chat session state across user inputs
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Render previous conversation history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User chat input prompt box
        if prompt := st.chat_input("Ask about recent WNBA player stats, ETL status, or insights..."):
            # Display user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Query Gemini model
            try:
                response = model.generate_content(
                    f"You are a professional WNBA sports analytics expert. "
                    f"Answer this prompt concisely and clearly: {prompt}"
                )
                reply = response.text
            except Exception as err:
                reply = f"Error generating AI response: {err}"

            # Display AI message
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as setup_err:
        st.error(f"Failed to initialize Gemini AI Client: {setup_err}")