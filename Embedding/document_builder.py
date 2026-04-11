from langchain_core.documents import Document

def chunks_to_documents(chunks):
    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            )
        )

    return documents
