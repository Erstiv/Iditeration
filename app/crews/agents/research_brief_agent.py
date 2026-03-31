"""Research Brief Agent — standalone deep-research tool.

Not part of the pipeline. Takes a one-off question from the user, uses Google
Search grounding to gather evidence, then synthesises a structured research brief.
"""
import json
import logging
import re
import time
from datetime import datetime, timezone
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.config import GEMINI_API_KEY, AGENT_TEMPERATURE, AGENT_MAX_TOKENS
from app.models import ResearchBrief, RunStatus, Project

logger = logging.getLogger("idideration.research_brief_agent")

_MODEL = "gemini-2.5-flash"

_SYSTEM_PROMPT = """You are a world-class research analyst with deep expertise across neuroscience, behavioral psychology, marketing science, media studies, and consumer behavior. You have access to Google Search and can find real, current information.

When given a question, you:
1. Search thoroughly using multiple relevant queries
2. Synthesise findings from academic research, industry studies, and real-world examples
3. Distinguish between well-established findings vs. emerging/contested ideas
4. Connect insights directly to practical marketing and audience strategy implications
5. Always cite your sources

Be direct. If there is a clear consensus, state it. Be honest about uncertainty. Always bring findings back to what this means for marketing strategy and audience reach. Cite real URLs wherever possible.
"""

_SYNTHESIS_SYSTEM = (
    "You are a research synthesiser. Take raw research findings and organise them "
    "into a clean, structured JSON format. Be thorough. Where information is uncertain, "
    "note the confidence level. Every sentence should add value — no padding."
)


