# Neural Sentry

Neural Sentry is an intelligent, automated threat detection and news monitoring agent. It is designed to ingest real-time information (e.g., RSS feeds), analyze it for personal relevance and potential danger using Google Gemini models, verify findings via web search, and alert the user through Telegram.

## Architecture & Key Files

### Core Logic
*   **`sentry.py`**: Defines the `LangGraph` state machine (`sentry_app`). This is the brain of the operation, containing the node definitions (`profiler_node`, `triage_node`, `analyst_node`, etc.) and the conditional routing logic.
*   **`ingest.py`**: The main entry point for the continuous monitoring daemon. It polls RSS feeds defined in configuration, deduplicates entries using SQLite, and triggers the `sentry_app` workflow for new items.
*   **`user_profile.json`**: A JSON file defining the user's persona (location, interests, job role) used by the Profiler node to determine relevance.

The system employs a multi-agent **Retrieval-Augmented Generation (RAG)** architecture using `LangGraph` to orchestrate distinct roles:
*   **Profiler:** Filters news based on the user's personal context (location, job, interests).
*   **Retriever:** Fetches historical context from a local vector database (Qdrant) as part of the RAG retrieval phase.
*   **Triage (Agent A):** A fast, lightweight model (Gemini 1.5 Flash) to quickly flag potential threats.
*   **Analyst (Agent B):** A capability-focused model (Gemini 1.5 Pro) for deep threat analysis and risk assessment.
*   **Validator (Agent C):** Verifies claims using web search tools.
*   **Notifier:** Sends alerts via Telegram for verified threats.
*   **Archiver:** Stores relevant events in long-term memory (Qdrant) to support future RAG retrieval and context.

### Data & Configuration
*   **`requirements.txt`**: Python dependencies (e.g., `langgraph`, `langchain-google-genai`, `qdrant-client`).
*   **`.env`**: Configuration for API keys (Google, Telegram) and operational settings (Poll intervals, RSS feeds). **Note:** Use `.env.template` as a reference.
*   **`qdrant_data/`**: Directory storing the local Qdrant vector database files.
*   **`ingestion_history.db`**: SQLite database used by `ingest.py` to track processed RSS item hashes and prevent duplicate processing.

## Setup & Development

### Prerequisites
*   Python 3.9+
*   Google Gemini API Key
*   Telegram Bot Token & Chat ID

### Installation
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configure environment:
    ```bash
    cp .env.template .env
    # Edit .env with your API keys and RSS feeds
    ```
3.  Customize Profile:
    *   Edit `user_profile.json` to match the target user's details.

### Running the System
*   **Continuous Monitoring:**
    ```bash
    python ingest.py
    ```
*   **Manual Testing:**
    ```bash
    python test_sentry.py
    ```
