"""Agent 4: Competitive Intelligence — Landscape mapping and competitor analysis."""
import json
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope

_p = load_prompt_module("04_competitive_intelligence")


class CompetitiveIntelligenceAgent(BaseAgent):
    agent_name = "competitive_intelligence"
    system_prompt = _p.COMPETITIVE_INTELLIGENCE_SYSTEM_PROMPT

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        sections.append(self.bible.to_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        if "intake_analyst" in prior_outputs:
            sections.append("=== PRODUCT ASSESSMENT (from Intake Analyst) ===")
            sections.append(json.dumps(prior_outputs["intake_analyst"], indent=2, default=str)[:25000])

        if "psychometrics_expert" in prior_outputs:
            sections.append("\n=== AUDIENCE SEGMENTS (from Psychometrics Expert) ===")
            # Only pass segment names and key behavioral predictions to keep context lean
            psych = prior_outputs["psychometrics_expert"]
            segments_summary = []
            for seg in psych.get("audience_segments", []):
                segments_summary.append({
                    "segment_name": seg.get("segment_name"),
                    "one_line_description": seg.get("one_line_description"),
                    "media_consumption_pattern": seg.get("behavioral_predictions", {}).get("media_consumption_pattern"),
                })
            sections.append(json.dumps(segments_summary, indent=2))

        sections.append("\n=== YOUR TASK ===")
        sections.append("Conduct comprehensive competitive audit using web search.")
        sections.append("Find real data — follower counts, revenue, ratings, etc.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
