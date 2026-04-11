import pandas as pd

def save_results_to_excel(all_results, file_name="similarity_results.xlsx"):
    if not all_results:
        print("No results to save.")
        return

    output_df = pd.DataFrame(all_results)
    output_df.to_excel(file_name, index=False)
    print(f"Created Excel with {len(output_df)} rows at {file_name}")