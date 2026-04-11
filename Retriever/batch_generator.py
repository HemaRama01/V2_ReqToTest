def generate_batches(df, batch_size=100):
    """
    Generator that yields DataFrame batches of given size.

    :param df: pandas DataFrame
    :param batch_size: number of rows per batch
    :return: yields DataFrame chunks
    """
    if df is None or df.empty:
        return

    total_rows = len(df)

    for start in range(0, total_rows, batch_size):
        end = start + batch_size
        yield df.iloc[start:end]