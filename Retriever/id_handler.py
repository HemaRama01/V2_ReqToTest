def id_validator(df, id_value):
    df.columns = df.columns.str.strip().str.lower()

    # if "id" not in df.columns:
    #     print(" 'id' column not found in Excel file.")
    #     return None

    # if id_value not in df["id"].values:
    #     print(f" Invalid ID: {id_value} not found in selected project.")
    #     return None

    # return df[df["id"] == id_value]
     # Check if ANY of the provided IDs exist in the dataframe
    # Using .isin() to create a boolean mask
    mask = df["id"].isin(id_value)
    
    if not mask.any():
        print(f" No matching IDs from {id_value} found in selected project.")
        return None

    # Return only rows where the 'id' is in the provided list
    return df[mask]
