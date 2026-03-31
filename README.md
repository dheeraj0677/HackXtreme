<![CDATA[<div align="center">

# 🛡️ GlobalSentry

### Multi-Agent RAG Threat Intelligence Platform

**Real-time global threat detection across epidemics, climate disasters, and supply chain disruptions — powered by a self-correcting AI pipeline running 100% locally.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-FF6F00)](https://github.com/langchain-ai/langgraph)
[![Ollama](https://img.shields.io/badge/Ollama-Llama3_Local-000000?logo=llama)](https://ollama.com)
[![Flutter](https://img.shields.io/badge/Flutter-Mobile_App-02569B?logo=flutter&logoColor=white)](https://flutter.dev)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC382D)](https://qdrant.tech)

---

**🏆 Built for HackXtreme Hackathon**

[Architecture](#-architecture) · [Features](#-key-features) · [Setup](#-quick-start) · [Tech Stack](#%EF%B8%8F-tech-stack) · [API Docs](#-api-endpoints) · [SDG Alignment](#-sdg-alignment)

</div>

---

## 🧠 What is GlobalSentry?

GlobalSentry is an **autonomous threat intelligence platform** that ingests live RSS feeds from Indian and global news sources, runs them through a **9-node multi-agent AI pipeline**, and surfaces actionable alerts across three critical domains:

| Mode | Domain | SDG | Example Threats |
|------|--------|-----|-----------------|
| 🩺 **Epi-Sentry** | Public Health | SDG 3 | Cholera outbreaks, Nipah virus clusters, dengue surges |
| 🌪️ **Eco-Sentry** | Climate & Disasters | SDG 11/13 | Floods, earthquakes, cyclones, heatwaves, GLOFs |
| ♻️ **Supply-Sentry** | Supply Chain | SDG 12 | Port congestion, chip shortages, pharma API disruptions |

### 💡 Key Innovation: The Neural Moat

GlobalSentry's **cross-mode correlator** (the "Neural Moat") detects **cascading risks between domains** that single-domain systems miss:

> *Example: A flood in Bangladesh (🌪️ Eco) → triggers cholera outbreak (🩺 Epi) → disrupts garment supply chain (♻️ Supply)*

This convergence detection is powered by **cross-domain vector similarity search** in Qdrant, making it the platform's core differentiator.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GLOBALSENTRY                                │
│                                                                     │
│  ┌──────────────┐   ┌─────────────────────────────────────────┐    │
│  │  RSS Feeds    │──▶│       9-Node LangGraph Pipeline         │    │
│  │  (India +     │   │                                         │    │
│  │   Global)     │   │  Profiler → Triage → Retriever(RAG)    │    │
│  └──────────────┘   │     → Analyst → Correlator(Neural Moat) │    │
│                      │     → Validator → [Reflection Loop]     │    │
│                      │     → Notify → Archiver                 │    │
│                      └──────────┬──────────────────────────────┘    │
│              ┌──────────────────┼──────────────────────┐            │
│              ▼                  ▼                      ▼            │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Qdrant Vector   │  │ alerts.json  │  │  FastAPI Backend    │   │
│  │  DB (720+ pts)   │  │ (live store) │  │  (api.py)           │   │
│  │  RAG + Correlator│  └──────┬───────┘  └────────┬────────────┘   │
│  └──────────────────┘         │                   │                 │
│                               ▼                   ▼                 │
│                    ┌──────────────────────────────────────┐         │
│                    │        Frontend Clients               │         │
│                    │  🌐 Web Dashboard (Vanilla JS)        │         │
│                    │  📱 Flutter Mobile App                │         │
│                    │  🌍 3D Threat Globe (Three.js)        │         │
│                    │  🎞️ Conveyor Pipeline Viewer          │         │
│                    └──────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

### The 9-Node Pipeline

| # | Node | Role | Details |
|---|------|------|---------|
| 1 | **Profiler** | Relevance scoring | Scores news against stakeholder profile (region, role, interests) |
| 2 | **Triage** (Agent A) | Threat classifier | Mode-aware YES/NO filter — drops irrelevant noise fast |
| 3 | **Retriever** | RAG context | Queries Qdrant for same-mode historical events (filtered by mode) |
| 4 | **Analyst** (Agent B) | Deep analysis | Domain expert analysis — outputs severity (1–5) + confidence (0–1) |
| 5 | **Correlator** | 🧠 Neural Moat | Cross-mode vector search — finds cascading risks between EPI↔ECO↔SUPPLY |
| 6 | **Validator** (Agent C) | Fact-checker | Verifies claims via live DuckDuckGo search |
| 7 | **Retry Counter** | Reflection loop | If unverified, routes back to Analyst with new evidence (max 1 retry) |
| 8 | **Notify** | Alert dispatcher | Saves structured alert to `alerts.json` for the web dashboard |
| 9 | **Archiver** | Memory builder | Stores event + metadata in Qdrant for future RAG and correlation |

---

## ✨ Key Features

- **🤖 Autonomous Scanning** — Background loop continuously ingests RSS feeds and runs them through the AI pipeline
- **🧠 Cross-Domain Correlation** — Neural Moat detects cascading risks across EPI ↔ ECO ↔ SUPPLY domains
- **🔄 Self-Correcting Reflection Loop** — Validator can reject an analysis and send it back to the Analyst with new evidence
- **🌍 3D Threat Globe** — Interactive Three.js globe showing geo-located threats with severity-colored markers
- **🎞️ Live Conveyor View** — Real-time pipeline visualization showing each headline flowing through AI nodes
- **📱 Flutter Mobile App** — Cross-platform companion app with alert details, analytics, and pipeline views
- **🔒 100% Local** — Runs entirely on local hardware — Ollama (Llama 3), local embeddings, local Qdrant — no cloud APIs
- **📡 Live RSS Feeds** — Curated Indian + global news sources for each sentry mode
- **📊 Threat Analytics** — Severity distribution charts, mode-wise counts, processing statistics

---

## 📂 Project Structure

```
HackExtreme/
│
├── Radio/                              ← 🤖 AI Agent Engine (Python)
│   ├── sentry.py                       ← Core LangGraph pipeline (9 nodes + graph wiring)
│   ├── ingest.py                       ← RSS polling daemon — triggers pipeline per headline
│   ├── seed_data.py                    ← Pre-loads 18 demo events into Qdrant
│   ├── user_profile.json               ← Stakeholder profile (region, role, interests)
│   ├── alerts.json                     ← Live alert store (written by Notify node)
│   ├── requirements.txt                ← Python dependencies for the agent
│   ├── .env.template                   ← Environment config template
│   ├── qdrant_data/                    ← Local Qdrant vector database (720+ vectors)
│   └── tests/                          ← Test results and validation
│
├── GlobalSentry-Web/                   ← 🌐 Web Dashboard & API Server
│   ├── api.py                          ← FastAPI backend (1100+ lines) — serves data + runs agent
│   ├── requirements.txt                ← Python dependencies for the web server
│   ├── epi_feed.xml                    ← Pre-generated RSS feed — Epidemic mode (500 items)
│   ├── eco_feed.xml                    ← Pre-generated RSS feed — Ecological mode (500 items)
│   ├── supply_feed.xml                 ← Pre-generated RSS feed — Supply chain mode (500 items)
│   ├── generate_feeds.py               ← Feed generator scripts
│   └── frontend/                       ← Vanilla HTML/CSS/JS Frontend
│       ├── index.html                  ← Main dashboard (alerts, charts, mode switcher)
│       ├── style.css                   ← Full design system (dark theme, glassmorphism)
│       ├── app.js                      ← Dashboard logic (polling, rendering, charts)
│       ├── globe.html                  ← 3D threat globe (Three.js + WebGL)
│       ├── conveyor.html               ← Live pipeline conveyor visualization
│       ├── conveyor.css                ← Conveyor styling
│       └── conveyor.js                 ← Conveyor animation logic
│
├── global_sentry_app/                  ← 📱 Flutter Mobile App
│   ├── lib/
│   │   ├── main.dart                   ← App entry point
│   │   ├── screens/
│   │   │   ├── home_screen.dart        ← Home — mode selector + live threat cards
│   │   │   ├── dashboard_screen.dart   ← Dashboard — summary + navigation
│   │   │   ├── alert_detail_screen.dart← Full alert detail view
│   │   │   ├── analytics_screen.dart   ← Charts + threat distribution
│   │   │   └── pipeline_screen.dart    ← Pipeline node progress visualization
│   │   ├── models/                     ← Data models
│   │   ├── theme/                      ← App theme + colors
│   │   └── widgets/                    ← Reusable UI components
│   └── pubspec.yaml                    ← Flutter dependencies
│
└── README.md                           ← This file
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Python 3.11+** | Backend + Agent | [python.org](https://python.org) |
| **Ollama** | Local LLM (Llama 3) | [ollama.com](https://ollama.com) |
| **Flutter 3.19+** | Mobile app (optional) | [flutter.dev](https://flutter.dev) |

### 1. Start Ollama

```bash
ollama pull llama3
ollama serve
```

### 2. Setup the Agent Engine

```bash
cd Radio
pip install -r requirements.txt
cp .env.template .env        # Edit if needed
python seed_data.py          # Seeds 18 demo events into Qdrant
```

### 3. Start the Web Dashboard

```bash
cd GlobalSentry-Web
pip install -r requirements.txt
uvicorn api:app --port 8000
```

### 4. Open in Browser

```
🌐  Dashboard:    http://localhost:8000
🌐  3D Globe:     http://localhost:8000/globe.html
🌐  Conveyor:     http://localhost:8000/conveyor.html
📄  API Docs:     http://localhost:8000/api/docs
```

### 5. (Optional) Run the Flutter App

```bash
cd global_sentry_app
flutter pub get
flutter run
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **LLM** | Ollama + Llama 3 | 100% local, no API keys, fast inference |
| **Agent Orchestration** | LangGraph + LangChain | Stateful multi-agent DAG with conditional routing |
| **Vector Database** | Qdrant (local) | Cosine similarity search, filtered by mode, cross-mode correlation |
| **Embeddings** | `all-MiniLM-L6-v2` | Local sentence embeddings (384 dim), no API needed |
| **Backend API** | FastAPI + Uvicorn | Async, auto-docs, serves both API and static frontend |
| **Web Frontend** | Vanilla HTML/CSS/JS | Lightweight, no build step, glassmorphism dark theme |
| **3D Globe** | Three.js + WebGL | Interactive geo-visualization of threats |
| **Mobile App** | Flutter + Dart | Cross-platform (iOS/Android/Web) companion app |
| **Web Search** | DuckDuckGo (DDGS) | Free, no API key — used by Validator for fact-checking |
| **RSS Parsing** | feedparser | Robust RSS/Atom feed ingestion |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api` | Health check + version info |
| `GET` | `/api/alerts?mode=epi&limit=15` | Get alerts (processed + RSS) with optional mode filter |
| `GET` | `/api/feed/{mode}?page=1&per_page=15` | Paginated raw RSS feed headlines |
| `GET` | `/api/threat-counts` | Per-mode totals: total / processed / pending |
| `GET` | `/api/globe-threats` | All alerts with geo-coordinates for 3D globe |
| `GET` | `/api/convergence` | Cross-mode convergence detections (Neural Moat) |
| `GET` | `/api/status` | System status, active mode, pipeline health |
| `GET` | `/api/user-profile` | Current stakeholder profile |
| `POST` | `/api/trigger` | Manually trigger analysis for a headline |
| `PUT` | `/api/mode/{mode}` | Switch active sentry mode |

Full interactive docs at **`/api/docs`** (Swagger UI).

---

## 🌍 SDG Alignment

GlobalSentry directly addresses three UN Sustainable Development Goals:

| SDG | Goal | How GlobalSentry Helps |
|-----|------|------------------------|
| **SDG 3** | Good Health & Well-being | 🩺 Epi-Sentry detects disease outbreaks early, enabling faster public health response |
| **SDG 11** | Sustainable Cities & Communities | 🌪️ Eco-Sentry monitors climate disasters — floods, earthquakes, heatwaves — for urban safety |
| **SDG 12** | Responsible Consumption & Production | ♻️ Supply-Sentry tracks supply chain disruptions and ESG violations |
| **SDG 13** | Climate Action | 🌍 Cross-domain correlation reveals how climate events cascade into health and economic crises |

---

## 📊 Qdrant Database Stats

The local vector database acts as the platform's long-term memory:

| Collection | Vectors | Dimensions | Model | Purpose |
|---|---|---|---|---|
| `global_sentry_memory` | **720+** | 384 | MiniLM-L6-v2 | RAG retrieval + cross-mode correlation |
| `neural_sentry_memory` | 0 | 768 | (reserved) | Future expansion |

Each vector stores: `page_content` (event text) + `metadata` (mode, severity).

---

## 🖼️ Screenshots

| Dashboard | 3D Globe | Pipeline Conveyor |
|-----------|----------|-------------------|
| Alert cards with severity, source, convergence warnings | Interactive WebGL globe with threat markers | Live animation of headlines flowing through AI nodes |

---

## 👥 Team

Built with ❤️ for **HackXtreme**.

---

<div align="center">

**GlobalSentry** — *Because threats don't stay in silos. Neither should intelligence.*

</div>
]]>
