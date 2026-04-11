

def clean_colon_prefixes(df):
    """
    Removes prefixes before ':' in all string cells of the DataFrame
    Example: 'qwert:gtrtujm rgh:gfdghj' -> 'gtrtujm gfdghj'
    """
    df = df.copy()

    def _remove_prefix(text):
        if not isinstance(text, str):
            return text
        return " ".join(word.split(":", 1)[-1] for word in text.split())

    string_cols = df.select_dtypes(include="object").columns
    df[string_cols] = df[string_cols].map(_remove_prefix)

    return df

