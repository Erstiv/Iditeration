"""Agent 2: Behavioral Scientist — Neuroscience research and behavioral frameworks."""
import json
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope

_p = load_prompt_module("02_behavioral_scientist")


class BehavioralScientistAgent(BaseAgent):
    agent_name = "behavioral_scientist"
    system_prompt = _p.BEHAVIORAL_SCIENTIST_SYSTEM_PROMPT
    output_schema = _p.BEHAVIORAL_SCIENTIST_OUTPUT_SCHEMA

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        # Marketing Bible — full version for the neuroscience/behavioral sections
        sections.append(self.bible.to_full_prompt_text(BibleScope.GLOBAL))

        # Product Bible
        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        # Intake Analyst output (critical — contains research directives)
        if "intake_analyst" in prior_outputs:
            sections.append("=== PRODUCT ASSESSMENT (from Intake Analyst) ===")
            sections.append(json.dumps(prior_outputs["intake_analyst"], indent=2, default=str)[:30000])

            # Extract and highlight research directives (may be list or dict)
            directives = prior_outputs["intake_analyst"].get("Research Directives",
                         prior_outputs["intake_analyst"].get("research_directives", []))
            if isinstance(directives, list):
                sections.append("\n=== RESEARCH DIRECTIVES ===")
                for d in directives:
                    sections.append(f"  - {d}" if isinstance(d, str) else f"  - {json.dumps(d)}")
            elif isinstance(directives, dict) and directives.get("for_behavioral_scientist"):
                sections.append("\n=== SPECIFIC RESEARCH DIRECTIVES FOR YOU ===")
                for d in directives["for_behavioral_scientist"]:
                    sections.append(f"  - {d}")

        sections.append("\n=== YOUR TASK ===")
        sections.append("Conduct your behavioral science analysis. Find real academic research.")
        sections.append("Build a custom behavioral framework for this product.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
