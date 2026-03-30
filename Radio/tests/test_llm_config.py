import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sentry import get_llm

def test_llm_init():
    print("--- Testing LLM Initialization ---")
    
    # Test 1: Default (Gemini)
    print("\nTest 1: Default Provider (Gemini)")
    os.environ["LLM_PROVIDER"] = "gemini"
    llm = get_llm("gemini-1.5-flash")
    if llm:
        print(f"✅ Gemini initialized: {type(llm)}")
    else:
        print("❌ Gemini initialization failed (Expected if no API key)")

    # Test 2: Grok (No Key - Should Fallback)
    print("\nTest 2: Grok (No Key - Should Fallback to Gemini)")
    os.environ["LLM_PROVIDER"] = "grok"
    os.environ["XAI_API_KEY"] = ""
    llm = get_llm("gemini-1.5-flash")
    if llm:
        print(f"✅ Fallback to Gemini successful: {type(llm)}")
    else:
        print("❌ Fallback failed")

    # Test 3: Grok (With Key - Mocked check)
    print("\nTest 3: Grok (With Key placeholder)")
    os.environ["LLM_PROVIDER"] = "grok"
    os.environ["XAI_API_KEY"] = "sk-placeholder"
    try:
        llm = get_llm("grok-beta")
        if llm:
            print(f"✅ Grok (OpenAI client) initialized: {type(llm)}")
    except Exception as e:
        print(f"❌ Grok initialization error: {e}")

if __name__ == "__main__":
    test_llm_init()
