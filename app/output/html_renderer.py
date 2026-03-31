"""
Recursive JSON-to-HTML renderer for agent outputs.
Mirrors docx_generator's adaptive rendering but outputs styled HTML fragments.
"""
import re

SKIP_KEYS = {
    "productName", "product_name", "analysisVersion", "analysis_version",
    "product_bible_entries", "psychometricAnalysisVersion", "productAnalyzed",
    "expertName", "expert_name", "analysisDate", "analysis_date",
    "preparedBy", "prepared_by", "version", "grandStrategyTitle",
    "behavioralScientist", "missing_information_alert",
    "sources_cited", "sources",  # rendered in bibliography section
}


def _humanize_key(key: str) -> str:
    """Convert camelCase or snake_case key to readable heading."""
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
    s = s.replace('_', ' ')
    s = re.sub(r'^part\s*\d+\s*', '', s, flags=re.IGNORECASE)
    return s.strip().title()


def _esc(text: str) -> str:
    """Escape HTML entities."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_value_html(value, depth=0) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return f'<p style="margin:0.25rem 0;line-height:1.5;">{_esc(value)}</p>' if value else ""
    if isinstance(value, bool):
        return f'<p style="margin:0.25rem 0;">{_esc(str(value))}</p>'
    if isinstance(value, (int, float)):
        return f'<p style="margin:0.25rem 0;">{_esc(str(value))}</p>'
    if isinstance(value, list):
        parts = []
        has_dicts = any(isinstance(item, dict) for item in value)
        if has_dicts:
            for item in value:
                if isinstance(item, dict):
                    parts.append(f'<div style="border-bottom:1px solid var(--border);padding:0.5rem 0;">{_render_dict_html(item, depth)}</div>')
                elif isinstance(item, str):
                    parts.append(f'<div style="padding:0.25rem 0;padding-left:1rem;">&#8226; {_esc(item)}</div>')
                else:
                    parts.append(_render_value_html(item, depth))
        else:
            items = "".join(
                f'<li style="margin:0.15rem 0;">{_esc(str(item))}</li>'
                for item in value if item
            )
            if items:
                parts.append(f'<ul style="margin:0.25rem 0;padding-left:1.25rem;">{items}</ul>')
        return "".join(parts)
    if isinstance(value, dict):
        return _render_dict_html(value, depth)
    return f'<p style="margin:0.25rem 0;">{_esc(str(value))}</p>'


def _render_dict_html(data: dict, depth=0) -> str:
    if not data:
        return ""

    simple = {}
    complex_ = {}
    for k, v in data.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, (str, int, float, bool)) and v != "":
            simple[k] = v
        elif isinstance(v, (list, dict)) and v:
            complex_[k] = v

    parts = []

    for k, v in simple.items():
        label = _humanize_key(k)
        parts.append(
            f'<p style="margin:0.3rem 0;line-height:1.5;">'
            f'<strong style="color:var(--text);">{_esc(label)}:</strong> '
            f'<span style="color:var(--text-dim);">{_esc(str(v))}</span></p>'
        )

    tag = f"h{min(depth + 3, 6)}"
    sizes = {3: "1rem", 4: "0.9rem", 5: "0.85rem", 6: "0.8rem"}
    size = sizes.get(min(depth + 3, 6), "0.8rem")

    for k, v in complex_.items():
        label = _humanize_key(k)
        parts.append(
            f'<{tag} style="font-size:{size};margin:0.75rem 0 0.25rem;color:var(--accent);">'
            f'{_esc(label)}</{tag}>'
        )
        parts.append(f'<div style="padding-left:0.75rem;">{_render_value_html(v, depth + 1)}</div>')

    return "".join(parts)


def _render_bibliography_html(output_json: dict) -> str:
    """Render annotated bibliography from sources_cited / legacy sources."""
    sources = output_json.get("sources_cited", [])
    legacy = output_json.get("sources", [])
    combined = list(sources)
    for url in legacy:
        if isinstance(url, str):
            combined.append({
                "url": url,
                "title": url.split("//")[-1].split("/")[0],
                "description": "",
                "finding": "",
            })
    if not combined:
        return ""

    parts = [
        '<hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0 1rem;">',
        '<h3 style="font-size:1rem;color:var(--accent);margin-bottom:0.75rem;">Sources</h3>',
    ]
    for i, cite in enumerate(combined, 1):
        title = _esc(cite.get("title", "Untitled Source"))
        url = cite.get("url", "")
        desc = cite.get("description", "")
        finding = cite.get("finding", "")

        card = (
            f'<div style="border-left:3px solid var(--accent);padding:0.5rem 0.75rem;'
            f'margin-bottom:0.75rem;background:rgba(255,255,255,0.03);">'
            f'<div style="font-weight:600;font-size:0.9rem;color:var(--text);">[{i}] {title}</div>'
        )
        if url and url != "N/A":
            card += (
                f'<div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.15rem;'
                f'word-break:break-all;">{_esc(url)}</div>'
            )
        if desc:
            card += (
                f'<div style="font-size:0.85rem;margin-top:0.3rem;">'
                f'<span style="color:var(--text-dim);font-style:italic;">Contains: </span>'
                f'{_esc(desc)}</div>'
            )
        if finding:
            card += (
                f'<div style="font-size:0.85rem;margin-top:0.2rem;">'
                f'<span style="color:var(--text-dim);font-style:italic;">Key finding: </span>'
                f'{_esc(finding)}</div>'
            )
        card += '</div>'
        parts.append(card)

    return "".join(parts)


def render_agent_output_html(output_json: dict) -> str:
    """Render an agent's output JSON as a styled HTML fragment."""
    if not output_json:
        return '<p style="color:var(--text-dim);">No output available.</p>'
    filtered = {k: v for k, v in output_json.items() if k not in SKIP_KEYS and v}
    if not filtered:
        return '<p style="color:var(--text-dim);">Agent returned empty output.</p>'
    html = _render_dict_html(filtered, depth=0)
    html += _render_bibliography_html(output_json)
    return html
