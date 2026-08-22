import os
import requests
import chromadb
from chromadb.utils import embedding_functions
from gpt4all import GPT4All
from deep_translator import GoogleTranslator

class LocalStudyAgent:
    def __init__(self):
        print("Initializing Local AI Model (this may take a while to download if it's the first time)...")
        # UPGRADED to Meta-Llama-3-8B-Instruct.Q4_0.gguf for highly advanced reasoning.
        # This is the smartest CPU-friendly model that won't crash and understands complex instructions.
        self.model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", n_ctx=4096)
        
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

    def search_documents(self, query: str, n_results: int = 3) -> dict:
        """Hybrid Search: ChromaDB (Semantic) + BM25 (Keyword)."""
        try:
            count = self.collection.count()
            if count == 0:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            
            actual_n = min(n_results, count)
            
            # 1. Semantic Search (ChromaDB)
            results = self.collection.query(query_texts=[query], n_results=actual_n)
            semantic_docs = results['documents'][0] if results['documents'] else []
            semantic_metas = results['metadatas'][0] if results['metadatas'] else []
            
            # 2. Keyword Search (BM25)
            try:
                from rank_bm25 import BM25Okapi
                import numpy as np
                all_data = self.collection.get()
                all_docs = all_data['documents']
                all_metas = all_data['metadatas']
                
                # Simple tokenization
                tokenized_corpus = [doc.lower().split(" ") for doc in all_docs]
                bm25 = BM25Okapi(tokenized_corpus)
                tokenized_query = query.lower().split(" ")
                
                # Get top N indices
                doc_scores = bm25.get_scores(tokenized_query)
                top_n = np.argsort(doc_scores)[::-1][:actual_n]
                
                keyword_docs = [all_docs[i] for i in top_n if doc_scores[i] > 0]
                keyword_metas = [all_metas[i] for i in top_n if doc_scores[i] > 0]
            except Exception as e:
                print(f"BM25 Error: {e}")
                keyword_docs = []
                keyword_metas = []
                
            # Combine and deduplicate
            combined_docs = []
            combined_metas = []
            seen = set()
            
            for doc, meta in zip(semantic_docs + keyword_docs, semantic_metas + keyword_metas):
                if doc not in seen:
                    seen.add(doc)
                    combined_docs.append(doc)
                    combined_metas.append(meta)
                    
            # Return top 4 combined
            return {"documents": [combined_docs[:4]], "metadatas": [combined_metas[:4]]}
            
        except Exception as e:
            print(f"Search error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def clear_documents(self):
        """Clear all documents from the ChromaDB collection."""
        try:
            doc_data = self.collection.get()
            if doc_data and doc_data['ids']:
                self.collection.delete(ids=doc_data['ids'])
            return True
        except Exception as e:
            print(f"Error clearing documents: {e}")
            return False

    def fetch_news(self) -> list:
        """Fetch current affairs completely free using public RSS feeds."""
        import feedparser
        news = []
        
        # RSS Feeds (Free, no keys needed, no limits)
        feeds = [
            ("The Hindu", "https://www.thehindu.com/news/national/feeder/default.rss"),
            ("Times of India", "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms")
        ]
        
        for source_name, url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:4]:  # Top 4 from each
                    news.append({
                        "title": getattr(entry, "title", ""),
                        "description": getattr(entry, "summary", getattr(entry, "description", "")),
                        "source": source_name,
                        "url": getattr(entry, "link", ""),
                        "published": getattr(entry, "published", "")
                    })
            except Exception as e:
                print(f"Failed to fetch from {source_name}: {e}")
                
        return news

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text using free Google Translate (deep-translator)."""
        if not text or target_lang == "English" or target_lang == "en":
            return text
        
        target_code = self.lang_codes.get(target_lang, target_lang)
        if target_code == "en":
            return text
            
        try:
            input_text = text[:4500]
            translated = GoogleTranslator(source='en', target=target_code).translate(input_text)
            return translated if translated else text
        except Exception as e:
            return text

    def format_news_response(self, news: list) -> str:
        """Format news articles into a readable response."""
        if not news:
            return "I couldn't fetch current affairs right now. Please check your internet connection."
        
        response = "📰 Here are the latest Current Affairs from India (Live & Free):\n\n"
        seen_titles = set()
        count = 0
        for article in news:
            title = article.get("title", "").strip()
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            count += 1
            
            # Clean HTML tags out of descriptions
            import re
            desc = article.get("description", "") or ""
            desc = re.sub(r'<[^>]+>', '', desc)
            
            source = article.get("source", "News")
            response += f"{count}. {title}\n"
            if desc:
                response += f"   {desc[:150]}...\n"
            response += f"   — {source}\n\n"
            if count >= 8:
                break
        
        response += "💡 Ask me about any of these topics for more details, or upload a study document!"
        return response

    def process_prompt(self, prompt: str, tier: str = "Fast", language: str = "English", history: list = None, stream: bool = False):
        """Process user prompts using Local LLM + ChromaDB RAG, with full history and streaming support."""
        if history is None:
            history = []
            
        prompt_lower = prompt.strip().lower()
        import re
        import json
        
        # 1. Greetings
        greetings = ["hi", "hello", "hey", "how are you", "who are you", "good morning", 
                      "good evening", "good night", "namaste", "namaskar", "what can you do"]
        
        clean_prompt_lower = re.sub(r'[^a-z0-9\s]', '', prompt_lower).strip()
        
        if clean_prompt_lower in greetings:
            response = (
                "🙏 Namaste! I am the Bharat Study Chatbot — your AI study companion for UPSC, Defence, and Tech exam preparation.\n\n"
                "How can I help you today? Here are some questions you can ask me:\n"
                "👉 \"Create a 30-day Study Roadmap for UPSC Prelims\"\n"
                "👉 \"Review my answer for the 1857 Revolt (Answer Writing Feedback)\"\n"
                "👉 \"Start a Mock Interview for GPSC\"\n"
                "👉 \"What is the news today?\"\n\n"
                "You can also change the language using the globe icon below!"
            )
            final_text = self.translate_text(response, language)
            if stream:
                def gen():
                    yield json.dumps({"text": final_text}) + "\n"
                    yield json.dumps({"sources": []}) + "\n"
                return gen()
            return {"response": final_text, "model": "Local Llama-3 AI", "sources": []}

        # 2. Current Affairs Request
        news_keywords = ["news", "current affairs", "current events", "headlines", "todays news",
                         "latest news", "whats happening", "current affair"]
        if any(kw in clean_prompt_lower for kw in news_keywords):
            news = self.fetch_news()
            response = self.format_news_response(news)
            final_text = self.translate_text(response, language)
            sources = list(set([a.get("source", "News") for a in news[:5]]))
            if stream:
                def gen():
                    yield json.dumps({"text": final_text}) + "\n"
                    yield json.dumps({"sources": sources}) + "\n"
                return gen()
            return {"response": final_text, "model": "News Aggregator", "sources": sources}

        # 3. RAG Search + Local LLM
        sources = []
        system_prompt = ""
        
        search_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', prompt).lower().strip()
        
        if self.collection.count() > 0:
            results = self.search_documents(search_query, n_results=3)
            if results['documents'] and results['documents'][0] and len(results['documents'][0]) > 0:
                context_chunks = results['documents'][0]
                sources = list(set([meta['source'] for meta in results['metadatas'][0]]))
                context_str = "\n".join(context_chunks[:3])
                
                system_prompt = (
                    "1. You are the Bharat Study Chatbot, an advanced AI Mentor built for UPSC, GPSC, SSC, and PSC aspirants.\n"
                    "2. When explaining concepts, ALWAYS use UPSC-Style Structured Answers: provide a clear Introduction, a main Body with bullet points and subheadings, and a crisp Conclusion.\n"
                    "3. If a user asks for a Study Roadmap, generate a highly personalized, structured day-by-day study plan.\n"
                    "4. If a user pastes an answer, provide elite 'Answer Writing Feedback' (evaluate Introduction, Body, Conclusion, and suggest improvements/marks).\n"
                    "5. If a user asks for 'Mock Interview', ask them a tough interview question and wait for their response to evaluate them.\n"
                    "6. Base your answers strictly on the provided context if available, otherwise use your expert knowledge.\n"
                    "7. Answer in the language requested by the user, but maintain high-quality academic language.\n\n"
                    f"Document Context:\n{context_str}"
                )
            else:
                system_prompt = (
                    "1. You are the Bharat Study Chatbot, an advanced AI Mentor built for UPSC, GPSC, SSC, and PSC aspirants.\n"
                    "2. When explaining concepts, ALWAYS use UPSC-Style Structured Answers: provide a clear Introduction, a main Body with bullet points and subheadings, and a crisp Conclusion.\n"
                    "3. If a user asks for a Study Roadmap, generate a highly personalized, structured day-by-day study plan.\n"
                    "4. If a user pastes an answer, provide elite 'Answer Writing Feedback' (evaluate Introduction, Body, Conclusion, and suggest improvements/marks).\n"
                    "5. If a user asks for 'Mock Interview', ask them a tough interview question and wait for their response to evaluate them.\n"
                    "6. Base your answers strictly on the provided context if available, otherwise use your expert knowledge.\n"
                    "7. Answer in the language requested by the user, but maintain high-quality academic language.\n\n"
                )
                sources = ["Local LLM Pre-trained Knowledge Base"]
        else:
            system_prompt = (
                "You are Bharat Study Chatbot, a highly knowledgeable AI study assistant specialized in the UPSC syllabus, "
                "current affairs, and general study preparation. Use the chat history to understand context. Interpret the user's question despite any casing, "
                "punctuation, or grammar inconsistencies and answer clearly, concisely, and accurately."
            )
            sources = ["Local LLM Pre-trained Knowledge Base"]
        
        # Build the Llama-3 style prompt with full history
        full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_prompt}<|eot_id|>"
        
        # Append history to prompt (truncate old messages to save tokens)
        for msg in history:
            role_map = "user" if msg.get("role") == "user" else "assistant"
            content = msg.get("content", "")
            if len(content) > 500:
                content = content[:500] + "... [truncated]"
            full_prompt += f"<|start_header_id|>{role_map}<|end_header_id|>\n{content}<|eot_id|>"
            
        # Append the new prompt
        full_prompt += f"<|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
        
        if stream:
            def llm_generator():
                print("Streaming response via Local LLM...")
                try:
                    for token in self.model.generate(full_prompt, max_tokens=1500, temp=0.2, streaming=True):
                        yield json.dumps({"text": token}) + "\n"
                except Exception as e:
                    print(f"LLM Stream Error: {e}")
                    yield json.dumps({"text": "\n[Error generating response]"}) + "\n"
                # Send sources at the end
                yield json.dumps({"sources": sources}) + "\n"
            return llm_generator()
        else:
            try:
                print("Generating response via Local LLM...")
                output = self.model.generate(full_prompt, max_tokens=1500, temp=0.2)
                response_text = output.strip()
            except Exception as e:
                print(f"LLM Generation Error: {e}")
                response_text = "I encountered an error while trying to process your request."

            final_text = self.translate_text(response_text, language)
            return {"response": final_text, "model": "Local Llama-3 AI", "sources": sources}