# INFORMATION CASCADE INTELLIGENCE

> *"We don't just detect information. We understand its journey."*

An academic research platform for discovering emerging information, analyzing how it evolves across diverse public sources, mapping multi-source narrative trees, studying journalistic coverage cascades, evaluating evidence, and estimating potential societal impact.

---

## 1. Project Overview & Research Lens

**Information Cascade Intelligence** is an academic AI research system designed to observe, trace, and understand how public information spreads and transforms over time across independent newsrooms and scientific agencies.

### What the System Answers:
1. **What information is emerging?** Semantic TF-IDF and cosine similarity clustering uncover developing news events and topical spikes.
2. **Where did the information originate?** Identifies initial observed publishing timestamps and primary reporting publishers.
3. **How is the information evolving?** Tracks sequential additions of named entities (persons, organizations, locations, quantities) and lexical vocabulary shifts.
4. **Which sources are reporting similar information?** Cross-publisher clustering compares how BBC, The Guardian, UN News, WHO, GDELT, Open-Meteo, and NASA report related phenomena.
5. **How is the narrative changing over time?** Interactive narrative trees (React Flow) map initial reports, corroborations, expansions, updates, and divergent claims.
6. **What potential impact could this information have on society?** Automatic impact categorization across Public Health, Environment, Public Safety, Economy, Government & Policy, and Technology.
7. **Is the information supported by multiple independent sources?** Multi-source corroboration modeling flags consensus claims, conflicting figures, and evidentiary gaps.
8. **What could happen to the topic in the near future?** Mathematical growth forecasting models project article volume over +24h, +48h, and +72h horizons with explicit prediction intervals.

> **CRITICAL RESEARCH BOUNDARY:**
> This platform is **NOT a conventional binary fake-news detector** and does **NOT label articles simply as true or false**. Measured journalistic article volume represents public editorial publication activity and must not be confused with peer-to-peer social media impressions or private virality.

---

## 2. Technology Stack

- **Frontend**:
  - React.js 18 + Vite
  - Tailwind / Custom Research Theme (Soft Pink `#fdf2f8`, Light Blue `#f0f9ff`, Yellow `#fefce8`, Lavender `#faf5ff`, Dark Navy typography `#0f172a`)
  - **React Flow (`@xyflow/react`)**: Interactive, zoomable, draggable narrative tree graphs with labeled evidentiary edges
  - **Recharts**: Responsive timeline area charts, publisher distribution bars, ranking charts
  - **Lucide React**: Research icons
- **Backend**:
  - Python 3.11+ / 3.14+
  - FastAPI: Modular REST APIs with validation and error handling
  - Background asynchronous multi-source collection jobs
- **Database**:
  - Dual Engine: Supabase PostgreSQL & SQLite (`cascade_intelligence.db`)
  - All 11 research tables: `articles`, `sources`, `topics`, `topic_articles`, `extracted_entities`, `narrative_relationships`, `evidence_records`, `cascade_metrics`, `impact_assessments`, `predictions`, `collection_logs`
- **AI & NLP Pipeline**:
  - TF-IDF Vectorization (`scikit-learn`)
  - Cosine Similarity matrix calculation
  - Linguistic pattern-based Named Entity Recognition (NER) for ORG, PERSON, GPE, QUANTITY, EVENT
  - Lexical delta & semantic overlap analysis
  - Time-decayed velocity forecasting with lower/upper prediction intervals

---

## 3. Integrated Public Data Sources

The platform connects directly to public APIs without requiring paid credentials:

| Source | API Endpoint | Purpose |
|---|---|---|
| **GDELT DOC 2.0 API** | `https://api.gdeltproject.org/api/v2/doc/doc` | Real-time global journalistic coverage discovery across thousands of international domains |
| **BBC World RSS** | `https://feeds.bbci.co.uk/news/world/rss.xml` | Tier-1 international news coverage and timestamps |
| **The Guardian World RSS** | `https://www.theguardian.com/world/rss` | Global reporting and analytical commentary |
| **UN News RSS** | `https://news.un.org/feed/subscribe/en/news/all/rss.xml` | Official humanitarian, geopolitical, and international development updates |
| **WHO News RSS** | `https://www.who.int/rss-feeds/news-english.xml` | Global health emergencies, disease surveillance, and advisories |
| **Open-Meteo API** | `https://api.open-meteo.com/v1/forecast` | Contextual atmospheric, temperature, and environmental ground-truth data |
| **NASA EONET API** | `https://eonet.gsfc.nasa.gov/api/v3/events` | Real-time natural hazard tracking (wildfires, severe storms, sea ice) |

---

## 4. The 10 Dashboard Modules

