"""
GlobalSentry - FastAPI Backend
Serves mock + real alert data to the frontend dashboard.
Run with: uvicorn api:app --reload --port 8000
"""

import os
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(
    title="GlobalSentry API",
    description="Intelligence Platform API — Epi, Eco, Supply Sentry Modes",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

# Allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        },
        {
            "id": str(uuid.uuid4()),
            "headline": "Category 4 cyclone forming in Bay of Bengal — landfall predicted in 72hrs",
            "mode": "eco",
            "severity": 4,
            "confidence": 0.89,
            "is_verified": True,
            "source": "IMD Cyclone Warning",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "analysis": "Track models show 85% probability of Odisha/Andhra landfall. Storm surge 3–5m above normal tide. 12M population in impact corridor.",
            "convergence_warning": None,
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
        },
    ],
}

# Runtime state
_state = {
    "active_mode": "eco",
    "last_poll": datetime.utcnow().isoformat(),
    "feed_health": {"epi": "OK", "eco": "OK", "supply": "OK"},
    "triggered_analyses": [],
}

# ─── Models ───────────────────────────────────────────────────────────────────

class TriggerRequest(BaseModel):
    headline: str
    mode: Literal["epi", "eco", "supply"] = "eco"

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api")
@app.get("/api/")
def root():
    return {"message": "GlobalSentry API is live", "docs": "/api/docs"}


@app.get("/api/alerts")
def get_alerts(mode: Optional[str] = None, limit: int = 10):
    """Returns last N alerts — optionally filtered by mode."""
    if mode and mode not in ("epi", "eco", "supply"):
        raise HTTPException(status_code=400, detail="Invalid mode. Use: epi, eco, supply")

    if mode:
        alerts = MOCK_ALERTS.get(mode, [])
    else:
        alerts = []
        for m in ("epi", "eco", "supply"):
            alerts.extend(MOCK_ALERTS[m])
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)

    # Also include any triggered analyses
    triggered = [a for a in _state["triggered_analyses"] if not mode or a["mode"] == mode]
    result = triggered + alerts
    return {"alerts": result[:limit], "total": len(result), "mode_filter": mode}


@app.post("/api/trigger")
def trigger_analysis(req: TriggerRequest):
    """Manually trigger a sentry run with a custom headline."""
    
    # Simulate AI analysis pipeline
    severity = random.randint(2, 5)
    confidence = round(random.uniform(0.65, 0.95), 2)
    is_verified = confidence > 0.75

    mode_analyses = {
        "epi": f"Epidemiological triage complete. Symptom pattern cross-matched with {random.randint(3, 12)} historical outbreaks in Qdrant memory. R0 estimation in progress.",
        "eco": f"Geophysical risk model applied. Satellite data cross-referenced. Affected population zone estimated at {random.randint(50, 500)}K residents.",
        "supply": f"Supply chain dependency graph queried. {random.randint(2, 8)} Tier-1 suppliers identified in impact zone. ESG registry cross-checked.",
    }

    new_alert = {
        "id": str(uuid.uuid4()),
        "headline": req.headline,
        "mode": req.mode,
        "severity": severity,
        "confidence": confidence,
        "is_verified": is_verified,
        "source": "Live Demo — Manual Trigger",
        "timestamp": datetime.utcnow().isoformat(),
        "analysis": mode_analyses[req.mode],
        "convergence_warning": "⚠️ CONVERGENCE DETECTED: Cross-mode pattern match found in memory." if random.random() > 0.6 else None,
    }

    _state["triggered_analyses"].insert(0, new_alert)
    _state["last_poll"] = datetime.utcnow().isoformat()

    return {
        "status": "analysis_complete",
        "alert": new_alert,
        "pipeline_steps": [
            {"node": "Ingest & Profiler", "status": "done", "ms": random.randint(120, 300)},
            {"node": "Retriever (RAG)", "status": "done", "ms": random.randint(200, 600)},
            {"node": "Agent A — Triage", "status": "done", "ms": random.randint(80, 200)},
            {"node": "Agent B — Analyst", "status": "done", "ms": random.randint(400, 1200)},
            {"node": "Agent C — Validator", "status": "done", "ms": random.randint(300, 800)},
            {"node": "Notify & Archive", "status": "done", "ms": random.randint(50, 150)},
        ],
    }


@app.get("/api/status")
def get_status():
    """Returns system status — current mode, feed health, last poll time."""
    return {
        "active_mode": _state["active_mode"],
        "last_poll": _state["last_poll"],
        "feed_health": _state["feed_health"],
        "alerts_in_memory": {
            "epi": len(MOCK_ALERTS["epi"]) + len([a for a in _state["triggered_analyses"] if a["mode"] == "epi"]),
            "eco": len(MOCK_ALERTS["eco"]) + len([a for a in _state["triggered_analyses"] if a["mode"] == "eco"]),
            "supply": len(MOCK_ALERTS["supply"]) + len([a for a in _state["triggered_analyses"] if a["mode"] == "supply"]),
        },
        "uptime_pct": 99.7,
        "version": "1.0.0",
    }


@app.put("/api/mode/{mode}")
def switch_mode(mode: str):
    """Switch the active sentry monitoring mode."""
    if mode not in ("epi", "eco", "supply"):
        raise HTTPException(status_code=400, detail="Invalid mode")
    _state["active_mode"] = mode
    return {"active_mode": mode, "switched_at": datetime.utcnow().isoformat()}


# ─── Serve Frontend (MUST be last) ────────────────────────────────────────────
# Mount the frontend directory at root so http://localhost:8000/ serves index.html
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
