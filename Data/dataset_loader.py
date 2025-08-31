import os
import pandas as pd
import sqlite3

# Get project root (Movora)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
RAW_DIR = os.path.join(BASE_DIR, "Data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "Data", "processed")
DB_PATH = os.path.join(BASE_DIR, "Database", "movora.db")

# Ensure processed folder exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_column_names(df):
    """Standardize column names to lowercase and underscores."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(" ", "_")
    )
    return df

def load_and_process_csv(filename):
    """Load, clean, and save a CSV file."""
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")
    
    df = pd.read_csv(path)
    df = clean_column_names(df)
    processed_path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(processed_path, index=False)
    
    print(f"✅ Processed {filename} -> {processed_path}")
    print(df.head(), "\n")  # Preview first 5 rows
    return df

def create_database(cars_all_df, cars_indian_df, cars_master_df):
    """Save DataFrames to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cars_all_df.to_sql("cars_all", conn, if_exists="replace", index=False)
    cars_indian_df.to_sql("cars_indian", conn, if_exists="replace", index=False)
    cars_master_df.to_sql("cars_master", conn, if_exists="replace", index=False)
    conn.close()
    print(f"💾 Database created at {DB_PATH}")

def merge_datasets(cars_all_df, cars_indian_df):
    """Merge both datasets into a single master table with common columns."""
    # Find common columns
    common_cols = set(cars_all_df.columns).intersection(set(cars_indian_df.columns))
    common_cols = list(common_cols)

    # Merge and remove duplicates
    merged_df = pd.concat(
        [cars_all_df[common_cols], cars_indian_df[common_cols]],
        ignore_index=True
    ).drop_duplicates()

    print(f"🔗 Merged datasets into 'cars_master' with {len(merged_df)} records and {len(common_cols)} columns.")
    return merged_df

if __name__ == "__main__":
    print("🔄 Loading and processing datasets...\n")

    cars_all_df = load_and_process_csv("All_cars_dataset.csv")
    cars_indian_df = load_and_process_csv("Indian_Cars_Data.csv")

    print("📊 Merging datasets...")
    cars_master_df = merge_datasets(cars_all_df, cars_indian_df)

    print("💾 Creating SQLite database...")
    create_database(cars_all_df, cars_indian_df, cars_master_df)

    print("🎯 All done! Movora data is ready.")
