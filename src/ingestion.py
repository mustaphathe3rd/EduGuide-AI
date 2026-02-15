import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found.")
    exit()
    
DATA_PATH = "data/books/"
DB_FAISS_PATH = "vector_store/"

def create_vector_db():
    print("PAGE 1: Loading PDF documents...")
    
    # Load all PDFs in the data/books directory
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    if not documents:
        print("❌ No PDFs found in data/books/. Please add a file.")
        return
    
    print(f" - Loaded {len(documents)} pages.")
    
    # Split text into chunks (so the AI doesn't get overwhelmed)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    print(f"PAGE 2: Creating EMbeddings (This uses your API quota)...")
    
    # Use Google's embeddings model
    # NEW (Correct - add 'model=')
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Create the Vector Store
    db = FAISS.from_documents(texts, embeddings)
    
    # Save it locally
    db.save_local(DB_FAISS_PATH)
    
    print(f"✅ SUCCESS: Vector Database saved to '{DB_FAISS_PATH}'")
    
if __name__ == "__main__":
    create_vector_db() 
