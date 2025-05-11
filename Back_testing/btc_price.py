import pandas as pd

# Read the CSV file.
# Replace 'path_to_your_csv_file.csv' with the actual path to your CSV file.
df = pd.read_csv('btc_1d_data_2018_to_2025.csv', parse_dates=['Open time'], dayfirst=True)

# Inspect the first few rows to verify the data.
print("Full Data Head:")
print(df.head())

# Optional: Rename columns for clarity. Changing 'Open time' to 'Date' and 'Close' to 'Close_BTC'
df.rename(columns={'Open time': 'Date', 'Close': 'Close_BTC'}, inplace=True)

# Extract only the Date and Closing Price columns.
df_closing_prices = df[['Date', 'Close_BTC']]

# Display the extracted data.
print("\nExtracted Closing Prices:")
print(df_closing_prices.head())

# Optionally, save the extracted data to a new CSV file.
df_closing_prices.to_csv("extracted_closing_prices.csv", index=False)
