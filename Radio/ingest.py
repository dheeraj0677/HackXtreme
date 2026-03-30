import os
import time
import feedparser
import sqlite3
import hashlib
from dotenv import load_dotenv
from sentry import sentry_app

load_dotenv()

# Configuration
RSS_FEEDS = os.getenv("RSS_FEEDS", "").split(",")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))
DB_PATH = "ingestion_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS processed_items
                 (hash TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def is_processed(item_hash):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed_items WHERE hash=?", (item_hash,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_as_processed(item_hash):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO processed_items (hash) VALUES (?)", (item_hash,))
    conn.commit()
    conn.close()

def get_item_hash(item):
    # Combine title and link for a unique identifier
    content = f"{item.get('title', '')}|{item.get('link', '')}"
    return hashlib.sha256(content.encode()).hexdigest()

def process_feed(url):
    print(f"\n[Ingest] Checking feed: {url}")
    try:
        feed = feedparser.parse(url)
        new_items = 0
        for entry in feed.entries:
            item_hash = get_item_hash(entry)
            if not is_processed(item_hash):
                headline = entry.get('title', 'No Title')
                print(f"  > New Headline: {headline}")
                
                # Invoke the Neural Sentry Graph
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
                    sentry_app.invoke(initial_state)
                except Exception as e:
                    print(f"  [Error] Sentry App failed: {e}")
                
                mark_as_processed(item_hash)
                new_items += 1
        
        print(f"[Ingest] Finished. Processed {new_items} new items.")
    except Exception as e:
        print(f"[Error] Failed to parse {url}: {e}")

def main():
    print("--- Neural Sentry: Phase 4 Ingestion Engine ---")
    init_db()
    
    while True:
        for url in RSS_FEEDS:
            if url.strip():
                process_feed(url.strip())
        
        print(f"\n[Sleep] Waiting {POLL_INTERVAL} seconds for next poll...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
