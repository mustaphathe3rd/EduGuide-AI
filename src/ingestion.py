import os
import shutil
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Define paths
DB_PATH = "vector_store/"

def ingest_new_files(uploaded_files):
    """
    1. WIPES the old database.
    2. Processes new files.
    3. Creates a fresh database.
    """
    # --- STEP 1: NUCLEAR WIPE (Do this first!) ---
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print("💥 Old database deleted successfully.")
        except Exception as e:
            return f"❌ Error deleting old brain: {e}"
    # ---------------------------------------------

    # 2. Get API Key
    api_key = os.getenv("GOOGLE_API_KEY") 
    if not api_key:
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            return "❌ Error: Google API Key not found. Check Streamlit Secrets."

    # 3. Save Uploaded Files to Temp
    temp_dir = "data/uploaded_books"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)
    
    # 4. Load PDFs
    documents = []
    for path in saved_paths:
        try:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
        except Exception as e:
            return f"Error loading {path}: {e}"

    if not documents:
        return "No valid text found in PDFs."

    # 5. Split Text & Rebuild Brain
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=api_key 
        )
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(DB_PATH)
    except Exception as e:
        return f"❌ AI Error: {str(e)}"
    
    return f"✅ SUCCESS! Old brain wiped. Learned {len(saved_paths)} new file(s)."