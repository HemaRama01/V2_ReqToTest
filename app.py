import uuid
import io
import pandas as pd
import streamlit as st
from Pre_processing.lowercase_cleaner import convert_to_lowercase
from Pre_processing.colon_cleaner import clean_colon_prefixes
from Pre_processing.row_chunker import row_based_chunking
from Embedding.document_builder import chunks_to_documents
from Embedding.embedding_model import load_embedding_model
from Embedding.vector_store import store_documents
from Retriever.batch_generator import generate_batches
from Retriever.similarity_executor import execute_similarity_for_row
# Step 1 & 2 — Streamlit page
st.title("Similarity Detector")

# Loaded ONCE for entire app — shared across all users and all reruns
@st.cache_resource
def model_loader():
    return load_embedding_model()

embeddings = model_loader()

# Step 3 — Session bootstrap
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "old_db" not in st.session_state:
    st.session_state.old_db = None
if "df" not in st.session_state:
    st.session_state.df = None
if "validated_id" not in st.session_state:
    st.session_state.validated_id = None

# Step 3 — Input 1 upload
old_file = st.file_uploader(
    "Upload Old Requirements (Excel only)",
    type=["xlsx", "xls"],
    accept_multiple_files=False,
    key="inp1"
)

if old_file is not None and st.session_state.old_db is None:

    # Step 4 — Acknowledge upload
    st.success("File uploaded successfully!")
    df_old = pd.read_excel(old_file)

    with st.spinner("Processing old requirements..."):

        # Step 6 — Full preprocessing + embedding pipeline
        df_old    = convert_to_lowercase(df_old)
        df_old    = clean_colon_prefixes(df_old)
        chunks    = row_based_chunking(df_old)
        documents = chunks_to_documents(chunks)
        st.session_state.old_db = store_documents(
            documents,
            embeddings,
            collection_name=f"req_{st.session_state.session_id}"
        )

    st.info(f"Old requirements processed- ({len(documents)} requirements!)")
if st.session_state.old_db is None:
    st.warning("Please upload and process Input 1 first.")
    st.stop()
#Step5:Input2
new_file = st.file_uploader(
    "Upload New Requirements (Excel only)",
    type=["xlsx", "xls"],
    accept_multiple_files=False,
    key="inp2"
)
if new_file is not None:
    st.session_state.df = pd.read_excel(new_file)
    st.success("File uploaded and saved!")
current_df = st.session_state.df

if current_df is not None:
    act = st.toggle("ID Mode")
    if not act:
        st.session_state.validated_id = None
    if act:
        req_id = st.text_input("Enter Req ID:", placeholder="Numbers only")
        if req_id:
            if req_id.isdigit():
                num = int(req_id)
                if num > 0:
                    st.session_state.validated_id = num
                else:
                    st.error("Please enter a number greater than zero.")
                    st.session_state.validated_id = None
            else:
                st.error("Invalid input. Please remove alphabets/symbols.")
                st.session_state.validated_id = None

current_id = st.session_state.validated_id

if current_df is None:
    st.warning("Please upload Input 2 file.")
    st.stop()
    
if st.button("Process Similarity"):

    # Step 5 — ID filter or full file
    if current_id is not None:
        df_to_process = current_df.query("ID == @current_id")
        if df_to_process.empty:
            st.error(f"ID {current_id} not found in the file.")
            st.stop()
    else:
        df_to_process = current_df

    # Step 8,9 — Batch + similarity
    all_results = []
    db = st.session_state.old_db

    with st.spinner("Processing similarity... please wait."):
        for batch in generate_batches(df_to_process, batch_size=100):
            for idx in range(len(batch)):
                current_row = batch.iloc[[idx]]
                row_results = execute_similarity_for_row(db, current_row, k=1)
                all_results.extend(row_results)

    # Step 10 — Club results + download
    final_df = pd.DataFrame(all_results)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, index=False, sheet_name="Similarity Results")

    if not final_df.empty:
        st.success(f"Done! Processed {len(final_df)} rows successfully.")
        st.download_button(
            label="Download Results as Excel",
            data=buffer.getvalue(),
            file_name="similarity_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )