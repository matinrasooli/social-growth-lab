# Social Growth Lab

A local-first, compliant Instagram content-strategy, analytics, and virality
simulation tool for a real business or creator account.

Social Growth Lab helps you understand what content performs best, generate
better hooks/captions/CTAs, plan a content calendar, analyze Instagram
Insights data you upload yourself, and test strategy ideas in a closed,
synthetic virality simulator. It does **not** automate Instagram, scrape
anything, or fabricate engagement of any kind.

## What this app does

- **Insights analysis** -- upload Instagram Insights exports (CSV, JSON,
  pasted text, or manual entry) and get a real analytics dashboard: reach
  over time, best/worst content, hook/topic/CTA comparisons, save/share/
  comment rates, and posting-time patterns.
- **Content generation** -- score a content idea, generate hooks across 12
  proven styles, generate caption variations, generate CTAs matched to
  funnel stage, and build a 30-day content calendar (month/week/table/kanban
  views).
- **Experiment tracking** -- log hypotheses, results, and lessons learned
  across your content tests.
- **Comment & DM help** -- classify comments/DMs and draft replies for you
  to review. Replies are always **draft-only**; nothing is ever auto-sent.
- **Competitor notes** -- log your own manual observations about
  competitors (never scraped) and get pattern/gap analysis.
- **Closed virality simulator** -- a fully synthetic, in-memory social
  network (fake users, fake posts, several graph topologies) you can use to
  compare hooks, posting times, topics, and CTAs before you ever post
  anything real.
- **Compliance guardrail & logs** -- every free-text request is checked
  against an explicit blocklist before it reaches an LLM or gets persisted;
  every check is logged and visible in the app.

## What this app will never do

- Create fake accounts, fake email accounts, or automate account creation.
- Automate likes, comments, views, follows, unfollows, saves, shares, story
  views, or DMs.
- Scrape Instagram or any other platform.
- Bypass CAPTCHAs, rate limits, or platform detection; rotate IPs/proxies;
  spoof device fingerprints; or otherwise evade platform protections.
- Store or ask for your Instagram password.
- Use unofficial/reverse-engineered Instagram APIs or browser automation
  (Selenium/Playwright/Puppeteer) against Instagram.
- Auto-send any comment or DM reply.

See [`docs/compliance_philosophy.md`](docs/compliance_philosophy.md) for the
full reasoning and how the guardrail is implemented and tested.

## Architecture

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, SQLite (local dev).
- **Frontend:** React + Vite, React Router, Recharts.
- **LLM providers:** OpenAI, Anthropic, Ollama, or a dependency-free mock
  provider (the default -- the whole app works with zero API keys).

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown.

## Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Docker + Docker Compose, if you'd rather not install Python/Node locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # defaults work with zero configuration (mock LLM provider)
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`. On startup, tables are created automatically
from the SQLAlchemy models (fine for local/dev use). For a production-style
setup, use Alembic instead:

```bash
alembic upgrade head
```

### Frontend

```bash
cd frontend
cp .env.example .env               # points at http://localhost:8000 by default
npm install
npm run dev
```

The app is now at `http://localhost:5173`. Register a local username/password
on first load -- there's no external auth provider.

### Docker Compose (both services at once)

```bash
docker compose up --build
```

### Loading sample data

A sample-data generator is included (pure Python, no dependencies):

```bash
cd backend
python3 scripts/seed_sample_data.py
```

This regenerates the files already included in `/sample_data`:

- `instagram_insights_sample.csv` -- 60 synthetic posts (20 reels, 20
  stories, 10 carousels, 10 static posts) in the Insights import format.
- `instagram_insights_sample.json` -- the same data in JSON export format.
- `competitor_notes_sample.json` -- 5 example manual competitor
  observations.
- `experiments_sample.json` -- 10 example experiment definitions.
- `content_calendar_campaigns_sample.json` -- 5 example campaign
  definitions.

Upload `instagram_insights_sample.csv` from the **Upload Insights** page to
populate the Analytics dashboard immediately. The 300 simulated users used
by the Virality Simulator are generated live at run time (not static sample
data), since they're meant to be regenerated per experiment.

### Configuring an LLM provider (optional)

The app works fully offline with the `mock` provider (the default): content
generation falls back to deterministic templates, and scoring falls back to
transparent rules-based heuristics. To use a real LLM for sharper
generation/critique, set in `backend/.env`:

```bash
DEFAULT_LLM_PROVIDER=anthropic     # or: openai | ollama | mock
ANTHROPIC_API_KEY=sk-ant-...
```

## Running tests

### Backend (pytest)

```bash
cd backend
pip install -r requirements.txt
pytest
```

Covers: the compliance guardrail (the most heavily tested module -- every
blocked category has an explicit test), Insights parsers, content scoring,
the virality simulation engine, and full API endpoint flows (including that
unsafe requests return a 400 with a compliant alternative).

### Frontend (Vitest)

```bash
cd frontend
npm install
npm test
```

Covers: dashboard rendering, the insights upload flow, the content scoring
flow, the virality simulation run flow, and that a blocked request surfaces
the guardrail's message and compliant alternative in the UI.

## Future roadmap

Planned, **compliant** extensions:

- Official Meta Graph API integration (approved, OAuth-based) for read-only
  analytics and, eventually, human-confirmed publishing/sending.
- Manual scheduling export (e.g., to a calendar file or CSV) for use with
  Meta's own Creator Studio/Business Suite scheduler.
- Team collaboration (multiple users per account, roles/permissions).
- Brand voice memory across generation features.
- CRM integration (HubSpot, generic webhook/CSV export).
- UTM tracking and landing-page conversion tracking.
- Shopify integration for product-tagged content performance.
- Influencer CRM for tracking real collaboration relationships.
- Paid ads creative analyzer (for ads you already run, via official Ads API).

**Explicitly and permanently excluded**, regardless of future roadmap items:
bot engagement, fake accounts, scraping, IP/proxy rotation, anti-detection
logic, automated Instagram activity, and unofficial APIs.

## License

This is a reference implementation provided as-is for your own use and
modification.
