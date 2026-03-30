import os
import requests
import uuid
import json
from typing import TypedDict, List, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Qdrant
from langchain_community.tools import DuckDuckGoSearchRun
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Infrastructure ---

# Initialize specialized LLMs
api_key = os.getenv("GOOGLE_API_KEY")
xai_api_key = os.getenv("XAI_API_KEY")
llm_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_llm(model_name: str, force_provider: str = None):
    provider = force_provider or llm_provider
    
    if provider == "ollama":
        try:
            return ChatOllama(
                model=ollama_model,
                base_url=ollama_base_url
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Ollama ({ollama_model}). Error: {e}")
            return get_llm(model_name, force_provider="gemini")

    if provider == "grok":
        if not xai_api_key:
            print("Warning: XAI_API_KEY not found. Falling back to Gemini.")
            return get_llm(model_name, force_provider="gemini")
        try:
            # Grok models: grok-beta, grok-vision-beta
            return ChatOpenAI(
                model="grok-beta",
                openai_api_key=xai_api_key,
                base_url="https://api.x.ai/v1"
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Grok. Error: {e}")
            return get_llm(model_name, force_provider="gemini")
            
    # Default to Gemini
    if not api_key:
        return None
    try:
        return ChatGoogleGenerativeAI(model=model_name)
    except Exception as e:
        print(f"Warning: Failed to initialize {model_name}. Error: {e}")
        return None

# Agent A (Triage) uses Flash for speed
triage_llm = get_llm("gemini-1.5-flash")
# Agent B (Analyst) uses Pro for depth
analyst_llm = get_llm("gemini-1.5-pro") or triage_llm

if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment. Using mock logic.")
    embeddings = None
else:
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    except Exception as e:
        print(f"Warning: Failed to initialize embeddings. Error: {e}")
        embeddings = None

# Initialize Tools
# Removed DuckDuckGoSearchRun due to dependency issues
from duckduckgo_search import DDGS

def search_tool_run(query: str):
    """Fallback search tool using DDGS directly."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append(f"{r['title']}: {r['body']}")
    return "\n".join(results)

# Initialize Qdrant (Local)
QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "neural_sentry_memory"

client = QdrantClient(path=QDRANT_PATH)
collections = client.get_collections().collections
if not any(c.name == COLLECTION_NAME for c in collections):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print(f"Initialized Qdrant collection: {COLLECTION_NAME}")

# --- State Profile ---

class AgentState(TypedDict):
    news_item: str
    is_threat: bool
    threat_analysis: str
    verification_results: str
    is_verified: bool
    relevance_score: float # 0.0 to 1.0
    context: List[str] # Historical context from RAG
    logs: List[str]

# --- Nodes ---

def profiler_node(state: AgentState):
    """New Phase 5 Node: Calculates relevance to the user profile."""
    news = state['news_item']
    profile_path = os.getenv("USER_PROFILE_PATH", "user_profile.json")
    relevance_score = 0.0
    logs = state.get('logs', []) + ["Profiler: Evaluating personal relevance..."]
    
    profile_data = {}
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
            
    if triage_llm and profile_data:
        try:
            prompt = f"""
            USER PROFILE: {json.dumps(profile_data)}
            NEWS ITEM: {news}
            
            TASK: On a scale of 0.0 to 1.0, how relevant is this news to this specific user? 
            Consider their location, job, and interests.
            Respond ONLY with the numerical score.
            """
            response = triage_llm.invoke(prompt).content.strip()
            relevance_score = float(response)
            logs[-1] += f" Relevance Score: {relevance_score}"
        except Exception as e:
            logs[-1] += f" Profiling failed: {e}. Defaulting to 0.5."
            relevance_score = 0.5
    else:
        logs[-1] += " Skipping Profiling (No LLM or Profile)."
        relevance_score = 0.5

    return {"relevance_score": relevance_score, "logs": logs}

def retriever_node(state: AgentState):
    news = state['news_item']
    logs = state.get('logs', []) + ["Retriever: Searching historical memory..."]
    context = []
    
    if embeddings:
        try:
            vectorstore = Qdrant(client=client, collection_name=COLLECTION_NAME, embeddings=embeddings)
            docs = vectorstore.similarity_search(news, k=3)
            context = [doc.page_content for doc in docs]
            logs[-1] += f" Found {len(context)} relevant items."
        except Exception as e:
            logs[-1] += f" Search failed: {e}"
    else:
        logs[-1] += " Skipping RAG (No embeddings)."

    return {"context": context, "logs": logs}

def triage_node(state: AgentState):
    """Agent A: The Triage (Lightweight/Flash)"""
    news = state['news_item']
    is_threat = False
    
    if triage_llm:
        try:
            prompt = f"""
            QUICK TRIAGE: Is this news item a potential PHYSICAL threat to life or safety? 
            Examples: Natural disasters (floods, quakes), riots, mob attacks, active violence, or infrastructure collapse.
            NEWS: '{news}'
            Respond ONLY with 'YES' or 'NO'.
            """
            response = triage_llm.invoke(prompt).content.strip().upper()
            is_threat = "YES" in response
            logs_msg = f"Triage: {'Physical threat suspected' if is_threat else 'Safe'}"
        except Exception as e:
            print(f"Triage Node Error: {e}")
            is_threat = any(word in news.lower() for word in ["danger", "leak", "warning", "threat"])
            logs_msg = "Triage: (Fallback) Threat suspected" if is_threat else "Triage: (Fallback) Safe"
    else:
        is_threat = any(word in news.lower() for word in ["danger", "leak", "warning", "threat"])
        logs_msg = "Triage: (Mock) Threat suspected" if is_threat else "Triage: (Mock) Safe"

    print(f"[Triage] {logs_msg}")
    return {"is_threat": is_threat, "logs": state.get('logs', []) + [logs_msg]}

def analyst_node(state: AgentState):
    """Agent B: The Analyst (Heavyweight/Pro)"""
    news = state['news_item']
    context_str = "\n".join(state.get('context', []))
    
    if analyst_llm:
        try:
            prompt = f"""
            ROLE: Senior Crisis & Safety Analyst
            HISTORICAL CONTEXT:
            {context_str}
            
            NEW EVENT:
            {news}
            
            TASK: Perform a Life-Safety Risk Assessment. 
            1. How does this physical event impact the user's safety given history?
            2. Identify high-risk zones and potential escalation.
            3. Provide immediate safety recommendations (e.g., evacuation routes, shelter, avoidance).
            Respond with a detailed analysis and specific safety actions.
            """
            analysis = analyst_llm.invoke(prompt).content
        except Exception as e:
            analysis = f"Analyst Fallback: High probability of danger due to {news} context."
    else:
        analysis = "Analyst Mock: Analysis complete. High risk detected."

    print(f"[Analyst] {analysis[:100]}...")
    return {"threat_analysis": analysis, "logs": state.get('logs', []) + ["Analyst: Deep analysis performed."]}

def validator_node(state: AgentState):
    """Agent C: The Validator (Search Engine Integration)"""
    news = state['news_item']
    is_verified = False
    
    print("[Validator] Hunting for second source...")
    try:
        search_query = f"Verify news: {news}"
        verification_results = search_tool_run(search_query)
        
        # Determine verification status
        if analyst_llm and len(verification_results) > 20:
            prompt = f"Compare this news: '{news}' with these search results: '{verification_results}'. Is the news verified by secondary sources? Respond 'VERIFIED' or 'UNVERIFIED'."
            resp = analyst_llm.invoke(prompt).content.upper()
            is_verified = "VERIFIED" in resp
        else:
            is_verified = len(verification_results) > 50 # Heuristic
    except Exception as e:
        print(f"Validator Error: {e}")
        verification_results = "Search failed."
        is_verified = True # Fallback to warning user anyway

    print(f"[Validator] Verified: {is_verified}")
    return {
        "is_verified": is_verified, 
        "verification_results": verification_results,
        "logs": state.get('logs', []) + [f"Validator: Search results obtained. Verified={is_verified}"]
    }

def notify_node(state: AgentState):
    msg = f"!!! NEURAL SENTRY ALERT !!!\n\nTHREAT: {state['news_item']}\n\nANALYSIS: {state['threat_analysis'][:500]}...\n\nVERIFICATION: {state['verification_results'][:200]}..."
    print(f"[Notify] Sending Alert...")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg})
        except Exception as e:
            print(f"[Notify] Telegram failed: {e}")
    else:
        print(f"[Notify] Mock Alert sent:\n{msg}")

    return {"logs": state.get('logs', []) + ["Notification processed."]}

def archiver_node(state: AgentState):
    news = state['news_item']
    logs = state.get('logs', []) + ["Archiver: Storing news in personal memory..."]
    
    if embeddings:
        try:
            vectorstore = Qdrant(client=client, collection_name=COLLECTION_NAME, embeddings=embeddings)
            vectorstore.add_texts([news], ids=[str(uuid.uuid4())])
            logs[-1] += " Successfully stored."
        except Exception as e:
            logs[-1] += f" Storage failed: {e}"
    else:
        logs[-1] += " Skipping Archival (No embeddings)."
        
    return {"logs": logs}

# --- Router functions ---

def decide_to_analyze(state: AgentState) -> Literal["analyze", "end"]:
    # Neural Moat: Only analyze if it's a threat AND personally relevant
    relevance = state.get('relevance_score', 0.5)
    if state['is_threat'] and relevance > 0.4:
        return "analyze"
    return "end"

def decide_to_verify(state: AgentState) -> Literal["verify", "end"]:
    # For phase 3, we verify everything that's analyzed
    return "verify"

def decide_to_notify(state: AgentState) -> Literal["notify", "end"]:
    if state['is_verified']:
        return "notify"
    return "end"

# --- Build the graph ---

workflow = StateGraph(AgentState)

workflow.add_node("profiler", profiler_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("triage", triage_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("validator", validator_node)
workflow.add_node("notify", notify_node)
workflow.add_node("archiver", archiver_node)

workflow.set_entry_point("profiler")

workflow.add_edge("profiler", "triage")

workflow.add_conditional_edges(
    "triage",
    decide_to_analyze,
    {
        "analyze": "retriever",
        "end": "archiver"
    }
)

workflow.add_edge("retriever", "analyst")
workflow.add_edge("analyst", "validator")

workflow.add_conditional_edges(
    "validator",
    decide_to_notify,
    {
        "notify": "notify",
        "end": "archiver"
    }
)

workflow.add_edge("notify", "archiver")
workflow.add_edge("archiver", END)

sentry_app = workflow.compile()

if __name__ == "__main__":
    test_state = {"news_item": "Severe thunderstorm warning.", "logs": []}
    sentry_app.invoke(test_state)
