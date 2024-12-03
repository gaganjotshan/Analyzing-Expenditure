import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from ydata_profiling import ProfileReport
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

class ExploratoryDataAnalysis:
    def __init__(self):
        self.processed_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/processed/expenditure_analysis")
        self.final_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/final/expenditure_analysis")
        self.artifacts_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/artifacts/expenditure_analysis")
        self.plots_dir = self.artifacts_dir / "plots"
        self.html_reports_dir = self.artifacts_dir / "HTML-reports"
        
        for dir in [self.plots_dir, self.html_reports_dir]:
            dir.mkdir(parents=True, exist_ok=True)

    def load_and_combine_data(self, data_type):
        logger.info(f"Loading and combining {data_type} data")
        data_dir = self.processed_data_dir if data_type == 'transformed' else self.final_data_dir
        file_pattern = f"*_{data_type}.csv"
        
        all_dataframes = []
        for file in data_dir.glob(file_pattern):
            category = file.stem.replace(f"_{data_type}", "")
            df = pd.read_csv(file)
            df['Exp_Category'] = category
            all_dataframes.append(df)
        
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        combined_df = combined_df[['Exp_Category', 'State', 'Year', 'Value']]
        
        output_file = data_dir / f"{data_type}_expenditure.csv"
        combined_df.to_csv(output_file, index=False)
        logger.info(f"Combined {data_type} data saved to: {output_file}")
        
        return combined_df

    def generate_profile_report(self, df, filename):
        logger.info(f"Generating profile report: {filename}")
        profile = ProfileReport(df, title=f"{filename} Profile Report")
        profile.to_file(self.html_reports_dir / f"{filename}_profile_report.html")

    def plot_null_values_heatmap(self, df):
        logger.info("Plotting null values heatmap")
        plt.figure(figsize=(12, 8))
        sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap='viridis')
        plt.title('Null Values Heatmap')
        plt.tight_layout()
        plt.savefig(self.plots_dir / "null_values_heatmap.png")
        plt.close()

    def plot_data(self, df, plot_type):
        plt.figure(figsize=(15, 8))
        
        if plot_type == 'expenditure_over_time':
            for category in df['Exp_Category'].unique():
                category_data = df[df['Exp_Category'] == category]
                sns.lineplot(data=category_data, x='Year', y='Value', label=category)
            plt.title('Expenditure Over Time by Category')
            plt.legend(title='Exp_Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        elif plot_type == 'state_wise_expenditure':
            state_totals = df.groupby('State')['Value'].sum().sort_values(ascending=False)
            sns.barplot(x=state_totals.index, y=state_totals.values)
            plt.title('Total Expenditure by State')
            plt.ylabel('Total Expenditure')
        elif plot_type == 'category_distribution':
            category_totals = df.groupby('Exp_Category')['Value'].sum()
            category_totals.plot(kind='pie', autopct='%1.1f%%')
            plt.title('Distribution of Expenditure Categories')
            plt.axis('equal')
        elif plot_type == 'total_expenditure_trend':
            yearly_totals = df.groupby('Year')['Value'].sum()
            sns.lineplot(x=yearly_totals.index, y=yearly_totals.values)
            plt.title('Total Expenditure Trend Over Time')
            plt.ylabel('Total Expenditure')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.plots_dir / f'{plot_type}.png')
        plt.close()

    def run_eda(self):
        # Combine transformed data and generate profile report
        transformed_df = self.load_and_combine_data('transformed')
        
        # Replace '-' with NaN in Value column for transformed data
        transformed_df['Value'] = transformed_df['Value'].replace('-', np.nan)
        
        # Convert Value to numeric
        transformed_df['Value'] = pd.to_numeric(transformed_df['Value'], errors='coerce')

        # Generate profile report before processing
        self.generate_profile_report(transformed_df, "before_processing")

        # Plot null value heatmap for transformed data
        self.plot_null_values_heatmap(transformed_df)

        # Combine cleaned data and generate profile report
        cleaned_df = self.load_and_combine_data('cleaned')

        # Generate profile report after processing
        self.generate_profile_report(cleaned_df, "after_processing")

        # Descriptive statistics
        desc_stats = cleaned_df.describe()
        logger.info(f"Descriptive statistics:\n{desc_stats}")
        
        # Perform EDA on the cleaned data
        plot_types = ['expenditure_over_time', 'state_wise_expenditure', 'category_distribution', 'total_expenditure_trend']
        
        for plot_type in plot_types:
            self.plot_data(cleaned_df, plot_type)

        logger.info("EDA completed successfully for cleaned expenditure data")

def main():
    eda = ExploratoryDataAnalysis()
    eda.run_eda()

if __name__ == "__main__":
    main()