# 🏀 WNBA Live Analytics & Predictive AI Pipeline

An automated, end-to-end Big Data & AI Engineering pipeline for WNBA game analytics. This system extracts live WNBA data, cleans and stages it into a PostgreSQL relational database, builds predictive Machine Learning models (Random Forest vs Linear Regression), serves an interactive Tableau Public dashboard, and provides a plain-English Text-to-SQL AI Assistant powered by Groq API.

---

## 📑 1. Data Dictionary (`wnba_analytics_view`)
# 🏀 WNBA Live Analytics & Predictive AI Pipeline

An automated, end-to-end Big Data & AI Engineering pipeline for WNBA game analytics. This system extracts live WNBA data, cleans and stages it into a PostgreSQL relational database, builds predictive Machine Learning models (Random Forest vs Linear Regression), serves an interactive Tableau Public dashboard, and provides a plain-English Text-to-SQL AI Assistant powered by Groq API.

---

## 📑 1. Data Dictionary (`wnba_analytics_view`)

| Column Name | Data Type | Description |
| `game_id` | `INTEGER` | Unique identifier for each individual WNBA match. |
| `season` | `INTEGER` | The WNBA season year (e.g., 2024). |
| `home_team` | `VARCHAR` | Name of the home team (e.g., Dallas Wings, Las Vegas Aces). |
| `visitor_team` | `VARCHAR` | Name of the visiting/away team. |
| `home_team_score` | `INTEGER` | Points scored by the home team. |
| `visitor_team_score`| `INTEGER` | Points scored by the visiting team. |
| `pts_total` | `INTEGER` | Total combined match score (`home_team_score` + `visitor_team_score`). |
| `point_diff` | `INTEGER` | Point differential (`home_team_score` - `visitor_team_score`). |
| `home_win` | `INTEGER` | Binary indicator (`1` if home team won, `0` if home team lost). |
| `field_goal_pct` | `NUMERIC` | Field goal shooting efficiency percentage. |
| `turnovers` | `INTEGER` | Total match turnovers recorded. |

---

## 🔄 2. Data Flow Architecture

┌─────────────────────────┐
                   │   WNBA REST Data API    │
                   └────────────┬────────────┘
                                │ (Requests / JSON)
                                ▼
                   ┌─────────────────────────┐
                   │  etl_pipeline.py (ETL)  │ ◄─── Driven by scheduler.py
                   └────────────┬────────────┘
                                │ (Cleaned Data Ingestion)
                                ▼
                   ┌─────────────────────────┐
                   │ PostgreSQL Database     │
                   │ (wnba_analytics_view)   │
                   └──────┬───────────┬──────┘
                          │           │
       ┌──────────────────┘           └──────────────────┐
       ▼                                                 ▼
┌──────────────────────┐                         ┌───────────────────────┐
│ machine_learning.py  │                         │   ai_assistant.py     │
│ (Random Forest ML)   │                         │ (Groq LLM Text-to-SQL)│
└──────────┬───────────┘                         └───────────────────────┘
│ (Predictions CSV)
▼
┌──────────────────────┐
│  Tableau Dashboard   │
│  (Tableau Public)    │
└──────────────────────┘


1. **Extract & Load:** `etl_pipeline.py` extracts raw JSON game stats from the API, logs validation checks to `pipeline.log`, and stages clean rows into PostgreSQL (`wnba_analytics_view`).
2. **Predictive Modeling:** `machine_learning.py` pulls clean game metrics from PostgreSQL, trains Linear Regression and Random Forest Regressors, checks for overfitting (`max_depth=6`), and exports predictions to `wnba_ml_predictions.csv`.
3. **Visualization:** Tableau Public connects to the generated CSV feeds to display interactive dashboards (Avg Home Points, ML Actual vs Predicted, Home-Court Advantage).
4. **AI Assistant:** `ai_assistant.py` receives natural language questions from the user, translates them to SQL queries using Groq API (`llama-3.3-70b-versatile`), executes the SQL against PostgreSQL, and converts the raw DB output back into a human-friendly response.

---

## 🚀 3. Installation & Setup Guide

### Prerequisites
* Python 3.10+
* PostgreSQL Database Server
* Groq API Key (Free at [console.groq.com](https://console.groq.com))

### Environment Setup
1. Clone or navigate to the project directory:
   ```cmd
   cd D:\Downloads\BIGDATA-FINAL\WNBA-etl
Activate the virtual environment:

DOS
etlb-venv\Scripts\activate.bat
Install required packages:

DOS
pip install -r requirements.txt
Create a .env file in the root directory with your credentials:

Code snippet
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wnba_bigdata_db
GROQ_API_KEY=gsk_your_groq_api_key
⚙️ 4. Running the Components
Run Data Ingestion & ETL:

DOS
python etl_pipeline.py
Run ML Training & Overfitting Checks:

DOS
python machine_learning.py
Launch Automated Scheduler:

DOS
python scheduler.py
Launch AI Assistant CLI:

DOS
python ai_assistant.py
Run Automated Unit Tests (pytest):

DOS
pytest -v test_pipeline.py
📊 5. Published Tableau Dashboard
Live Dashboard Link: https://public.tableau.com/authoring/WNBALiveAnalyticsMLDashboard/Dashboard1#1
