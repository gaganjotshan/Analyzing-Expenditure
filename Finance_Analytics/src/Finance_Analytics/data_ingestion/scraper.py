import time
import sys
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import yaml
from pathlib import Path

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

def load_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

class FinancialDataScraper:
    def __init__(self, config_file='/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/config/path_config.yaml', download_categories=["expenditure_analysis"]):
        # Load configurations
        config = load_config(config_file)

        self.url = "https://rbi.org.in/scripts/OccasionalPublications.aspx?head=Handbook%20of%20Statistics%20on%20State%20Government%20Finances%20-%202010"
        self.tables_to_download = {
            "expenditure_analysis": {
                'Aggregate_Expenditure': 'Table 14 : Aggregate Expenditure',
                'Revenue_Expenditure': 'Table 15 : Revenue Expenditure',
                'Capital_Expenditure': 'Table 19 : Capital Expenditure',
                'Social_Sector_Expenditure': 'Table 22 : Social Sector Expenditure',
                'Gross_Fiscal_Deficit': 'Table 1 : Gross Fiscal Deficit',
                'Revenue_Deficit': 'Table 2 : Revenue Deficit',
                'Own_Tax_Revenue': 'Table 6 : Own Tax Revenue'
            },
            "anomaly_detection": {
                'Aggregate_Receipts': 'Table 4 : Aggregate Receipts',
                'Capital_Receipts': 'Table 12 : Capital Receipts',
                'Revenue_Receipts': 'Table 5 : Revenue Receipts',
                'Market_Borrowings': 'Table 27 : Market Borrowings',
                'Outstanding_Liabilities': 'Table 28 : Composition of Outstanding Liabilities'
            }
        }

        # Set absolute path for raw data directory from config
        self.download_categories = download_categories
        self.raw_data_dir = Path(config['paths']['raw_data_dir'])
        self.expenditure_analysis_dir = self.raw_data_dir / "expenditure_analysis"
        self.anomaly_detection_dir = self.raw_data_dir / "anomaly_detection"
        
        # Create directories if they don't exist
        self.expenditure_analysis_dir.mkdir(parents=True, exist_ok=True)
        self.anomaly_detection_dir.mkdir(parents=True, exist_ok=True)

    def download_tables(self):
        logger.info(f"Accessing URL: {self.url}")
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(self.url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for task in self.download_categories:
                    if task in self.tables_to_download:
                        for table_name, table_text in self.tables_to_download[task].items():
                            self._download_single_table(soup, table_name, table_text, task)
                
                logger.info("All specified tables have been processed.")
                break
            
            except requests.RequestException as e:
                if attempt < retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed. Retrying...")
                    time.sleep(5)
                else:
                    logger.error(f"Error accessing the website: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    def _download_single_table(self, soup, table_name, table_text, task):
        try:
            links = soup.find_all('a', string=table_text)
            if not links:
                logger.warning(f"No link found for table: {table_name}")
                return
            
            logger.info(f"Found {len(links)} links for {table_name}")
            
            for link in links:
                href = link.get('href', '')
                full_url = urljoin('https://rbi.org.in/scripts/', href)
                
                logger.info(f"Checking link: {full_url}")
                
                self._find_and_download_excel_file(full_url, table_name, task)

        except Exception as e:
            logger.error(f"Unexpected error while processing {table_name}: {e}")

    def _find_and_download_excel_file(self, publication_url, table_name, task):
        try:
            response = requests.get(publication_url, timeout=30)
            response.raise_for_status()
            pub_soup = BeautifulSoup(response.content, 'html.parser')

            download_links = pub_soup.find_all('a', href=True)

            found_file = False

            for link in download_links:
                href = link['href']
                if any(ext in href.lower() for ext in ['.xls', '.xlsx']):
                    excel_file_url = urljoin('https://rbidocs.rbi.org.in', href)
                    
                    logger.info(f"Found file for {table_name}: {excel_file_url}")

                    self._download_file(excel_file_url, table_name, task)
                    found_file = True
                    break
            
            if not found_file:
                logger.warning(f"No suitable Excel file found on publication page for {table_name}")

        except requests.RequestException as e:
            logger.error(f"Error accessing publication page for {table_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error accessing publication page for {table_name}: {e}")

    def _download_file(self, url, table_name, task):
        retries = 3
        for attempt in range(retries):
            try:
                file_response = requests.get(url, timeout=30)
                file_response.raise_for_status()
                
                if task == "expenditure_analysis":
                    file_path = self.expenditure_analysis_dir / f'{table_name}.xls'
                else:
                    file_path = self.anomaly_detection_dir / f'{table_name}.xls'
                    
                with open(file_path, 'wb') as f:
                    f.write(file_response.content)
                    
                logger.info(f"Downloaded {table_name} to {file_path}")
                
                # Convert to CSV after downloading
                self.convert_xls_to_csv(file_path)
                
                return
            
            except requests.RequestException as e:
                logger.error(f"Error downloading {table_name}: {e}")
                
                if attempt < retries - 1:
                    logger.info(f"Retrying download for {table_name} (attempt {attempt + 1})...")
                    time.sleep(5) 
            except Exception as e:
                logger.error(f"Unexpected error while downloading file: {e}")

    def convert_xls_to_csv(self, xls_file_path):
        try:
            df = pd.read_excel(xls_file_path) 
            csv_file_path = xls_file_path.with_suffix('.csv')
            df.to_csv(csv_file_path, index=False)
            logger.info(f"Converted {xls_file_path} to {csv_file_path}")
        except Exception as e:
            logger.error(f"Error converting XLS to CSV: {e}")

def main():
    scraper = FinancialDataScraper(download_categories=["expenditure_analysis"])
    scraper.download_tables()

if __name__ == "__main__":
    main()