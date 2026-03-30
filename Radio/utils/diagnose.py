import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
print(f"DEBUG: Using API Key starting with: {api_key[:10]}... (Total length: {len(api_key)})")

if not api_key:
    print("ERROR: No GOOGLE_API_KEY found in environment or .env file.")
else:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
        response = llm.invoke("Say 'Key is alive'")
        print(f"API SUCCESS (Chat): {response.content}")
        
        print("Testing Embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        vector = embeddings.embed_query("Neural Sentry Test")
        print(f"API SUCCESS (Embeddings): Vector length {len(vector)}")
    except Exception as e:
        print(f"API FAILURE: {e}")

try:
    from qdrant_client import QdrantClient
    import shutil
    
    # Try with a fresh absolute path to bypass OneDrive potential locks
    test_path = os.path.abspath("./qdrant_test_temp")
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    print(f"Trying Qdrant Local initialization at: {test_path}...")
    client = QdrantClient(path=test_path)
    print("Qdrant Local Success!")
except Exception as e:
    print(f"QDRANT FAILURE: {e}")
