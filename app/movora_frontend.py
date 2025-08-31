import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Movora - Vehicle Recommender", layout="wide")

# ✅ Try both local + Streamlit paths
possible_paths = [
    os.path.join("Data", "raw", "All_cars_dataset.csv"),   # local dev
    os.path.join("app", "Data", "raw", "All_cars_dataset.csv"),  # if structure shifts
    "All_cars_dataset.csv"  # fallback if kept at root
]

file_path = None
for path in possible_paths:
    if os.path.exists(path):
        file_path = path
        break

if not file_path:
    st.error("❌ Dataset not found! Please make sure `All_cars_dataset.csv` is inside `Data/raw/` and committed to GitHub.")
    st.stop()

# ✅ Load dataset
df = pd.read_csv(file_path)
st.success(f"✅ Using dataset: {file_path} ({len(df)} rows)")

# --- Preprocess price ---
def convert_price(price_str):
    """Convert '69.98 Lakh' or '1.2 Crore' into numeric INR value"""
    if isinstance(price_str, str):
        price_str = price_str.strip().lower()
        if "lakh" in price_str:
            return float(price_str.replace("lakh", "").strip()) * 1e5
        elif "crore" in price_str:
            return float(price_str.replace("crore", "").strip()) * 1e7
        else:
            try:
                return float(price_str)
            except:
                return None
    return price_str

df["price_cleaned"] = df["price"].apply(convert_price)

# --- Sidebar controls ---
st.sidebar.header("🔍 Filter Vehicles")
min_price = st.sidebar.selectbox("Min Price (₹)", sorted(df["price_cleaned"].dropna().unique()))
max_price = st.sidebar.selectbox("Max Price (₹)", sorted(df["price_cleaned"].dropna().unique(), reverse=True))

if min_price >= max_price:
    st.warning("⚠ Please select a valid min < max price range")
else:
    results = df[(df["price_cleaned"] >= min_price) & (df["price_cleaned"] <= max_price)]

    st.subheader(f"🚗 Vehicles between ₹{min_price:,.0f} and ₹{max_price:,.0f}")
    if results.empty:
        st.warning("⚠ No vehicles found in this range.")
    else:
        st.dataframe(results[["name", "price", "mileage", "engine", "fuel_type", "seating_capacity", "top_speed"]])
