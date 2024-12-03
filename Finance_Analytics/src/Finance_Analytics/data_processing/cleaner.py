import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

class DataCleaner:
    def __init__(self):
        self.processed_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/processed/expenditure_analysis")
        self.final_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/final/expenditure_analysis")
        self.final_data_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, file_path):
        logger.info(f"Loading transformed data from {file_path}")
        df = pd.read_csv(file_path)
        df.loc[:, 'Value'] = df['Value'].replace('–', np.nan)
        df['State'] = df['State'].astype('category')
        df['Year'] = df['Year'].astype('category')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        return df

    def clean_data(self, df):
        logger.info("Cleaning data")
        df['Year'] = df['Year'].astype(str).replace('nan', np.nan)
        df.loc[:, 'Value'] = df['Value'].replace('–', np.nan)

        def standardize_year(year):
            if isinstance(year, str):
                year = year.replace(" (BE)", "").replace(" (RE)", "")
                if len(year) >= 7 and '-' in year:
                    return year[:7]
            return np.nan

        df.loc[:, 'Year'] = df['Year'].apply(standardize_year)
        df = df.dropna(subset=['Year'])
        
        df.loc[:, 'Value'] = pd.to_numeric(df['Value'], errors='coerce')
        state_means = df.groupby('State')['Value'].transform('mean')
        df['Value'] = df.apply(lambda row: state_means[row.name] if pd.isna(row['Value']) or row['Value'] == 0 else row['Value'], axis=1)
        
        df = df.drop_duplicates()
        
        return df

    def save_cleaned_data(self, df, category):
        output_path = self.final_data_dir / f"{category}_cleaned.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned data saved to: {output_path}")

    def clean_all_files(self):
        for file in self.processed_data_dir.glob("*_transformed.csv"):
            category = file.stem.replace("_transformed", "")
            df = self.load_data(file)
            cleaned_df = self.clean_data(df)
            self.save_cleaned_data(cleaned_df, category)

def main():
    cleaner = DataCleaner()
    cleaner.clean_all_files()

if __name__ == "__main__":
    main()