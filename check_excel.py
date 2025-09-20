import pandas as pd

# Read the Excel file
file_path = r'c:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES\input.xlsx'
df = pd.read_excel(file_path)

# Print the column names
print("Column names:")
print(df.columns.tolist())

# Print the first few rows
print("\nFirst few rows:")
print(df.head(20))

# Check if 'ABTLEN' exists
if 'ABTLEN' in df['Variable'].values:
    print("\nABTLEN found in the file")
else:
    print("\nABTLEN not found in the file")
    print("Available variables:")
    print(df['Variable'].unique())