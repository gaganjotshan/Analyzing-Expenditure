import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pathlib import Path
import yaml  # Import PyYAML for loading YAML files

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.Finance_Analytics import logger
from src.Finance_Analytics.data_ingestion.scraper import FinancialDataScraper
from src.Finance_Analytics.data_processing.transformer import process_files
from src.Finance_Analytics.data_processing.cleaner import DataCleaner
from airflow.configuration import conf
from sqlalchemy import create_engine
import pandas as pd

def load_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Load configuration
config_file = '/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/config/path_config.yaml'
config = load_config(config_file)

# Get the SQL Alchemy connection string from the Airflow configuration
sql_alchemy_conn = conf.get("database", "sql_alchemy_conn")

# Define paths from config
RAW_DATA_DIR = Path(config['paths']['raw_data_dir']) / "expenditure_analysis"
PROCESSED_DATA_DIR = Path(config['paths']['processed_data_dir']) / "expenditure_analysis"
FINAL_DATA_DIR = Path(config['paths']['final_data_dir']) / "expenditure_analysis"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3, 
    'retry_delay': timedelta(minutes=5),  
}

dag = DAG(
    'expenditure_data_pipeline',
    default_args=default_args,
    description='Ingest, transform, clean, and load expenditure data',
    schedule_interval=timedelta(days=1),
)

def scrape_financial_data():
    logger.info("Starting data scraping")
    scraper = FinancialDataScraper()
    scraper.download_tables()
    logger.info("Data scraping completed")

def transform_and_clean_data():
    logger.info("Starting data transformation and cleaning")
    
    # Transform data
    all_dataframes, skipped_files = process_files(RAW_DATA_DIR)
    
    if skipped_files:
        logger.warning("The following files were skipped during transformation:")
        for filename, reason in skipped_files:
            logger.warning(f"{filename}: {reason}")
    
    # Clean data
    cleaner = DataCleaner()
    cleaner.clean_all_files()
    
    logger.info("Data transformation and cleaning completed")

def load_to_postgres():
    logger.info("Starting data loading to PostgreSQL")
    engine = create_engine(sql_alchemy_conn)
    
    # Create master table for expenditure categories
    with engine.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenditure_master (
                id SERIAL PRIMARY KEY,
                exp_category VARCHAR(255) UNIQUE NOT NULL
            );
        """)
    
    # Load cleaned data into PostgreSQL
    total_rows = 0
    
    for file in FINAL_DATA_DIR.glob("*_cleaned.csv"):
        df = pd.read_csv(file)
        category = file.stem.replace("_cleaned", "")
        
        # Insert category into master table
        with engine.connect() as conn:
            conn.execute(f"""
                INSERT INTO expenditure_master (exp_category) 
                VALUES ('{category}') 
                ON CONFLICT (exp_category) DO NOTHING;
            """)
        
        # Load data into main table
        df.to_sql('cleaned_expenditure', engine, if_exists='append', index=False)
        total_rows += len(df)
        logger.info(f"Loaded {file.name} into PostgreSQL")
    
    logger.info(f"Total rows loaded: {total_rows}")
    logger.info("Data loading to PostgreSQL completed")

# Define tasks
scrape_task = PythonOperator(
    task_id='scrape_financial_data',
    python_callable=scrape_financial_data,
    dag=dag,
    execution_timeout=timedelta(minutes=30),
)

transform_and_clean_task = PythonOperator(
    task_id='transform_and_clean_data',
    python_callable=transform_and_clean_data,
    dag=dag,
    execution_timeout=timedelta(minutes=30),
)

load_task = PythonOperator(
    task_id='load_to_postgres',
    python_callable=load_to_postgres,
    dag=dag,
    execution_timeout=timedelta(minutes=30),
)

# Set task dependencies
scrape_task >> transform_and_clean_task >> load_task