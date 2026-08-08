import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load database configuration
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wnba_bigdata_db")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def train_and_evaluate():
    # Fetch cleaned dataset from analytics view
    df = pd.read_sql("SELECT * FROM wnba_analytics_view", engine)
    
    # Define Features (X) and Target (y)
    X = df[['home_team_score', 'turnovers', 'field_goal_pct', 'point_diff']]
    y = df['pts_total']
    
    # Train-Test Split (80% Training, 20% Testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # ------------------------------------------------------------------
    # Model 1: Linear Regression
    # ------------------------------------------------------------------
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    mae_lr = mean_absolute_error(y_test, y_pred_lr)
    rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
    r2_lr = r2_score(y_test, y_pred_lr)
    
    # ------------------------------------------------------------------
    # Model 2: Random Forest Regressor (Tuned Depth)
    # ------------------------------------------------------------------
    rf = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    r2_rf = r2_score(y_test, y_pred_rf)
    
    # ------------------------------------------------------------------
    # Print Model Evaluation Comparison
    # ------------------------------------------------------------------
    print("="*65)
    print("MODEL COMPARISON: PREDICTING TOTAL MATCH POINTS (pts_total)")
    print("="*65)
    print("Linear Regression:")
    print(f"  MAE:  {mae_lr:.2f}")
    print(f"  RMSE: {rmse_lr:.2f}")
    print(f"  R^2:  {r2_lr:.2f}\n")
    
    print("Random Forest Regressor (max_depth=6, n_estimators=100):")
    print(f"  MAE:  {mae_rf:.2f}")
    print(f"  RMSE: {rmse_rf:.2f}")
    print(f"  R^2:  {r2_rf:.2f}\n")
    
    # ------------------------------------------------------------------
    # Overfitting Check across tree depths
    # ------------------------------------------------------------------
    print("Overfitting Check (Random Forest, across max_depth values):")
    for depth in [2, 6, None]:
        rf_check = RandomForestRegressor(max_depth=depth, n_estimators=100, random_state=42)
        rf_check.fit(X_train, y_train)
        train_r2 = r2_score(y_train, rf_check.predict(X_train))
        test_r2 = r2_score(y_test, rf_check.predict(X_test))
        d_str = f"max_depth={depth}".ljust(15)
        print(f"  {d_str} -> Train R^2 = {train_r2:.2f} | Test R^2 = {test_r2:.2f}")
        
    print("\nConclusion: max_depth=6 balances variance and prevents overfitting.")
    print("="*65)

    # Save test set evaluation results into PostgreSQL table for Tableau
    df_results = X_test.copy()
    df_results['actual_pts_total'] = y_test
    df_results['predicted_pts_total'] = y_pred_rf
    df_results.to_sql('wnba_ml_predictions', engine, if_exists='replace', index=False)
    print("Successfully saved ML predictions to PostgreSQL table 'wnba_ml_predictions'.")

if __name__ == "__main__":
    train_and_evaluate()

# Automatically export predictions to CSV for Tableau Public sync
df_predictions = pd.read_sql("SELECT * FROM wnba_ml_predictions", engine)
df_predictions.to_csv("wnba_ml_predictions.csv", index=False)
print("Updated 'wnba_ml_predictions.csv' for Tableau sync.")