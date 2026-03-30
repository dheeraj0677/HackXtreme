import os
import sys
import time
import json

# Bypass Telegram and RSS for demo mode
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""

try:
    from sentry import sentry_app
    MOCK_AVAILABLE = True
except Exception as e:
    print(f"[Warning] Sentry app could not load due to environment error: {e}")
    MOCK_AVAILABLE = False

def print_header(simulated=False):
    style = " (SIMULATED MODE)" if simulated else ""
    print("\n" + "="*60)
    print(f"      🛡️  NEURAL SENTRY: HACKATHON DEMO{style} 🛡️")
    print("="*60)
    print("Focus: Natural Disasters, Riots, Physical Threats")
    print("Mode: Interactive Terminal (Manual Input)")
    print("="*60 + "\n")

def get_simulated_response(headline):
    """Simulates agent reasoning for common hackathon scenarios."""
    print(f"\n[System] Ingesting: \"{headline}\"")
    print("[System] Neural Sentry agents are starting work...\n")
    time.sleep(1) # Dramatic pause
    
    # Common scenarios
    is_disaster = any(x in headline.lower() for x in ["flood", "quake", "fire", "storm", "hurricane"])
    is_riot = any(x in headline.lower() for x in ["riot", "mob", "protest", "violent", "attack"])
    
    logs = [
        "Profiler: Evaluating personal relevance... Match found: User is in the reported region.",
        "Retriever: Searching historical memory... Found 2 similar incidents in the past 12 months.",
    ]
    
    if is_disaster or is_riot:
        logs.append("Triage: Physical threat suspected. Escalating to Analyst node.")
        logs.append("Analyst: Performing Life-Safety Risk Assessment...")
        logs.append("Analyst: High probability of danger detected. Calculating evacuation routes.")
        logs.append("Validator: Hunting for second source... VERIFIED by local emergency channels.")
        logs.append("Notify: Mock Alert triggered for SMS/Telegram.")
        logs.append("Archiver: Storing event in Qdrant memory.")
        
        analysis = (
            "CRISIS ANALYSIS: This event poses an immediate threat to physical safety.\n"
            "RECOMMENDATION: Avoid the affected area immediately. \n"
            "SAFE ZONES: Local community shelters appearing active. \n"
            "ACTION: Follow official evacuation orders and maintain emergency radio contact."
        )
        return {"is_threat": True, "is_verified": True, "logs": logs, "threat_analysis": analysis}
    else:
        logs.append("Triage: Safe / No physical threat suspected. Process complete.")
        logs.append("Archiver: Headline archived for non-urgent context.")
        return {"is_threat": False, "is_verified": False, "logs": logs, "threat_analysis": ""}

def run_interactive_demo():
    simulated = not MOCK_AVAILABLE
    if not simulated:
        choice = input("Do you want to run in [A] Live Mode OR [B] Simulated Mode (Backup for Demo)? ").strip().upper()
        simulated = (choice == 'B')

    print_header(simulated)
    
    while True:
        try:
            headline = input("\n[Prompt] Enter a news headline to analyze (or 'exit'): ").strip()
            
            if headline.lower() in ['exit', 'quit', 'q']:
                break
                
            if not headline: continue
                
            if simulated:
                result = get_simulated_response(headline)
            else:
                print(f"\n[System] Ingesting: \"{headline}\"")
                print("[System] Neural Sentry agents are starting work...\n")
                initial_state = {
                    "news_item": headline, "is_threat": False, "threat_analysis": "",
                    "verification_results": "", "is_verified": False, "relevance_score": 0.0,
                    "context": [], "logs": []
                }
                result = sentry_app.invoke(initial_state)
            
            print("-" * 40)
            print("🧠 AGENT REASONING LOGS:")
            for log in result.get('logs', []):
                print(f"  ▶ {log}")
                time.sleep(0.5) # For demo effect
            print("-" * 40)
            
            if result.get('is_threat'):
                print(f"\n🚨 FINAL VERDICT: 🔴 THREAT DETECTED (VERIFIED)")
                print(f"\n[Analyst Report]:\n{result.get('threat_analysis')}")
            else:
                print("\n🚨 FINAL VERDICT: 🟢 SAFE / NO PHYSICAL THREAT")
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt: break
        except Exception as e:
            print(f"\n[Error] Something went wrong: {e}")
            if not simulated:
                print("\nSuggestion: Try running in Simulated Mode for the demo.")

if __name__ == "__main__":
    run_interactive_demo()
