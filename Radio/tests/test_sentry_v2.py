import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentry import sentry_app
import time

def run_test(headline: str):
    print(f"\n--- Processing: {headline} ---")
    initial_state = {
        "news_item": headline,
        "is_threat": False,
        "verification_sources": [],
        "is_verified": False,
        "context": [],
        "world_model": "",
        "logs": []
    }
    try:
        result = sentry_app.invoke(initial_state)
        print("Logs Overview:")
        for log in result.get('logs', []):
            if "Found" in log or "stored" in log or "Triage" in log:
                print(f"  > {log}")
    except Exception as e:
        print(f"ERROR: {e}")
    print("-----------------------------------")

if __name__ == "__main__":
    # Part 1: Initial event (Triage should detect it, Archiver should store it)
    run_test("Reports of a minor chemical spill on Industrial Way.")
    
    # Wait a bit
    print("\nWaiting for memory to settle...\n")
    time.sleep(2)
    
    # Part 2: Related event (Retriever should find Part 1, Triage should use it for high alert)
    run_test("Emergency sirens heard near Industrial Way; residents reporting a strong sulfur smell.")
    
    # Part 3: Unrelated event (Should be safe)
    run_test("New library exhibit features local history.")
