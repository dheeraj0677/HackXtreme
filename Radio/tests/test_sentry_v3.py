import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentry import sentry_app
import time

def run_test_v3(headline: str):
    print(f"\n--- [Phase 3 Test] Processing: {headline} ---")
    initial_state = {
        "news_item": headline,
        "is_threat": False,
        "threat_analysis": "",
        "verification_results": "",
        "is_verified": False,
        "context": [],
        "logs": []
    }
    try:
        result = sentry_app.invoke(initial_state)
        print("\n[Final Report Summary]")
        print(f"  Threat Detected: {result.get('is_threat')}")
        print(f"  Verified: {result.get('is_verified')}")
        
        if result.get('threat_analysis'):
            print(f"\n  Analyst Reasoning (First 200 chars):\n  {result.get('threat_analysis')[:200]}...")
            
        if result.get('verification_results'):
            print(f"\n  Web Search Results (First 150 chars):\n  {result.get('verification_results')[:150]}...")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    print("------------------------------------------")

if __name__ == "__main__":
    # Test Scenario: A realistic threat that requires analyst depth and web validation
    # Scenario 1: Natural Disaster
    run_test_v3("Large wildfire spreading near suburban residential areas.")
    
    time.sleep(2)
    
    # Scenario 2: Benign news (Should stop at Triage)
    run_test_v3("New community garden opens this weekend.")
