# import uuid
# import io
# import pandas as pd
# import streamlit as st
# from Pre_processing.lowercase_cleaner import convert_to_lowercase
# from Pre_processing.colon_cleaner import clean_colon_prefixes
# from Pre_processing.row_chunker import row_based_chunking
# from Embedding.document_builder import chunks_to_documents
# from Embedding.embedding_model import load_embedding_model
# from Embedding.vector_store import store_documents
# from Retriever.batch_generator import generate_batches
# from Retriever.similarity_executor import execute_similarity_for_row
# # Step 1 & 2 — Streamlit page
# st.title("Similarity Detector")

# # Loaded ONCE for entire app — shared across all users and all reruns
# @st.cache_resource
# def model_loader():
#     return load_embedding_model()

# embeddings = model_loader()

# # Step 3 — Session bootstrap
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())
# if "old_db" not in st.session_state:
#     st.session_state.old_db = None
# if "df" not in st.session_state:
#     st.session_state.df = None
# if "validated_id" not in st.session_state:
#     st.session_state.validated_id = None

# # Step 3 — Input 1 upload
# old_file = st.file_uploader(
#     "Upload Old Requirements (only 1 Excel file)",
#     type=["xlsx", "xls"],
#     accept_multiple_files=False,
#     key="inp1"
# )

# if old_file is not None and st.session_state.old_db is None:

#     # Step 4 — Acknowledge upload
#     st.success("File uploaded successfully!")
#     df_old = pd.read_excel(old_file)

#     with st.spinner("Processing old requirements..."):

#         # Step 6 — Full preprocessing + embedding pipeline
#         df_old    = convert_to_lowercase(df_old)
#         df_old    = clean_colon_prefixes(df_old)
#         chunks    = row_based_chunking(df_old)
#         documents = chunks_to_documents(chunks)
#         st.session_state.old_db = store_documents(
#             documents,
#             embeddings,
#             collection_name=f"req_{st.session_state.session_id}"
#         )

#     st.info(f"Old requirements processed- ({len(documents)} requirements!)")
# if st.session_state.old_db is None:
#     st.warning("Please upload and process Input 1 first.")
#     st.stop()
# #Step5:Input2
# new_file = st.file_uploader(
#     "Upload New Requirements (only 1 Excel file)",
#     type=["xlsx", "xls"],
#     accept_multiple_files=False,
#     key="inp2"
# )
# if new_file is not None:
#     st.session_state.df = pd.read_excel(new_file)
#     st.success("File uploaded and saved!")
# current_df = st.session_state.df

# if current_df is not None:
#     act = st.toggle("ID Mode")
#     if not act:
#         st.session_state.validated_id = None
#     if act:
#         req_id = st.text_input("Enter Req ID:", placeholder="Numbers only")
#         if req_id:
#             if req_id.isdigit():
#                 num = int(req_id)
#                 if num > 0:
#                     st.session_state.validated_id = num
#                 else:
#                     st.error("Please enter a number greater than zero.")
#                     st.session_state.validated_id = None
#             else:
#                 st.error("Invalid input. Please remove alphabets/symbols.")
#                 st.session_state.validated_id = None

# current_id = st.session_state.validated_id

# if current_df is None:
#     st.warning("Please upload Input 2 file.")
#     st.stop()
    
# if st.button("Process Similarity"):

#     # Step 5 — ID filter or full file
#     if current_id is not None:
#         df_to_process = current_df.query("ID == @current_id")
#         if df_to_process.empty:
#             st.error(f"ID {current_id} not found in the file.")
#             st.stop()
#     else:
#         df_to_process = current_df

#     # Step 8,9 — Batch + similarity
#     all_results = []
#     db = st.session_state.old_db

#     with st.spinner("Processing similarity... please wait."):
#         for batch in generate_batches(df_to_process, batch_size=100):
#             for idx in range(len(batch)):
#                 current_row = batch.iloc[[idx]]
#                 row_results = execute_similarity_for_row(db, current_row, k=1)
#                 all_results.extend(row_results)

#     # Step 10 — Club results + download
#     final_df = pd.DataFrame(all_results)

#     buffer = io.BytesIO()
#     with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
#         final_df.to_excel(writer, index=False, sheet_name="Similarity Results")

#     if not final_df.empty:
#         st.success(f"Done! Processed {len(final_df)} rows successfully.")
#         st.download_button(
#             label="Download Results as Excel",
#             data=buffer.getvalue(),
#             file_name="similarity_results.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

import uuid
import io
import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from Pre_processing.lowercase_cleaner import convert_to_lowercase
from Pre_processing.colon_cleaner import clean_colon_prefixes
from Pre_processing.row_chunker import row_based_chunking
from Embedding.document_builder import chunks_to_documents
from Embedding.embedding_model import load_embedding_model
from Embedding.vector_store import store_documents
from Retriever.batch_generator import generate_batches
from Retriever.similarity_executor import execute_similarity_for_row

# --- Page Configuration ---
st.set_page_config(page_title="Similarity Detector Pro", layout="wide")


# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "old_db" not in st.session_state:
    st.session_state.old_db = None
if "db_ready" not in st.session_state:
    st.session_state.db_ready = False
