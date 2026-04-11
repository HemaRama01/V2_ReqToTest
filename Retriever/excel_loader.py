import pandas as pd


def load_excel_sheet(file_path):
    """
    Loads selected Excel sheet and returns DataFrame
    """
    try:
        df = pd.read_excel(file_path)
        print(" Excel sheet loaded successfully.\n")
        return df
    except Exception as e:
        print(f" Error loading Excel sheet: {e}")
        return None