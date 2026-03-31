"""Shared prompt fragments and schema components for all agents."""

# ── Citation schema fragment ──────────────────────────────────────
# Added to every agent's output_schema so Gemini constrained decoding
# guarantees valid citation JSON.

SOURCES_CITED_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "url":         {"type": "string"},
            "title":       {"type": "string"},
            "description": {"type": "string"},
            "finding":     {"type": "string"},
        },
    },
}

# ── Citation prompt fragment ──────────────────────────────────────
# Appended to every agent's system prompt.

SOURCES_CITED_PROMPT = """

## CITATION REQUIREMENTS
You MUST include a `sources_cited` array in your JSON output. For every claim, statistic, framework, or recommendation that draws on external information, cite the source.

Each citation object has four fields:
- `url` — the full URL where the information was found (use the most direct link available; if no URL exists, use "N/A")
- `title` — short name or title of the source (e.g., "Nielsen Social Media Report 2025", "Harvard Business Review: Brand Trust Study")
- `description` — ONE sentence describing what this source contains
- `finding` — ONE sentence describing the specific insight or data point you drew from it for this analysis

Aim for at least 3 citations. More is better when your analysis draws on many sources. Include academic papers, industry reports, platform documentation, news articles, and any other external references that support your output.
"""
