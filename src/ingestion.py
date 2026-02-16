import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# Define paths
DB_PATH = "vector_store/"

def ingest_new_files(uploaded_files):
    """
    Accepts a list of Streamlit UploadedFile objects, saves them,
    and rebuilds the Vector Database.
    """
    # 1. Save Uploaded Files to a Temp Directory
    temp_dir = "data/uploaded_books"
    os.makedirs(temp_dir, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)
    
    # 2. Load and Process PDFs
    documents = []
    for path in saved_paths:
        try:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {path}: {e}")

    if not documents:
        return "No valid text found in PDFs."

    # 3. Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # 4. Create/Overwrite Vector DB
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(DB_PATH)
    
    return f"✅ Successfully processed {len(saved_paths)} files!"