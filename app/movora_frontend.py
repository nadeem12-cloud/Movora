import streamlit as st
import pandas as pd
import re

# Load dataset (update path if needed)
file_path = r"C:\Users\nadee\Documents\Movora\Data\processed\All_cars_dataset.csv"
df = pd.read_csv(file_path)

# -------------------------
# 🔹 Price cleaning function
# -------------------------
def clean_price(price_str):
    if pd.isna(price_str):
        return None
    price_str = str(price_str).strip()

    # If value already numeric, return as float
    try:
        return float(price_str)
    except:
        pass

    # Match Crore
    crore_match = re.match(r"([\d\.]+)\s*Crore", price_str, re.IGNORECASE)
    if crore_match:
        return float(crore_match.group(1)) * 100  # 1 Crore = 100 Lakh

    # Match Lakh
    lakh_match = re.match(r"([\d\.]+)\s*Lakh", price_str, re.IGNORECASE)
    if lakh_match:
        return float(lakh_match.group(1))

    return None

# Apply cleaning
df["price_clean"] = df["price"].apply(clean_price)

# Drop rows where price could not be parsed
df = df.dropna(subset=["price_clean"])

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Movora Vehicle Recommender", layout="wide")

st.sidebar.header("🔍 Filter Options")

min_price = st.sidebar.selectbox("Minimum Price (Lakh)", sorted(df["price_clean"].unique()))
max_price = st.sidebar.selectbox("Maximum Price (Lakh)", sorted(df["price_clean"].unique(), reverse=True))

# Filter data
results = df[(df["price_clean"] >= min_price) & (df["price_clean"] <= max_price)]

# -------------------------
# Display results
# -------------------------
st.title("🚗 Movora - Vehicle Recommender")

if not results.empty:
    st.success(f"✅ Found {len(results)} vehicles in your price range!")

    # Show results with price formatted back into Lakh/Crore
    def format_price(val):
        if val >= 100:
            return f"{val/100:.2f} Crore"
        else:
            return f"{val:.2f} Lakh"

    results_display = results.copy()
    results_display["price"] = results_display["price_clean"].apply(format_price)

    st.dataframe(results_display[["name", "price", "mileage", "engine", "transmission", "fuel_type"]])

else:
    st.warning("⚠ No vehicles found for the selected criteria.")
