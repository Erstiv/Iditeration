# Idideration — Session Handoff
**Date:** March 29, 2026
**Session:** Initial build + deployment

---

## What Idideration Is

AI-powered marketing strategy platform that replaces entire marketing departments. Orchestrates 9 specialized AI agents to produce comprehensive, behaviorally-grounded marketing plans from minimal input. Internal tool for Elliot, first case study is Homestead: The Series (Angel Studios).

## Current State: WORKING (with known bugs being ironed out)

### Architecture
- **Backend:** FastAPI (Python) + SQLAlchemy + SQLite (local) / SQLite (Hetzner too, for now)
- **AI:** Google Gemini 2.5 (Flash for data agents, Pro for reasoning agents)
- **Frontend:** Jinja2 templates + HTMX, dark theme
- **Local:** `/Users/JERS/Idideration/` — runs on port 8006, venv at `./venv`
- **Production:** `/opt/idideration/` on Hetzner (ssh filou) — port 8011, systemd service `idideration`, nginx reverse proxy
- **Domain:** https://iditeration.com (NOTE: one 'd' — iditeration, not idideration)
- **SSL:** Let's Encrypt cert, auto-renew configured
- **Nginx config:** `/etc/nginx/sites-available/idideration` — has 50MB upload limit

### The 9 Agents (execution order)
| # | Agent | Model | Status |
|---|-------|-------|--------|
| 0 | Research Agent | Flash | NEW — uses Google Search grounding, 2-step (search → synthesize). Has fallback if grounding returns None |
| 1 | Intake Analyst | Flash | Working |
| 2 | Behavioral Scientist | Pro | Working — fixed: handles Research Directives as list or dict |
| 3 | Psychometrics Expert | Pro | Working — fixed: same Research Directives fix. JSON self-repair in base agent handles its occasional malformed output |
| 4 | Competitive Intelligence | Flash | Working |
| 5 | Social Strategist | Flash | Working — note: returned mostly empty arrays on Homestead run, may need prompt tuning |
| 6 | Chief Strategist | Pro | Working |
| 7 | Creative Director | Pro | Working |
| 8 | Stakeholder Agent | Flash | Available, runs standalone or in pipeline |

### Key Files
```
app/main.py                    — FastAPI app, lifespan (DB init, user creation, bible seeding)
app/config.py                  — Env vars, agent model mapping, loads .env via dotenv
app/models.py                  — SQLAlchemy models (Project, CrewRun, AgentRun, BibleEntry, etc.)
app/database.py                — Engine setup (SQLite-aware, no pool for SQLite)
app/crews/crew_runner.py       — Sequential agent orchestration, creates/executes CrewRuns
app/crews/marketing_bible.py   — MarketingBibleTool — read/write interface for knowledge base
app/crews/agents/base.py       — BaseAgent class — Gemini calls, JSON parsing with 4-level fallback + self-repair
app/crews/agents/research_agent.py  — Agent 0, Google Search grounding
app/crews/agents/*.py          — All other agents
app/output/docx_generator.py   — Adaptive DOCX generator — walks JSON trees, adds page numbers
app/routes/projects.py         — All routes: dashboard, project CRUD, runs, file parsing, bible, stakeholders
app/templates/                 — base.html, dashboard.html, project.html, run_status.html, new_project.html
prompts/                       — System prompts for each agent (00-08)
marketing_bible_seed/seed_data.json — 40 entries, ~125KB
```

### Knowledge Base System
- **Marketing Bible (Global):** 40 seed entries across 8 categories (psychometrics, neuroscience, behavioral_economics, social_media, game_theory, content_strategy, brand_building, frameworks)
- **Product Bible (Per-Project):** Agents write to it during execution. Manual entries via UI.
- **Directives category:** NEW — renders as `!!! MANDATORY DIRECTIVES (ALL AGENTS MUST FOLLOW) !!!` in agent prompts. Sorted first. Used for hard constraints like "do NOT recommend X."

