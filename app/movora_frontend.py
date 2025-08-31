import streamlit as st
import pandas as pd
import re

# --- Load dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv("Data/raw/All_cars_dataset.csv")

    # Normalize column names (strip spaces, lower case)
    df.columns = df.columns.str.strip()

    # Try to detect price column (handles "Price", "price", etc.)
    price_col = None
    for col in df.columns:
        if col.lower() == "price":
            price_col = col
            break

    if price_col is None:
        st.error("❌ No 'Price' column found in dataset.")
        return df

    # Convert price values
    df["price_cleaned"] = df[price_col].apply(convert_price)
    return df


# --- Convert Price Strings ("Lakh", "Crore") to numeric (in Lakhs) ---
def convert_price(price_str):
    if pd.isna(price_str):
        return None
    price_str = str(price_str).replace(",", "").strip()

    match = re.match(r"([\d\.]+)\s*(Lakh|Crore)", price_str, re.IGNORECASE)
    if not match:
        return None

    value, unit = match.groups()
    value = float(value)

    if unit.lower() == "crore":
        return value * 100  # 1 Crore = 100 Lakhs
    return value  # already in Lakhs


# --- Load data ---
df = load_data()

# --- Sidebar controls ---
st.sidebar.header("🔍 Filter Options")

if "price_cleaned" in df.columns:
    min_price = float(df["price_cleaned"].min())
    max_price = float(df["price_cleaned"].max())

    selected_min = st.sidebar.selectbox("Minimum Price", sorted(df["price_cleaned"].unique()), index=0)
    selected_max = st.sidebar.selectbox("Maximum Price", sorted(df["price_cleaned"].unique()), index=len(df["price_cleaned"].unique()) - 1)

    # Filter data
    filtered_df = df[(df["price_cleaned"] >= selected_min) & (df["price_cleaned"] <= selected_max)]
else:
    st.warning("⚠️ No price data available, showing all vehicles.")
    filtered_df = df

# --- Main content ---
st.title("🚗 Movora - Vehicle Recommender")
st.subheader("📋 Matching Vehicles")

if filtered_df.empty:
    st.warning("⚠️ No vehicles found for the selected criteria.")
else:
    st.dataframe(filtered_df)
    st.caption(f"Showing {len(filtered_df)} results from {len(df)} total vehicles.")
