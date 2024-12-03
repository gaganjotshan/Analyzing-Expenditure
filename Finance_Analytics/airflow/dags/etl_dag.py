import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.Finance_Analytics.data_ingestion.scraper import FinancialDataScraper
from src.Finance_Analytics.data_processing.transformer import main as transform_data
from src.Finance_Analytics.data_processing.cleaner import DataCleaner
from airflow.configuration import conf

# Get the SQL Alchemy connection string from the new configuration
sql_alchemy_conn = conf.get("database", "sql_alchemy_conn")

# You can print or log this connection string for debugging purposes
print(f"SQL Alchemy Connection: {sql_alchemy_conn}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'expenditure_data_pipeline',
    default_args=default_args,
    description='Ingest, transform, and clean expenditure data',
    schedule_interval=timedelta(days=1),
)

# Extract data from the sources
def scrape_financial_data():
    scraper = FinancialDataScraper()
    scraper.download_tables()

scrape_task = PythonOperator(
    task_id='data_ingestion',
    python_callable=scrape_financial_data,
    dag=dag,
)

# Transform the data into clean csv format 
def process_data():
    # Step 1: Transform data
    transform_data()
    
    # Step 2: Clean data
    cleaner = DataCleaner()
    df = cleaner.load_data()
    cleaned_df = cleaner.clean_data(df)
    cleaner.save_cleaned_data(cleaned_df)

process_task = PythonOperator(
    task_id='data_processing',
    python_callable=process_data,
    dag=dag,
)

scrape_task >> process_task 