1. **Module 1: Overview Dashboard**: Key metrics (total articles, emerging topics, publishers, increasing coverage topics), activity timeline, source distribution, and topic growth comparison.
2. **Module 2: Emerging Topic Discovery**: Mathematical semantic clustering with keyword extraction, first/latest observed timestamps, and article drill-down.
3. **Module 3: Information Narrative Tree (React Flow)**: Interactive graph mapping initial reports, cross-publisher corroborations, expansions, updates, and narrative variants with labeled evidentiary edges.
4. **Module 4: Information Evolution Analysis**: Chronological timeline tracking entity introduction vs retention, lexical overlap ratios, and claim shifts.
5. **Module 5: Cascade Analysis**: 0–100 Cascade Activity indicator balancing volume, publisher diversity, and acceleration velocity with transparent mathematical weights.
6. **Module 6: Credibility and Evidence Analysis**: Source corroboration indicators, consensus claims, conflicting numerical details, evidence gaps, and "Insufficient Evidence" guardrails.
7. **Module 7: Social Impact Analysis**: Categorization across 6 domains (Public Health, Environment, Public Safety, Economy, Government & Policy, Technology), potential severity, urgency, and affected areas.
8. **Module 8: Growth Prediction**: 24h, 48h, and 72h article coverage volume forecasting with lower, expected, and upper confidence intervals.
9. **Module 9: Information Classification Matrix (2×2)**: Verified Breaking News, Niche Fact, Isolated Rumor, and Viral Disinformation Risk quadrants.
10. **Module 10: Search and Exploration**: Multi-parameter search across headlines, keywords, and publishers, with side-by-side topic comparison mode.

---

## 5. Windows PowerShell Setup & Run Instructions

### Prerequisites
- Python 3.11+ installed and available in PATH
- Node.js 18+ and npm installed

### Step 1: Clone or Navigate to Directory
```powershell
cd "c:\Users\HP\Documents\THRUSHA Y K\New folder\Information-Cascade-Intelligence"
```

### Step 2: Start the Backend (Terminal 1)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Step 3: Start the Frontend (Terminal 2)
```powershell
cd frontend
npm install
npm run dev
```
- Dashboard Interface: [http://localhost:5173](http://localhost:5173)

### Step 4: Run the Automated Test Suite
```powershell
$env:PYTHONPATH="."
.\backend\.venv\Scripts\pytest.exe -v tests/test_analysis.py tests/test_endpoints.py -p no:cacheprovider
```

---

## 6. Environment Variables (`backend/.env`)

```ini
# Database Configuration
# Optional: Provide Supabase credentials for PostgreSQL cloud storage.
# If left blank, the system automatically runs locally on SQLite (cascade_intelligence.db).
SUPABASE_URL=https://piubkjyxjfydkrdfsltt.supabase.co
SUPABASE_KEY=sb_publishable_AdiygOEP3HGPhNaStOzwGg_equkgwsF
SUPABASE_TABLE=articles

# Local Database Fallback
DATABASE_URL=sqlite:///./cascade_intelligence.db

# GDELT Configuration
GDELT_TIMESPAN=24h
MAX_GDELT_RECORDS=75

# Environmental Context (Open-Meteo)
WEATHER_ENABLED=true
WEATHER_LAT=12.9141
WEATHER_LON=74.8560
WEATHER_LOCATION=Mangaluru

# NASA EONET
NASA_EONET_ENABLED=true
NASA_API_KEY=DEMO_KEY

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## 7. Database Architecture

The system uses 11 relational tables defined in `database/schema.sql` (PostgreSQL) and mirrored in SQLite:
1. `articles`: Primary records preserving URL, title, description, source, publication time, and collection origin.
2. `sources`: Aggregated newsrooms and data providers with coverage statistics and reliability tiers.
3. `topics`: Semantic clusters with cascade scores, corroboration scores, and extracted keywords.
4. `topic_articles`: Many-to-many relationship mapping articles to topics with similarity scores.
5. `extracted_entities`: Entities extracted via NLP (ORG, PERSON, GPE, QUANTITY, EVENT) with textual salience.
6. `narrative_relationships`: Graph edges linking articles with labeled relationships for React Flow.
7. `evidence_records`: Corroboration levels, consensus claims, conflicting points, and unresolved questions.
8. `cascade_metrics`: Detailed cascade activity scores, velocity, and acceleration rates.
9. `impact_assessments`: Qualitative evaluations across 6 societal sectors with severity ratings.
10. `predictions`: 24h, 48h, 72h article coverage volume forecasts with confidence bounds.
11. `collection_logs`: Historical audit trail of collection runs, items saved, and API errors.
