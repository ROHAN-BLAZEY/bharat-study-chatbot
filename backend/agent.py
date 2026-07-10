import os
import requests
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
from openai import OpenAI

class DualRAGAgent:
    def __init__(self):
        # 1. NVIDIA H200 vLLM Local Endpoint (Llama 3 70B)
        self.llama_client = OpenAI(base_url="http://localhost:8000/v1", api_key="local-h200-key")
        
        # 2. Gemini API Fallback
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # 3. Vector Database (ChromaDB) Setup
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction() # Uses an optimized transformer model
        self.collection = self.chroma_client.get_or_create_collection(
            name="enterprise_knowledge_base", 
            embedding_function=self.embed_fn
        )

    def ingest_document(self, text: str, filename: str):
        """Chunks massive documents and stores them in the Vector Database."""
        # Chunk text into 1000-character blocks for precise retrieval
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]
        
        # Add embedded vectors to ChromaDB
        self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)

    def fetch_news(self) -> list:
        # Same news logic as before (GNews & NewsData APIs)
        news = []
        try:
            res = requests.get(f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&country=in&apikey={os.getenv('GNEWS_API_KEY', 'YOUR_KEY')}").json()
            if 'articles' in res:
                news.extend([{"title": a["title"], "source": "GNews"} for a in res["articles"][:3]])
        except Exception: pass
        return news

    def process_prompt(self, prompt: str, tier: str) -> dict:
        """Queries the Vector DB for context, then sends to the LLMs."""
        # 1. Retrieve most relevant context chunks from Vector DB
        results = self.collection.query(query_texts=[prompt], n_results=3)
        
        context = ""
        sources = []
        if results['documents'] and results['documents'][0]:
            context = "\n...\n".join(results['documents'][0])
            sources = list(set([meta['source'] for meta in results['metadatas'][0]]))
            
        system_prompt = (
            "You are the Bharat Study Chatbot, a premium enterprise assistant. "
            "Use the provided context to answer the user accurately. "
            "If requested, generate mind-maps strictly using ```mermaid code blocks."
        )

        # 2. Route to AI Tier
        if tier == "Fast":
            full_prompt = f"{system_prompt}\n\nRetrieved Context: {context}\n\nUser: {prompt}"
            try:
                res = self.gemini_model.generate_content(full_prompt)
                return {"response": res.text, "model": "Gemini API", "sources": sources}
            except Exception as e:
                return {"response": f"Gemini Error: {str(e)}", "model": "Error", "sources": []}
        else:
            temp = 0.3 if tier == "Fast-Elite" else 0.7
            try:
                res = self.llama_client.chat.completions.create(
                    model="llama3-70b-rag",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Context:\n{context}\n\nUser:\n{prompt}"}
                    ],
                    temperature=temp, max_tokens=2048
                )
                return {"response": res.choices[0].message.content, "model": "Llama 3 70B (H200)", "sources": sources}
            except Exception as e:
                return {"response": f"H200 Error: Details: {str(e)}", "model": "Error", "sources": []}