def run_research_brief(db: Session, brief_id: int) -> None:
    """Execute a research brief in the background. Updates the ResearchBrief record."""
    brief = db.query(ResearchBrief).filter(ResearchBrief.id == brief_id).first()
    if not brief:
        logger.error(f"ResearchBrief {brief_id} not found")
        return

    brief.status = RunStatus.RUNNING
    brief.started_at = datetime.now(timezone.utc)
    brief.model_used = _MODEL
    db.commit()

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        # ── Grab project context ────────────────────────────────────────────────
        project = db.query(Project).filter(Project.id == brief.project_id).first()
        project_context = ""
        if project:
            project_context = (
                f"\n\n=== PROJECT CONTEXT ===\n"
                f"This question is being asked in the context of a marketing project for: "
                f"{project.name} ({project.project_type.value.replace('_', ' ')})\n"
            )
            if project.description:
                project_context += f"Project description: {project.description}\n"
            project_context += (
                "Please tailor your research and implications to this product/audience where relevant."
            )

        # ── Step 1: Google Search grounding ────────────────────────────────────
        logger.info(f"Research Brief {brief_id}: Step 1 — searching with Google grounding...")
        search_tool = types.Tool(google_search=types.GoogleSearch())
        search_prompt = (
            f"=== RESEARCH QUESTION ===\n\n"
            f"{brief.question}"
            f"{project_context}\n\n"
            f"=== YOUR TASK ===\n\n"
            f"Research this question thoroughly. Search for:\n"
            f"- Academic studies, meta-analyses, and peer-reviewed research\n"
            f"- Industry reports, case studies, and real-world examples\n"
            f"- Statistics, data points, and measurable findings\n"
            f"- Expert opinions and practitioner perspectives\n"
            f"- Counterarguments and limitations of the research\n\n"
            f"Gather as much evidence as possible from multiple angles."
        )

        # Retry up to 3 times with backoff
        raw_research = ""
        search_tokens_in = 0
        search_tokens_out = 0
        for attempt in range(3):
            try:
                search_response = client.models.generate_content(
                    model=_MODEL,
                    contents=search_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=_SYSTEM_PROMPT,
                        temperature=AGENT_TEMPERATURE,
                        max_output_tokens=AGENT_MAX_TOKENS,
                        tools=[search_tool],
                    ),
                )
                raw_research = search_response.text or ""
                if not raw_research:
                    try:
                        parts = search_response.candidates[0].content.parts
                        raw_research = "\n".join(
                            p.text for p in parts if hasattr(p, "text") and p.text
                        )
                    except (IndexError, AttributeError):
                        pass
                if hasattr(search_response, "usage_metadata") and search_response.usage_metadata:
                    u = search_response.usage_metadata
                    search_tokens_in = getattr(u, "prompt_token_count", 0) or 0
                    search_tokens_out = getattr(u, "candidates_token_count", 0) or 0
                break
            except Exception as e:
                logger.warning(f"Research Brief {brief_id}: search attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))

        if not raw_research:
            logger.warning(f"Research Brief {brief_id}: grounded search empty, falling back...")
            fb = client.models.generate_content(
                model=_MODEL,
                contents=search_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                    temperature=AGENT_TEMPERATURE,
                    max_output_tokens=AGENT_MAX_TOKENS,
                ),
            )
            raw_research = fb.text or "No research data could be gathered."

        logger.info(f"Research Brief {brief_id}: Step 1 done. {len(raw_research)} chars gathered.")

        # ── Step 2: Synthesise into structured JSON ────────────────────────────
        logger.info(f"Research Brief {brief_id}: Step 2 — synthesising into JSON...")
        synthesis_prompt = (
            f"=== ORIGINAL QUESTION ===\n\n{brief.question}\n\n"
            f"=== RAW RESEARCH FINDINGS ===\n\n{raw_research}\n\n"
            f"=== SYNTHESIS TASK ===\n\n"
            f"Based on the research findings above, produce a single valid JSON object with these fields:\n\n"
            f'- "question": the original question (verbatim)\n'
            f'- "summary": a clear, direct 2–3 paragraph answer to the question (no hedging)\n'
            f'- "background_context": key concepts needed to understand the answer\n'
            f'- "key_findings": array of objects, each with "finding" (1-2 sentences), '
            f'"confidence" ("high"/"medium"/"low"), "explanation" (detail/nuance), '
            f'"source_hint" (brief reference)\n'
            f'- "academic_perspective": what peer-reviewed research says — specific studies, theories\n'
            f'- "industry_perspective": how practitioners and brands apply this — real examples\n'
            f'- "data_points": array of objects, each with "stat" and "source"\n'
            f'- "implications_for_marketing": concrete ways this applies to marketing strategy '
            f'and audience work\n'
            f'- "caveats_and_limitations": what the research does not tell us, conflicts, context\n'
            f'- "related_topics": array of 3-5 related research areas worth exploring\n'
            f'- "sources_cited": array of objects, each with "url", "title", "description", "finding"\n\n'
            f"Return ONLY valid JSON. No markdown fences, no explanation."
        )

        synthesis_tokens_in = 0
        synthesis_tokens_out = 0
        for attempt in range(3):
            try:
                synthesis_response = client.models.generate_content(
                    model=_MODEL,
                    contents=synthesis_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=_SYNTHESIS_SYSTEM,
                        temperature=0.3,
                        max_output_tokens=AGENT_MAX_TOKENS,
                        response_mime_type="application/json",
                    ),
                )
                if hasattr(synthesis_response, "usage_metadata") and synthesis_response.usage_metadata:
                    u = synthesis_response.usage_metadata
                    synthesis_tokens_in = getattr(u, "prompt_token_count", 0) or 0
                    synthesis_tokens_out = getattr(u, "candidates_token_count", 0) or 0
                break
            except Exception as e:
                logger.warning(f"Research Brief {brief_id}: synthesis attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise

        raw_text = synthesis_response.text or ""
        brief.output_raw = raw_text

        # ── Parse JSON ─────────────────────────────────────────────────────────
        output = _parse_json(raw_text)
        # Ensure question is always present
        if isinstance(output, dict) and "question" not in output:
            output["question"] = brief.question

        # ── Token accounting ───────────────────────────────────────────────────
        total_in = search_tokens_in + synthesis_tokens_in
        total_out = search_tokens_out + synthesis_tokens_out
        brief.input_tokens = total_in
        brief.output_tokens = total_out
        # Flash pricing: $0.15/M in, $0.60/M out
        brief.cost_usd = round((total_in / 1_000_000) * 0.15 + (total_out / 1_000_000) * 0.60, 4)

        brief.output_json = output
        brief.status = RunStatus.COMPLETED
        brief.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Research Brief {brief_id}: completed. Cost: ${brief.cost_usd:.4f}")

    except Exception as e:
        logger.error(f"Research Brief {brief_id}: failed — {e}", exc_info=True)
        brief.status = RunStatus.FAILED
        brief.error_message = str(e)
        brief.completed_at = datetime.now(timezone.utc)
        db.commit()


def _parse_json(text: str) -> dict:
    """Parse JSON from model output with fallbacks."""
    if not text:
        return {}
    # Strip markdown fences if present
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean.strip())
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try to find first { ... }
        m = re.search(r"\{.*\}", clean, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    return {"summary": text, "error": "Could not parse structured output"}
