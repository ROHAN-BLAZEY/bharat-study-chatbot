AI GPU Summer Internship Program
CSS7000 INTERNSHIP REPORT
Submitted by
ROHAN BLAZEY – 20241CAI0078
Under the guidance of,
Dr . John Bennet J
BACHELOR OF TECHNOLOGY
IN
COMPUTER SCIENCE AND ENGINEERING (Artificial Intelligence and Machine Learning)
PRESIDENCY UNIVERSITY
BENGALURU
AUGUST 2026

PRESIDENCY SCHOOL OF ARTIFICIAL INTELLIGENCE & ADVANCED COMPUTING 
DEPARTMENT OF AI & ROBOTICS

BONAFIDE CERTIFICATE
Certified that this report “AI GPU summer Internship program” is a bonafide work of ROHAN BLAZEY (20241CAI0078), who has successfully carried out the internship work and submitted the report for partial fulfillment of the requirements for the award of the degree of BACHELOR OF TECHNOLOGY in PRESIDENCY SCHOOL OF ARTIFICIAL INTELLIGENCE & ADVANCED COMPUTING , AI & Robotics  during 2026-2027.

Mr. John Bennet J
Assistant Professor
Internship Guide
PSAIAC 
Presidency University

Mr. Anandan B
Assistant Professor
Program Internship Coordinator
PSAIAC
Presidency University

Dr. Geetha Arjunan
Associate Professor
School Internship Coordinator
PSAIAC
Presidency University

Dr. Zafar Ali Khan N
Professor & Head of the Department 
AI & Robotics  
PSAIAC 
Presidency University

Dr. Shakkeera L 
Dean
PSAIAC 
Presidency University

DECLARATION
I am a student of Pre - Final year B.Tech in COMPUTER SCIENCE AND ENGINEERING (Artificial Intelligence and Machine Learning), at Presidency University, Bengaluru, named, ROHAN BLAZEY hereby declare that the internship work titled “AI GPU summer Internship program” has been independently carried out by me and submitted in partial fulfillment for the award of the degree of B.Tech in COMPUTER SCIENCE AND ENGINEERING  during the academic year of 2026-2027. Further, the matter embodied in the internship has not been submitted previously by anybody for the award of any Degree or Diploma to any other institution.      

ROHAN BLAZEY                USN:  20241CAI0078                           Signature 
PLACE: BENGALURU
DATE:   

ACKNOWLEDGEMENTS
For completing this internship work, I have received the support and the guidance from many people whom I would like to mention with deep sense of gratitude and indebtedness. I extend my gratitude to our beloved Chancellor, Pro-Vice Chancellor, and Registrar for their support and encouragement in completion of the internship. 

I would like to sincerely thank my internal guide Mr. John Bennet J, Assistant Professor Presidency School of Artificial Intelligence & Advanced Computing Presidency University, for his moral support, motivation, timely guidance and encouragement provided to me during the period of internship work.

I am also thankful to Dr. Zafar Ali Khan N, Professor & Head of the Department, AI & Robotics Presidency School of Artificial Intelligence & Advanced Computing, Presidency University, for his mentorship and encouragement. 

I express my cordial thanks to Dr. Shakeera L, Dean, Presidency School of Artificial Intelligence & Advanced Computing, Presidency University for providing the required facilities and intellectually stimulating environment that aided in the completion of my internship work.

We are grateful to Dr. Geetha Arjunan, Associate Professor, School Internship Coordinator, Mr. Anandan B, Assistant Professor, Program Internship Coordinator, Presidency School of Artificial Intelligence & Advanced Computing, Presidency University for facilitating problem statements, coordinating reviews, monitoring progress, and providing their valuable support and guidance.

I am also grateful to Teaching and Non-Teaching staff of Presidency School Of Artificial Intelligence & Advanced Computing and also staff from other departments who have extended their valuable help and cooperation.

ROHAN BLAZEY

# ABSTRACT
Large Language Models (LLMs) have revolutionized natural language processing, offering unprecedented text generation capabilities across multiple domains. However, they traditionally suffer from factual hallucinations due to their reliance on static, point-in-time training data. When deployed in critical educational contexts, such as preparation for highly competitive Indian examinations like the Union Public Service Commission (UPSC), National Defence Academy (NDA), Graduate Aptitude Test in Engineering (GATE), and Staff Selection Commission (SSC), ensuring the absolute accuracy of information is paramount. Even a slight factual hallucination can result in severe consequences for a student's preparation and understanding of core subjects.

While Retrieval-Augmented Generation (RAG) paradigms were introduced to mitigate this issue by injecting external data into the LLM prompt, early implementations often remained passive, rigid, and lacked the complex reasoning and multi-step verification capabilities required for nuanced academic queries. The naive approach to RAG relies heavily on a simple cosine similarity match which, more often than not, retrieves chunks that are lexically similar but semantically disconnected from the overarching context of the query.

