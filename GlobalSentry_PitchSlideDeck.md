# 🎤 GlobalSentry: Pitch Deck Outline (HackExtreme)
*Mapped perfectly to the provided 7-slide hackxtreme_temp.pptx template.*

## Slide 1: Team Details
* **a. Team name:** *[Your Team Name]*
* **b. Team leader name:** *[Your Name]*
* **c. Team Members Names:** *[Other Members]*
* **d. College Name:** *[Your College]*
* **Notes:** Include the SDG Badges (3, 11, 12, 13) in the corner of this title slide to immediately show theme alignment.

## Slide 2: Problem Statement
* **The Problem:** The world generates massive amounts of data regarding climate, health, and supply chains daily, but it is too noisy to manually process.
* **The Gap:** We lack unified, automated systems to detect converging global crises (epidemics, climate disasters) *before* they hit mainstream news.
* **The Consequence:** Reactive responses cost lives and billions of dollars. We need personalized, localized early-warning systems.

## Slide 3: Proposed Solution
* **The Solution:** **GlobalSentry** - A unified, true Multi-Agent RAG ecosystem.
* **The Concept:** A web platform where stakeholders toggle between three distinct monitoring modes:
  * 🩺 **Epi-Sentry (SDG 3):** Early epidemic detection from WHO/Health blogs.
  * 🌪️ **Eco-Sentry (SDG 11/13):** Climate disaster prediction from meteorological/seismic data.
  * ♻️ **Supply-Sentry (SDG 12):** Supply chain transparency via ESG and whistle-blower reports.
* **The Core Magic:** It transforms from "reactive tracking" into an active "Neural Moat" that autonomously cross-references and verifies threats before alerting.

## Slide 4: Architecture Diagram *(The LangGraph Node Breakdown)*
*(Draw a clean flowchart showing these exact nodes)*
* **1. Ingest & Profiler:** Filters noise based on the specific Sentry Mode toggled (The Personalizer).
* **2. The Retriever:** Searches our Qdrant Vector DB for historical context (The Historian).
* **3. Agent A (Triage):** High-speed local filtering on headlines (The Sentry).
* **4. Agent B (Analyst):** Deep reasoning and cross-modal analysis (The Brain).
* **5. Agent C (Validator):** Real-time web search fact-checking to prevent hallucinations (The Fact-Checker).
* **6. Notify & Archive:** Telegram alerts (The Messenger) and Qdrant storage (The Memory).

## Slide 5: Technologies/Tools Used
* **AI Orchestration:** `LangGraph` (for complex, multi-stage Agent routing)
* **Local LLM Engine:** `Ollama` (using Llama-3/Mixtral for **Zero-Cost, 100% Private** local execution)
* **Vector Database:** `Qdrant` (Long-term RAG memory to recognize historical patterns)
* **Continuous Daemon:** Python + SQLite deduplication for 24/7 monitoring.
* **Frontend/Alerts:** `React` / `Next.js` Web Dashboard & `Telegram API`.

## Slide 6: Target Audience/Market & Future Scope
* **The Audience:** Government Planners (Eco), Medical NGOs (Epi), Supply Chain Auditors (Supply).
* **Future Scope (The Roadmap):**
  * *Multi-Modal Analysis:* Using Vision models to analyze satellite/infrastructure images.
  * *Knowledge Graphs:* Mapping relationships (e.g., how a local flood impacts a specific corporate supply chain).
  * *Autonomous Remediation:* Agents automatically drafting and sending emergency evacuation notices based on verified threats.

## Slide 7: Thank You
* **We appreciate your time!**
* **Contact:** *[Team Lead Contact Info]*
* **Call to Action:** "GlobalSentry: Moving from a system that simply watches, to a system that acts and remembers."
