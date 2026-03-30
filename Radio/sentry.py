import os
import requests
import uuid
import json
import re
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import SentenceTransformerEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, Filter, FieldCondition, MatchValue
)
from dotenv import load_dotenv

load_dotenv(override=True)

# ─── Infrastructure ────────────────────────────────────────────────────────

OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Agent A — Triage (speed matters, same model)
triage_llm  = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
# Agent B — Analyst (depth matters)
analyst_llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

# Local embeddings — no API key required
embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

print(f"[GlobalSentry] Ollama model : {OLLAMA_MODEL} @ {OLLAMA_BASE_URL}")
print(f"[GlobalSentry] Embeddings   : {EMBEDDING_MODEL}")

# ─── DuckDuckGo Search ────────────────────────────────────────────────────

from duckduckgo_search import DDGS

def search_tool_run(query: str) -> str:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(f"{r['title']}: {r['body']}")
    except Exception as e:
        return f"Search failed: {e}"
    return "\n".join(results)

# ─── Qdrant (Local Vector DB) — Lazy Singleton ───────────────────────────
#
# With uvicorn --reload, the module is re-imported in a NEW process before
# the old one fully shuts down. Qdrant's local storage uses an exclusive
# file lock, so eager initialization causes a "database already in use"
# conflict. By deferring init to first use, we avoid the race entirely.

QDRANT_PATH     = "./qdrant_data"
COLLECTION_NAME = "global_sentry_memory"
VECTOR_SIZE     = 384           # all-MiniLM-L6-v2 dimension

_qdrant_client = None  # lazy singleton

