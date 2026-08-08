import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load database credentials from .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wnba_bigdata_db")

# SQLAlchemy connection
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def run_eda():
    # Query data directly from our clean SQL view
    df = pd.read_sql("SELECT * FROM wnba_analytics_view", engine)
    
    print("="*65)
    print(" 1. DATASET OVERVIEW & SUMMARY STATISTICS")
    print("="*65)
    print(f"Total Rows (Games Analyzed): {df.shape[0]}")
    print(f"Total Columns:              {df.shape[1]}")
    print("\nColumn Data Types:")
    print(df.dtypes)
    
    print("\nMissing Values Count per Column:")
    print(df.isnull().sum())
    
    print("\nNumerical Feature Breakdown:")
    print(df[['home_team_score', 'visitor_team_score', 'pts_total', 'point_diff', 'field_goal_pct', 'turnovers']].describe())
    
    print("\n" + "="*65)
    print(" 2. CATEGORICAL BREAKDOWN & HOME ADVANTAGE")
    print("="*65)
    print("Games Played per Home Team:")
    print(df['home_team'].value_counts())
    
    home_win_pct = df['home_win'].mean() * 100
    print(f"\nHome Court Advantage: Home teams won {home_win_pct:.2f}% of matches.")
    
    print("\n" + "="*65)
    print(" 3. CORRELATION WITH TOTAL MATCH POINTS (pts_total)")
    print("="*65)
    numeric_df = df.select_dtypes(include=['number'])
    correlations = numeric_df.corr()['pts_total'].sort_values(ascending=False)
    print(correlations)

    print("\n" + "="*65)
    print(" 4. PLAIN-LANGUAGE EDA SUMMARY")
    print("="*65)
    print(
        f"Summary: The dataset contains {len(df)} cleaned WNBA game records.\n"
        f"The average combined game score across all matches is {df['pts_total'].mean():.1f} points.\n"
        f"Home teams maintained a win rate of {home_win_pct:.1f}%.\n"
        f"Individual team scoring is the strongest predictor of total game points,\n"
        f"while turnover volume displays minor variance across team performances."
    )
    print("="*65)

if __name__ == "__main__":
    run_eda()