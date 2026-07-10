import os
from dotenv import load_dotenv
load_dotenv()
import PyPDF2
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext
from agent import DualRAGAgent

Base = declarative_base()
engine = create_engine("sqlite:///./bharat_study.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ai_agent = DualRAGAgent()

@app.get("/")
def read_root():
    return {"status": "Bharat Study Chatbot Backend is running!", "version": "2.0", "engine": "Document Search + News APIs"}

class AuthData(BaseModel):
    name: str = ""
    email: str
    phone: str = ""
    password: str

@app.post("/api/register")
def register(data: AuthData):
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        db.close()
        raise HTTPException(status_code=400, detail="Account already exists.")
    new_user = User(name=data.name, email=data.email, phone=data.phone, password=pwd_context.hash(data.password))
    db.add(new_user)
    db.commit()
    db.close()
    return {"status": "success"}

@app.post("/api/login")
def login(data: AuthData):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    db.close()
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return {"status": "success", "username": user.name}

@app.post("/api/chat")
async def chat_endpoint(prompt: str = Form(...), tier: str = Form("Fast"), language: str = Form("English"), file: UploadFile = File(None)):
    if file:
        file_path = f"./temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        text_content = ""
        ext = os.path.splitext(file.filename)[1].lower()
        try:
            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()
            elif ext == ".pdf":
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text_content += page.extract_text() or ""
            
            if text_content:
                chunks = ai_agent.ingest_document(text_content, file.filename)
                print(f"Ingested {chunks} chunks from {file.filename}")
                
        except Exception as e:
            print(f"Error processing document: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                
    result = ai_agent.process_prompt(prompt, tier, language)
    return {
        "response": result["response"],
        "sources": result["sources"] if result["sources"] else ["Global Knowledge Base"],
        "model": result["model"]
    }

@app.get("/api/news")
def get_news():
    """Get current affairs as formatted text + raw data."""
    news = ai_agent.fetch_news()
    formatted = ai_agent.format_news_response(news)
    return {"news": news, "formatted": formatted, "count": len(news)}

@app.get("/api/languages")
def get_languages():
    """Return supported languages for the frontend dropdown."""
    return {"languages": list(ai_agent.lang_codes.keys())}

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    doc_count = ai_agent.collection.count()
    return {
        "status": "healthy",
        "documents_indexed": doc_count,
        "news_apis": ["GNews", "NewsData", "ApiTube"],
        "translation": "deep-translator (free)"
    }