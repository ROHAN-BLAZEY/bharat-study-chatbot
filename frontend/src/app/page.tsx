"use client";

import React, { useState, useEffect, useRef } from "react";
import { Moon, Sun, Paperclip, Send, Menu, X, MessageSquare, FileText, Globe, Newspaper, BookOpen, Mic, Volume2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import TextareaAutosize from "react-textarea-autosize";
const LANGUAGES = [
  { code: "English", label: "English", flag: "🇬🇧" },
  { code: "Hindi", label: "हिन्दी", flag: "🇮🇳" },
  { code: "Telugu", label: "తెలుగు", flag: "🇮🇳" },
  { code: "Tamil", label: "தமிழ்", flag: "🇮🇳" },
  { code: "Marathi", label: "मराठी", flag: "🇮🇳" },
  { code: "Bengali", label: "বাংলা", flag: "🇮🇳" },
  { code: "Gujarati", label: "ગુજરાતી", flag: "🇮🇳" },
  { code: "Malayalam", label: "മലയാളം", flag: "🇮🇳" },
  { code: "Kannada", label: "ಕನ್ನಡ", flag: "🇮🇳" },
  { code: "Punjabi", label: "ਪੰਜਾਬੀ", flag: "🇮🇳" },
  { code: "Odia", label: "ଓଡ଼ିଆ", flag: "🇮🇳" },
  { code: "Urdu", label: "اردو", flag: "🇮🇳" },
];

export default function Home() {
  const [theme, setTheme] = useState("light");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoginView, setIsLoginView] = useState(true);

  // Chat States
  const [messages, setMessages] = useState<{ role: string; content: string; sources?: string[] }[]>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [language, setLanguage] = useState("English");
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const langDropdownRef = useRef<HTMLDivElement>(null);

  // Speech Recognition setup
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const SpeechRecognition = typeof window !== "undefined" ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition : null;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;
  if (recognition) {
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = language === "English" ? "en-US" : "hi-IN"; // basic mapping
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      setInput(prev => prev + " " + text);
      setIsRecording(false);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);
  }

  const toggleRecording = () => {
    if (!recognition) return alert("Speech recognition not supported in this browser.");
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
    } else {
      recognition.start();
      setIsRecording(true);
    }
  };

  const playAudio = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      // Remove markdown symbols for cleaner reading
      const cleanText = text.replace(/[*#_`]/g, '').replace(/\[.*?\]\(.*?\)/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = language === "English" ? "en-US" : "hi-IN";
      utterance.rate = 0.95; // Slightly slower for better clarity
      window.speechSynthesis.speak(utterance);
    }
  };

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Close language dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (langDropdownRef.current && !langDropdownRef.current.contains(e.target as Node)) {
        setLangDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getBaseUrl = () => {
    if (typeof window !== "undefined") {
      return `http://${window.location.hostname}:8080`;
    }
    return "http://127.0.0.1:8080";
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;
    try {
      const formData = { email: username, password, name: username };
      const baseUrl = getBaseUrl();
      const res = await fetch(`${baseUrl}/api/${isLoginView ? "login" : "register"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (res.ok) {
        setIsLoggedIn(true);
      } else {
        alert(data.detail || "Authentication Failed");
      }
    } catch {
      alert("Error connecting to backend. Make sure the backend is running.");
    }
  };

  const handleSendMessage = async (e?: React.FormEvent, overridePrompt?: string) => {
    if (e) e.preventDefault();
    const messageText = overridePrompt || input;
    if (!messageText.trim() && attachedFiles.length === 0) return;

    // Save history before adding the new message
    const historyToSend = messages.slice(-20).map(m => ({ role: m.role, content: m.content }));
    
    setMessages((prev) => [...prev, { role: "user", content: messageText }]);
    setInput("");
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("prompt", messageText || "Analyze the attached files.");
      formData.append("tier", "Fast");
      formData.append("language", language);
      formData.append("history", JSON.stringify(historyToSend));
      attachedFiles.forEach(file => {
        formData.append("files", file);
      });

      const baseUrl = getBaseUrl();
      const res = await fetch(`${baseUrl}/api/chat`, {
        method: "POST",
        body: formData,
      });
      
      if (res.ok) {
        if (res.headers.get('content-type')?.includes('application/x-ndjson')) {
            const reader = res.body?.getReader();
            const decoder = new TextDecoder();
            setMessages((prev) => [...prev, { role: "bot", content: "", sources: [] }]);
            setAttachedFiles([]);
            setIsLoading(false);
            
            let buffer = "";
            while (true) {
                const { done, value } = await reader!.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;
                
                const lines = buffer.split('\n');
                buffer = lines.pop() || "";
                
                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        if (data.text) {
                            setMessages(prev => {
                                const newMsg = [...prev];
                                const last = { ...newMsg[newMsg.length - 1] };
                                last.content += data.text;
                                newMsg[newMsg.length - 1] = last;
                                return newMsg;
                            });
                        }
                        if (data.sources) {
                            setMessages(prev => {
                                const newMsg = [...prev];
                                const last = { ...newMsg[newMsg.length - 1] };
                                last.sources = data.sources;
                                newMsg[newMsg.length - 1] = last;
                                return newMsg;
                            });
                        }
                    } catch {}
                }
            }
        } else {
            const data = await res.json();
            setMessages((prev) => [...prev, { role: "bot", content: data.response, sources: data.sources }]);
            setAttachedFiles([]);
            setIsLoading(false);
        }
      } else {
        const errText = await res.text();
        setMessages((prev) => [...prev, { role: "bot", content: `Error from backend: ${res.status} - ${errText}` }]);
        setIsLoading(false);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [...prev, { role: "bot", content: `Connection failed: ${message}. Make sure the backend is running.` }]);
      setIsLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachedFiles(Array.from(e.target.files));
    }
  };

  const handleQuickAction = (action: string) => {
    handleSendMessage(undefined, action);
  };

  const handleClearDocuments = async () => {
    if (confirm("Are you sure you want to delete all uploaded documents from the AI's memory?")) {
      try {
        const baseUrl = getBaseUrl();
        const res = await fetch(`${baseUrl}/api/clear_documents`, { method: "POST" });
        if (res.ok) {
          setAttachedFiles([]);
          alert("All documents have been successfully cleared.");
          setSidebarOpen(false);
        }
      } catch {
        alert("Failed to clear documents.");
      }
    }
  };

  const currentLang = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];

  // ─── LOGIN SCREEN ─────────────────────────────────────
  if (!isLoggedIn) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4 safe-area-padding">
        {/* Theme toggle removed to force Light Mode (black text) */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel w-full max-w-md p-8 rounded-3xl"
        >
          <div className="text-center mb-8">
            <div className="text-5xl mb-3">🇮🇳</div>
            <h1 className="text-3xl font-bold mb-2">Bharat Study</h1>
            <p className="text-sm opacity-80">Your AI Study Companion</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div suppressHydrationWarning>
              <label className="block text-sm font-medium mb-1">Email / Username</label>
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/50 dark:bg-black/50 border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="Enter your email"
                suppressHydrationWarning
              />
            </div>
            <div suppressHydrationWarning>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/50 dark:bg-black/50 border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="Enter your password"
                suppressHydrationWarning
              />
            </div>
            <button type="submit" className="w-full py-3 mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-blue-500/30 active:scale-[0.98]">
              {isLoginView ? "Enter Chatbot" : "Register & Enter"}
            </button>
            <p className="text-center text-sm mt-4 opacity-80 cursor-pointer hover:underline" onClick={() => setIsLoginView(!isLoginView)}>
              {isLoginView ? "New user? Register here" : "Already have an account? Login"}
            </p>
          </form>
        </motion.div>
      </main>
    );
  }

  // ─── MAIN CHAT SCREEN ─────────────────────────────────
  return (
    <div className="flex h-screen h-dvh overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ x: sidebarOpen ? 0 : "-100%" }}
        className="fixed md:relative z-50 w-72 h-full glass-panel border-r flex flex-col md:translate-x-0 transition-transform duration-300"
      >
        <div className="p-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-800">
          <h2 className="font-bold text-xl flex items-center gap-2">
            <MessageSquare size={20} /> Bharat AI
          </h2>
          <button className="md:hidden p-1" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto space-y-6">
          <div>
            <p className="text-xs uppercase font-bold opacity-50 mb-2">User</p>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                {username.charAt(0).toUpperCase()}
              </div>
              <span className="font-medium truncate">{username}</span>
            </div>
          </div>

          <div>
            <p className="text-xs uppercase font-bold opacity-50 mb-2">Quick Actions</p>
            <div className="space-y-2">
              <button 
                onClick={() => { handleQuickAction("Show me the latest current affairs"); setSidebarOpen(false); }}
                className="w-full text-left px-3 py-2.5 rounded-xl bg-white/30 dark:bg-white/5 hover:bg-white/50 dark:hover:bg-white/10 transition-all flex items-center gap-2 text-sm active:scale-[0.98]"
              >
                <Newspaper size={16} className="text-orange-500" /> Current Affairs
              </button>
              <button 
                onClick={() => { handleQuickAction("What topics can you help me study?"); setSidebarOpen(false); }}
                className="w-full text-left px-3 py-2.5 rounded-xl bg-white/30 dark:bg-white/5 hover:bg-white/50 dark:hover:bg-white/10 transition-all flex items-center gap-2 text-sm active:scale-[0.98]"
              >
                <BookOpen size={16} className="text-blue-500" /> Study Topics
              </button>
              <button 
                onClick={handleClearDocuments}
                className="w-full text-left px-3 py-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 transition-all flex items-center gap-2 text-sm active:scale-[0.98] mt-4"
              >
                <X size={16} /> Clear All Documents
              </button>
            </div>
          </div>

          <div>
            <p className="text-xs uppercase font-bold opacity-50 mb-2">Knowledge Base</p>
            <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-green-700 dark:text-green-400 text-sm flex flex-col gap-1">
              <span className="font-semibold flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div> Connected</span>
              <span className="opacity-80">Document Search Active</span>
              {attachedFiles.length > 0 && (
                <span className="opacity-80 flex items-center gap-1 mt-2 text-blue-600 dark:text-blue-400"><FileText size={14}/> {attachedFiles.length} file(s) attached</span>
              )}
            </div>
          </div>

        {/* Theme toggle removed */}
        </div>
      </motion.aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative w-full h-full">
        {/* Header */}
        <header className="glass-panel border-b px-4 py-3 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <button className="md:hidden p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 active:scale-95 transition-all" onClick={() => setSidebarOpen(true)}>
              <Menu size={22} />
            </button>
            <div>
              <h2 className="font-semibold text-base text-black">Bharat Study Chatbot</h2>
              <p className="text-xs opacity-70 text-gray-800">
                {attachedFiles.length > 0 ? `📄 ${attachedFiles.length} file(s) attached` : "📚 Ready to help you study"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-xs px-2 py-1 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 font-medium hidden sm:block">
              {currentLang.flag} {currentLang.label}
            </span>
          </div>
        </header>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center max-w-md">
                <div className="text-6xl mb-4">🇮🇳</div>
                <h2 className="text-2xl font-bold mb-2">Welcome to Bharat Study</h2>
                <p className="text-sm opacity-60 mb-8">Your AI-powered study companion for competitive exams</p>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button 
                    onClick={() => handleQuickAction("Show me the latest current affairs")}
                    className="glass-panel p-4 rounded-2xl hover:bg-white/30 dark:hover:bg-white/5 transition-all text-left active:scale-[0.98] group"
                  >
                    <Newspaper size={20} className="text-orange-500 mb-2 group-hover:scale-110 transition-transform" />
                    <p className="font-semibold text-sm">📰 Current Affairs</p>
                    <p className="text-xs opacity-60 mt-1">Latest Indian headlines</p>
                  </button>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="glass-panel p-4 rounded-2xl hover:bg-white/30 dark:hover:bg-white/5 transition-all text-left active:scale-[0.98] group"
                  >
                    <FileText size={20} className="text-blue-500 mb-2 group-hover:scale-110 transition-transform" />
                    <p className="font-semibold text-sm">📄 Upload Document</p>
                    <p className="text-xs opacity-60 mt-1">PDF or TXT study material</p>
                  </button>
                  <button 
                    onClick={() => handleQuickAction("Tell me about UPSC preparation")}
                    className="glass-panel p-4 rounded-2xl hover:bg-white/30 dark:hover:bg-white/5 transition-all text-left active:scale-[0.98] group"
                  >
                    <BookOpen size={20} className="text-green-500 mb-2 group-hover:scale-110 transition-transform" />
                    <p className="font-semibold text-sm">📚 UPSC Prep</p>
                    <p className="text-xs opacity-60 mt-1">Study guidance</p>
                  </button>
                  <button 
                    onClick={() => handleQuickAction("hello")}
                    className="glass-panel p-4 rounded-2xl hover:bg-white/30 dark:hover:bg-white/5 transition-all text-left active:scale-[0.98] group"
                  >
                    <MessageSquare size={20} className="text-purple-500 mb-2 group-hover:scale-110 transition-transform" />
                    <p className="font-semibold text-sm">💬 Say Hello</p>
                    <p className="text-xs opacity-60 mt-1">See what I can do</p>
                  </button>
                </div>
              </motion.div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={idx} 
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`max-w-[90%] sm:max-w-[80%] md:max-w-[70%] p-4 rounded-2xl ${msg.role === "user" ? "bg-blue-100 border border-blue-200 text-black font-medium rounded-tr-sm shadow-md" : "glass-panel text-gray-900 dark:text-gray-100 rounded-tl-sm shadow-sm"}`}>
                  <div className="prose prose-sm sm:prose-base max-w-none text-base sm:text-lg whitespace-pre-wrap leading-relaxed font-medium">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>
                  
                  {msg.role === "bot" && (
                    <button onClick={() => playAudio(msg.content)} className="mt-2 p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors" title="Read Aloud">
                      <Volume2 size={16} className="text-blue-500" />
                    </button>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-black/10 dark:border-white/10">
                      <p className="text-xs font-semibold mb-1 flex items-center gap-1"><FileText size={12}/> Sources Consulted:</p>
                      <ul className="text-xs opacity-80 list-disc list-inside">
                        {msg.sources.map((s, i) => (
                          <li key={i} className="truncate">{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="glass-panel p-4 rounded-2xl rounded-tl-sm flex gap-2 items-center">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-3 sm:p-4 md:p-6 bg-transparent safe-area-bottom">
          <div className="max-w-4xl mx-auto glass-panel rounded-2xl sm:rounded-full p-2 flex items-center gap-1 sm:gap-2 shadow-2xl relative">
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              accept=".pdf,.txt"
              multiple
            />
            
            {/* File Attach Button */}
            <button 
              type="button" 
              onClick={() => fileInputRef.current?.click()}
              className={`p-2.5 sm:p-3 rounded-full transition-colors shrink-0 ${attachedFiles.length > 0 ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30' : 'hover:bg-black/5 dark:hover:bg-white/5'}`}
              title="Attach File"
            >
              {attachedFiles.length > 0 ? <FileText size={18} /> : <Paperclip size={18} />}
            </button>

            {/* Language Globe Dropdown */}
            <div className="relative shrink-0" ref={langDropdownRef}>
              <button
                type="button"
                onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                className={`p-2.5 sm:p-3 rounded-full transition-colors ${langDropdownOpen ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30' : 'hover:bg-black/5 dark:hover:bg-white/5'}`}
                title={`Language: ${currentLang.label}`}
              >
                <Globe size={18} />
              </button>
              
              <AnimatePresence>
                {langDropdownOpen && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    className="absolute bottom-14 left-0 glass-panel rounded-2xl p-2 shadow-2xl w-52 max-h-72 overflow-y-auto z-50 border border-gray-200 dark:border-gray-700"
                  >
                    <p className="text-xs font-bold uppercase opacity-50 px-3 py-1.5">Select Language</p>
                    {LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => { setLanguage(lang.code); setLangDropdownOpen(false); }}
                        className={`w-full text-left px-3 py-2 rounded-xl text-sm flex items-center gap-2 transition-colors ${language === lang.code ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 font-semibold' : 'hover:bg-black/5 dark:hover:bg-white/5'}`}
                      >
                        <span>{lang.flag}</span>
                        <span>{lang.label}</span>
                        {language === lang.code && <span className="ml-auto text-blue-500">✓</span>}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="flex-1 flex items-center gap-1 sm:gap-2 min-w-0">
              <TextareaAutosize 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                minRows={1}
                maxRows={6}
                placeholder={attachedFiles.length > 0 ? `Ask about ${attachedFiles.length} file(s)...` : "Message Bharat Study..."}
                className="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 px-3 py-3 text-base sm:text-lg min-w-0 resize-none text-black font-semibold placeholder-gray-800"
                disabled={isLoading}
              />

              <button 
                type="button"
                onClick={toggleRecording}
                className={`p-2.5 sm:p-3 rounded-full transition-colors shrink-0 ${isRecording ? 'bg-red-500 text-white animate-pulse' : 'hover:bg-black/5 dark:hover:bg-white/5 text-gray-500'}`}
                title="Speak to Chatbot"
              >
                <Mic size={18} />
              </button>

              <button 
                type="submit" 
                disabled={(!input.trim() && attachedFiles.length === 0) || isLoading}
                className="p-2.5 sm:p-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0 active:scale-95"
              >
                <Send size={18} />
              </button>
            </form>
            
            {attachedFiles.length > 0 && (
              <button 
                onClick={() => setAttachedFiles([])}
                className="absolute -top-10 left-4 glass-panel px-3 py-1 rounded-full text-xs flex items-center gap-1 text-red-500 hover:bg-red-500/10 transition-colors"
              >
                Clear {attachedFiles.length} file(s) <X size={12}/>
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
