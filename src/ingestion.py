import os
import shutil  # <--- NEW IMPORT for deleting folders
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Define paths
DB_PATH = "vector_store/"

def ingest_new_files(uploaded_files):
    """
    Accepts a list of Streamlit UploadedFile objects, saves them,
    and rebuilds the Vector Database.
    """
    # 1. Robust API Key Retrieval
    api_key = os.getenv("GOOGLE_API_KEY") 
    if not api_key:
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            return "❌ Error: Google API Key not found. Please check Streamlit Secrets."

    # 2. Save Uploaded Files to a Temp Directory
    temp_dir = "data/uploaded_books"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir) # Clean up old temp files
    os.makedirs(temp_dir, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)
    
    # 3. Load and Process PDFs
    documents = []
    for path in saved_paths:
        try:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
        except Exception as e:
            return f"Error loading {path}: {e}"

    if not documents:
        return "No valid text found in PDFs."

    # 4. Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # 5. Create/Overwrite Vector DB
    try:
        # --- NUCLEAR FIX: DELETE OLD BRAIN FIRST ---
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)  # Deletes the folder completely
        # -------------------------------------------

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=api_key 
        )
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(DB_PATH)
    except Exception as e:
        return f"❌ AI Error: {str(e)}"
    
    return f"✅ Successfully processed {len(saved_paths)} file(s)! The old brain was wiped."