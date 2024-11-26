import sys
import os
import pandas as pd
from pathlib import Path

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Finance_Analytics import logger


# Define the directory containing the CSV files
raw_directory_path = "/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/raw/expenditure_analysis"
transformed_directory_path = "/Users/gaganjotshan/Documents/Projects/Analyzing-Expenditure/Finance_Analytics/data/processed/expenditure_analysis"

# Create transformed directory if it doesn't exist
os.makedirs(transformed_directory_path, exist_ok=True)

def load_csv(file_path):
    """Load a CSV file into a DataFrame."""
    try:
        df = pd.read_csv(file_path, header=None)
        logger.info(f"File {file_path} read successfully")
        return df
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def find_states_index(df):
    """Find the row and column index for 'States'."""
    try:
        states_row_index = df.index[df.eq("States").any(axis=1)].tolist()[0]
        states_col_index = df.iloc[states_row_index].tolist().index("States")
        logger.info("Found 'States' row and column.")
        return states_row_index, states_col_index
    except Exception as e:
        logger.error(f"Error locating 'States': {e}")
        return None, None

def clean_dataframe(df, states_row_index, states_col_index):
    """Clean the DataFrame by slicing and renaming columns."""
    df_cleaned = df.iloc[states_row_index:, states_col_index:]
    logger.info("DataFrame sliced to relevant data")

    # Set the first row (containing headers) as the column names
    df_cleaned.columns = df_cleaned.iloc[0]
    df_cleaned = df_cleaned.drop(df_cleaned.index[0])

    # Remove rows that do not have a number in the "State" column
    df_cleaned = df_cleaned[df_cleaned['States'].str.contains(r'^\d+\.', regex=True)]
    
    # Remove numbers from state names
    df_cleaned['States'] = df_cleaned['States'].str.replace(r'^\d+\.', '', regex=True).str.strip()
    logger.info("State names cleaned")
    
    return df_cleaned

def transform_dataframe(df_cleaned):
    """Transform the cleaned DataFrame into long format."""
    melted_df = pd.melt(df_cleaned, id_vars=['States'], var_name='Year', value_name='Value')
    logger.info("DataFrame melted to long format")
    
    # Rename columns to match desired output
    melted_df = melted_df.rename(columns={'States': 'State'})
    
    return melted_df

def process_files(raw_directory_path):
    """Process all CSV files in the specified directory."""
    all_dataframes = []
    skipped_files = []  # List to store skipped files and errors
    
    for filename in os.listdir(raw_directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(raw_directory_path, filename)
            logger.info(f"Processing file: {filename}")
            
            category = os.path.splitext(filename)[0].replace(" ", "_").lower().capitalize()
            logger.info(f"Using category: {category}")

            # Load the CSV file
            df = load_csv(file_path)
            if df is None:
                skipped_files.append((filename, "Loading error"))
                continue  # Skip this file if loading failed
            
            # Find indices for 'States'
            states_row_index, states_col_index = find_states_index(df)
            if states_row_index is None or states_col_index is None:
                skipped_files.append((filename, "Error locating 'States'"))
                continue  # Skip this file if indices cannot be found
            
            # Clean and transform the DataFrame
            try:
                df_cleaned = clean_dataframe(df, states_row_index, states_col_index)
                melted_df = transform_dataframe(df_cleaned)

                # Append this DataFrame to our list along with its category
                all_dataframes.append((melted_df, category))
                logger.info(f"Processed DataFrame for {category} appended to list")
            except Exception as e:
                skipped_files.append((filename, f"Cleaning/Transforming error: {e}"))
                logger.error(f"Error processing file {filename}: {e}")

    return all_dataframes, skipped_files

def combine_dataframes(all_dataframes):
    """Combine all DataFrames and add an 'Exp Category' column for each."""
    combined_df = pd.concat([df.assign(Exp_Category=category) for df, category in all_dataframes], ignore_index=True)
    logger.info("All DataFrames combined")

    # Reorder columns to make 'Exp Category' the first column
    combined_df = combined_df[['Exp_Category', 'State', 'Year', 'Value']]
    logger.info("Columns reordered")
    
    return combined_df

def save_combined_dataframe(combined_df, output_file_path):
    """Save the combined DataFrame to a CSV file."""
    combined_df.to_csv(output_file_path, index=False)
    logger.info(f"Combined transformed file saved at: {output_file_path}")

def main():
    logger.info(f"Processing files in directory: {raw_directory_path}")
    
    all_dataframes, skipped_files = process_files(raw_directory_path)
    
    if all_dataframes:
        combined_df = combine_dataframes(all_dataframes)
        
        combined_output_file_path = os.path.join(transformed_directory_path, "transformed_expenditure.csv")
        save_combined_dataframe(combined_df, combined_output_file_path)

    # Log skipped files and their reasons
    if skipped_files:
        logger.warning("The following files were skipped due to errors:")
        for filename, reason in skipped_files:
            logger.warning(f"{filename}: {reason}")

if __name__ == "__main__":
    main()