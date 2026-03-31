# Idideration — Session Handoff
**Date:** March 30, 2026
**Session:** Stability fixes + Tier 1 human-in-loop + citations

---

## What Idideration Is

AI-powered marketing strategy platform that replaces entire marketing departments. Orchestrates 9 specialized AI agents to produce comprehensive, behaviorally-grounded marketing plans from minimal input. Internal tool for Elliot, first case study is Homestead: The Series (Angel Studios).

## Current State: WORKING — Tier 1 features complete, citations live

### Architecture
- **Backend:** FastAPI (Python) + SQLAlchemy + SQLite
- **AI:** Google Gemini 2.5 (Flash for data agents, Pro for reasoning agents)
- **Frontend:** Jinja2 templates + HTMX, dark theme
- **Local:** `/Users/JERS/Idideration/` — runs on port 8006, venv at `./venv`
- **Production:** `/opt/idideration/` on Hetzner (ssh filou) — port 8011, systemd service `idideration`, nginx reverse proxy
- **Domain:** https://iditeration.com (NOTE: one 'd' — iditeration, not idideration)
- **SSL:** Let's Encrypt cert, auto-renew configured
- **Git:** initialized locally, no remote yet (needs: `git remote add origin git@github.com/Erstiv/iditeration.git && git push -u origin main`)

### The 9 Agents (execution order)
| # | Agent | Model | Status |
|---|-------|-------|--------|
| 0 | Research Agent | Flash | Working — Google Search grounding, 2-step (search → synthesize), fallback if grounding returns None |
| 1 | Intake Analyst | Flash | Working |
| 2 | Behavioral Scientist | Pro | Working |
| 3 | Psychometrics Expert | Pro | Working |
| 4 | Competitive Intelligence | Flash | Working |
| 5 | Social Strategist | Flash | Working — was failing with JSON parse errors, fixed with `response_schema` constrained decoding |
| 6 | Chief Strategist | Pro | Working — was failing with 503s, fixed with retry logic covering 503/unavailable |
| 7 | Creative Director | Pro | Working |
| 8 | Stakeholder Agent | Flash | Available, runs standalone or in pipeline |

### Key Files
```
app/main.py                    — FastAPI app, lifespan (DB init, user creation, bible seeding)
app/config.py                  — Env vars, agent model mapping, AGENT_MAX_TOKENS=65536
app/models.py                  — SQLAlchemy models (Project, CrewRun, AgentRun, BibleEntry, AgentNote, ResearchCitation)
app/database.py                — Engine setup (SQLite-aware, no pool for SQLite)
app/crews/crew_runner.py       — Sequential agent orchestration, rerun_single_agent(), continue_crew_run()
app/crews/marketing_bible.py   — MarketingBibleTool — read/write interface for knowledge base
app/crews/agents/base.py       — BaseAgent: Gemini calls with response_schema, exponential backoff (429/503), 300s timeout, 6-level JSON parse/repair
app/crews/agents/research_agent.py  — Agent 0, Google Search grounding, structured sources_cited output
app/crews/agents/*.py          — All other agents (each sets output_schema from prompt file)
app/output/docx_generator.py   — Adaptive DOCX generator with annotated bibliography
app/output/html_renderer.py    — HTML fragment renderer with bibliography cards
app/routes/projects.py         — All routes: dashboard, project CRUD, runs, file parsing, bible, stakeholders, ask/refocus, delete
app/templates/                 — base.html, dashboard.html, project.html, run_status.html, new_project.html
app/templates/partials/        — _agent_chat.html, _agent_output.html, _note_item.html
prompts/__init__.py            — Shared SOURCES_CITED_SCHEMA + SOURCES_CITED_PROMPT (used by all agents)
prompts/00-08_*.py             — System prompts + output schemas for each agent (all include citation support)
marketing_bible_seed/seed_data.json — 40 entries, ~125KB
```

### Stability Fixes (this session)
1. **Social Strategist JSON parse failures** — Root cause: `response_mime_type="application/json"` doesn't guarantee valid JSON on large outputs. Fix: all agents now pass their `output_schema` to Gemini's `response_schema` parameter for constrained decoding. Invalid JSON is now structurally impossible.
2. **503/Unavailable retries** — `_call_gemini()` now retries on 429, 503, "unavailable", "high demand", "resource_exhausted" with exponential backoff (5s, 10s, 20s, 40s).
3. **300s hard timeout** — ThreadPoolExecutor wraps Gemini calls to prevent indefinite hangs.
4. **JSON parse pipeline** — 6 attempts: direct parse, control char escape, trailing commas, outermost object extraction, outermost+commas, Gemini self-repair.
5. **output_raw saved before parsing** — raw Gemini text saved to DB immediately, so even if parsing fails you can inspect the raw output.

