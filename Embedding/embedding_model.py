import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings


def load_embedding_model():
    print("  → Initializing HuggingFaceEmbeddings (ES large BASE)")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    print("  → HuggingFaceEmbeddings initialized successfully")
    return embeddings
