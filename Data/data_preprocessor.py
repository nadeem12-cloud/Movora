import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import os

RAW_PATH = r"C:\Users\nadee\Documents\Movora\Data\raw\All_cars_dataset.csv"
ML_PATH = r"C:\Users\nadee\Documents\Movora\Data\processed\cars_master_ml.csv"
DB_PATH = r"C:\Users\nadee\Documents\Movora\Data\movora.db"

# ------------------- STEP 1: Add Vehicle_Type -------------------
def add_vehicle_type(df):
    # Convert to numeric first to avoid type errors
    df["Seating Capacity"] = pd.to_numeric(df["Seating Capacity"], errors="coerce")
    df["Displacement (cc)"] = pd.to_numeric(df["Displacement (cc)"], errors="coerce")

    df["Vehicle_Type"] = df.apply(
        lambda row: "2W" if (pd.notna(row["Seating Capacity"]) and row["Seating Capacity"] <= 2
                             and pd.notna(row["Displacement (cc)"]) and row["Displacement (cc)"] <= 400)
        else "4W",
        axis=1
    )
    return df

# ------------------- STEP 2: Preprocess Data -------------------
def preprocess_data(df):
    # Add target column if missing
    if "Vehicle_Type" not in df.columns:
        df = add_vehicle_type(df)

    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    if "Vehicle_Type" in categorical_cols:
        categorical_cols.remove("Vehicle_Type")

    # Clean numeric columns
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    # Scale numeric data
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df[numeric_cols]), columns=numeric_cols)

    # Encode categorical data
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded_cats = encoder.fit_transform(df[categorical_cols])
    encoded_col_names = encoder.get_feature_names_out(categorical_cols)
    encoded_df = pd.DataFrame(encoded_cats, columns=encoded_col_names)

    # Fix duplicate column names
    if encoded_df.columns.duplicated().any():
        encoded_df.columns = [
            f"{col}_{i}" if dup else col
            for i, (col, dup) in enumerate(zip(encoded_df.columns, encoded_df.columns.duplicated()))
        ]

    # Combine into final ML dataset
    df_ml = pd.concat(
        [df_scaled.reset_index(drop=True),
         encoded_df.reset_index(drop=True),
         df["Vehicle_Type"].reset_index(drop=True)],
        axis=1
    )

    return df_ml

# ------------------- STEP 3: Save to CSV & SQLite -------------------
def save_data(df_ml):
    os.makedirs(os.path.dirname(ML_PATH), exist_ok=True)
    df_ml.to_csv(ML_PATH, index=False)

    conn = sqlite3.connect(DB_PATH)
    df_ml.to_sql("cars_master_ml", conn, if_exists="replace", index=False)
    conn.close()

# ------------------- STEP 4: Run -------------------
if __name__ == "__main__":
    df_raw = pd.read_csv(RAW_PATH)
    print(f"📥 Loaded dataset with {len(df_raw)} rows and {len(df_raw.columns)} columns.")

    df_ml = preprocess_data(df_raw)
    print(f"⚙️ Processed dataset for ML: {df_ml.shape[0]} rows, {df_ml.shape[1]} features.")

    save_data(df_ml)
    print(f"💾 Saved ML-ready dataset to {ML_PATH} and SQLite database.")
