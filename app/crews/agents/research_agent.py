"""Agent 0: Research Agent — Uses Google Search grounding to research a product."""
import json
import logging
from google.genai import types
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import Project, BibleScope
from app.config import AGENT_TEMPERATURE, AGENT_MAX_TOKENS

logger = logging.getLogger("idideration.research_agent")

_p = load_prompt_module("00_research_agent")


class ResearchAgent(BaseAgent):
    agent_name = "research_agent"
    system_prompt = _p.RESEARCH_AGENT_SYSTEM_PROMPT

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        """Build the research prompt from project data."""
        sections = []
        project = self.db.query(Project).filter(Project.id == self.project_id).first()

        sections.append("=== PRODUCT TO RESEARCH ===")
        sections.append(f"Product Name: {project.name}")
        sections.append(f"Product Type: {project.project_type.value}")
        if project.description:
            sections.append(f"Description: {project.description}")
        if project.raw_data:
            sections.append(f"\nAdditional Context / Notes:\n{project.raw_data}")

        # Build specific search queries the agent should focus on
        name = project.name
        sections.append("\n=== SUGGESTED SEARCH QUERIES ===")
        sections.append(f'1. "{name}"')
        sections.append(f'2. "{name}" marketing')
        sections.append(f'3. "{name}" social media')
        sections.append(f'4. "{name}" reviews')
        sections.append(f'5. "{name}" competitors')
        sections.append(f'6. "{name}" {project.project_type.value.replace("_", " ")}')

        sections.append("\n=== YOUR TASK ===")
        sections.append(
            "Research this product thoroughly using Google Search. "
            "Find everything you can about the product, its marketing, "
            "its audience, its competition, and its reception. "
            "Return your findings as a single valid JSON object matching the schema "
            "described in your system prompt. Include product_bible_entries as an array "
            "of objects with 'category', 'title', and 'content' fields."
        )
        return "\n\n".join(sections)

    def _call_gemini(self, prompt: str) -> object:
        """Override to use Google Search grounding for research.

        Uses a two-step approach:
        1. First call with google_search tool to gather raw information
        2. Second call to synthesize into structured JSON output
        """
        # Step 1: Search and gather raw information with grounding
        logger.info("Research Agent: Step 1 — Searching with Google grounding...")
        search_tool = types.Tool(google_search=types.GoogleSearch())

        search_response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=AGENT_TEMPERATURE,
                max_output_tokens=AGENT_MAX_TOKENS,
                tools=[search_tool],
            ),
        )

        # Extract the raw research text — handle None/empty responses
        raw_research = search_response.text
        if not raw_research:
            # Try to extract from candidates/parts if .text is None
            try:
                parts = search_response.candidates[0].content.parts
                raw_research = "\n".join(
                    p.text for p in parts if hasattr(p, "text") and p.text
                )
            except (IndexError, AttributeError):
                raw_research = ""

            if not raw_research:
                # Fall back to a non-grounded search call
                logger.warning("Research Agent: Grounded search returned empty. Falling back to standard call...")
                fallback_response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        temperature=AGENT_TEMPERATURE,
                        max_output_tokens=AGENT_MAX_TOKENS,
                    ),
                )
                raw_research = fallback_response.text or "No research data could be gathered."

        logger.info(f"Research Agent: Step 1 complete. Raw research length: {len(raw_research)}")

        # Step 2: Synthesize into structured JSON
        logger.info("Research Agent: Step 2 — Synthesizing into structured JSON...")
        synthesis_prompt = (
            "=== RAW RESEARCH FINDINGS ===\n\n"
            f"{raw_research}\n\n"
            "=== SYNTHESIS TASK ===\n\n"
            "Based on the research findings above, produce a single valid JSON object "
            "with the following top-level keys:\n\n"
            '- "product_brief": object with keys: name, type, description, premise, '
            "key_people (array of strings), platform_distribution, release_timeline, "
            "financial_performance\n"
            '- "existing_marketing": object with keys: social_accounts (array), '
            "follower_counts (object), marketing_tactics (array), key_campaigns (array), "
            "website_urls (array)\n"
            '- "competitive_landscape": object with keys: direct_competitors (array), '
            "adjacent_competitors (array), unique_positioning (string)\n"
            '- "audience_signals": object with keys: primary_audiences (array), '
            "demographic_notes (array), reception_summary (string)\n"
            '- "research_gaps": array of strings describing what you could NOT find\n'
            '- "suggested_stakeholder_questions": array of strings — questions for the '
            "product owner about things you couldn't find\n"
            '- "product_bible_entries": array of objects, each with "category" (one of: '
            "product_overview, research_findings, audience_segments, competitive_data, "
            'social_data), "title" (string), and "content" (string)\n'
            '- "sources": array of URL strings where you found information\n\n'
            "Return ONLY valid JSON. No markdown, no explanation."
        )

        synthesis_response = self.client.models.generate_content(
            model=self.model,
            contents=synthesis_prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a research synthesizer. Take raw research findings and "
                    "organize them into a clean, structured JSON format. Be thorough "
                    "and include all findings. Where information was not found, explicitly "
                    "note it in the research_gaps array."
                ),
                temperature=0.3,
                max_output_tokens=AGENT_MAX_TOKENS,
                response_mime_type="application/json",
            ),
        )

        # Track tokens from both calls
        total_input = 0
        total_output = 0
        for resp in [search_response, synthesis_response]:
            if hasattr(resp, "usage_metadata") and resp.usage_metadata:
                usage = resp.usage_metadata
                total_input += getattr(usage, "prompt_token_count", 0) or 0
                total_output += getattr(usage, "candidates_token_count", 0) or 0

        # Store combined usage on the synthesis response for the base class to read
        # We create a simple namespace to hold the combined values
        class CombinedUsage:
            prompt_token_count = total_input
            candidates_token_count = total_output

        synthesis_response.usage_metadata = CombinedUsage()

        return synthesis_response
