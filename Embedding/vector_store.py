
# import os
# from langchain_chroma import Chroma

# def store_documents(documents, embeddings, collection_name, persist_dir="chroma_store"):
#     persist_dir = os.path.abspath(persist_dir)
#     print(f"   → Persist directory: {persist_dir}")

#     os.makedirs(persist_dir, exist_ok=True)

#     print("   → Creating Chroma vector store")
#     db = Chroma(
#         collection_name=collection_name,
#         embedding_function=embeddings,
#         persist_directory=persist_dir
#     )

#     print("   → Adding documents to Chroma")
#     batch_size = 1600
#     total_docs = len(documents)

#     for i in range(0, total_docs, batch_size):
#         batch = documents[i:i+batch_size]
#         print(f"      - Adding batch {i // batch_size + 1} ({len(batch)} docs)")
#         db.add_documents(batch)

#     # Persist the collection to disk
    
#     print(f"   → Chroma finished successfully. Total documents added: {total_docs}")

#     return db

from langchain_chroma import Chroma

def store_documents(documents, embeddings, collection_name):
    """
    Stores documents in an in-memory Chroma vector store.
    No persistence — lives only in RAM for the current session.
    """

    print("   → Creating in-memory Chroma vector store")
    db = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings
    )

    print("   → Adding documents to Chroma")
    batch_size = 1600
    total_docs = len(documents)

    for i in range(0, total_docs, batch_size):
        batch = documents[i:i + batch_size]
        print(f"      - Added batch {i // batch_size + 1} ({len(batch)} docs)")
        db.add_documents(batch)

    print(f"   → Vectorisation finished successfully. Total documents added: {total_docs}")

    return db