def get_qdrant_client() -> QdrantClient:
    """Returns a lazily-initialized QdrantClient singleton."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path=QDRANT_PATH)
        collections = _qdrant_client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            _qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            print(f"[GlobalSentry] Initialized Qdrant collection: {COLLECTION_NAME}")
        else:
            print(f"[GlobalSentry] Qdrant collection '{COLLECTION_NAME}' ready.")
    return _qdrant_client

# ─── Mode-Aware Prompts ───────────────────────────────────────────────────

TRIAGE_PROMPTS = {
    "epi": (
        "Is this news about a disease outbreak, epidemic, virus spread, "
        "or public health emergency? Respond ONLY with YES or NO."
    ),
    "eco": (
        "Is this news about climate disaster, extreme weather, flood, earthquake, "
        "wildfire, or ecological collapse? Respond ONLY with YES or NO."
    ),
    "supply": (
        "Is this news about supply chain disruption, logistics failure, ESG violation, "
        "corporate fraud, or critical resource shortage? Respond ONLY with YES or NO."
    ),
    "general": (
        "Is this news a potential PHYSICAL threat to life, safety, or societal stability? "
        "Respond ONLY with YES or NO."
    ),
}

ANALYST_PROMPTS = {
    "epi": (
        "ROLE: WHO Epidemiologist & Public Health Expert\n"
        "Analyze the following event for epidemic risk:\n"
        "1. Pathogen type and transmission potential.\n"
        "2. Affected region and population vulnerability.\n"
        "3. Containment and public health action recommendations.\n"
        "End your response with EXACTLY this line:\nSEVERITY: <1-5> | CONFIDENCE: <0.0-1.0>"
    ),
    "eco": (
        "ROLE: Senior Climate Scientist & Disaster Risk Analyst\n"
        "Analyze the following event for ecological and climate risk:\n"
        "1. Event severity and geographic scope.\n"
        "2. Secondary risks (e.g., flood → disease, wildfire → air quality).\n"
        "3. Immediate safety and evacuation recommendations.\n"
        "End your response with EXACTLY this line:\nSEVERITY: <1-5> | CONFIDENCE: <0.0-1.0>"
    ),
    "supply": (
        "ROLE: Global Supply Chain Auditor & ESG Analyst\n"
        "Analyze the following event for supply chain and economic risk:\n"
        "1. Affected commodities, regions, or industries.\n"
        "2. Downstream cascading effects (shortages, price spikes).\n"
        "3. Recommended monitoring and mitigation actions.\n"
        "End your response with EXACTLY this line:\nSEVERITY: <1-5> | CONFIDENCE: <0.0-1.0>"
    ),
    "general": (
        "ROLE: Senior Crisis & Safety Analyst\n"
        "Perform a Life-Safety Risk Assessment:\n"
        "1. How this event impacts safety given historical context.\n"
        "2. Identify high-risk zones and potential escalation.\n"
        "3. Immediate safety recommendations.\n"
        "End your response with EXACTLY this line:\nSEVERITY: <1-5> | CONFIDENCE: <0.0-1.0>"
    ),
}

# Cross-mode correlation threshold (cosine similarity, 0–1)
CORRELATION_THRESHOLD = float(os.getenv("CORRELATION_THRESHOLD", "0.75"))

# ─── Agent State ──────────────────────────────────────────────────────────

class AgentState(TypedDict):
    news_item:            str
    sentry_mode:          str            # "epi" | "eco" | "supply" | "general"
    is_threat:            bool
    threat_analysis:      str
    severity_level:       int            # 1–5
    confidence_score:     float          # 0.0–1.0
    convergence_warning:  str            # Cross-mode correlation result (Neural Moat)
    verification_results: str
    is_verified:          bool
    relevance_score:      float
    retry_count:          int            # Reflection loop counter (max 1 retry)
    context:              List[str]
    logs:                 List[str]

# ─── Helpers ──────────────────────────────────────────────────────────────

def parse_float(text: str, default: float = 0.5) -> float:
    match = re.search(r'\d+\.?\d*', text)
    return float(match.group()) if match else default

def parse_severity_confidence(analysis: str):
    severity, confidence = 3, 0.5
    match = re.search(r'SEVERITY:\s*(\d)\s*\|\s*CONFIDENCE:\s*([\d.]+)', analysis)
    if match:
        severity   = int(match.group(1))
        confidence = float(match.group(2))
    return severity, confidence

# ─── Nodes ────────────────────────────────────────────────────────────────

def profiler_node(state: AgentState):
    """Calculates relevance of the event to the stakeholder profile."""
    news  = state['news_item']
    mode  = state.get('sentry_mode', 'general')
    logs  = state.get('logs', []) + [f"Profiler: Evaluating relevance (mode={mode})..."]
    profile_path = os.getenv("USER_PROFILE_PATH", "user_profile.json")

    profile_data = {}
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)

    relevance_score = 0.5
    try:
        prompt = (
            f"STAKEHOLDER PROFILE: {json.dumps(profile_data)}\n"
            f"SENTRY MODE: {mode}\n"
            f"NEWS ITEM: {news}\n\n"
            f"On a scale of 0.0 to 1.0, how relevant is this news to this stakeholder "
            f"given their region, role, and sentry mode? Respond ONLY with the number."
        )
        response = triage_llm.invoke(prompt).content.strip()
        relevance_score = parse_float(response, default=0.5)
        logs[-1] += f" Score={relevance_score:.2f}"
    except Exception as e:
        logs[-1] += f" Failed: {e}. Default=0.5"

    return {"relevance_score": relevance_score, "logs": logs}


def triage_node(state: AgentState):
    """Agent A — Fast, mode-aware threat classifier."""
    news  = state['news_item']
    mode  = state.get('sentry_mode', 'general')
    prompt = f"{TRIAGE_PROMPTS.get(mode, TRIAGE_PROMPTS['general'])}\nNEWS: '{news}'"
    is_threat = False
    logs_msg  = ""

    try:
        response  = triage_llm.invoke(prompt).content.strip().upper()
        is_threat = "YES" in response
        logs_msg  = f"Triage [{mode}]: {'Threat detected' if is_threat else 'No threat'}"
    except Exception as e:
        fallback_words = ["danger", "warning", "outbreak", "disaster", "shortage", "flood",
                          "earthquake", "epidemic", "crisis", "collapse"]
        is_threat = any(w in news.lower() for w in fallback_words)
        logs_msg  = f"Triage [{mode}]: (Fallback) Threat={'Yes' if is_threat else 'No'} — {e}"

    print(f"[Triage] {logs_msg}")
    return {"is_threat": is_threat, "logs": state.get('logs', []) + [logs_msg]}


def retriever_node(state: AgentState):
    """Fetches same-mode historical context from Qdrant for RAG."""
    news  = state['news_item']
    mode  = state.get('sentry_mode', 'general')
    logs  = state.get('logs', []) + [f"Retriever: Searching {mode} memory..."]
    context = []

    try:
        # Filter for events of the SAME mode to maintain domain coherence
        mode_filter = Filter(
            must=[FieldCondition(key="mode", match=MatchValue(value=mode))]
        )
        vectorstore = Qdrant(client=get_qdrant_client(), collection_name=COLLECTION_NAME, embeddings=embeddings)
        docs = vectorstore.similarity_search(news, k=3, filter=mode_filter)
        context = [doc.page_content for doc in docs]
        logs[-1] += f" Found {len(context)} item(s)."
    except Exception as e:
        logs[-1] += f" Search failed: {e}"

    return {"context": context, "logs": logs}


def analyst_node(state: AgentState):
    """Agent B — Deep domain expert analysis with structured severity/confidence output.
    On retry (reflection loop), it receives the validator's search results as new context.
    """
    news          = state['news_item']
    mode          = state.get('sentry_mode', 'general')
    context_str   = "\n".join(state.get('context', [])) or "No historical context available."
    retry_count   = state.get('retry_count', 0)
    verification  = state.get('verification_results', '')
    analysis      = ""

    role_prompt = ANALYST_PROMPTS.get(mode, ANALYST_PROMPTS['general'])

    # On reflection retry, inject the validator's search results so the analyst
    # can reconsider its conclusion with real-world evidence.
    reflection_block = ""
    if retry_count > 0 and verification:
        reflection_block = (
            f"\n⚠️ REFLECTION PASS {retry_count}: Your previous analysis was flagged as UNVERIFIED.\n"
            f"The following real-world search results were found by the Validator:\n"
            f"{verification}\n\n"
            f"Revise your analysis accordingly. If the evidence contradicts the threat, "
            f"lower severity. If it supports it, maintain or raise severity.\n"
        )

    prompt = (
        f"{role_prompt}\n\n"
        f"HISTORICAL CONTEXT:\n{context_str}\n"
        f"{reflection_block}\n"
        f"EVENT:\n{news}"
    )
    try:
        analysis = analyst_llm.invoke(prompt).content
    except Exception as e:
        analysis = (
            f"Analyst fallback: Could not complete analysis. Error: {e}\n"
            f"SEVERITY: 3 | CONFIDENCE: 0.4"
        )

    severity, confidence = parse_severity_confidence(analysis)
    pass_label = f"(Reflection #{retry_count})" if retry_count > 0 else ""
    print(f"[Analyst] {pass_label} Severity={severity} Confidence={confidence:.2f}")
    return {
        "threat_analysis":  analysis,
        "severity_level":   severity,
        "confidence_score": confidence,
        "logs": state.get('logs', []) + [f"Analyst [{mode}]{pass_label}: Severity={severity} Confidence={confidence:.2f}"],
    }


def correlator_node(state: AgentState):
    """
    🧠 THE NEURAL MOAT — Cross-mode threat correlator.

    Queries Qdrant for events from OTHER sentry modes that are semantically
    similar to the current event. If found, the analyst synthesises a
    CONVERGENCE WARNING — the core differentiator of GlobalSentry.
    """
    news    = state['news_item']
    mode    = state.get('sentry_mode', 'general')
    logs    = state.get('logs', []) + ["Correlator: Scanning cross-mode memory..."]
    convergence_warning = ""

    try:
        # Embed the current news item
        query_vector = embeddings.embed_query(news)

        # Search for semantically similar events from OTHER modes only
        cross_mode_filter = Filter(
            must_not=[FieldCondition(key="mode", match=MatchValue(value=mode))]
        )
        cross_results = get_qdrant_client().search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=3,
            query_filter=cross_mode_filter,
            score_threshold=CORRELATION_THRESHOLD,
            with_payload=True,
        )

        if cross_results:
            correlated_events = []
            for r in cross_results:
                payload = r.payload or {}
                correlated_events.append(
                    f"[{payload.get('mode','?').upper()}-SENTRY | "
                    f"Score={r.score:.2f}] {payload.get('text', str(payload))}"
                )

            crossed_modes = list({(r.payload or {}).get('mode', '?') for r in cross_results})
            logs[-1] += f" ⚠️ Convergence detected with {crossed_modes}!"

            # Ask the analyst to synthesise the cross-domain risk
            convergence_prompt = (
                f"ROLE: GlobalSentry Cross-Domain Risk Synthesiser\n\n"
                f"A new [{mode.upper()}-SENTRY] event has been detected:\n"
                f"  EVENT: {news}\n\n"
                f"The following CORRELATED events from OTHER domains are in our historical memory:\n"
                + "\n".join(correlated_events)
                + "\n\n"
                f"TASK: In 3-4 sentences, explain how these events are linked and what "
                f"cascading risk they represent together (e.g., flood → cholera → supply shortage). "
                f"Be specific and alarming if warranted. Start with '⚠️ CONVERGENCE WARNING:'."
            )
            try:
                convergence_warning = analyst_llm.invoke(convergence_prompt).content.strip()
            except Exception as e:
                convergence_warning = (
                    f"⚠️ CONVERGENCE WARNING: Cross-mode correlation detected with "
                    f"{crossed_modes} events, but synthesis failed: {e}"
                )
        else:
            logs[-1] += " No cross-mode correlations found."

    except Exception as e:
        logs[-1] += f" Correlator error: {e}"

    print(f"[Correlator] {'⚠️ Convergence found!' if convergence_warning else 'No convergence.'}")
    return {"convergence_warning": convergence_warning, "logs": logs}


def validator_node(state: AgentState):
    """Agent C — Verifies the threat claim with a live DuckDuckGo web search."""
    news       = state['news_item']
    is_verified = False

    print("[Validator] Searching for secondary sources...")
    try:
        verification_results = search_tool_run(f"Verify recent news: {news}")

        if len(verification_results) > 20:
            prompt = (
                f"Compare this news: '{news}'\n"
                f"With these search results:\n'{verification_results}'\n"
                f"Is the news claim supported by secondary sources? "
                f"Respond ONLY with VERIFIED or UNVERIFIED."
            )
            resp = analyst_llm.invoke(prompt).content.upper()
            is_verified = "VERIFIED" in resp
        else:
            is_verified = len(verification_results) > 50
    except Exception as e:
        print(f"[Validator] Error: {e}")
        verification_results = "Search failed."
        is_verified = True   # warn user anyway

    print(f"[Validator] Verified: {is_verified}")
    return {
        "is_verified":         is_verified,
        "verification_results": verification_results,
        "logs": state.get('logs', []) + [f"Validator: Verified={is_verified}"],
    }


def notify_node(state: AgentState):
    """Stores the alert in a shared JSON file (alerts.json) so the web dashboard displays it.
    Also prints a formatted summary to the console.
    """
    mode = state.get('sentry_mode', 'general')
    mode_icons   = {"epi": "🩺", "eco": "🌪️", "supply": "♻️", "general": "🚨"}
    severity_bars = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🔴🔴"}

    icon       = mode_icons.get(mode, "🚨")
    severity   = state.get('severity_level', 3)
    confidence = state.get('confidence_score', 0.5)
    bar        = severity_bars.get(severity, "🔴")
    convergence = state.get('convergence_warning', '')

    # Build the alert object for the web dashboard
    import json as _json
    from datetime import datetime as _dt

    alert_obj = {
        "id": str(uuid.uuid4()),
        "headline": state['news_item'],
        "mode": mode,
        "severity": severity,
        "confidence": round(confidence, 2),
        "is_verified": state.get('is_verified', False),
        "source": "Live Agent Pipeline",
        "timestamp": _dt.utcnow().isoformat(),
        "analysis": state.get('threat_analysis', '')[:800],
        "convergence_warning": convergence if convergence else None,
    }

    # Append to alerts.json (shared with the web API)
    alerts_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alerts.json")
    try:
        existing = []
        if os.path.exists(alerts_file):
            with open(alerts_file, "r", encoding="utf-8") as f:
                existing = _json.load(f)
        existing.insert(0, alert_obj)
        # Keep last 1000 alerts
        existing = existing[:1000]
        with open(alerts_file, "w", encoding="utf-8") as f:
            _json.dump(existing, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Notify] Failed to write alerts.json: {e}")

    # Console summary
    msg = (
        f"\n{icon} GLOBALSENTRY ALERT {icon}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Mode     : {mode.upper()}-SENTRY\n"
        f"Severity : {bar} {severity}/5\n"
        f"Confidence: {confidence:.0%}\n\n"
        f"📰 EVENT:\n{state['news_item']}\n\n"
        f"🔍 ANALYSIS:\n{state['threat_analysis'][:300]}...\n"
    )
    if convergence:
        msg += f"\n{convergence[:300]}\n"

    print(f"[Notify] Alert saved to alerts.json → visible on web dashboard")
    print(msg)

    return {"logs": state.get('logs', []) + ["Alert saved to web dashboard."]}


def archiver_node(state: AgentState):
    """Stores the event in Qdrant with mode + severity metadata for future RAG and correlation."""
    news     = state['news_item']
    mode     = state.get('sentry_mode', 'general')
    severity = state.get('severity_level', 0)
    logs     = state.get('logs', []) + [f"Archiver: Storing [{mode}] event..."]

    try:
        vectorstore = Qdrant(
            client=get_qdrant_client(),
            collection_name=COLLECTION_NAME,
            embeddings=embeddings
        )
        vectorstore.add_texts(
            texts=[news],
            metadatas=[{"mode": mode, "severity": severity, "text": news}],
            ids=[str(uuid.uuid4())]
        )
        logs[-1] += " Stored."
    except Exception as e:
        logs[-1] += f" Storage failed: {e}"

    return {"logs": logs}

# ─── Router functions ─────────────────────────────────────────────────────

def decide_to_analyze(state: AgentState) -> Literal["analyze", "end"]:
    """Proceed only if flagged as a threat AND relevant to the stakeholder."""
    relevance  = state.get('relevance_score', 0.5)
    threshold  = float(os.getenv("ALERT_THRESHOLD", "0.15"))
    if state['is_threat'] and relevance >= threshold:
        return "analyze"
    return "end"


MAX_RETRIES = 1  # How many times the analyst can reflect before giving up

def decide_to_notify(state: AgentState) -> Literal["notify", "reflect", "end"]:
    """3-way router after validation:
    - verified         → notify the stakeholder
    - unverified + retries left → reflect (send back to analyst with new context)
    - unverified + no retries  → end (archive silently)
    """
    if state['is_verified']:
        return "notify"
    retry_count = state.get('retry_count', 0)
    if retry_count < MAX_RETRIES:
        print(f"[Router] Unverified. Sending back to analyst for reflection (retry {retry_count + 1}/{MAX_RETRIES})...")
        return "reflect"
    print("[Router] Unverified after max retries. Archiving silently.")
    return "end"

# ─── Build the LangGraph ──────────────────────────────────────────────────

workflow = StateGraph(AgentState)

workflow.add_node("profiler",    profiler_node)
workflow.add_node("triage",      triage_node)
workflow.add_node("retriever",   retriever_node)
workflow.add_node("analyst",     analyst_node)
workflow.add_node("correlator",  correlator_node)   # 🧠 Neural Moat
workflow.add_node("validator",   validator_node)
workflow.add_node("notify",      notify_node)
workflow.add_node("archiver",    archiver_node)

workflow.set_entry_point("profiler")

workflow.add_edge("profiler", "triage")

workflow.add_conditional_edges(
    "triage",
    decide_to_analyze,
    {"analyze": "retriever", "end": "archiver"}
)

workflow.add_edge("retriever",  "analyst")
workflow.add_edge("analyst",    "correlator")   # analyst → correlator (Neural Moat)
workflow.add_edge("correlator", "validator")    # correlator → validator

# Reflection loop: validator can send control back to analyst
def increment_retry(state: AgentState):
    """Bumps retry_count before re-entering the analyst."""
    return {"retry_count": state.get('retry_count', 0) + 1}

workflow.add_node("retry_counter", increment_retry)

workflow.add_conditional_edges(
    "validator",
    decide_to_notify,
    {"notify": "notify", "reflect": "retry_counter", "end": "archiver"}
)

# retry_counter → analyst (closes the reflection loop)
workflow.add_edge("retry_counter", "analyst")

workflow.add_edge("notify",   "archiver")
workflow.add_edge("archiver", END)

global_sentry_app = workflow.compile()

# Backward compatibility alias
sentry_app = global_sentry_app

# ─── Quick test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_state = {
        "news_item":            "Cholera outbreak spreading in flood-hit Bangladesh district",
        "sentry_mode":          "epi",
        "is_threat":            False,
        "threat_analysis":      "",
        "severity_level":       0,
        "confidence_score":     0.0,
        "convergence_warning":  "",
        "verification_results": "",
        "is_verified":          False,
        "relevance_score":      0.0,
        "context":              [],
        "logs":                 [],
    }
    result = global_sentry_app.invoke(test_state)
    print("\n─── Final Logs ───")
    for log in result['logs']:
        print(f"  {log}")
    if result.get('convergence_warning'):
        print(f"\n{result['convergence_warning']}")
