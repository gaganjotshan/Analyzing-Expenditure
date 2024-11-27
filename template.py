import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = "Finance_Analytics"

# List of files and directories to be created
list_of_files = [
    ".github/workflows/.gitkeep",
    "artifacts/.gitkeep",
    "artifacts/models/.gitkeep",
    "artifacts/plots/.gitkeep",
    "artifacts/HTML-reports/.gitkeep",
    "artifacts/logs/.gitkeep",
    f"src/{project_name}/__init__.py",
    f"src/{project_name}/data_ingestion/__init__.py",
    f"src/{project_name}/data_ingestion/scraper.py",
    f"src/{project_name}/data_processing/__init__.py",
    f"src/{project_name}/data_processing/cleaner.py",
    f"src/{project_name}/data_processing/transformer.py",
    f"src/{project_name}/data_analysis/__init__.py",
    f"src/{project_name}/data_analysis/eda.py",
    f"src/{project_name}/visualization/__init__.py",
    f"src/{project_name}/visualization/dashboard.py",
    f"src/{project_name}/utils/__init__.py",
    f"src/{project_name}/utils/config.py",
    f"src/{project_name}/utils/logger.py",
    "airflow/dags/__init__.py",
    "airflow/dags/data_ingestion_dag.py",
    "airflow/dags/data_processing_dag.py",
    "airflow/dags/data_analysis_dag.py",
    "airflow/plugins/__init__.py",
    "airflow/plugins/custom_operators/__init__.py",
    "airflow/config/airflow.cfg",
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
    "data/final/.gitkeep",
    "notebooks/exploratory_data_analysis.ipynb",
    "tests/__init__.py",
    "tests/test_data_ingestion.py",
    "tests/test_data_processing.py",
    "tests/test_data_analysis.py",
    "docs/project_structure.md",
    "docs/data_dictionary.md",
    "docs/airflow_setup.md",
    "config/config.yaml",
    "requirements.txt",
    "setup.py",
    "templates/index.html",
    "README.md",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml"
]

for filepath in list_of_files:
    filepath = Path(project_name) / filepath
    filedir, filename = os.path.split(filepath)
    
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")
    
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
        logging.info(f"Creating empty file: {filepath}")
    
    else:
        logging.info(f"{filename} already exists")


logging.info("Project structure created successfully!")