import random

subjects = {
    "History": [
        "the Indus Valley Civilization", "the Mauryan Empire", "the Mughal administration", 
        "the Revolt of 1857", "the Indian National Congress", "the Non-Cooperation Movement", 
        "the Quit India Movement", "the Bhakti Movement", "the Chola architecture", 
        "the Vijayanagara Empire", "the Maratha expansion", "the Partition of Bengal"
    ],
    "Polity": [
        "the Preamble of the Constitution", "Fundamental Rights", "Directive Principles of State Policy", 
        "the role of the President", "the Parliamentary system", "the Supreme Court's jurisdiction", 
        "Panchayati Raj institutions", "the Election Commission", "the GST Council", 
        "Article 356 (President's Rule)", "the Anti-Defection Law", "Judicial Review"
    ],
    "Geography": [
        "the Himalayan river system", "the monsoon mechanism", "the Western Ghats biodiversity", 
        "El Nino and La Nina", "plate tectonics", "ocean currents", "cyclone formation", 
        "soil types in India", "agricultural cropping patterns", "industrial corridors", 
        "population demographics", "coral bleaching"
    ],
    "Economy": [
        "the Reserve Bank of India's monetary policy", "inflation targeting", "Foreign Direct Investment (FDI)", 
        "the banking sector NPAs", "the agricultural subsidies", "the World Trade Organization (WTO)", 
        "the fiscal deficit", "cryptocurrency regulations", "Special Economic Zones (SEZs)", 
        "the ease of doing business", "universal basic income", "MSME sector growth"
    ],
    "Environment": [
        "the Paris Agreement", "the National Action Plan on Climate Change", "Project Tiger", 
        "wetland conservation", "renewable energy targets", "air pollution in Delhi", 
        "the Wildlife Protection Act", "biodiversity hotspots", "carbon trading", 
        "plastic waste management", "the Western Ghats ecology", "marine pollution"
    ]
}

question_templates = [
    "What is the significance of {topic} in the context of Indian {subject}?",
    "Can you explain the main features of {topic}?",
    "How does {topic} impact the overall landscape of {subject}?",
    "Discuss the historical and contemporary relevance of {topic}.",
    "What are the major challenges associated with {topic}?",
    "In what ways has {topic} evolved over the years?",
    "Provide a detailed overview of {topic}.",
    "What should an aspirant know about {topic} for the UPSC exam?",
    "Analyze the pros and cons related to {topic}.",
    "Why is {topic} frequently asked in the UPSC {subject} section?"
]

answer_templates = [
    "{topic} is a crucial aspect of {subject}. Understanding it requires a deep dive into its origins, its socio-economic impacts, and its relevance to current affairs. It frequently appears in both Prelims and Mains.",
    "The core features of {topic} revolve around its structural importance in {subject}. Aspirants must analyze its pros, cons, and recent developments related to it.",
    "In the context of {subject}, {topic} plays a pivotal role. It influences policy decisions and has a widespread impact on the national framework. Memorizing its key components is essential.",
    "Historically and presently, {topic} represents a major milestone in {subject}. A thorough analysis of its implications helps in writing well-rounded Mains answers.",
    "The primary challenges regarding {topic} involve implementation issues, geographical/economic constraints, and policy gaps. Addressing these requires a multi-dimensional approach.",
    "{topic} has evolved significantly. Initially viewed through a narrow lens in {subject}, it is now understood as a complex, multi-faceted issue requiring holistic study.",
    "A detailed overview of {topic} involves understanding its background, its functional mechanisms, and its future trajectory within {subject}.",
    "For the UPSC exam, knowing about {topic} means understanding its constitutional/legal backing, historical context, and current relevance in {subject}.",
    "The advantages of {topic} are numerous, yet it faces criticism. A balanced UPSC answer should weigh these pros and cons objectively within the framework of {subject}.",
    "{topic} is a favorite for examiners in {subject} because it connects static syllabus concepts with dynamic current affairs, testing the candidate's analytical skills."
]

def generate_qa_file(filename, num_questions):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Massive UPSC Knowledge Base - Generated Sample Questions\n\n")
        
        for i in range(1, num_questions + 1):
            subject = random.choice(list(subjects.keys()))
            topic = random.choice(subjects[subject])
            
            q_template = random.choice(question_templates)
            a_template = random.choice(answer_templates)
            
            question = q_template.format(topic=topic, subject=subject)
            answer = a_template.format(topic=topic, subject=subject)
            
            f.write(f"Q{i}: {question}\n")
            f.write(f"A{i}: {answer}\n\n")

if __name__ == "__main__":
    generate_qa_file('massive_upsc_qa.txt', 2500)
    print("Generated 2500 questions successfully!")
