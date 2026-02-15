import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# MODELS
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.6, # Slightly lower for consistent advice
    google_api_key=api_key
)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
DB_PATH = "vector_store/"

# LOAD DATABASE
try:
    vector_db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
except Exception:
    retriever = None

# --- MODE A: SOCRATIC TUTOR (Updated for Patience) ---
tutor_template = """
You are EduGuide, a patient and encouraging tutor.
CONTEXT: {context}
QUESTION: {question}

RULES:
1. Never give the direct answer to homework. Guide them step-by-step.
2. Use emojis to be friendly (e.g., 📚, 💡).
3. If the context is missing, say: "I don't see that in your lecture notes, but let's try to reason through it..."
"""
tutor_prompt = ChatPromptTemplate.from_template(tutor_template)

# --- MODE B: EMPATHETIC ADVISOR (Updated for Tone) ---
advisor_template = """
You are a caring Academic Advisor. 
STUDENT PROFILE: {student_profile}
QUESTION: {question}

INSTRUCTIONS:
1. **Bad News:** If grades are low/failing, be empathetic first. Say "I notice things are tough in [Course Name] right now," before giving warnings.
2. **Good News:** If grades are high, celebrate it! "You're crushing it in [Course Name]! 🎉"
3. **Actionable:** Always end with one specific next step (e.g., "Email Prof. Smith today").
"""
advisor_prompt = ChatPromptTemplate.from_template(advisor_template)

# CHAINS
def get_tutor_response(question):
    if not retriever: return "Error: Knowledge Base not found."
    chain = (
        {"context": retriever, "question": RunnablePassthrough()} 
        | tutor_prompt | llm | StrOutputParser()
    )
    return chain.invoke(question)

def get_advisor_response(question, formatted_profile):
    chain = (
        {"student_profile": RunnablePassthrough(), "question": RunnablePassthrough()} 
        | advisor_prompt | llm | StrOutputParser()
    )
    return chain.invoke({"student_profile": formatted_profile, "question": question})