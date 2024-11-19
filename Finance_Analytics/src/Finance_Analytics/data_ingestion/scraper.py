import sys
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd  

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

class RBIDataScraper:
    def __init__(self):
        self.url = "https://rbi.org.in/scripts/OccasionalPublications.aspx?head=Handbook%20of%20Statistics%20on%20State%20Government%20Finances%20-%202010"
        self.tables_to_download = {
            # Essential tables for Expenditure Analysis Dashboard
            'Aggregate_Expenditure': 'Table 14 : Aggregate Expenditure',
            'Revenue_Expenditure': 'Table 15 : Revenue Expenditure',
            'Capital_Expenditure': 'Table 19 : Capital Expenditure',
            'Social_Sector_Expenditure': 'Table 22 : Social Sector Expenditure',
            
            # Supporting tables for Expenditure Analysis Dashboard
            'Interest_Payments': 'Table 16 : Interest Payments',
            'Pension': 'Table 17 : Pension',
            'Administrative_Services': 'Table 18 : Administrative Services',
            'Gross_Fiscal_Deficit': 'Table 1 : Gross Fiscal Deficit',
            
            # Additional tables for Anomaly Detection Model
            'Revenue_Deficit': 'Table 2 : Revenue Deficit',
            'Aggregate_Receipts': 'Table 4 : Aggregate Receipts',
            'Own_Tax_Revenue': 'Table 6 : Own Tax Revenue',
            'Capital_Receipts': 'Table 12 : Capital Receipts',
            'Revenue_Receipts': 'Table 5 : Revenue Receipts',
            'Market_Borrowings': 'Table 27 : Market Borrowings',
            'Outstanding_Liabilities': 'Table 28 : Composition of Outstanding Liabilities'
        }
        # Set absolute path for raw data directory
        self.raw_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/raw")
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def download_tables(self):
        logger.info(f"Accessing URL: {self.url}")
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for table_name, table_text in self.tables_to_download.items():
                self._download_single_table(soup, table_name, table_text)
            logger.info("All specified tables have been processed.")
        except requests.RequestException as e:
            logger.error(f"Error accessing the website: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def _download_single_table(self, soup, table_name, table_text):
        try:
            links = soup.find_all('a', string=table_text)
            if not links:
                logger.warning(f"No link found for table: {table_name}")
                return
            
            logger.info(f"Found {len(links)} links for {table_name}")
            
            for link in links:
                href = link.get('href', '')
                full_url = f'https://rbi.org.in/scripts/{href}' if href.startswith('PublicationsView.aspx') else f'https://rbi.org.in/{href}'
                
                logger.info(f"Checking link: {full_url}")
                
                self._find_and_download_excel_file(full_url, table_name)

        except Exception as e:
            logger.error(f"Unexpected error while processing {table_name}: {e}")

    def _find_and_download_excel_file(self, publication_url, table_name):
        try:
            response = requests.get(publication_url)
            response.raise_for_status()
            pub_soup = BeautifulSoup(response.content, 'html.parser')

            download_links = pub_soup.find_all('a', href=True)

            found_file = False

            for link in download_links:
                href = link['href']
                if any(ext in href.lower() for ext in ['.xls', '.xlsx']):
                    # Check if href starts with http or https
                    if not href.startswith('http'):
                        excel_file_url = 'https://rbidocs.rbi.org.in' + href
                    else:
                        excel_file_url = href
                    
                    logger.info(f"Found file for {table_name}: {excel_file_url}")

                    # Download the file
                    self._download_file(excel_file_url, table_name)
                    found_file = True
                    break
            
            if not found_file:
                logger.warning(f"No suitable Excel file found on publication page for {table_name}")

        except requests.RequestException as e:
            logger.error(f"Error accessing publication page for {table_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error accessing publication page for {table_name}: {e}")

    def _download_file(self, url, table_name):
        try:
            file_response = requests.get(url)
            file_response.raise_for_status()

            file_path = self.raw_data_dir / f'{table_name}.xls'  # Save as .xls initially
            
            with open(file_path, 'wb') as f:
                f.write(file_response.content)

            logger.info(f"Downloaded {table_name} to {file_path}")

            # Convert .xls files to .csv format
            self.convert_xls_to_csv(file_path)

        except requests.RequestException as e:
            logger.error(f"Error downloading {table_name}: {e}")

    def convert_xls_to_csv(self, xls_file_path):
        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(xls_file_path) 
            
            # Define the CSV file path based on the Excel filename
            csv_file_path = xls_file_path.with_suffix('.csv')
            
            # Save DataFrame to CSV
            df.to_csv(csv_file_path, index=False)
            
            logger.info(f"Converted {xls_file_path} to {csv_file_path}")
        except Exception as e:
            logger.error(f"Error converting XLS to CSV: {e}")

def main():
    scraper = RBIDataScraper()
    scraper.download_tables()

if __name__ == "__main__":
    main()