"""Agent 3: Psychometrics Expert — Audience segmentation and persona development."""
import json
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope

_p = load_prompt_module("03_psychometrics_expert")


class PsychometricsExpertAgent(BaseAgent):
    agent_name = "psychometrics_expert"
    system_prompt = _p.PSYCHOMETRICS_EXPERT_SYSTEM_PROMPT

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        sections.append(self.bible.to_full_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        if "intake_analyst" in prior_outputs:
            sections.append("=== PRODUCT ASSESSMENT (from Intake Analyst) ===")
            sections.append(json.dumps(prior_outputs["intake_analyst"], indent=2, default=str)[:30000])

            directives = prior_outputs["intake_analyst"].get("Research Directives",
                         prior_outputs["intake_analyst"].get("research_directives", []))
            if isinstance(directives, list):
                sections.append("\n=== RESEARCH DIRECTIVES ===")
                for d in directives:
                    sections.append(f"  - {d}" if isinstance(d, str) else f"  - {json.dumps(d)}")
            elif isinstance(directives, dict) and directives.get("for_psychometrics_expert"):
                sections.append("\n=== SPECIFIC RESEARCH DIRECTIVES FOR YOU ===")
                for d in directives["for_psychometrics_expert"]:
                    sections.append(f"  - {d}")

        if "behavioral_scientist" in prior_outputs:
            sections.append("\n=== BEHAVIORAL FRAMEWORK (from Behavioral Scientist) ===")
            sections.append(json.dumps(prior_outputs["behavioral_scientist"], indent=2, default=str)[:30000])

        sections.append("\n=== YOUR TASK ===")
        sections.append("Build detailed psychometric audience profiles.")
        sections.append("Ground every claim in validated frameworks (OCEAN, VALS, Schwartz, Haidt).")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