if "df_new" not in st.session_state:
    st.session_state.df_new = None



# --- Model Loader ---
@st.cache_resource
def model_loader():
    return load_embedding_model()

embeddings = model_loader()

st.title("Similarity Detector")
st.warning("Instructions: You cannot refresh the page anytime without losing uploaded files./n 1. Old requirement must have its id , text, verified by features before giving input./n 2. New requirement should have id and text ")

# --- Step 1: Input Section (Parallel File Uploads) ---
col1, col2 = st.columns(2)

with col1:
    st.header("Input 1: Old Requirements")
    old_files = st.file_uploader(
        "Upload Old Requirements (Multiple Excels supported)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="inp1"
    )

with col2:
    st.header("Input 2: New Requirements")
    new_file = st.file_uploader(
        "Upload New Requirements (Single Excel)",
        type=["xlsx", "xls"],
        accept_multiple_files=False,
        key="inp2"
    )

# --- Step 2: Background Processing for Input 1 ---
# This triggers immediately when files are uploaded
if old_files and not st.session_state.db_ready:
    with st.status("Indexing Knowledge Base...", expanded=True) as status:
        st.write("Merging ...")
        # Parallel-style concatenation
        df_list = [pd.read_excel(f) for f in old_files]
        df_old = pd.concat(df_list, ignore_index=True)
        
        st.write("Preprocessing...")
        df_old = convert_to_lowercase(df_old)
        df_old = clean_colon_prefixes(df_old)
        
        st.write("Memory creation...")
        chunks = row_based_chunking(df_old)
        documents = chunks_to_documents(chunks)
        st.session_state.old_db = store_documents(
            documents,
            embeddings,
            collection_name=f"req_{st.session_state.session_id}"
        )
        st.session_state.db_ready = True
        status.update(label="Input 1 Ready!", state="complete", expanded=False)

# Store Input 2 in state when uploaded
if new_file:
    st.session_state.df_new = pd.read_excel(new_file)
    st.status(f" Input 2 Ready: {new_file.name}")

st.divider()

# --- Step 3: Execution Logic (The "Gate") ---
# The tool only functions once both inputs are valid
if st.session_state.db_ready and st.session_state.df_new is not None:
    
    # Mode Selection
    id_mode = st.toggle("ID Mode (UI Visualization Only)")
    
    validated_id = None
    if id_mode:
        req_id_input = st.text_input("Enter Req ID:", placeholder="Numbers only")
        if req_id_input:
            if req_id_input.isdigit():
                validated_id = int(req_id_input)
            else:
                st.error("Please enter a valid numeric ID.")

    # Main Process Button
    if st.button("Process Similarity", type="primary"):
        current_df = st.session_state.df_new
        db = st.session_state.old_db

        # ID MODE LOGIC
        if id_mode:
            if validated_id is not None:
                df_to_process = current_df.query("ID == @validated_id")
                if df_to_process.empty:
                    st.error(f"ID {validated_id} not found in Input 2.")
                else:
                    with st.spinner(f"Searching for most similar matches for ID: {validated_id}..."):
                        # k=3 for better visual context in UI
                        results = execute_similarity_for_row(db, df_to_process, k=3)
                    st.dataframe(pd.DataFrame(results), use_container_width=True) 
            else:
                st.warning("Please provide a Req ID for ID Mode.")

        # FULL BATCH MODE LOGIC
        else:
            all_results = []
            batches = list(generate_batches(current_df, batch_size=50))
            total_batches = len(batches)
            
            # Progress Bar Implementation
            progress_text = "Processing similarities in parallel. Please wait."
            my_bar = st.progress(0, text=progress_text)
            
            # Helper for thread execution
            def process_batch_parallel(batch_df):
                batch_res = []
                for i in range(len(batch_df)):
                    row = batch_df.iloc[[i]]
                    batch_res.extend(execute_similarity_for_row(db, row, k=1))
                return batch_res

            # Parallel Execution using ThreadPool
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_batch = {executor.submit(process_batch_parallel, b): i for i, b in enumerate(batches)}
                
                for future in future_to_batch:
                    batch_index = future_to_batch[future]
                    all_results.extend(future.result())
                    # Update progress bar
                    percent_complete = (batch_index + 1) / total_batches
                    my_bar.progress(percent_complete, text=f"Processed batch {batch_index + 1} of {total_batches}")

            my_bar.empty() # Remove progress bar when done
            
            # Results and Download
            final_df = pd.DataFrame(all_results)
            if not final_df.empty:
                st.success(f"Analysis Complete! Processed {len(final_df)} rows.")
                st.dataframe(final_df, use_container_width=True) # UI Preview
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    final_df.to_excel(writer, index=False, sheet_name="Similarity Results")
                
                st.download_button(
                    label="Download Full Results (Excel)",
                    type = "secondary",
                    data=buffer.getvalue(),
                    file_name="similarity_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

elif not st.session_state.db_ready and new_file:
    st.info("Input 2 is uploaded. Waiting for Input 1 to finish processing...")
elif st.session_state.db_ready and not new_file:
    st.info("Input 1 is ready. Please upload Input 2 to enable processing.")
else:
    st.info("Please upload both Input 1 and Input 2 files to begin.")