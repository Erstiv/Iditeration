"""Shared prompt fragments and schema components for all agents."""

# ── Citation schema fragment ──────────────────────────────────────
# Added to every agent's output_schema so Gemini constrained decoding
# guarantees valid citation JSON.
#
# Updated 2026-04-15 in response to human-in-loop feedback:
#   - Users could not verify citations given only [Author, Journal, Year].
#   - They need article_title as a MINIMUM to search for a paper.
#   - Preferred: full MLA with a working URL.
#   - Agents must produce MORE sources per claim (old minimum of 3 was shallow).
#   - Better to skip a citation than fabricate one.

SOURCES_CITED_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            # Core verifiable identity — all four required for any academic claim.
            "authors":        {"type": "string"},   # "Smith, J., & Jones, K." or "Smith et al."
            "article_title":  {"type": "string"},   # the ACTUAL article/paper title (NOT the journal)
            "publication":    {"type": "string"},   # journal, book, outlet, report, platform docs
            "year":           {"type": "integer"},

            # Access
            "url":            {"type": "string"},   # direct link, or "N/A" if none exists
            "doi":            {"type": "string"},   # DOI if known, else ""

            # MLA-formatted one-liner the user can paste into a bibliography.
            # Format: Authors. "Article Title." Publication, Year, URL.
            "citation_mla":   {"type": "string"},

            # Context
            "description":    {"type": "string"},   # one sentence: what this source IS
            "finding":        {"type": "string"},   # one sentence: the specific insight drawn
            "relevance":      {"type": "string"},   # one sentence: why this applies to THIS product

            # Honesty signals
            "source_type":    {"type": "string"},   # "peer-reviewed" | "meta-analysis" | "book" | "industry-report" | "news" | "platform-docs" | "general-knowledge"
            "confidence":     {"type": "string"},   # "verified" (agent is certain this paper exists as cited) | "likely" (real author + real topic, title may be paraphrased) | "general-consensus" (no specific citation, stating field-level consensus)
        },
        "required": ["authors", "article_title", "publication", "year", "citation_mla", "finding", "confidence"],
    },
}

# ── Citation prompt fragment ──────────────────────────────────────
# Appended to every agent's system prompt.

SOURCES_CITED_PROMPT = """

## CITATION REQUIREMENTS — READ CAREFULLY

Downstream users need to VERIFY every citation. They cannot do that with just [Author, Journal, Year]. You must provide enough to look a paper up, and you must be honest when you cannot.

### What every citation MUST contain

Each entry in `sources_cited` is a JSON object with these fields:

- **`authors`** — Full author string, e.g., `"Knudsen, B., Rick, S., & Loewenstein, G."` or `"Knudsen et al."` when 4+ authors. Never leave blank.
- **`article_title`** — The EXACT title of the paper/article/chapter. This is the field users said was missing. It is NOT the journal name. Example: `"Neural predictors of purchases."` — that is the title. `"Neuron"` is the journal.
- **`publication`** — Journal, book, outlet, or report name. Example: `"Neuron"`, `"Journal of Consumer Research"`, `"Nielsen Audience Report 2024"`.
- **`year`** — 4-digit integer.
- **`url`** — A direct link. Use the paper's DOI resolver (`https://doi.org/...`), publisher page, or PubMed/JSTOR link when you know it. If no URL is known, write `"N/A"` — do NOT invent one.
- **`doi`** — DOI string if known, else `""`.
- **`citation_mla`** — One-line MLA-formatted citation the user can paste directly into a bibliography. Format: `Authors. "Article Title." Publication, Year, URL.` Example: `Knudsen, B., et al. "Neural Predictors of Purchases." Neuron, vol. 53, no. 1, 2007, pp. 147-156, https://doi.org/10.1016/j.neuron.2006.11.010.`
- **`description`** — One sentence: what the source contains.
- **`finding`** — One sentence: the specific insight you drew from it for this analysis.
- **`relevance`** — One sentence: why this matters for the current product/campaign.
- **`source_type`** — one of: `"peer-reviewed"`, `"meta-analysis"`, `"book"`, `"industry-report"`, `"news"`, `"platform-docs"`, `"general-knowledge"`.
- **`confidence`** — one of:
  - `"verified"` — you are certain the paper exists exactly as cited (authors + title + year all correct). Use sparingly and only when you are confident.
  - `"likely"` — the authors are real and worked on this topic; the title may be slightly paraphrased; year may be off by a year or two. The user should be able to find the real paper by searching authors + topic.
  - `"general-consensus"` — no specific paper; you are stating an established field-level finding. In this case, `article_title` should describe the consensus (e.g., `"Meta-analyses of variable-ratio reinforcement"`), `authors` should be `"Multiple researchers"` or a representative reviewer like `"Per Skinner, Ferster, and subsequent replications"`, and `url`/`doi` should be `"N/A"`.

### Anti-hallucination rule — CRITICAL

If you cannot produce `authors` AND `article_title` AND `year` with at least `"likely"` confidence, DO NOT fabricate a citation. Instead:
  - either cite a real paper you actually know (even if only at `"likely"` confidence), or
  - mark the entry as `"general-consensus"` and describe the field-level finding honestly.

A fabricated citation that the user cannot find will destroy trust in this entire report. The user explicitly said: *"If I don't have a link to the paper, I need [Author, Article Title, Year]."* Meet that bar or flag the gap.

### How many citations

Aim for **10–15 distinct sources per major analytical section** (e.g., for Behavioral Scientist: 10+ in the literature review alone; for Psychometrics: 10+ across segments; for Competitive Intelligence: 10+ sources).

A minimum of 10 applies to Behavioral Scientist, Psychometrics Expert, Competitive Intelligence, and Chief Strategist. Other agents should cite 3–5 at minimum but more when available. Depth beats breadth — a single study cited across three agents counts three times in the final bibliography deduplication, which is fine.

### Coverage

Every claim that relies on external evidence (neuroscience, psychology, economics, industry stats, platform behaviors, competitor performance) must have a corresponding entry in `sources_cited`. Unsourced claims should be framed as opinion or inference, not evidence.
"""