This capstone project presents the comprehensive design, development, deployment, and evaluation of the "Bharat Study Chatbot"—an enterprise-grade RAG AI assistant specifically purpose-built to address the unique challenges of Indian competitive exam preparation. The system was developed over the course of a rigorous 10-day intensive training program focusing on advanced artificial intelligence and high-performance computing, utilizing state-of-the-art NVIDIA H200 GPU infrastructure hosted at Presidency University, Bengaluru. The core intention of this project was to move beyond theoretical AI models and sandbox prototypes to deliver a tangible, deployable, production-ready solution that directly benefits the student community by grounding answers in factual, verifiable study material.

Architecturally, the chatbot implements a decoupled, modern full-stack web application structure that maximizes both performance and developer velocity. It features a robust FastAPI backend written in Python, chosen for its high performance, asynchronous capabilities, and native compatibility with modern machine learning ecosystems. This is paired with a dynamic, server-side rendered Next.js frontend built with React and TypeScript, ensuring lightning-fast initial load times and robust search engine optimization (SEO) capabilities. Central to its core operation is the employment of ChromaDB as a persistent, embedded vector database. This specialized database facilitates the rapid semantic retrieval of documents by storing high-dimensional vector embeddings of text chunks derived from user-uploaded study materials, which typically include extensive PDF textbooks and detailed TXT notes.

A key differentiator of this system is its deliberate architectural departure from conventional, fully generative LLM-dependent chatbots like ChatGPT or Claude. Recognizing the massive cost implications at scale and the residual risk of hallucination inherent in any generative process, the production system operates fundamentally as a highly sophisticated, self-contained semantic document search engine. It surfaces exact, verbatim excerpts from verified source materials rather than synthesizing new, potentially inaccurate text. To ensure comprehensive exam preparation support, this core retrieval engine is augmented by a sophisticated orchestration layer that integrates three real-time news APIs (GNews, NewsData, and ApiTube). This feature provides on-demand, formatted digests of current affairs, a critical and constantly evolving component of the UPSC syllabus. Furthermore, acknowledging the immense linguistic diversity of the target user base across the Indian subcontinent, the system incorporates free, robust multilingual translation capabilities, natively supporting 12 major Indian regional languages via the deep-translator library.

The platform is deployed globally as both a standard highly responsive Website and an installable Progressive Web Application (PWA). This dual deployment strategy ensures it is accessible as a native-like mobile application through any modern browser on any device, democratizing access to advanced study tools regardless of the user's hardware limitations. Ultimately, this specific architectural design successfully eliminates the dependency on expensive, recurring commercial LLM API quotas, driving operational costs down significantly, while simultaneously maintaining extremely high retrieval accuracy and factual reliability through targeted vector-similarity search over user-verified study materials.

# 1. INTRODUCTION

## 1.1 Problem Statement and Context
The integration of Retrieval-Augmented Generation (RAG) into Large Language Model (LLM) architectures represents a major paradigm shift in how artificial intelligence systems interact with and synthesize information. Historically, the utility of LLMs in specialized domains such as law, medicine, and competitive academic examinations was severely constrained by their fundamental design: they relied solely on massive but static, pre-trained datasets. This reliance frequently led to the phenomenon of "hallucinations"—the generation of plausible-sounding but entirely factually incorrect information. An LLM predicting the next most likely token does not inherently "know" truth; it only knows statistical probability based on its training distribution. 

Furthermore, these static models inherently lacked access to real-time events, breaking news, or proprietary, user-specific knowledge repositories. For a student preparing for the UPSC exam, where current affairs from the past 24 hours can be the subject of an essay question, a model trained on data from a year ago is fundamentally inadequate. The need to ground these powerful language models in factual, verifiable, and constantly updating external data sources became the most pressing challenge in the field of Applied AI.

Over time, the technological landscape has evolved dramatically to address these core deficiencies. We have transitioned from simple, unconstrained text-generation models to highly sophisticated frameworks that actively leverage external, verified data repositories to enhance both the accuracy and the contextual relevance of their outputs. In its current state, RAG has moved beyond an experimental technique to become a foundational enterprise technology. It serves as the crucial stepping stone enabling the rise of "agentic" AI systems—autonomous entities capable of complex planning, intelligent tool usage, interacting with APIs, and executing multi-step reasoning workflows to solve complex user intents.

The primary purpose of this report is to comprehensively analyze the current ecosystem of RAG-based chatbot development specifically within the context of educational technology for competitive examinations. It deeply explores key methodologies, recent advancements in dense embedding technologies, and the industry's broader transition toward more autonomous, agentic workflows. The extensive research and development detailed in this report draw upon a comprehensive review of academic foundations, industry-standard implementation guides, and emerging developments observed at recent global AI hackathons and technology initiatives.

