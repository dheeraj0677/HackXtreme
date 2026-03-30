import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentry import sentry_app

def run_test(headline: str):
    print(f"\n--- Testing Headline: {headline} ---")
    initial_state = {
        "news_item": headline,
        "is_threat": False,
        "verification_sources": [],
        "is_verified": False,
        "logs": []
    }
    try:
        result = sentry_app.invoke(initial_state)
        print("Final State Logs:")
        for log in result.get('logs', []):
            print(f"  - {log}")
    except Exception as e:
        print(f"ERROR during execution: {e}")
        import traceback
        traceback.print_exc()
    print("-----------------------------------")

if __name__ == "__main__":
    test_cases = [
        "A new park is opening in downtown today.", # Should be SAFE
        "Major gas leak reported near your primary office building.", # Should be THREAT -> VERIFY -> NOTIFY
        "Warning: High solar radiation expected next week.", # Might be THREAT -> UNVERIFIED
    ]

    for case in test_cases:
        run_test(case)
