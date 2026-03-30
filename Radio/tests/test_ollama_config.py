import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sentry import get_llm

def test_ollama_init():
    print("--- Testing Ollama Initialization ---")
    
    # Test: Ollama
    print("\nTest: Ollama Provider")
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["OLLAMA_MODEL"] = "llama3" # Or llama3.2
    
    try:
        llm = get_llm("any-model")
        if llm:
            print(f"✅ Ollama (LangChain-Ollama) initialized: {type(llm)}")
            print(f"Model: {llm.model}")
            print("\nAttempting a quick ping (requires Ollama running with llama3 pulled)...")
            try:
                # We don't want to hang forever if Ollama isn't running
                # but ChatOllama doesn't have a simple timeout in the constructor that works for invoke easily here
                # so we just try it.
                response = llm.invoke("Hi. Respond with 'Ollama is alive' if you hear me.").content
                print(f"Response: {response}")
            except Exception as e:
                print(f"⚠️ Ollama ping failed (This is expected if Ollama is not running or model not pulled): {e}")
        else:
            print("❌ Ollama initialization failed")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")

if __name__ == "__main__":
    test_ollama_init()
