"""
DOCX Marketing Plan Generator — Adaptive version.
Walks agent output JSON trees and renders them regardless of key naming conventions.
"""
from datetime import datetime
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def _add_page_numbers(doc: Document):
    """Add centered page numbers to the document footer."""
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # "Page X of Y" using Word field codes
        run1 = p.add_run("Page ")
        run1.font.size = Pt(8)
        run1.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

        # PAGE field
        fld_page = OxmlElement("w:fldSimple")
        fld_page.set(qn("w:instr"), "PAGE")
        run_page = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "16")
        rpr.append(sz)
        color = OxmlElement("w:color")
        color.set(qn("w:val"), "999999")
        rpr.append(color)
        run_page.append(rpr)
        run_page_t = OxmlElement("w:t")
        run_page_t.text = "1"
        run_page.append(run_page_t)
        fld_page.append(run_page)
        p._element.append(fld_page)

        run2 = p.add_run(" of ")
        run2.font.size = Pt(8)
        run2.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

        # NUMPAGES field
        fld_total = OxmlElement("w:fldSimple")
        fld_total.set(qn("w:instr"), "NUMPAGES")
        run_total = OxmlElement("w:r")
        rpr2 = OxmlElement("w:rPr")
        sz2 = OxmlElement("w:sz")
        sz2.set(qn("w:val"), "16")
        rpr2.append(sz2)
        color2 = OxmlElement("w:color")
        color2.set(qn("w:val"), "999999")
        rpr2.append(color2)
        run_total.append(rpr2)
        run_total_t = OxmlElement("w:t")
        run_total_t.text = "1"
        run_total.append(run_total_t)
        fld_total.append(run_total)
        p._element.append(fld_total)


# ─── Agent display order and section titles ────────────────
AGENT_SECTIONS = [
    ("chief_strategist", "1. Executive Summary & Grand Strategy"),
    ("intake_analyst", "2. Product Assessment"),
    ("behavioral_scientist", "3. Behavioral Framework"),
    ("psychometrics_expert", "4. Audience Segmentation & Psychometrics"),
    ("competitive_intelligence", "5. Competitive Landscape"),
    ("social_strategist", "6. Social Media Strategy"),
    ("creative_director", "7. Creative Brief & Campaign Deliverables"),
]

# Keys to skip (metadata, not content)
SKIP_KEYS = {
    "productName", "product_name", "analysisVersion", "analysis_version",
    "product_bible_entries", "psychometricAnalysisVersion", "productAnalyzed",
    "expertName", "expert_name", "analysisDate", "analysis_date",
    "preparedBy", "prepared_by", "version", "grandStrategyTitle",
    "behavioralScientist", "missing_information_alert",
}


def _humanize_key(key: str) -> str:
    """Convert camelCase or snake_case key to readable heading."""
    import re
    # Handle camelCase
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
    # Handle snake_case
    s = s.replace('_', ' ')
    # Remove common prefixes like part1_, part2_
    s = re.sub(r'^part\s*\d+\s*', '', s, flags=re.IGNORECASE)
    # Title case
    s = s.strip().title()
    return s


def _render_value(doc, value, depth=2):
    """Recursively render a JSON value into the document."""
    if value is None:
        return

    if isinstance(value, str):
        if len(value) > 0:
            doc.add_paragraph(value)

    elif isinstance(value, bool):
        doc.add_paragraph(str(value))

    elif isinstance(value, (int, float)):
        doc.add_paragraph(str(value))

    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                doc.add_paragraph(item, style="List Bullet")
            elif isinstance(item, dict):
                _render_dict(doc, item, depth=depth)
                # Add small spacing between list items
            elif isinstance(item, list):
                for sub in item:
                    if isinstance(sub, str):
                        doc.add_paragraph(sub, style="List Bullet")
                    else:
                        _render_value(doc, sub, depth=depth)

    elif isinstance(value, dict):
        _render_dict(doc, value, depth=depth)


def _render_dict(doc, data: dict, depth=2):
    """Render a dictionary. Tries to be smart about structure."""
    if not data:
        return

    # Check if this looks like a simple key-value record (all string/number values)
    simple_values = {}
    complex_values = {}
    for k, v in data.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, (str, int, float, bool)) and v != "":
            simple_values[k] = v
        elif isinstance(v, (list, dict)) and v:
            complex_values[k] = v

    # Render simple values as bold-label paragraphs
    for k, v in simple_values.items():
        label = _humanize_key(k)
        p = doc.add_paragraph()
        run = p.add_run(f"{label}: ")
        run.bold = True
        run.font.size = Pt(10)
        p.add_run(str(v))

    # Render complex values with headings
    heading_level = min(depth, 4)  # Cap at Heading 4
    for k, v in complex_values.items():
        label = _humanize_key(k)
        if heading_level <= 3:
            doc.add_heading(label, level=heading_level)
        else:
            p = doc.add_paragraph()
            run = p.add_run(label)
            run.bold = True
            run.font.size = Pt(11)
        _render_value(doc, v, depth=heading_level + 1)


