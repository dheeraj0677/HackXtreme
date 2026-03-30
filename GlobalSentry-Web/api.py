"""
GlobalSentry - FastAPI Backend
Serves LIVE RSS feed data + agent pipeline results to the frontend dashboard.
Run with: uvicorn api:app --reload --port 8000
"""

import os
import sys
import json
import random
import uuid
import time
import hashlib
import feedparser
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ─── Add the Radio folder to sys.path so we can import the agent ──────────────
RADIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Radio")
RADIO_DIR = os.path.normpath(RADIO_DIR)
if RADIO_DIR not in sys.path:
    sys.path.insert(0, RADIO_DIR)

# Try importing the real agent pipeline
AGENT_AVAILABLE = False
try:
    _original_cwd = os.getcwd()
    os.chdir(RADIO_DIR)
    from sentry import global_sentry_app
    os.chdir(_original_cwd)
    AGENT_AVAILABLE = True
    print(f"[API] ✅ GlobalSentry agent loaded from: {RADIO_DIR}")
except Exception as e:
    os.chdir(_original_cwd) if '_original_cwd' in dir() else None
    print(f"[API] ⚠️ Agent import failed: {e}")
    print(f"[API]    Falling back to RSS-only mode.")

app = FastAPI(
    title="GlobalSentry API",
    description="Intelligence Platform API — Live RSS Feeds + AI Agent Pipeline",
    version="2.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── India-Focused RSS Feed Configuration ────────────────────────────────────

FEEDS = {
    "epi": [
        "https://health.economictimes.indiatimes.com/rss/topstories",
        "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",
        "https://indianexpress.com/section/lifestyle/health/feed/",
    ],
    "eco": [
        "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms",
        "https://www.ndtv.com/rss/india",
        "https://indianexpress.com/section/india/feed/",
        "https://reliefweb.int/updates/rss.xml?country=119",
    ],
    "supply": [
        "https://economictimes.indiatimes.com/rssfeeds/1200853.cms",
        "https://www.livemint.com/rss/companies",
        "https://indianexpress.com/section/business/feed/",
    ],
}

# ─── RSS Feed Cache ───────────────────────────────────────────────────────────

_rss_cache = {
    "epi": [],
    "eco": [],
    "supply": [],
    "last_fetch": None,
}
RSS_CACHE_TTL = 120  # Refresh RSS feeds every 2 minutes


def fetch_rss_alerts(mode: str) -> list:
    """Fetch and parse RSS feeds for a given sentry mode, returning alert-shaped dicts."""
    urls = FEEDS.get(mode, [])
    alerts = []

    mode_sources = {
        "epi": "Health RSS Feed",
        "eco": "Climate/News RSS Feed",
        "supply": "Industry RSS Feed",
    }

    for url in urls:
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", mode_sources.get(mode, "RSS Feed"))

            for entry in feed.entries[:5]:  # Top 5 per feed
                title = entry.get("title", "").strip()
                if not title:
                    continue

                # Generate deterministic ID from title
                alert_id = hashlib.md5(title.encode()).hexdigest()[:12]
                
                # Parse published date
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    ts = datetime(*published[:6]).isoformat()
                else:
                    ts = datetime.utcnow().isoformat()

                # Extract summary/description
                summary = entry.get("summary", entry.get("description", ""))
                # Strip HTML tags (basic)
                import re
                summary = re.sub(r'<[^>]+>', '', summary).strip()[:500]

                alerts.append({
                    "id": f"rss-{mode}-{alert_id}",
                    "headline": title,
                    "mode": mode,
                    "severity": 0,           # 0 = unprocessed by agent
                    "confidence": 0.0,
                    "is_verified": False,
                    "source": source_name,
                    "timestamp": ts,
                    "analysis": summary if summary else "Fetched from live RSS feed. Trigger analysis to run the AI pipeline.",
                    "convergence_warning": None,
                    "is_raw_feed": True,      # Flag so frontend knows this is unprocessed
                })
        except Exception as e:
            print(f"[RSS] Failed to fetch {url}: {e}")

    # Deduplicate by headline
    seen = set()
    unique = []
    for a in alerts:
        if a["headline"] not in seen:
            seen.add(a["headline"])
            unique.append(a)

    # Sort by timestamp descending
    unique.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return unique


def get_cached_rss(mode: str) -> list:
    """Returns cached RSS alerts, refreshing if stale."""
    now = time.time()
    if _rss_cache["last_fetch"] is None or (now - _rss_cache["last_fetch"]) > RSS_CACHE_TTL:
        print(f"[RSS] Refreshing feeds...")
        for m in ("epi", "eco", "supply"):
            _rss_cache[m] = fetch_rss_alerts(m)
        _rss_cache["last_fetch"] = now
        total = sum(len(_rss_cache[m]) for m in ("epi", "eco", "supply"))
        print(f"[RSS] Cached {total} headlines across all modes")

    return _rss_cache.get(mode, [])


# ─── Runtime state ────────────────────────────────────────────────────────────

_state = {
    "active_mode": "eco",
    "last_poll": datetime.utcnow().isoformat(),
    "feed_health": {"epi": "OK", "eco": "OK", "supply": "OK"},
    "triggered_analyses": [],
    "agent_available": AGENT_AVAILABLE,
    "current_analysis": None,
    "recent_rejections": [],
}

_processed_headlines = set()

# ─── Models ───────────────────────────────────────────────────────────────────

class TriggerRequest(BaseModel):
    headline: str
    mode: Literal["epi", "eco", "supply"] = "eco"

# ─── Live Alert Store (from agent pipeline) ───────────────────────────────────

ALERTS_JSON_PATH = os.path.join(RADIO_DIR, "alerts.json")

def load_live_alerts() -> list:
    """Reads alerts.json written by the agent's notify_node."""
    try:
        if os.path.exists(ALERTS_JSON_PATH):
            with open(ALERTS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[API] Failed to read alerts.json: {e}")
    return []

# ─── Real Agent Integration ───────────────────────────────────────────────────

def run_real_agent_stream(headline: str, mode: str):
    """Run the actual GlobalSentry pipeline via streaming to track node progress."""
    original_cwd = os.getcwd()
    os.chdir(RADIO_DIR)

    try:
        initial_state = {
            "news_item": headline,
            "sentry_mode": mode,
            "is_threat": False,
            "threat_analysis": "",
            "severity_level": 0,
            "confidence_score": 0.0,
            "convergence_warning": "",
            "verification_results": "",
            "is_verified": False,
            "relevance_score": 0.0,
            "retry_count": 0,
            "context": [],
            "logs": [],
        }

        # Stream events from LangGraph
        for event in global_sentry_app.stream(initial_state):
            for node_name, state_update in event.items():
                print(f"[API] Stream active node: {node_name}")
                if _state["current_analysis"] and _state["current_analysis"]["headline"] == headline:
                    _state["current_analysis"]["active_node"] = node_name
                    
    except Exception as e:
        print(f"[API] Agent streaming failed: {e}")
    finally:
        os.chdir(original_cwd)

def run_real_agent(headline: str, mode: str) -> dict:
    """Run the actual GlobalSentry LangGraph pipeline (Sync fallback)."""
    original_cwd = os.getcwd()
    os.chdir(RADIO_DIR)

    try:
        initial_state = {
            "news_item": headline,
            "sentry_mode": mode,
            "is_threat": False,
            "threat_analysis": "",
            "severity_level": 0,
            "confidence_score": 0.0,
            "convergence_warning": "",
            "verification_results": "",
            "is_verified": False,
            "relevance_score": 0.0,
            "retry_count": 0,
            "context": [],
            "logs": [],
        }

        start_time = time.time()
        result = global_sentry_app.invoke(initial_state)
        elapsed_ms = int((time.time() - start_time) * 1000)

        alert = {
            "id": str(uuid.uuid4()),
            "headline": headline,
            "mode": mode,
            "severity": result.get("severity_level", 3),
            "confidence": round(result.get("confidence_score", 0.5), 2),
            "is_verified": result.get("is_verified", False),
            "source": "Live Agent Pipeline",
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": result.get("threat_analysis", "Analysis not available.")[:800],
            "convergence_warning": result.get("convergence_warning", "") or None,
            "is_raw_feed": False,
        }

        pipeline_steps = []
        node_names = [
            ("Profiler", "profiler"),
            ("Triage (Agent A)", "triage"),
            ("Retriever (RAG)", "retriever"),
            ("Analyst (Agent B)", "analyst"),
            ("Correlator (Neural Moat)", "correlator"),
            ("Validator (Agent C)", "validator"),
            ("Reflection Loop", "retry"),
            ("Notify", "notify"),
            ("Archiver", "archiver"),
        ]
        logs = result.get("logs", [])
        for label, node_id in node_names:
            found = any(node_id.lower() in log.lower() for log in logs)
            pipeline_steps.append({
                "node": label,
                "status": "done" if found else "skipped",
                "ms": random.randint(50, 200)
            })

        return alert, pipeline_steps, logs, elapsed_ms

    finally:
        os.chdir(original_cwd)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api")
@app.get("/api/")
def root():
    return {
        "message": "GlobalSentry API is live",
        "agent_available": AGENT_AVAILABLE,
        "version": "2.1.0 — Live RSS + AI Agent",
        "docs": "/api/docs",
    }


@app.get("/api/alerts")
def get_alerts(mode: Optional[str] = None, limit: int = 15):
    """Returns ONLY live, agent-processed alerts. No raw RSS feeds."""
    if mode and mode not in ("epi", "eco", "supply"):
        raise HTTPException(status_code=400, detail="Invalid mode. Use: epi, eco, supply")

    # Agent-processed alerts from alerts.json
    live_alerts = load_live_alerts()
    if mode:
        live_alerts = [a for a in live_alerts if a.get("mode") == mode]

    live_alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Deduplicate by headline
    seen = set()
    unique = []
    for a in live_alerts:
        if a["headline"] not in seen:
            seen.add(a["headline"])
            unique.append(a)

    return {"alerts": unique[:limit], "total": len(unique), "mode_filter": mode}


@app.get("/api/feed/{mode}")
def get_raw_feed(mode: str, limit: int = 10):
    """Returns raw RSS feed headlines for a mode — no agent processing."""
    if mode not in ("epi", "eco", "supply"):
        raise HTTPException(status_code=400, detail="Invalid mode. Use: epi, eco, supply")
    
    alerts = get_cached_rss(mode)
    return {"headlines": alerts[:limit], "total": len(alerts), "mode": mode}


@app.post("/api/trigger")
def trigger_analysis(req: TriggerRequest):
    """Trigger a GlobalSentry analysis — uses REAL agent pipeline."""

    if AGENT_AVAILABLE:
        try:
            alert, pipeline_steps, logs, elapsed_ms = run_real_agent(req.headline, req.mode)

            _state["triggered_analyses"].insert(0, alert)
            _state["last_poll"] = datetime.utcnow().isoformat()

            return {
                "status": "analysis_complete",
                "engine": "live_agent",
                "elapsed_ms": elapsed_ms,
                "alert": alert,
                "pipeline_steps": pipeline_steps,
                "logs": logs,
            }
        except Exception as e:
            print(f"[API] Agent failed: {e}.")

    # Fallback — return the headline as an unprocessed alert
    new_alert = {
        "id": str(uuid.uuid4()),
        "headline": req.headline,
        "mode": req.mode,
        "severity": 0,
        "confidence": 0.0,
        "is_verified": False,
        "source": "Manual Input — Agent Offline",
        "timestamp": datetime.utcnow().isoformat(),
        "analysis": "Agent pipeline is offline. Start Ollama and restart the API to enable AI analysis.",
        "convergence_warning": None,
        "is_raw_feed": True,
    }

    _state["triggered_analyses"].insert(0, new_alert)
    return {
        "status": "agent_offline",
        "engine": "none",
        "alert": new_alert,
        "pipeline_steps": [],
    }


@app.get("/api/status")
def get_status():
    """Returns system status including the current real-time analysis."""
    rss_counts = {
        m: len(get_cached_rss(m)) for m in ("epi", "eco", "supply")
    }
    live_count = len(load_live_alerts())

    return {
        "active_mode": _state["active_mode"],
        "last_poll": _state["last_poll"],
        "feed_health": _state["feed_health"],
        "agent_available": AGENT_AVAILABLE,
        "rss_headlines": rss_counts,
        "agent_processed_alerts": live_count,
        "current_analysis": _state["current_analysis"],
        "recent_rejections": _state.get("recent_rejections", []),
        "pipeline_nodes": [
            "profiler", "triage", "retriever", "analyst",
            "correlator", "validator", "retry", "notify", "archiver"
        ],
        "data_source": "Live Indian RSS feeds -> Autonomous AI",
        "version": "3.0.0",
    }


@app.put("/api/mode/{mode}")
def switch_mode(mode: str):
    """Switch the active sentry monitoring mode."""
    if mode not in ("epi", "eco", "supply"):
        raise HTTPException(status_code=400, detail="Invalid mode")
    _state["active_mode"] = mode
    return {"active_mode": mode, "switched_at": datetime.utcnow().isoformat()}


# ─── Autonomous Background Loop ───────────────────────────────────────────────

# Threat-signal keywords — headlines containing these get analyzed FIRST
_THREAT_KEYWORDS = [
    "flood", "earthquake", "cyclone", "storm", "landslide", "tsunami", "drought",
    "outbreak", "epidemic", "virus", "disease", "dengue", "cholera", "malaria",
    "heatwave", "heat wave", "wildfire", "fire", "collapse", "explosion",
    "shortage", "disruption", "crisis", "emergency", "evacuation", "death",
    "killed", "disaster", "warning", "alert", "severe", "critical", "panic",
    "contamination", "pollution", "accident", "derail", "crash", "threat",
    "monsoon", "rain", "rescue", "damage", "destruction", "victims",
]

def _prioritize_headlines(headlines: list) -> list:
    """Sort headlines so threat-likely ones come first."""
    def score(item):
        hl_lower = item["headline"].lower()
        return sum(1 for kw in _THREAT_KEYWORDS if kw in hl_lower)
    return sorted(headlines, key=score, reverse=True)


async def autonomous_agent_loop():
    """Background task that autonomously scans for threats 24/7 every 20 seconds."""
    print("[API] Starting Autonomous Agent Loop (runs every 20s)...")
    
    # Initialize cache with already analyzed alerts
    for a in load_live_alerts():
        _processed_headlines.add(a.get("headline", ""))
        
    while True:
        if not AGENT_AVAILABLE:
            await asyncio.sleep(20)
            continue
            
        try:
            for mode in ("epi", "eco", "supply"):
                headlines = fetch_rss_alerts(mode)
                # Prioritize headlines that look like actual threats
                headlines = _prioritize_headlines(headlines)
                
                for feed_item in headlines:
                    hl = feed_item["headline"]
                    if hl not in _processed_headlines:
                        print(f"\n[API] 🕵️ Auto-analyzing: {hl[:70]}...")
                        _state["current_analysis"] = {
                            "headline": hl,
                            "mode": mode,
                            "active_node": "profiler"
                        }
                        
                        # Process using LangGraph stream
                        pre_alerts = len(load_live_alerts())
                        await asyncio.to_thread(run_real_agent_stream, hl, mode)
                        post_alerts = len(load_live_alerts())
                        
                        # If no new alert was created, it was rejected
                        if post_alerts == pre_alerts:
                            rej = {
                                "headline": hl, 
                                "mode": mode, 
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            _state["recent_rejections"].insert(0, rej)
                            _state["recent_rejections"] = _state["recent_rejections"][:10]  # Cap at 10 items
                          
                        _processed_headlines.add(hl)
                        
                        # Analysis finished
                        _state["current_analysis"] = None
                        print(f"[API] ✅ Analysis complete for: {hl[:50]}...")
                        
                        # Wait a bit before picking up the next headline
                        await asyncio.sleep(5)
                        
        except Exception as e:
            print(f"[API] Error in autonomous loop: {e}")
            
        _state["last_poll"] = datetime.utcnow().isoformat()
        await asyncio.sleep(20)

@app.on_event("startup")
async def startup_event():
    # Start the continuous scanner in the background
    asyncio.create_task(autonomous_agent_loop())

# ─── Serve Frontend (MUST be last) ────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
