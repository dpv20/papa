import pandas as pd

# Load the Excel file
file_path = 'Base Presto.xlsx'
sheet_name = 'Recursos'

# Read and preprocess data
df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)
df.columns = ['Codigo', 'Nat', 'Ud', 'Resumen', 'CanPres', 'Pres', 'ImpPres']
df.dropna(subset=['Codigo'], inplace=True)
df.reset_index(drop=True, inplace=True)

# Initialize category and subcategory
current_cat, current_subcat = None, None
df['Categoria'], df['Subcategoria'] = None, None

# Set hierarchy based on Nat and Codigo
for i, row in df.iterrows():
    if row['Nat'] == 'Capítulo':
        if len(str(row['Codigo'])) <= 2:
            current_cat = row['Resumen']
            current_subcat = None
        else:
            current_subcat = row['Resumen']
    df.at[i, 'Categoria'] = current_cat
    df.at[i, 'Subcategoria'] = current_subcat

# Keep only items that aren't chapters
items_df = df[df['Nat'] != 'Capítulo'].copy()

# Add the fixed date column as the last column
items_df['Fecha'] = '30/04/2025'

# Define column order explicitly with Fecha at the end
final_df = items_df[['Codigo', 'Nat', 'Ud', 'Resumen', 'CanPres', 'Pres', 'ImpPres', 'Categoria', 'Subcategoria', 'Fecha']]

# Export to CSV
final_df.to_csv('construction_budget_data.csv', index=False)

print("CSV file created successfully with date as the last column!")
