import pandas as pd

# Columns to exclude from metadata filtering
EXCLUDED_COLUMNS = ["id", "text","state","verified by","reuses","reused by"]  # only Text is embedded, ID excluded to avoid self-match

def build_or_filter(row_dict):
    """
    Build OR metadata filter for vector DB based on present metadata values.

    - Ignore columns in EXCLUDED_COLUMNS (like 'text', 'id')
    - Ignore null, NaN, or empty strings
    - If at least one metadata field exists, build OR filter
    - If no metadata fields exist, return None (search full DB)
    """
    metadata_conditions = []

    for col, value in row_dict.items():
        # Skip excluded columns
        if col.lower() in EXCLUDED_COLUMNS:
            continue

        # Skip None / NaN / empty string
        if value is None:
            continue
        if isinstance(value, float) and pd.isna(value):
            continue
        if isinstance(value, str) and value.strip() == "":
            continue

        # Include present metadata in OR filter
        metadata_conditions.append({col.lower(): {"$eq": value}})

    if not metadata_conditions:
        # No metadata present → search full vector DB
        return None

    # Build OR filter for Chroma
    return {"$or": metadata_conditions}