import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from ydata_profiling import ProfileReport
import sys
import os

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

class ExploratoryDataAnalysis:
    def __init__(self):
        self.processed_data_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/final")
        self.artifacts_dir = Path("/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/artifacts")
        self.plots_dir = self.artifacts_dir / "plots"
        self.html_reports_dir = self.artifacts_dir / "HTML-reports"
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.html_reports_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        logger.info("Loading processed data")
        data_path = self.processed_data_dir / "expenditure_analysis.csv"
        #data_path = self.processed_data_dir / "expenditure1.csv"
        return pd.read_csv(data_path)
    

    def generate_profile_report(self, df, filename):
        logger.info(f"Generating eda profile report: {filename}")
        profile = ProfileReport(df, title=f"{filename} Profile Report")
        profile.to_file(self.html_reports_dir / f"{filename}_profile_report.html")

    def plot_expenditure_over_time(self, df):
        logger.info("Plotting expenditure over time")
        plt.figure(figsize=(15, 8))
        for category in df['Exp_Category'].unique():
            category_data = df[df['Exp_Category'] == category]
            sns.lineplot(data=category_data, x='Year', y='Value', label=category)
        plt.title('Expenditure Over Time by Category')
        plt.xticks(rotation=45)
        plt.legend(title='Exp_Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'expenditure_over_time.png')
        plt.close()

    def plot_state_wise_expenditure(self, df):
        logger.info("Plotting state-wise expenditure")
        plt.figure(figsize=(15, 8))
        state_totals = df.groupby('State')['Value'].sum().sort_values(ascending=False)
        sns.barplot(x=state_totals.index, y=state_totals.values)
        plt.title('Total Expenditure by State')
        plt.xticks(rotation=90)
        plt.ylabel('Total Expenditure')
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'state_wise_expenditure.png')
        plt.close()

    def plot_category_distribution(self, df):
        logger.info("Plotting category distribution")
        plt.figure(figsize=(10, 6))
        category_totals = df.groupby('Exp_Category')['Value'].sum()
        category_totals.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Distribution of Expenditure Categories')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'category_distribution.png')
        plt.close()

    def plot_total_expenditure_trend(self, df):
        logger.info("Plotting total expenditure trend")
        plt.figure(figsize=(15, 8))
        yearly_totals = df.groupby('Year')['Value'].sum()
        sns.lineplot(x=yearly_totals.index, y=yearly_totals.values)
        plt.title('Total Expenditure Trend Over Time')
        plt.xticks(rotation=45)
        plt.ylabel('Total Expenditure')
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'total_expenditure_trend.png')
        plt.close()

    def run_eda(self):
        df = self.load_data()
        self.generate_profile_report(df, "eda_expenditure_data")
        self.plot_expenditure_over_time(df)
        self.plot_state_wise_expenditure(df)
        self.plot_category_distribution(df)
        self.plot_total_expenditure_trend(df)
        logger.info("EDA completed successfully")

def main():
    eda = ExploratoryDataAnalysis()
    eda.run_eda()

if __name__ == "__main__":
    main()