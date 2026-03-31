"""Agent 7: Creative Director — Creative brief, messaging, CTAs, art direction."""
import json
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope

_p = load_prompt_module("07_creative_director")


class CreativeDirectorAgent(BaseAgent):
    agent_name = "creative_director"
    system_prompt = _p.CREATIVE_DIRECTOR_SYSTEM_PROMPT
    output_schema = _p.CREATIVE_DIRECTOR_OUTPUT_SCHEMA

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        sections.append(self.bible.to_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_full_prompt_text(BibleScope.PROJECT))

        # All prior agents — creative director needs the full picture
        agent_order = [
            "intake_analyst",
            "behavioral_scientist",
            "psychometrics_expert",
            "competitive_intelligence",
            "social_strategist",
            "chief_strategist",
        ]
        for agent_name in agent_order:
            if agent_name in prior_outputs:
                label = agent_name.replace("_", " ").title()
                sections.append(f"\n=== OUTPUT FROM: {label} ===")
                # Chief Strategist gets full output — it's the strategy foundation
                max_len = 40000 if agent_name == "chief_strategist" else 25000
                sections.append(json.dumps(prior_outputs[agent_name], indent=2, default=str)[:max_len])

        sections.append("\n=== YOUR TASK ===")
        sections.append("Create the Creative Brief, messaging architecture, and campaign deliverables.")
        sections.append("Every creative recommendation must trace to a strategic or behavioral rationale.")
        sections.append("Sample messages should be polished, usable copy.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
