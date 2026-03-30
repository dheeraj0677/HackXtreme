import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentry import sentry_app
import time
import os

def run_test_v5(headline: str):
    print(f"\n--- [Phase 5 Test] Processing: {headline} ---")
    initial_state = {
        "news_item": headline,
        "is_threat": False,
        "threat_analysis": "",
        "verification_results": "",
        "is_verified": False,
        "relevance_score": 0.0,
        "context": [],
        "logs": []
    }
    try:
        result = sentry_app.invoke(initial_state)
        print("\n[Final Report Summary]")
        print(f"  Relevance Score: {result.get('relevance_score')}")
        print(f"  Threat Detected: {result.get('is_threat')}")
        print(f"  Verified: {result.get('is_verified')}")
        
        # Check if it reached the Analyst/Validator path
        reached_analyst = any("Analyst" in log for log in result.get('logs', []))
        print(f"  Reached Analyst: {reached_analyst}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    print("------------------------------------------")

if __name__ == "__main__":
    # Scenario 1: Relevant Threat (Security + NYC)
    run_test_v5("Massive data breach reported at a New York-based financial institution.")
    
    time.sleep(2)
    
    # Scenario 2: Irrelevant Threat (Tokyo Weather)
    run_test_v5("Severe typhoon warning for Tokyo coastal regions.")
    
    time.sleep(2)
    
    # Scenario 3: Irrelevant News (Benign)
    run_test_v5("New park opening in Chicago.")
