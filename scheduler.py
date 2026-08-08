import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
import etl_pipeline

def run_scheduled_etl():
    print("\n" + "="*65)
    print(" [SCHEDULER] Triggering 15-Minute Automated ETL Refresh...")
    print("="*65)
    try:
        # Executes main ETL pipeline logic
        if hasattr(etl_pipeline, 'main'):
            etl_pipeline.main()
        else:
            os.system("python etl_pipeline.py")
            
        print(" [SCHEDULER] ETL Refresh Completed Successfully!")
    except Exception as e:
        print(f" [SCHEDULER ERROR] Failed to run ETL pipeline: {e}")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    
    # Schedule job to run every 15 minutes
    scheduler.add_job(run_scheduled_etl, 'interval', minutes=15)
    scheduler.start()

    print("="*65)
    print("   AUTOMATED ETL SCHEDULER STARTED (Interval: 15 minutes)   ")
    print("   Press Ctrl+C in this terminal to stop the scheduler.     ")
    print("="*65)

    # Run initial pipeline execution immediately upon starting
    run_scheduled_etl()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\n[SCHEDULER] Background task stopped.")