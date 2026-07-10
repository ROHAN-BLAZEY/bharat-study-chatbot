import os
import requests
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
from google.cloud import translate_v2 as translate

class DualRAGAgent:
    def __init__(self):
        # 1. Gemini API Setup (Replacing H200)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # 2. Translation API Setup
        try:
            self.translate_client = translate.Client()
        except Exception:
            self.translate_client = None
        
        # 3. Vector Database (ChromaDB) Setup
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name="enterprise_knowledge_base", 
            embedding_function=self.embed_fn
        )

    def ingest_document(self, text: str, filename: str):
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]
        self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)

    def fetch_news(self) -> list:
        news = []
        # GNews
        try:
            res = requests.get(f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&country=in&apikey={os.getenv('GNEWS_API_KEY', 'YOUR_KEY')}").json()
            if 'articles' in res:
                news.extend([{"title": a["title"], "source": "GNews"} for a in res["articles"][:2]])
        except Exception: pass
        
        # NewsData
        try:
            res = requests.get(f"https://newsdata.io/api/1/news?apikey={os.getenv('NEWSDATA_API_KEY', 'YOUR_KEY')}&country=in&language=en").json()
            if 'results' in res:
                news.extend([{"title": a["title"], "source": "NewsData"} for a in res["results"][:2]])
        except Exception: pass

        # ApiTube
        try:
            res = requests.get(f"https://api.apitube.io/v1/news/everything?api_key={os.getenv('APITUBE_API_KEY', 'YOUR_KEY')}&countries=IN").json()
            if 'results' in res:
                news.extend([{"title": a["title"], "source": "ApiTube"} for a in res["results"][:2]])
        except Exception: pass

        return news

    def translate_text(self, text: str, target_lang: str) -> str:
        if not self.translate_client or target_lang == "English":
            return text
        lang_codes = {
            "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "Marathi": "mr",
            "Bengali": "bn", "Gujarati": "gu", "Malayalam": "ml", "Kannada": "kn"
        }
        target_code = lang_codes.get(target_lang)
        if not target_code:
            return text
            
        try:
            result = self.translate_client.translate(text, target_language=target_code)
            return result['translatedText']
        except Exception as e:
            print(f"Translation Error: {e}")
            return text

    def process_prompt(self, prompt: str, tier: str, language: str = "English") -> dict:
        # Mock Data exclusively for human interactions (greetings/small talk)
        small_talk = ["hi", "hello", "hey", "how are you", "who are you", "good morning", "good evening"]
        if prompt.strip().lower() in small_talk:
            response = "Hello! I am the Bharat Study Chatbot. How can I assist you with your UPSC, Defence, or Tech exam preparation today?"
            final_text = self.translate_text(response, language)
            return {"response": final_text, "model": "Mocked Human Interaction", "sources": []}

        # Use RAG and LLM for everything else
        results = self.collection.query(query_texts=[prompt], n_results=3)
        
        context = ""
        sources = []
        if results['documents'] and results['documents'][0]:
            context = "\n...\n".join(results['documents'][0])
            sources = list(set([meta['source'] for meta in results['metadatas'][0]]))
            
        system_prompt = (
            "You are the Bharat Study Chatbot, a premium enterprise assistant for UPSC, Defence, Tech exams. "
            "Use the provided context to answer the user accurately. "
            "If requested, generate mind-maps strictly using ```mermaid code blocks."
        )

        full_prompt = f"{system_prompt}\n\nRetrieved Context: {context}\n\nUser: {prompt}"
        
        # Adjusting temp based on Tier
        temp = 0.2 if tier == "Fast" else (0.5 if tier == "Fast-Elite" else 0.8)
        generation_config = genai.types.GenerationConfig(temperature=temp)
        
        try:
            res = self.gemini_model.generate_content(full_prompt, generation_config=generation_config)
            final_text = self.translate_text(res.text, language)
            return {"response": final_text, "model": f"Gemini API ({tier})", "sources": sources}
        except Exception as e:
            return {"response": f"Gemini Error: {str(e)}", "model": "Error", "sources": []}