import os
import requests
import chromadb
from chromadb.utils import embedding_functions
from deep_translator import GoogleTranslator

class DualRAGAgent:
    def __init__(self):
        # 1. Vector Database (ChromaDB) Setup for document search
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name="enterprise_knowledge_base", 
            embedding_function=self.embed_fn
        )

        # 2. Language codes for translation
        self.lang_codes = {
            "English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta",
            "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu",
            "Malayalam": "ml", "Kannada": "kn", "Punjabi": "pa",
            "Odia": "or", "Assamese": "as", "Urdu": "ur"
        }

        # 3. Conversation memory for interactive chat
        self.conversation_history = []

    def ingest_document(self, text: str, filename: str):
        """Split document into chunks and store in ChromaDB."""
        chunk_size = 800
        overlap = 100
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)

        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        
        # Remove old chunks for the same file first
        try:
            existing = self.collection.get(where={"source": filename})
            if existing["ids"]:
                self.collection.delete(ids=existing["ids"])
        except Exception:
            pass
        
        self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)
        return len(chunks)

    def search_documents(self, query: str, n_results: int = 5) -> dict:
        """Search ChromaDB for relevant document chunks."""
        try:
            count = self.collection.count()
            if count == 0:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            
            actual_n = min(n_results, count)
            results = self.collection.query(query_texts=[query], n_results=actual_n)
            return results
        except Exception:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def fetch_news(self) -> list:
        """Fetch current affairs from all 3 news APIs."""
        news = []
        
        # GNews
        try:
            gnews_key = os.getenv('GNEWS_API_KEY', '')
            if gnews_key and gnews_key != 'YOUR_KEY':
                res = requests.get(
                    f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&country=in&apikey={gnews_key}",
                    timeout=8
                ).json()
                if 'articles' in res:
                    news.extend([{
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "GNews"),
                        "url": a.get("url", ""),
                        "published": a.get("publishedAt", "")
                    } for a in res["articles"][:5]])
        except Exception as e:
            print(f"GNews Error: {e}")
        
        # NewsData
        try:
            newsdata_key = os.getenv('NEWSDATA_API_KEY', '')
            if newsdata_key and newsdata_key != 'YOUR_KEY':
                res = requests.get(
                    f"https://newsdata.io/api/1/news?apikey={newsdata_key}&country=in&language=en",
                    timeout=8
                ).json()
                if 'results' in res and isinstance(res['results'], list):
                    for a in res["results"][:5]:
                        if isinstance(a, dict):
                            news.append({
                                "title": a.get("title", "") or "",
                                "description": a.get("description", "") or "",
                                "source": a.get("source_name", "NewsData") or "NewsData",
                                "url": a.get("link", "") or "",
                                "published": a.get("pubDate", "") or ""
                            })
        except Exception as e:
            print(f"NewsData Error: {e}")

        # ApiTube
        try:
            apitube_key = os.getenv('APITUBE_API_KEY', '')
            if apitube_key and apitube_key != 'YOUR_KEY':
                res = requests.get(
                    f"https://api.apitube.io/v1/news/everything?api_key={apitube_key}&countries=IN",
                    timeout=8
                ).json()
                if 'results' in res:
                    news.extend([{
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "ApiTube") if isinstance(a.get("source"), dict) else "ApiTube",
                        "url": a.get("url", ""),
                        "published": a.get("publishedAt", "")
                    } for a in res["results"][:5]])
        except Exception as e:
            print(f"ApiTube Error: {e}")

        return news

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text using free Google Translate (deep-translator)."""
        if not text or target_lang == "English" or target_lang == "en":
            return text
        
        target_code = self.lang_codes.get(target_lang, target_lang)
        if target_code == "en":
            return text
            
        try:
            # deep-translator handles large text by chunking automatically
            # Limit input to avoid timeouts
            input_text = text[:4500]
            translated = GoogleTranslator(source='en', target=target_code).translate(input_text)
            return translated if translated else text
        except Exception as e:
            # Silently fall back to English on any error
            return text

    def format_news_response(self, news: list) -> str:
        """Format news articles into a readable response."""
        if not news:
            return "I couldn't fetch current affairs right now. The news APIs may be temporarily unavailable. Please try again in a moment."
        
        response = "📰 **Here are the latest Current Affairs from India:**\n\n"
        seen_titles = set()
        count = 0
        for article in news:
            title = article.get("title", "").strip()
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            count += 1
            desc = article.get("description", "") or ""
            source = article.get("source", "News")
            response += f"**{count}. {title}**\n"
            if desc:
                response += f"   {desc[:200]}\n"
            response += f"   — *{source}*\n\n"
            if count >= 8:
                break
        
        response += "💡 *Ask me about any of these topics for more details, or upload a study document!*"
        return response

    def process_prompt(self, prompt: str, tier: str = "Fast", language: str = "English") -> dict:
        """Process user prompts without any LLM — using document search + smart responses."""
        
        prompt_lower = prompt.strip().lower()
        
        # 1. Greetings / Small Talk
        greetings = ["hi", "hello", "hey", "how are you", "who are you", "good morning", 
                      "good evening", "good night", "namaste", "namaskar", "what can you do"]
        if prompt_lower in greetings:
            response = (
                "🙏 Namaste! I am the **Bharat Study Chatbot** — your study companion for UPSC, Defence, and Tech exam preparation.\n\n"
                "Here's what I can do:\n"
                "• 📰 **Current Affairs** — Get the latest Indian news\n"
                "• 📄 **Document Q&A** — Upload a PDF/TXT file and ask questions about it\n"
                "• 🌐 **Multilingual** — Change language using the globe icon below\n\n"
                "How can I help you today?"
            )
            final_text = self.translate_text(response, language)
            return {"response": final_text, "model": "Bharat Study Bot", "sources": []}

        # 2. Current Affairs Request
        news_keywords = ["news", "current affairs", "current events", "headlines", "today's news",
                         "latest news", "whats happening", "what's happening", "current affair"]
        if any(kw in prompt_lower for kw in news_keywords):
            news = self.fetch_news()
            response = self.format_news_response(news)
            final_text = self.translate_text(response, language)
            sources = list(set([a.get("source", "News") for a in news[:5]]))
            return {"response": final_text, "model": "News Aggregator", "sources": sources}

        # 3. Document-based Q&A — Search uploaded files
        results = self.search_documents(prompt)
        
        if results['documents'] and results['documents'][0] and len(results['documents'][0]) > 0:
            # We found relevant content in uploaded documents
            context_chunks = results['documents'][0]
            sources = list(set([meta['source'] for meta in results['metadatas'][0]]))
            
            # Build a helpful response from the matched content
            response = f"📄 **Based on your uploaded documents, here's what I found:**\n\n"
            
            for i, chunk in enumerate(context_chunks[:3]):
                cleaned = chunk.strip()
                if len(cleaned) > 50:  # Only show substantive chunks
                    response += f"**Excerpt {i+1}:**\n{cleaned}\n\n"
            
            response += "---\n💡 *Want to know more? Try asking a more specific question about this topic, or upload another document.*"
            
            final_text = self.translate_text(response, language)
            return {"response": final_text, "model": "Document Search", "sources": sources}

        # 4. No documents uploaded — guide the user
        # Check if it's an exam-related question
        exam_keywords = ["upsc", "ias", "ips", "defence", "nda", "cds", "gate", "ssc", "banking",
                         "polity", "geography", "history", "economy", "science", "constitution",
                         "parliament", "president", "prime minister"]
        
        if any(kw in prompt_lower for kw in exam_keywords):
            response = (
                f"📚 Great question about **{prompt}**!\n\n"
                "I can help you study this topic effectively. Here's what you can do:\n\n"
                "1. 📄 **Upload a study PDF or notes** about this topic, and I'll search through it to find relevant answers\n"
                "2. 📰 **Ask for Current Affairs** to get the latest news related to this subject\n"
                "3. 🔍 **Ask specific questions** after uploading your study material\n\n"
                "💡 *Upload your NCERT, Laxmikanth, or any study material to get started!*"
            )
        else:
            response = (
                f"I'd love to help you with **\"{prompt}\"**!\n\n"
                "To give you the best answers, please:\n\n"
                "1. 📄 **Upload a document** (PDF or TXT) with your study material — I'll search it and find relevant answers\n"
                "2. 📰 **Try 'Current Affairs'** to get the latest Indian news\n"
                "3. 💬 **Ask exam-related questions** like UPSC, Defence, Gate topics\n\n"
                "💡 *The more documents you upload, the smarter I become about your subjects!*"
            )
        
        final_text = self.translate_text(response, language)
        return {"response": final_text, "model": "Bharat Study Bot", "sources": ["Global Knowledge Base"]}