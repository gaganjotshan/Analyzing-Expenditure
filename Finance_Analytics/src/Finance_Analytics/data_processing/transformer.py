import os
import sys
import pandas as pd
from pathlib import Path
import yaml  

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger

def load_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

class DataTransformer:
    def __init__(self, config_file='/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/config/path_config.yaml'):
        # Load configurations
        config = load_config(config_file)

        # Define directories from config
        self.raw_directory_path = Path(config['paths']['raw_data_dir']) / "expenditure_analysis"
        self.transformed_directory_path = Path(config['paths']['processed_data_dir']) / "expenditure_analysis"

        # Create transformed directory if it doesn't exist
        os.makedirs(self.transformed_directory_path, exist_ok=True)

    def load_csv(self, file_path):
        """Load a CSV file into a DataFrame."""
        try:
            df = pd.read_csv(file_path, header=None)
            logger.info(f"File {file_path} read successfully")
            return df
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def find_states_index(self, df):
        """Find the row and column index for 'States'."""
        try:
            states_row_index = df.index[df.eq("States").any(axis=1)].tolist()[0]
            states_col_index = df.iloc[states_row_index].tolist().index("States")
            logger.info("Found 'States' row and column.")
            return states_row_index, states_col_index
        except Exception as e:
            logger.error(f"Error locating 'States': {e}")
            return None, None

    def structure_dataframe(self, df, states_row_index, states_col_index):
        """Clean the DataFrame by slicing and renaming columns."""
        df_structured = df.iloc[states_row_index:, states_col_index:]
        logger.info("DataFrame sliced to relevant data")

        # Set the first row (containing headers) as the column names
        df_structured.columns = df_structured.iloc[0]
        df_structured = df_structured.drop(df_structured.index[0])

        # Remove rows that do not have a number in the "State" column
        df_structured = df_structured[df_structured['States'].str.contains(r'^\d+\.', regex=True)]

        # Remove numbers from state names
        df_structured['States'] = df_structured['States'].str.replace(r'^\d+\.', '', regex=True).str.strip()
        logger.info("State names cleaned")

        return df_structured

    def transform_dataframe(self, df_structured):
        """Transform the cleaned DataFrame into long format."""
        melted_df = pd.melt(df_structured, id_vars=['States'], var_name='Year', value_name='Value')
        logger.info("DataFrame melted to long format")

        # Rename columns to match desired output
        melted_df = melted_df.rename(columns={'States': 'State'})

        return melted_df

    def process_files(self):
        """Process all CSV files in the specified directory."""
        all_dataframes = []
        skipped_files = []  # List to store skipped files and errors

        for filename in os.listdir(self.raw_directory_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(self.raw_directory_path, filename)
                logger.info(f"Processing file: {filename}")

                category = os.path.splitext(filename)[0].replace(" ", "_").lower().capitalize()
                logger.info(f"Using category: {category}")

                # Load the CSV file
                df = self.load_csv(file_path)
                if df is None:
                    skipped_files.append((filename, "Loading error"))
                    continue  # Skip this file if loading failed

                # Find indices for 'States'
                states_row_index, states_col_index = self.find_states_index(df)
                if states_row_index is None or states_col_index is None:
                    skipped_files.append((filename, "Error locating 'States'"))
                    continue  # Skip this file if indices cannot be found

                # Clean and transform the DataFrame
                try:
                    df_structured = self.structure_dataframe(df, states_row_index, states_col_index)
                    melted_df = self.transform_dataframe(df_structured)

                    # Save each transformed DataFrame separately
                    output_file_path = os.path.join(self.transformed_directory_path, f"{category}_transformed.csv")
                    melted_df.to_csv(output_file_path, index=False)
                    logger.info(f"Transformed data saved for {category} at {output_file_path}")

                    all_dataframes.append((melted_df, category))
                    logger.info(f"Processed DataFrame for {category} appended to list")
                except Exception as e:
                    skipped_files.append((filename, f"Cleaning/Transforming error: {e}"))
                    logger.error(f"Error processing file {filename}: {e}")

        return all_dataframes, skipped_files

def main():
    transformer = DataTransformer()
    logger.info(f"Processing files in directory: {transformer.raw_directory_path}")
    
    all_dataframes, skipped_files = transformer.process_files()
    
    # Log skipped files and their reasons
    if skipped_files:
        logger.warning("The following files were skipped due to errors:")
        for filename, reason in skipped_files:
            logger.warning(f"{filename}: {reason}")

if __name__ == "__main__":
    main()