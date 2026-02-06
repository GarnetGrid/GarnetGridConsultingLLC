# JGPT Strategic Roadmap: The Path to AGI-Lite

This roadmap outlines the evolution of JGPT from a "Chatbot" to an "Autonomous Intelligence Console".

## Phase A: "The Reasoner" (Deep Intelligence) 🧠
**Objective**: Enable System 2 thinking. The model should pause, decompose complex problems, execute multi-step tools, and verify its own answers before responding.

### Features
1.  **Multi-Step Reasoning Loop**:
    *   Instead of a single LLM call, we implement a `while` loop that allows the model to "think" for up to *N* steps.
    *   **Architecture**: `Input -> [Thought -> Action -> Observation]*N -> Final Answer`.
2.  **Dynamic Tool Selection**:
    *   Give the Reasoner access to specific tools: `PythonREPL` (for math/logic), `ContextRetriever` (for memory), and `WebSearch` (future).
3.  **Self-Reflexion**:
    *   The model evaluates its own intermediate outputs. "Did this answer user's question? If no, try another approach."
4.  **UI Visualization**:
    *   The frontend must show the "Thought Process" (collapsible accordion) so the user sees the "Brain" working, not just the final output.

### Technical Stack
*   **Backend**: `LangChain` or custom `ReAct` loop in Python (FastAPI).
*   **Model**: Ollama (Mistral/Llama3) with structured prompting.
*   **Frontend**: React component for streaming "Thoughts".

---

## Phase B: "The Pulse" (Automated Knowledge) 🌐
**Objective**: Transform the system from passive (waiting for uploads) to active (hunting for knowledge).

### Features
1.  **The "News Cartel" Scraper**:
    *   A scheduled job (Cron) that visits top tech sources (Hacker News, TechCrunch, Verge).
    *   Extracts content, summarizes it using the LLM, and creates "Knowledge Chunks".
2.  **Daily Digest Generation**:
    *   Every morning at 8:00 AM, the system generates a Markdown report: "Today's Briefing".
    *   This is saved to the User Context automatically.
3.  **Smart Tagging**:
    *   Auto-categorize incoming info (e.g., "AI", "Crypto", "Hardware") for better retrieval.

### Technical Stack
*   **Scraping**: `BeautifulSoup4` or `Crawl4AI`.
*   **Scheduling**: `APScheduler` (Python) or system `cron`.
*   **Storage**: Existing PostgreSQL/pgvector.

---

## Phase C: "The Fortress" (Production Deployment) ☁️
**Objective**: Permanent, secure, and accessible infrastructure. Release the local tether.

### Features
1.  **Cloud VPS Deployment**:
    *   Migrate Docker Compose stack to a remote Ubuntu server.
2.  **Domain & SSL**:
    *   `https://jgpt.garnetgrid.com` secured via Let's Encrypt (Certbot).
3.  **CI/CD Pipeline**:
    *   GitHub Actions to auto-deploy changes when you push code.
4.  **Tunnel Removal**:
    *   Deprecate `ngrok`. Native exposure via Nginx Reverse Proxy.

### Technical Stack
*   **Infra**: DigitalOcean / Hetzner / AWS Lightsail.
*   **Proxy**: Nginx / Traefik.
*   **Security**: `UFW` firewall, Fail2Ban.

---

## Execution Order
1.  **Phase A (The Reasoner)** - *Starting Now*
2.  Phase B (The Pulse)
4.  Phase D (The Polish)

---

## Phase D: "The Polish" (Refinement) ✨
**Objective**: Final quality assurance and aesthetic perfection.
*   **Dark Mode Toggle**: Refine transitions and persistence.
*   **Smoke Test**: Full manual and automated regression testing of the entire site.

