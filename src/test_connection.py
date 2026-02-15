import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load the API Key safely
load_dotenv()
api_key= os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file")
    exit()
    
print("✅ API Key found. Connecting to Gemini...")

# 2. Initialize the Gemini model
# We use 'gemini-pro' for t3ext. It's fast and smart.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=api_key)

# 3. Send a Test Message
try:
    print("🤖 Sending test query: 'Hello, explain quantum physics in one sentence.'")
    response = llm.invoke("Hello, explain quantum physics in one sentence.")
    
    print("\n--- AI RESPONSE ---")
    print(response.content)
    print("-------------------")
    print("✅ SUCCESS: Your environment is ready for Day 2!")

except Exception as e:
    print(f"\n ❌ CONNECTION FAILED: {e} ")