### Tier 1 Human-in-the-Loop (this session)
1. **View/Hide Output toggle** — View Output button loads HTML-rendered agent output, toggles visibility
2. **Export Single Agent DOCX** — per-agent Word doc export with annotated bibliography
3. **Rerun Single Agent** — re-executes one agent with prior outputs intact
4. **Continue Pipeline** — resumes from first PENDING agent after a stall/failure
5. **Ask Mode** — Q&A with agents about their output (stored as AgentNote, uses Gemini with agent's system prompt + original output as context)
6. **Push to Bible** — promote any Ask Mode answer to a Product Bible entry
7. **Refocus Mode** — add a mandatory DIRECTIVE to Product Bible + rerun agent
8. **Delete Project** — with confirmation dialog
9. **Selective Agent Runs** — checkbox UI to run only specific agents (inline flex layout)
10. **Active Directives banner** — red-tinted card on run status page showing all active directives

### Citation System (this session)
- **All 9 agents** now include `sources_cited` in their output schema and system prompts
- Each citation has: `url`, `title`, `description` (1 sentence about source), `finding` (1 sentence about what we learned)
- **`prompts/__init__.py`** — shared `SOURCES_CITED_SCHEMA` dict + `SOURCES_CITED_PROMPT` text fragment, imported by all prompt files
- **SKIP_KEYS** — `sources_cited` and `sources` excluded from inline rendering (shown in bibliography only)
- **DOCX bibliography** — "Annotated Bibliography" section at end of both full pipeline and single-agent exports. Numbered entries with title, URL, "Contains:", "Key finding:"
- **HTML bibliography** — accent-bordered cards at bottom of each agent's View Output
- **Backward compatible** — old runs with `sources` (plain URL arrays) still render with domain name as title
- **Research Agent** — synthesis prompt updated to produce structured `sources_cited` instead of plain URL array

### Key Technical Details
- **`_flex_get()`** in `social_strategist.py` — normalizes dict keys (lowercase + strip non-alphanumeric) for case/format-insensitive lookup. Fixes key mismatch between agents.
- **`response_schema`** in `base.py` `_call_gemini()` — if `self.output_schema` is non-empty, passes it to Gemini for constrained decoding. All agents set `output_schema = _p.*_OUTPUT_SCHEMA`.
- **AgentNote model** — stores Ask/Refocus Q&A: question, answer, model_used, tokens, cost, nullable bible_entry_id FK
- **AGENT_CLASS_MAP** — maps AgentName enum to agent class, used by routes for Ask Mode Gemini calls

### Knowledge Base System
- **Marketing Bible (Global):** 40 seed entries across 8 categories
- **Product Bible (Per-Project):** Agents auto-write, manual entries via UI, Ask Mode push-to-bible
- **Directives category:** Renders as `!!! MANDATORY DIRECTIVES !!!` in agent prompts. Sorted first.

### Deployment Commands
```bash
# Deploy to Hetzner
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.db' --exclude='.env' --exclude='.git' /Users/JERS/Idideration/ filou:/opt/idideration/
ssh filou "systemctl restart idideration"

# Check status
ssh filou "systemctl status idideration"
ssh filou "journalctl -u idideration --no-pager -n 30"

# IMPORTANT: Before restarting, check for active runs:
# ssh filou "sqlite3 /opt/idideration/idideration.db \"SELECT id, status FROM crew_runs WHERE status='running';\""
```

### .env (both local and Hetzner)
```
DATABASE_URL=sqlite:///idideration.db  (local) or sqlite:////opt/idideration/idideration.db (Hetzner)
GEMINI_API_KEY=<in .env file, not committed — rotate if exposed>
SESSION_SECRET=<random>
NARRALYTICA_API_URL=http://localhost:8005/api
APP_HOST=0.0.0.0 (local) or 127.0.0.1 (Hetzner)
APP_PORT=8006 (local) or 8011 (Hetzner)
```

### Known Issues / TODO
1. **GitHub remote not set up** — needs `git remote add origin git@github.com/Erstiv/iditeration.git && git push -u origin main`
2. **File upload parsing** — drag-and-drop built but not verified end-to-end on production
3. **Social Strategist prompt quality** — key mismatch fixed, JSON fixed, but output quality may still need prompt tuning
4. **No auth** — single user (Elliot), user_id=1 hardcoded
5. **SQLite on Hetzner** — fine for single user, would need PostgreSQL for multi-user
6. **ResearchCitation model** — exists in DB but is never populated (citations live in agent output JSON instead)

### Future Tiers
- **Tier 2:** Edit agent output JSON directly, add guidance before rerun
- **Tier 3:** Google Drive integration
- **Auth/OAuth:** Deferred pending basic stability

### Related Projects
- **Narralytica** (`/Users/JERS/narralytica/`) — Video intelligence platform. Intake Analyst can fetch scene-level data from Narralytica API.
- **Cassian** (`/Users/JERS/Cassian/`) — Book editing AI, same architecture pattern.

### Port Map (Hetzner — ssh filou)
8011: Idideration
8005: Narralytica API
(see Narralytica HANDOFF.md for full port map)
