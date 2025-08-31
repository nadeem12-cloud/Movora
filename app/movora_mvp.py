import os
import pandas as pd

# File path to your data
data_folder = r"C:\Users\nadee\Documents\Movora\Data\processed"
file_name = "All_cars_dataset.csv"
file_path = os.path.join(data_folder, file_name)

# Check file exists
if not os.path.exists(file_path):
    print(f"❌ Data file not found at {file_path}")
    exit()

print(f"✅ Using file: {file_name}")

# Load CSV
df = pd.read_csv(file_path)

# Check columns
print("\n📌 Columns in dataset:", df.columns.tolist())

# Ensure price column exists (case-insensitive)
price_col = None
for col in df.columns:
    if col.strip().lower() == "price":
        price_col = col
        break

if price_col is None:
    print("❌ 'price' column not found. Please check your CSV headers.")
    exit()

# Clean price column
df[price_col] = df[price_col].astype(str) \
    .str.replace(",", "", regex=False) \
    .str.replace("₹", "", regex=False) \
    .str.strip()

df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
df = df.dropna(subset=[price_col])

# Ask for price range
min_price = float(input("Enter minimum price: "))
max_price = float(input("Enter maximum price: "))

# Filter results
results = df[(df[price_col] >= min_price) & (df[price_col] <= max_price)]

if results.empty:
    print("⚠ No vehicles found in this range.")
else:
    print(f"\n✅ Found {len(results)} vehicles in this range:\n")
    print(results[["name", price_col, "mileage", "engine", "fuel_type"]].head(20))
