import uuid

def row_based_chunking(df):
    """
    Each row = one chunk.
    'text' column used for embedding.
    All other columns used as metadata.
    'id' used as chunk ID.
    """

    df.columns = df.columns.str.strip().str.lower()

    if "text" not in df.columns:
        raise ValueError("Column 'text' not found")

    chunks = []

    for _, row in df.iterrows():

        chunk_id =  str(uuid.uuid4())

        # Metadata = everything except text
        metadata = {
            col: row[col]
            for col in df.columns
            if col != "text"
        }

        chunks.append({
            "id": chunk_id,        # Vector ID
            "text": str(row["text"]),
            "metadata": metadata
        })

    return chunks