## 1.2 Background and Evolution of RAG
Early iterations of informational AI systems attempted to solve the persistent knowledge gap by relying on dense semantic embedding models and vector databases. This early approach, often termed "Naive RAG," worked by chunking large documents into smaller text segments, converting these segments into mathematical vectors using pre-trained sentence transformers, and performing nearest-neighbor similarity searches in high-dimensional space to find relevant text based on the user's query vector. These chunks were then simply concatenated and fed into an LLM's context window alongside the original user's prompt.

While this "Naive RAG" approach successfully addressed general knowledge gaps and significantly reduced hallucinations compared to standard zero-shot prompting, it presented significant operational limitations in production environments. Existing academic literature and early corporate implementations frequently framed Naive RAG as a rigid, linear mechanism. These early models lacked the dynamic context-switching capacity required to cross-reference multiple documents intelligently. For instance, if a query required synthesizing information from page 10 of a textbook and page 45 of a news report, Naive RAG often failed if the chunks did not possess high individual cosine similarity to the prompt.

Furthermore, they lacked the crucial ability to self-correct, reflect, or iterate when an initial search query failed to retrieve adequate context. If the database returned irrelevant chunks, the LLM would blindly attempt to answer the question using the faulty data, resulting in "grounded hallucinations." The academic literature surrounding these early models was heavily dominated by benchmark-focused evaluations on pristine, standardized datasets like SQuAD or HotpotQA, often completely ignoring the complex, multi-tenant data challenges and extremely messy data formats (like poorly scanned PDFs or OCR errors) that occur when AI interacts with dynamic enterprise software or user-generated content in the real world.

## 1.3 Significance of the Research
This research and the resulting capstone project are absolutely critical for organizations, startups, and massive educational institutions navigating the incredibly complex transition from relying on experimental, static LLMs to deploying dynamic, agentic AI frameworks in mission-critical environments. By grounding large language models in proprietary, verified data through Advanced Retrieval-Augmented Generation (RAG), businesses and educators can significantly mitigate the risk of hallucinations, ensuring that AI outputs remain contextually accurate, safe for users, and immediately actionable without requiring constant human oversight.

Furthermore, this detailed study provides a practical, code-level roadmap for operationalizing autonomous agents capable of complex tool usage (such as querying external news APIs for current affairs) and multi-step reasoning workflows. It offers a scalable path to automate intricate, multi-layered workflows that previously required extensive human intervention and manual research.

The Bharat Study Chatbot serves as a tangible, fully deployed proof-of-concept. It clearly demonstrates that enterprise-grade AI assistants can be successfully deployed without creating expensive, ongoing, and unpredictable dependencies on commercial LLM API providers (like OpenAI's GPT-4 or Anthropic's Claude 3). By intelligently leveraging highly optimized semantic vector search combined with open-source models and completely free translation services, the system achieves its educational goals highly cost-effectively. 

Ultimately, the findings detailed in this comprehensive report enable clients, universities, and EdTech institutions to confidently transition from basic AI experimentation in isolated sandbox environments to deploying high-impact, highly reliable systems at scale. These production systems leverage vast amounts of institutional knowledge to gain a measurable competitive edge and provide significant, tangible value to end-users in the rapidly evolving and highly competitive AI landscape.

# 2. OBJECTIVE
The extensive development of the Bharat Study Chatbot and the associated deep-dive research were rigorously guided by the following primary objectives, formulated to ensure both academic rigor and practical industry applicability:

1. **Evaluate Architectural Paradigms:** To critically evaluate the fundamental architectural differences, profound implementation complexities, and critical performance trade-offs between standard, linear vector-search RAG pipelines and more advanced, dynamic, multi-step agentic reasoning frameworks. This evaluation is specifically contextualized within an educational setting where accuracy cannot be compromised.
2. **Identify Enterprise Tooling:** To systematically identify, stress-test, and document the key software tools, critical observability metrics, and robust validation techniques that are absolutely required to stabilize and deploy agentic AI pipelines at a massive enterprise scale, ensuring 99.9% uptime, reliability, and long-term code maintainability.
3. **Deliver a Functional Production System:** To design from scratch, develop using modern full-stack frameworks, and securely deliver an actionable, fully deployed chatbot system that practically demonstrates RAG principles in a real-world educational setting. The deployed system must reliably support massive document-based Q&A, provide strictly real-time current affairs updates by aggregating multiple live APIs, and facilitate seamless multilingual interaction to effectively serve a diverse Indian user base.
4. **Create an Actionable Technical Roadmap:** To synthesize the extensive technical learnings, debugging sessions, and architectural decisions from the entire development process into a highly actionable, step-by-step roadmap for organizations aiming to transition safely from basic, prompt-based AI experimentation to deploying high-impact, autonomous, and incredibly cost-effective AI systems in production.
