import os

class RAGPipeline:
    def __init__(self):
        print("Initializing RAG Pipeline Components...")
        self.vector_store = []
        
    def ingest_document(self, document_text):
        print("Chunking and vectorizing document...")
        self.vector_store.append(document_text)
        print("Document ingested successfully.")
        
    def query(self, user_prompt):
        print(f"Searching vector store for: {user_prompt}")
        return "Retrieved context for prompt."

if __name__ == '__main__':
    pipeline = RAGPipeline()
    pipeline.ingest_document("This is a study document for UPSC.")
    response = pipeline.query("What is this document about?")
    print("Response:", response)