def generate_marketing_plan(
    project_name: str,
    project_type: str,
    agent_outputs: dict[str, dict],
    output_path: str,
    citations: list[dict] = None,
) -> str:
    """Generate the comprehensive marketing plan DOCX from all agent outputs."""
    doc = Document()
    _setup_styles(doc)

    # ─── Cover Page ─────────────────────────────────────────
    doc.add_paragraph("")
    doc.add_paragraph("")
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(project_name.upper())
    run.font.size = Pt(36)
    run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    run.bold = True

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("Comprehensive Marketing Strategy")
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0x6C, 0x6C, 0x80)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f"Generated {datetime.now().strftime('%B %d, %Y')}")
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    run = meta.add_run(f"\nProduct Type: {project_type.replace('_', ' ').title()}")
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    run = meta.add_run("\nPowered by Idideration")
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.italic = True

    cost_line = meta.add_run("\n\nBehavioral Science \u2022 Neuroscience \u2022 Psychometrics \u2022 Game Theory")
    cost_line.font.size = Pt(9)
    cost_line.font.color.rgb = RGBColor(0x99, 0x99, 0xBB)

    doc.add_page_break()

    # ─── Table of Contents ──────────────────────────────────
    doc.add_heading("Table of Contents", level=1)
    for _, section_title in AGENT_SECTIONS:
        p = doc.add_paragraph(section_title)
        p.style = doc.styles["List Number"]
    doc.add_page_break()

    # ─── Render each agent's output ─────────────────────────
    for agent_key, section_title in AGENT_SECTIONS:
        agent_data = agent_outputs.get(agent_key, {})

        doc.add_heading(section_title, level=1)

        if not agent_data:
            doc.add_paragraph("(No data from this agent.)")
            doc.add_page_break()
            continue

        # Filter out metadata keys
        filtered = {k: v for k, v in agent_data.items()
                    if k not in SKIP_KEYS and v}

        # Render the agent's output tree
        _render_dict(doc, filtered, depth=2)

        doc.add_page_break()

    # ─── Footer note ────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Generated by Idideration \u2022 idideration.com")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.italic = True

    # Add page numbers and save
    _add_page_numbers(doc)
    doc.save(output_path)
    return output_path


def generate_single_agent_docx(
    project_name: str,
    agent_key: str,
    agent_output: dict,
    output_path: str,
) -> str:
    """Generate a DOCX for a single agent's output."""
    doc = Document()
    _setup_styles(doc)

    # Look up section title from AGENT_SECTIONS
    section_title = None
    for key, title in AGENT_SECTIONS:
        if key == agent_key:
            section_title = title
            break
    if not section_title:
        section_title = _humanize_key(agent_key)

    doc.add_heading(f"{project_name} — {section_title}", level=1)

    meta = doc.add_paragraph()
    run = meta.add_run(f"Generated {datetime.now().strftime('%B %d, %Y')}")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.italic = True

    doc.add_paragraph("")

    filtered = {k: v for k, v in agent_output.items() if k not in SKIP_KEYS and v}
    if filtered:
        _render_dict(doc, filtered, depth=2)
    else:
        doc.add_paragraph("(No data from this agent.)")

    _add_page_numbers(doc)
    doc.save(output_path)
    return output_path


def _setup_styles(doc: Document):
    """Configure document styles."""
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    for level in range(1, 4):
        style_name = f"Heading {level}"
        if style_name in doc.styles:
            heading_style = doc.styles[style_name]
            heading_style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    # Ensure List Bullet 2 exists
    if "List Bullet 2" not in doc.styles:
        doc.styles.add_style("List Bullet 2", WD_STYLE_TYPE.PARAGRAPH)


def generate_stakeholder_questions_docx(
    project_name: str,
    questions: list[dict],
    output_path: str,
) -> str:
    """Generate a stakeholder interview questions document."""
    doc = Document()
    _setup_styles(doc)

    doc.add_heading(f"{project_name} \u2014 Stakeholder Interview Questions", level=1)
    doc.add_paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')}")
    doc.add_paragraph("")

    current_role = None
    for q in questions:
        role = q.get("target_role", "general")
        if role != current_role:
            current_role = role
            doc.add_heading(role.replace("_", " ").title(), level=2)

        doc.add_paragraph(q.get("question", ""), style="List Number")
        if q.get("purpose"):
            p = doc.add_paragraph(f"  Purpose: {q['purpose']}")
            p.runs[0].italic = True
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)

        doc.add_paragraph("  Answer: _______________________________________________")
        doc.add_paragraph("")

    _add_page_numbers(doc)
    doc.save(output_path)
    return output_path
