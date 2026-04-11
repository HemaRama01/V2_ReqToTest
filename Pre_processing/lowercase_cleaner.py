

def convert_to_lowercase(df):
    """
    Converts:
    1. All column names to lowercase
    2. All string values in the DataFrame to lowercase

    Numbers, dates, and non-string values are left unchanged.
    """
    df = df.copy()

    # 1️ Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # 2️ Normalize string cell values
    string_cols = df.select_dtypes(include="object").columns
    df[string_cols] = df[string_cols].map(
        lambda x: x.lower() if isinstance(x, str) else x
    )

    return df