### DOCX Output
- Adaptive renderer — walks agent JSON trees regardless of key naming (agents use inconsistent keys: camelCase, Title Case, snake_case)
- `_humanize_key()` converts any format to readable headings
- `_render_value()` / `_render_dict()` recursively render nested structures
- Page numbers: "Page X of Y" in footer
- Cover page, TOC, 7 agent sections, footer

### Guided Intake Form (`/projects/new`)
- 4-step wizard: Basic Info → What You Know → Assets & Context → Research Options
- Step 2 has drag-and-drop file parsing: PDF/DOCX/TXT → extract text → Gemini Flash parses into form fields
- Step 4 checkboxes: auto-research (Agent 0), stakeholder questions, full pipeline
- POST creates project + optionally kicks off background agent runs

### Deployment Commands
```bash
# Local
cd /Users/JERS/Idideration && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload

# Deploy to Hetzner
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.db' --exclude='.env' /Users/JERS/Idideration/ filou:/opt/idideration/
ssh filou "systemctl restart idideration"

# Check status
ssh filou "systemctl status idideration"
ssh filou "journalctl -u idideration --no-pager -n 30"
```

### .env (both local and Hetzner)
```
DATABASE_URL=sqlite:///idideration.db  (local) or sqlite:////opt/idideration/idideration.db (Hetzner)
GEMINI_API_KEY=AIzaSyBeMhldC9wbJjRbduWY3egsNSEDkkF8TNQ
SESSION_SECRET=<random>
NARRALYTICA_API_URL=http://localhost:8005/api
APP_HOST=0.0.0.0 (local) or 127.0.0.1 (Hetzner)
APP_PORT=8006 (local) or 8011 (Hetzner)
```

### Completed First Run (Homestead)
- Project ID 1 on local DB
- Crew Run 2 completed: all 7 agents, 180K tokens, $0.41 total
- DOCX generated: `projects/1/output/Homestead_Marketing_Plan_20260329_104321.docx` (92.8 KB, 1526 paragraphs)
- Social Strategist returned mostly empty — may need prompt improvement

### Known Issues / TODO
1. **Social Strategist returns empty arrays** — its prompt may need better instructions or the prior context may be too large
2. **Research Agent grounding can fail** — fallback to non-grounded call is implemented but may produce weaker results
3. **Agent JSON key inconsistency** — agents return different key formats (camelCase vs snake_case vs Title Case). The adaptive DOCX renderer handles this, but agents reading each other's output need flexibility too (fixed for Research Directives, may appear elsewhere)
4. **Starlette 1.0 TemplateResponse** — uses new signature: `templates.TemplateResponse(request, "template.html", {context})` not the old dict-first format
5. **File upload parsing** — drag-and-drop is built but hasn't been verified working end-to-end on production yet
6. **No auth** — single user (Elliot), user_id=1 hardcoded. Fine for internal use.
7. **SQLite on Hetzner** — works for single user but should migrate to PostgreSQL if multi-user is ever needed
8. **Background task DB sessions** — FastAPI BackgroundTasks share the request's DB session which can cause issues. The crew_runner creates its own session but watch for this.

### Generated Documents (in /Users/JERS/Idideration/projects/)
- `Idideration_Product_Brief.docx` — 55KB, platform deep-dive
- `Idideration_Executive_Summary.docx` — 39KB, 2-page pitch
- `Homestead_Master_Brief.docx` — 59KB, case study reference
- `Homestead_Executive_Summary.docx` — 39KB, case study pitch

### Related Projects
- **Cassian** (`/Users/JERS/Cassian/`, github.com/Erstiv/Cassian) — Book editing AI, same architecture pattern. Idideration's crew system is modeled after Cassian's.
- **Narralytica** (`/Users/JERS/narralytica/`, github.com/Erstiv/Narralytica) — Video intelligence platform. Idideration's Intake Analyst can fetch scene-level data from Narralytica API when a show ID is linked.

### Port Map (Hetzner — ssh filou)
3000-3006, 3010, 3020: Various frontend services
8000, 8003, 8005, 8006, 8080, 8085, 8090: Various backends
**8011: Idideration**
