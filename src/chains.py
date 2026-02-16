import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 1. SETUP MODELS
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.6,
    google_api_key=api_key
)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
DB_PATH = "vector_store/"

# 2. PROMPTS
tutor_template = """
You are EduGuide, a patient and encouraging tutor.
CONTEXT: {context}
QUESTION: {question}

RULES:
1. Answer based ONLY on the context above.
2. If the context has the answer, explain it clearly.
3. If the context is missing, say: "I don't see that in your lecture notes."
"""
tutor_prompt = ChatPromptTemplate.from_template(tutor_template)

advisor_template = """
You are a caring Academic Advisor. 
STUDENT PROFILE: {student_profile}
QUESTION: {question}

INSTRUCTIONS:
1. Bad News: If grades are low/failing, be empathetic.
2. Good News: Celebrate high grades!
3. Actionable: End with specific advice.
"""
advisor_prompt = ChatPromptTemplate.from_template(advisor_template)

# 3. HELPER: LOAD DB FRESH EVERY TIME
def get_retriever():
    try:
        # We load the DB from disk *inside* the function to get latest updates
        vector_db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
        return vector_db.as_retriever(search_kwargs={"k": 5}) # Increased 'k' to find more text
    except Exception:
        return None

# 4. CHAINS
def get_tutor_response(question):
    retriever = get_retriever() # <--- FRESH LOAD HERE
    
    if not retriever:
        return "⚠️ knowledge Base is empty. Please upload a PDF first."
    
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