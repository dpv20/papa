import pandas as pd
import sqlite3
from sqlite3 import Error

def excel_to_df(file_path):
    """Read Excel file into DataFrame with proper cleaning"""
    try:
        # Read the Excel file (skip first 3 rows of metadata)
        df = pd.read_excel(
            file_path,
            sheet_name="Recursos",
            skiprows=3,
            usecols="A:G",
            dtype={"CanPres": float, "Pres": float}
        )
        
        # Clean column names
        df.columns = ["Código", "Nat", "Ud", "Resumen", "CanPres", "Pres", "ImpPres"]
        
        # Filter out empty rows and section headers
        df = df[df["Código"].notna() & ~df["Código"].str.startswith(("MA", "MB", "MC"))]
        
        # Calculate ImpPres if not properly read from Excel
        df["ImpPres"] = (df["CanPres"] * df["Pres"]).round(0)
        
        return df
    
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def save_to_csv(df, csv_path="materiales.csv"):
    """Save DataFrame to CSV"""
    try:
        df.to_csv(csv_path, index=False)
        print(f"Successfully saved to {csv_path}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

def save_to_sqlite(df, db_path="materiales.db"):
    """Save DataFrame to SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql("materiales", conn, if_exists="replace", index=False)
        print(f"Successfully saved to {db_path}")
    except Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Configuration
    excel_file = "Base Presto.xlsx"
    
    # Convert Excel to DataFrame
    materiales_df = excel_to_df(excel_file)
    
    if materiales_df is not None:
        # Save to CSV
        save_to_csv(materiales_df)
        
        # Save to SQLite
        save_to_sqlite(materiales_df)
        
        # Show sample data
        print("\nSample data:")
        print(materiales_df.head())