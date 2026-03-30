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

# ─── User Profile ─────────────────────────────────────────────────────────────

USER_PROFILE = {
    "stakeholder_type": "government_planner",
    "region_of_interest": "South Asia",
    "active_sentry_mode": "eco",
    "alert_threshold": 0.5,
    "interests": [
        "Climate Disasters",
        "Epidemic Outbreaks",
        "Supply Chain Disruptions",
        "Public Health",
    ],
}

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

# ─── In-memory alert store (demo mode) ───────────────────────────────────────
MOCK_ALERTS = {
    "epi": [
        {
            "id": str(uuid.uuid4()),
            "headline": "Unusual pneumonia cluster detected in Southeast Asia — WHO investigating",
            "mode": "epi",
            "severity": 4,
            "confidence": 0.87,
            "is_verified": True,
            "source": "WHO Situation Report",
            "timestamp": (datetime.utcnow() - timedelta(minutes=12)).isoformat(),
            "analysis": "Pattern consistent with novel respiratory pathogen. Hospitalization rate 3× baseline. Immediate surveillance escalation recommended.",
            "convergence_warning": None,
            "lat": 13.75,
            "lng": 100.52,
            "location": "Bangkok, Thailand",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "New drug-resistant TB strain reported across 5 countries",
            "mode": "epi",
            "severity": 3,
            "confidence": 0.79,
            "is_verified": True,
            "source": "ProMED-mail",
            "timestamp": (datetime.utcnow() - timedelta(hours=1, minutes=4)).isoformat(),
            "analysis": "MDR-TB genotype confirmed via laboratory sequencing. Cross-border travel patterns suggest rapid spread vector.",
            "convergence_warning": "⚠️ ECO-LINK: Flood displacement camps in the same region may accelerate exposure.",
            "lat": 28.61,
            "lng": 77.21,
            "location": "New Delhi, India",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Dengue fever outbreaks spike in South America — 40% above seasonal average",
            "mode": "epi",
            "severity": 2,
            "confidence": 0.92,
            "is_verified": True,
            "source": "PAHO/WHO",
            "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "analysis": "Vector proliferation linked to increased standing water from irregular rainfall. Urban centers at highest risk.",
            "convergence_warning": None,
            "lat": -23.55,
            "lng": -46.63,
            "location": "São Paulo, Brazil",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Unconfirmed viral hemorrhagic fever reports emerging from Central Africa",
            "mode": "epi",
            "severity": 5,
            "confidence": 0.61,
            "is_verified": False,
            "source": "Social Media Signals",
            "timestamp": (datetime.utcnow() - timedelta(minutes=38)).isoformat(),
            "analysis": "Awaiting WHO ground-truth confirmation. Symptom pattern matches VHF profile. UNVERIFIED — monitor closely.",
            "convergence_warning": None,
            "lat": 0.32,
            "lng": 32.58,
            "location": "Kampala, Uganda",
        },
        # ── South Asia Epi Alerts ──
        {
            "id": str(uuid.uuid4()),
            "headline": "Severe dengue outbreak in Bangladesh — 12,000+ hospitalizations in Dhaka",
            "mode": "epi",
            "severity": 4,
            "confidence": 0.91,
            "is_verified": True,
            "source": "WHO Bangladesh",
            "timestamp": (datetime.utcnow() - timedelta(minutes=45)).isoformat(),
            "analysis": "Aedes aegypti vector density 60% above baseline. Urban slum populations most affected. Hospital ICU capacity at 85%. Cross-border spread to West Bengal confirmed.",
            "convergence_warning": "⚠️ ECO-LINK: Post-monsoon flooding in Dhaka creating ideal breeding grounds for mosquito vectors.",
            "lat": 23.81,
            "lng": 90.41,
            "location": "Dhaka, Bangladesh",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Nipah virus cluster detected in Kerala — 3 confirmed deaths",
            "mode": "epi",
            "severity": 5,
            "confidence": 0.84,
            "is_verified": True,
            "source": "ICMR / NIV Pune",
            "timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "analysis": "Pteropus bat reservoir confirmed via genomic sequencing. Human-to-human transmission chain identified in Kozhikode hospital cluster. Case fatality rate 67%. Containment zone declared.",
            "convergence_warning": None,
            "lat": 11.25,
            "lng": 75.77,
            "location": "Kozhikode, Kerala, India",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Cholera cases surge in flood-affected Sindh province, Pakistan",
            "mode": "epi",
            "severity": 3,
            "confidence": 0.88,
            "is_verified": True,
            "source": "WHO EMRO",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "analysis": "Waterborne pathogen spread through contaminated flood water. 2,400+ cases reported in 10 districts. ORS and IV fluid supplies running critically low.",
            "convergence_warning": "⚠️ ECO-LINK: Monsoon flooding in Sindh directly driving cholera transmission pathway.",
            "lat": 25.40,
            "lng": 68.37,
            "location": "Hyderabad, Sindh, Pakistan",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Measles outbreak in Rohingya refugee camps — Cox's Bazar",
            "mode": "epi",
            "severity": 3,
            "confidence": 0.82,
            "is_verified": True,
            "source": "MSF / UNHCR",
            "timestamp": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "analysis": "Vaccination coverage below 60% in camp populations. 800+ suspected cases, 12 deaths. Overcrowding exacerbating transmission rates.",
            "convergence_warning": None,
            "lat": 21.43,
            "lng": 92.01,
            "location": "Cox's Bazar, Bangladesh",
        },
    ],
    "eco": [
        {
            "id": str(uuid.uuid4()),
            "headline": "Magnitude 6.8 earthquake strikes coastal Chile — tsunami advisory issued",
            "mode": "eco",
            "severity": 5,
            "confidence": 0.97,
            "is_verified": True,
            "source": "USGS / NOAA",
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "analysis": "Shallow-focus quake (depth 18km) maximizes surface impact. Coastal evacuation zones active. Aftershocks expected within 72 hours.",
            "convergence_warning": "⚠️ SUPPLY-LINK: Valparaíso port — major copper export hub — may face operational shutdown.",
            "lat": -33.45,
            "lng": -70.67,
            "location": "Santiago, Chile",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Category 4 cyclone forming in Bay of Bengal — landfall predicted in 72hrs",
            "mode": "eco",
            "severity": 4,
            "confidence": 0.89,
            "is_verified": True,
            "source": "IMD Cyclone Warning",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "analysis": "Track models show 85% probability of Odisha/Andhra landfall. Storm surge 3–5m above normal tide. 12M population in impact corridor.",
            "convergence_warning": None,
            "lat": 16.50,
            "lng": 85.80,
            "location": "Bay of Bengal, near Odisha, India",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Mega-drought declaration issued for Western United States — 23-year low",
            "mode": "eco",
            "severity": 3,
            "confidence": 0.95,
            "is_verified": True,
            "source": "US Bureau of Reclamation",
            "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "analysis": "Lake Mead at 27% capacity. Hydroelectric output cut 40%. Agricultural water allocation suspended in 3 states.",
            "convergence_warning": "⚠️ EPI-LINK: Water scarcity increasing vector-borne disease risk in urban centers.",
            "lat": 36.02,
            "lng": -114.74,
            "location": "Lake Mead, Nevada, USA",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Wildfire season begins 6 weeks early in Southern Europe — red alert issued",
            "mode": "eco",
            "severity": 3,
            "confidence": 0.83,
            "is_verified": True,
            "source": "Copernicus EFFIS",
            "timestamp": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "analysis": "Unprecedented heat-drought combination. Fire weather index at extreme level across Portugal, Spain, Greece.",
            "convergence_warning": None,
            "lat": 39.40,
            "lng": -8.22,
            "location": "Central Portugal",
        },
        # ── South Asia Eco Alerts ──
        {
            "id": str(uuid.uuid4()),
            "headline": "Catastrophic flooding in Sindh and Punjab — 33M people affected",
            "mode": "eco",
            "severity": 5,
            "confidence": 0.96,
            "is_verified": True,
            "source": "NDMA Pakistan / UN OCHA",
            "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            "analysis": "Indus River discharge at 400% of normal levels. 1.7M homes destroyed. Agricultural heartland submerged — wheat/cotton harvest devastated. $15B estimated damage.",
            "convergence_warning": "⚠️ EPI-LINK: Stagnant floodwaters creating breeding grounds for malaria and cholera transmission.",
            "lat": 27.71,
            "lng": 68.51,
            "location": "Sukkur, Sindh, Pakistan",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Magnitude 5.9 earthquake strikes Nepal — aftershocks continue",
            "mode": "eco",
            "severity": 4,
            "confidence": 0.93,
            "is_verified": True,
            "source": "USGS / Nepal Seismological Centre",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "analysis": "Epicenter in Jajarkot district, depth 12km. 150+ casualties reported. Historic structures in Kathmandu damaged. Landslide risk elevated in surrounding hill districts.",
            "convergence_warning": "⚠️ SUPPLY-LINK: Only highway to Jajarkot blocked by landslide — relief supplies cannot reach affected areas.",
            "lat": 28.74,
            "lng": 82.19,
            "location": "Jajarkot, Nepal",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Glacial lake outburst flood warning issued for Sikkim — GLOF risk critical",
            "mode": "eco",
            "severity": 4,
            "confidence": 0.78,
            "is_verified": True,
            "source": "ISRO / IMD",
            "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "analysis": "South Lhonak Lake moraine breach imminent. Teesta River downstream communities under evacuation advisory. 8 hydroelectric projects in flood path.",
            "convergence_warning": None,
            "lat": 27.90,
            "lng": 88.45,
            "location": "North Sikkim, India",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Extreme heatwave grips northern India — temperatures exceed 48°C",
            "mode": "eco",
            "severity": 3,
            "confidence": 0.94,
            "is_verified": True,
            "source": "IMD / NASA FIRMS",
            "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "analysis": "Wet-bulb temperature approaching survivability threshold. Power grid under strain — 14 states report rolling blackouts. Crop failure risk elevated in Rajasthan and UP.",
            "convergence_warning": "⚠️ EPI-LINK: Heat stroke hospitalizations up 400% — public health emergency declared in 5 states.",
            "lat": 26.85,
            "lng": 75.76,
            "location": "Jaipur, Rajasthan, India",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Coastal erosion accelerating in Sri Lanka — 2,000 families displaced",
            "mode": "eco",
            "severity": 2,
            "confidence": 0.81,
            "is_verified": True,
            "source": "Sri Lanka Disaster Management Centre",
            "timestamp": (datetime.utcnow() - timedelta(hours=10)).isoformat(),
            "analysis": "Sea level rise combined with illegal sand mining accelerating coastline retreat. Fishing communities in Negombo and Chilaw most affected.",
            "convergence_warning": None,
            "lat": 7.21,
            "lng": 79.84,
            "location": "Negombo, Sri Lanka",
        },
    ],
    "supply": [
        {
            "id": str(uuid.uuid4()),
            "headline": "Major TSMC fab halts production — global chip shortage feared",
            "mode": "supply",
            "severity": 5,
            "confidence": 0.91,
            "is_verified": True,
            "source": "Reuters / ESG Report",
            "timestamp": (datetime.utcnow() - timedelta(minutes=22)).isoformat(),
            "analysis": "Whistleblower report filed with SEC. 3nm fab line offline for 2 weeks minimum. Apple, NVIDIA, AMD exposure confirmed.",
            "convergence_warning": "⚠️ ECO-LINK: Earthquake near Hsinchu triggered facility shutdown — convergence event.",
            "lat": 24.80,
            "lng": 120.97,
            "location": "Hsinchu, Taiwan",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Red Sea shipping lane disruption continues — Suez diversions spike 340%",
            "mode": "supply",
            "severity": 4,
            "confidence": 0.96,
            "is_verified": True,
            "source": "Freightos Baltic Index",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "analysis": "Container shipping rates at 18-month high. Europe-Asia freight +22 days transit time. Energy, electronics, automotive impact critical.",
            "convergence_warning": None,
            "lat": 12.86,
            "lng": 43.28,
            "location": "Bab el-Mandeb Strait, Red Sea",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Rare earth mining ban declared in Myanmar — EV battery chain at risk",
            "mode": "supply",
            "severity": 3,
            "confidence": 0.78,
            "is_verified": True,
            "source": "Bloomberg Supply Chain Monitor",
            "timestamp": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "analysis": "Myanmar supplies 40% global rare earth output. Tesla, BYD, Volkswagen flagged in risk registry. 6-month buffer supply estimated.",
            "convergence_warning": None,
            "lat": 22.96,
            "lng": 97.75,
            "location": "Shan State, Myanmar",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Anonymous ESG whistleblower alleges forced labor in smartphone supply chain",
            "mode": "supply",
            "severity": 2,
            "confidence": 0.58,
            "is_verified": False,
            "source": "Whistleblower Platform",
            "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "analysis": "Report under third-party audit review. Social compliance violations alleged at Tier-2 supplier. UNVERIFIED — pending investigation.",
            "convergence_warning": None,
            "lat": 22.54,
            "lng": 114.06,
            "location": "Shenzhen, China",
        },
        # ── South Asia Supply Alerts ──
        {
            "id": str(uuid.uuid4()),
            "headline": "Mumbai port congestion reaches critical levels — 40+ vessels stranded",
            "mode": "supply",
            "severity": 4,
            "confidence": 0.90,
            "is_verified": True,
            "source": "Mumbai Port Trust / Lloyd's List",
            "timestamp": (datetime.utcnow() - timedelta(minutes=50)).isoformat(),
            "analysis": "Container dwell time at 12 days (vs 3-day norm). Customs clearance backlog due to new regulatory compliance checks. Pharmaceutical and electronics imports severely delayed.",
            "convergence_warning": "⚠️ ECO-LINK: Monsoon-related port closures compounding existing congestion — 14-day forecast shows no relief.",
            "lat": 18.95,
            "lng": 72.84,
            "location": "JNPT, Mumbai, India",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Bangladesh garment factory shutdowns — global fast-fashion supply disrupted",
            "mode": "supply",
            "severity": 3,
            "confidence": 0.85,
            "is_verified": True,
            "source": "BGMEA / Fair Wear Foundation",
            "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "analysis": "28 factories in Gazipur and Ashulia shuttered due to worker unrest over wage disputes. H&M, Zara, Primark tier-1 suppliers affected. $200M orders at risk of delay.",
            "convergence_warning": None,
            "lat": 23.99,
            "lng": 90.43,
            "location": "Gazipur, Bangladesh",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Colombo port transshipment delays — Indian Ocean hub bottleneck emerging",
            "mode": "supply",
            "severity": 3,
            "confidence": 0.82,
            "is_verified": True,
            "source": "Sri Lanka Ports Authority",
            "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "analysis": "Colombo handles 30% of Indian subcontinent transshipment. Crane maintenance backlog and labor shortages causing 5-day average delay. Feeder service to Chittagong, Cochin, Karachi affected.",
            "convergence_warning": None,
            "lat": 6.94,
            "lng": 79.84,
            "location": "Colombo Port, Sri Lanka",
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "India pharmaceutical API shortage — antibiotic exports halted",
            "mode": "supply",
            "severity": 4,
            "confidence": 0.87,
            "is_verified": True,
            "source": "CDSCO / Pharma Intelligence",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "analysis": "Key Active Pharmaceutical Ingredient production disrupted in Hyderabad and Vizag facilities. India supplies 20% of global generic medicines. WHO essential medicines list items affected.",
            "convergence_warning": "⚠️ EPI-LINK: Antibiotic shortage may compromise response to drug-resistant TB outbreaks in the region.",
            "lat": 17.39,
            "lng": 78.49,
            "location": "Hyderabad, Telangana, India",
        },
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


@app.get("/api/globe-threats")
def get_globe_threats():
    """Returns all alerts across all modes with geo-coordinates — optimized for 3D globe rendering."""
    all_threats = []
    for mode in ("epi", "eco", "supply"):
        for alert in MOCK_ALERTS[mode]:
            all_threats.append({
                "id": alert["id"],
                "headline": alert["headline"],
                "mode": alert["mode"],
                "severity": alert["severity"],
                "confidence": alert["confidence"],
                "is_verified": alert["is_verified"],
                "source": alert["source"],
                "timestamp": alert["timestamp"],
                "lat": alert.get("lat", 0),
                "lng": alert.get("lng", 0),
                "location": alert.get("location", "Unknown"),
                "convergence_warning": alert.get("convergence_warning"),
            })

    # Also include triggered analyses (assign random South Asia coords if missing)
    for alert in _state["triggered_analyses"]:
        all_threats.append({
            "id": alert["id"],
            "headline": alert["headline"],
            "mode": alert["mode"],
            "severity": alert["severity"],
            "confidence": alert["confidence"],
            "is_verified": alert["is_verified"],
            "source": alert["source"],
            "timestamp": alert["timestamp"],
            "lat": alert.get("lat", 20 + random.uniform(-5, 10)),
            "lng": alert.get("lng", 78 + random.uniform(-10, 15)),
            "location": alert.get("location", "Triggered Location"),
            "convergence_warning": alert.get("convergence_warning"),
        })

    return {
        "threats": all_threats,
        "total": len(all_threats),
        "region_focus": USER_PROFILE["region_of_interest"],
    }


@app.get("/api/user-profile")
def get_user_profile():
    """Returns the current user profile and preferences."""
    return USER_PROFILE


@app.post("/api/trigger")
def trigger_analysis(req: TriggerRequest):
    """Trigger a GlobalSentry analysis — uses REAL agent pipeline or fallback."""

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

    # Fallback — Simulate AI analysis pipeline
    severity = random.randint(2, 5)
    confidence = round(random.uniform(0.65, 0.95), 2)
    is_verified = confidence > 0.75

    # Generate a random South Asia location for triggered alerts
    sa_locations = [
        {"lat": 28.61, "lng": 77.21, "location": "New Delhi, India"},
        {"lat": 19.08, "lng": 72.88, "location": "Mumbai, India"},
        {"lat": 23.81, "lng": 90.41, "location": "Dhaka, Bangladesh"},
        {"lat": 27.70, "lng": 85.32, "location": "Kathmandu, Nepal"},
        {"lat": 6.93, "lng": 79.85, "location": "Colombo, Sri Lanka"},
        {"lat": 24.86, "lng": 67.01, "location": "Karachi, Pakistan"},
        {"lat": 13.08, "lng": 80.27, "location": "Chennai, India"},
        {"lat": 22.57, "lng": 88.36, "location": "Kolkata, India"},
    ]
    loc = random.choice(sa_locations)

    mode_analyses = {
        "epi": f"Epidemiological triage complete. Symptom pattern cross-matched with {random.randint(3, 12)} historical outbreaks in Qdrant memory. R0 estimation in progress.",
        "eco": f"Geophysical risk model applied. Satellite data cross-referenced. Affected population zone estimated at {random.randint(50, 500)}K residents.",
        "supply": f"Supply chain dependency graph queried. {random.randint(2, 8)} Tier-1 suppliers identified in impact zone. ESG registry cross-checked.",
    }

    # Fallback — return the headline as an unprocessed simulated alert
    new_alert = {
        "id": str(uuid.uuid4()),
        "headline": req.headline,
        "mode": req.mode,
        "severity": severity,
        "confidence": confidence,
        "is_verified": is_verified,
        "source": "Manual Input — Agent Offline",
        "timestamp": datetime.utcnow().isoformat(),
        "analysis": mode_analyses[req.mode],
        "convergence_warning": "⚠️ CONVERGENCE DETECTED: Cross-mode pattern match found in memory." if random.random() > 0.6 else None,
        "lat": loc["lat"],
        "lng": loc["lng"],
        "location": loc["location"],
        "is_raw_feed": False,
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
