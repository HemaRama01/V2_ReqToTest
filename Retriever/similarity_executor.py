
from difflib import ndiff

def execute_similarity_for_row(db, row_df, k=1):
    """
    Executes similarity search for a single row using optional metadata filter.
    Returns list of dictionaries (results).
    """
    from Pre_processing.lowercase_cleaner import convert_to_lowercase
    from Pre_processing.colon_cleaner import clean_colon_prefixes
    from Retriever.metadata_filter import build_or_filter

    current_row = row_df.copy()
    current_row = convert_to_lowercase(current_row)
    current_row = clean_colon_prefixes(current_row)

    query_text = "query: " + str(current_row["text"].iloc[0])
    actual_id = current_row["id"].iloc[0]

    # Build OR metadata filter
    filter_for_db = build_or_filter(current_row.iloc[0].to_dict())

    print(f"Performing similarity search for ID {actual_id}")

    results = db.similarity_search_with_relevance_scores(query_text, k=k, filter=filter_for_db)
    output = []
    for i, (doc, score) in enumerate(results, 1):
     row_data = current_row.to_dict(orient="records")[0]
     row_data.update({
        "Result_Rank": i,
        "Similarity_Score": score,
        "Matched_ReqID": doc.metadata.get("id"),
        "State": doc.metadata.get("state"),
        "Matched_Text": doc.page_content,
        "Verified by": doc.metadata.get("verified by"),
     })

     # Add error fields only if they exist in metadata
     if "error event name" in doc.metadata:
        row_data["Matched_Error_Event_Name"] = doc.metadata["error event name"]
     if "error name" in doc.metadata:
        row_data["Matched_Error_Name"] = doc.metadata["error name"]

     orig_text = str(row_data.get("text", ""))
     matched_text = str(doc.page_content)

     diff_lines = [
        line for line in ndiff(orig_text.split(), matched_text.split())
        if line.startswith("- ") or line.startswith("+ ")
     ]
     row_data["Difference"] = "\n".join(diff_lines)

     output.append(row_data)



    return output