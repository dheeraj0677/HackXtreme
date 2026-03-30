import feedparser
import os
from dotenv import load_dotenv

load_dotenv()
RSS_FEEDS = os.getenv("RSS_FEEDS", "").split(",")

def dry_run():
    print("--- Phase 4 Dry Run: Fetching Headlines ---")
    for url in RSS_FEEDS:
        url = url.strip()
        if not url: continue
        print(f"\nFeed: {url}")
        try:
            feed = feedparser.parse(url)
            print(f"Status: {feed.get('status', 'N/A')}")
            print(f"Items found: {len(feed.entries)}")
            for i, entry in enumerate(feed.entries[:3]):  # Just show top 3
                print(f"  {i+1}. {entry.get('title')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    dry_run()
