"use client";

import React, { useState, useEffect, useRef } from "react";
import { Moon, Sun, Paperclip, Send, Menu, X, MessageSquare, Plus, FileText, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [theme, setTheme] = useState("light");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoginView, setIsLoginView] = useState(true); // toggles between Login / Register

  // Chat States
  const [messages, setMessages] = useState<{ role: string; content: string; sources?: string[] }[]>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [language, setLanguage] = useState("English");
  const [tier, setTier] = useState("Fast");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const languages = ["English", "Hindi", "Telugu", "Tamil", "Marathi", "Bengali", "Gujarati", "Malayalam", "Kannada"];
  const tiers = ["Fast", "Fast-Elite", "Pro"];

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

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;
    try {
      const formData = { email: username, password, name: username }; // email used as login id
      const res = await fetch(`http://localhost:8000/api/${isLoginView ? "login" : "register"}`, {
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
    } catch (err) {
      alert("Error connecting to backend");
    }
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() && !attachedFile) return;

    const userMessage = input;
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("prompt", userMessage || "Analyze the attached file.");
      formData.append("tier", tier);
      formData.append("language", language);
      if (attachedFile) {
        formData.append("file", attachedFile);
      }

      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        body: formData,
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [...prev, { role: "bot", content: data.response, sources: data.sources }]);
        setAttachedFile(null);
      } else {
        setMessages((prev) => [...prev, { role: "bot", content: "Error processing request." }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", content: "Server connection failed." }]);
    }
    setIsLoading(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
    }
  };

  if (!isLoggedIn) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <div className="absolute top-4 right-4 z-50">
          <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} className="p-2 rounded-full glass-panel hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
            {theme === "dark" ? <Sun size={24} /> : <Moon size={24} />}
          </button>
        </div>
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel w-full max-w-md p-8 rounded-3xl"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Bharat Study Chatbot</h1>
            <p className="text-sm opacity-80">Premium Enterprise AI Assistant</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email / Username</label>
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/50 dark:bg-black/50 border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/50 dark:bg-black/50 border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="Enter your password"
              />
            </div>
            <button type="submit" className="w-full py-3 mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-blue-500/30">
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

  return (
    <div className="flex h-screen overflow-hidden">
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
        className={`fixed md:relative z-50 w-72 h-full glass-panel border-r flex flex-col md:translate-x-0 transition-transform duration-300`}
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
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
                {username.charAt(0).toUpperCase()}
              </div>
              <span className="font-medium truncate">{username}</span>
            </div>
          </div>

          <div>
            <p className="text-xs uppercase font-bold opacity-50 mb-2">Settings</p>
            <div className="space-y-3">
              <div>
                <label className="text-sm opacity-80 mb-1 block">Language</label>
                <div className="relative">
                  <select 
                    value={language} 
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full appearance-none bg-white/50 dark:bg-black/50 border border-gray-300 dark:border-gray-700 rounded-lg py-2 px-3 pr-8 focus:outline-none"
                  >
                    {languages.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                  <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none opacity-50" />
                </div>
              </div>
              <div>
                <label className="text-sm opacity-80 mb-1 block">Model Tier</label>
                <div className="relative">
                  <select 
                    value={tier} 
                    onChange={(e) => setTier(e.target.value)}
                    className="w-full appearance-none bg-white/50 dark:bg-black/50 border border-gray-300 dark:border-gray-700 rounded-lg py-2 px-3 pr-8 focus:outline-none"
                  >
                    {tiers.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                  <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none opacity-50" />
                </div>
              </div>
              <div className="flex items-center justify-between mt-4">
                <span className="text-sm opacity-80">Theme</span>
                <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} className="p-2 rounded-lg bg-white/50 dark:bg-black/50">
                  {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
                </button>
              </div>
            </div>
          </div>

          <div>
            <p className="text-xs uppercase font-bold opacity-50 mb-2">Knowledge Base</p>
            <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-700 dark:text-green-400 text-sm flex flex-col gap-1">
              <span className="font-semibold flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500"></div> Connected</span>
              <span className="opacity-80">Global Context Active</span>
              {attachedFile && (
                <span className="opacity-80 flex items-center gap-1 mt-2 text-blue-600 dark:text-blue-400"><FileText size={14}/> {attachedFile.name}</span>
              )}
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative w-full h-full">
        {/* Header */}
        <header className="glass-panel border-b p-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <button className="md:hidden p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5" onClick={() => setSidebarOpen(true)}>
              <Menu size={24} />
            </button>
            <div>
              <h2 className="font-semibold">Bharat Study Agent</h2>
              <p className="text-xs opacity-70">
                Connected to {attachedFile ? `Attached File: ${attachedFile.name}` : "Global Knowledge Base"}
              </p>
            </div>
          </div>
        </header>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center opacity-50">
              <MessageSquare size={48} className="mb-4" />
              <p>Start a conversation to begin exam preparation.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={idx} 
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`max-w-[85%] md:max-w-[70%] p-4 rounded-2xl ${msg.role === "user" ? "bg-blue-600 text-white rounded-tr-sm" : "glass-panel rounded-tl-sm"}`}>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
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
        <div className="p-4 md:p-6 bg-transparent">
          <div className="max-w-4xl mx-auto glass-panel rounded-full p-2 flex items-center gap-2 shadow-2xl relative">
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              accept=".pdf,.txt"
            />
            <button 
              type="button" 
              onClick={() => fileInputRef.current?.click()}
              className={`p-3 rounded-full transition-colors ${attachedFile ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30' : 'hover:bg-black/5 dark:hover:bg-white/5'}`}
              title="Attach File"
            >
              {attachedFile ? <FileText size={20} /> : <Paperclip size={20} />}
            </button>
            <form onSubmit={handleSendMessage} className="flex-1 flex items-center gap-2">
              <input 
                type="text" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={attachedFile ? `Ask about ${attachedFile.name}...` : "Message Bharat Study..."}
                className="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 px-2"
                disabled={isLoading}
              />
              <button 
                type="submit" 
                disabled={(!input.trim() && !attachedFile) || isLoading}
                className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={20} />
              </button>
            </form>
            {attachedFile && (
              <button 
                onClick={() => setAttachedFile(null)}
                className="absolute -top-10 left-4 glass-panel px-3 py-1 rounded-full text-xs flex items-center gap-1 text-red-500 hover:bg-red-500/10"
              >
                Remove {attachedFile.name} <X size={12}/>
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
