import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from ydata_profiling import ProfileReport as prf
import sys
import os

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

class DataCleaner:
    def __init__(self):
        self.processed_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/processed/expenditure_analysis")
        self.final_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/final")
        self.artifacts_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/artifacts")
        self.html_reports_dir = self.artifacts_dir / "HTML-reports"
        self.plots_dir = self.artifacts_dir / "plots"

        # Create directories if they do not exist
        for dir in [self.final_data_dir, self.html_reports_dir, self.plots_dir]:
            dir.mkdir(parents=True, exist_ok=True)

    """
    def convert_xlsx_to_csv(self):
        logger.info("Converting expenditure.xlsx to expenditure.csv")
        xlsx_path = self.processed_data_dir / "expenditure.xlsx"
        csv_path = self.processed_data_dir / "expenditure.csv"
        
        if xlsx_path.exists():
            df = pd.read_excel(xlsx_path)
            df.to_csv(csv_path, index=False)
            logger.info(f"Converted {xlsx_path} to {csv_path}")
        else:
            logger.error(f"Excel file not found: {xlsx_path}")
    """

    def load_data(self):
        logger.info("Loading transformed data")
        file_path = self.processed_data_dir / "transformed_expenditure.csv"
    
        # First, read the CSV file without specifying dtypes
        df = pd.read_csv(file_path)
    
        # Replace '–' with NaN in the 'Value' column
        df.loc[:, 'Value'] = df['Value'].replace('–', np.nan)
    
        # Now convert the columns to the desired dtypes
        df['Exp_Category'] = df['Exp_Category'].astype('category')
        df['State'] = df['State'].astype('category')
        df['Year'] = df['Year'].astype('category')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        return df

    def generate_profile_report(self, df, filename):
        logger.info(f"Generating profile report: {filename}")
        profile = prf(df, title=f"{filename} Profile Report")
        profile.to_file(self.html_reports_dir / f"{filename}.html")

    def plot_null_values_heatmap(self, df):
        logger.info("Plotting null values heatmap")
        plt.figure(figsize=(12, 8))
        sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap='viridis')
        plt.title('Null Values Heatmap')
        plt.tight_layout()
        plt.savefig(self.plots_dir / "null_values_heatmap.png")
        plt.close()

    def clean_data(self, df):
        logger.info("Cleaning data")

        # Convert Year to string and handle missing values
        df['Year'] = df['Year'].astype(str).replace('nan', np.nan)

        # Replace '–' with NaN in the Value column
        df.loc[:, 'Value'] = df['Value'].replace('–', np.nan)

        # Check null values in other columns
        null_counts = df.isnull().sum()
        logger.info(f"Null value counts before processing:\n{null_counts}")

        def standardize_year(year):
            if isinstance(year, str):
            # Remove " (BE)" and " (RE)" if present
                year = year.replace(" (BE)", "").replace(" (RE)", "")
                # Check if the year is in the format "YYYY-YY"
                if len(year) >= 7 and '-' in year:
                    return year[:7]  # Return the first 7 characters (e.g., "2015-16")
            return np.nan  # Return NaN for any non-string or invalid formats


        # Standardize the Year format
        df.loc[:, 'Year'] = df['Year'].apply(standardize_year)

        # Drop rows where Year is NaN after standardization
        df = df.dropna(subset=['Year'])
        
        logger.info("Standardized Year format")


        # Convert Value to float and handle errors
        df.loc[:, 'Value'] = pd.to_numeric(df['Value'], errors='coerce')

        # 1. Dealing missing values with respect to its state mean
        # Calculate mean values for each state
        state_means = df.groupby('State')['Value'].transform('mean')
        # Replace NaN and 0 with the respective state mean in the Value column
        df['Value'] = df.apply(lambda row: state_means[row.name] if pd.isna(row['Value']) or row['Value'] == 0 else row['Value'], axis=1)
        logger.info("Replaced missing and zero values with respective state means in the Value column")

        '''
        # 2. Dealing missing values with respect to the overall mean
        # Calculate the mean of the Value column (excluding NaN and 0)
        value_mean = df['Value'][(df['Value'] != 0) & (df['Value'].notna())].mean()
        # Replace NaN and 0 with the calculated mean in the Value column
        df['Value'] = df['Value'].replace({0: value_mean, np.nan: value_mean})
        df.loc[:, 'Value'] = df['Value'].fillna(value_mean).replace(0, value_mean)
        logger.info(f"Replaced missing and zero values with mean ({value_mean:.2f}) in the Value column")
        '''
        
        '''
        # 1. Dealing missing values and replacing zero values
        # Replace NaN and existing 0 values with 0 in the Value column
        df.loc[:, 'Value'] = df['Value'].fillna(0).replace(0, 0)
        logger.info("Replaced missing and zero values with 0 in the Value column")
        '''

        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        logger.info(f"Number of duplicate rows: {duplicate_count}")

        # Remove duplicates
        df = df.drop_duplicates()
        logger.info("Removed duplicate rows")

        # Check null values in other columns
        null_counts = df.isnull().sum()
        logger.info(f"Null value counts after processing:\n{null_counts}")

        return df

    def save_cleaned_data(self, df):
        output_path = self.final_data_dir / "expenditure_analysis.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned data saved to: {output_path}")

    def run_cleaning_process(self):
        
        # convert data file to csv
        #self.convert_xlsx_to_csv()
        
        # Load data
        expenditure = self.load_data()

        # Generate pre-cleaning profile report
        self.generate_profile_report(expenditure, "expenditure_before_preprocessing")

        # Plot null values heatmap
        self.plot_null_values_heatmap(expenditure)

        # Clean data
        cleaned_expenditure = self.clean_data(expenditure)

        # Generate post-cleaning profile report
        self.generate_profile_report(cleaned_expenditure, "expenditure_after_preprocessing")

        # Save cleaned data
        self.save_cleaned_data(cleaned_expenditure)

def main():
    cleaner = DataCleaner()
    cleaner.run_cleaning_process()

if __name__ == "__main__":
    main()