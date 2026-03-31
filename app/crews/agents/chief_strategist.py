"""Agent 6: Chief Strategist — Grand strategy and multi-channel plan synthesis."""
import json
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope

_p = load_prompt_module("06_chief_strategist")


class ChiefStrategistAgent(BaseAgent):
    agent_name = "chief_strategist"
    system_prompt = _p.CHIEF_STRATEGIST_SYSTEM_PROMPT
    output_schema = _p.CHIEF_STRATEGIST_OUTPUT_SCHEMA

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        # Full Marketing Bible — the strategist needs all frameworks
        sections.append(self.bible.to_full_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_full_prompt_text(BibleScope.PROJECT))

        # All prior agent outputs — the strategist sees EVERYTHING
        agent_order = [
            "intake_analyst",
            "behavioral_scientist",
            "psychometrics_expert",
            "competitive_intelligence",
            "social_strategist",
        ]
        for agent_name in agent_order:
            if agent_name in prior_outputs:
                label = agent_name.replace("_", " ").title()
                sections.append(f"\n=== OUTPUT FROM: {label} ===")
                sections.append(json.dumps(prior_outputs[agent_name], indent=2, default=str)[:30000])

        # Stakeholder input if available
        from app.models import StakeholderQuestion
        stakeholder_qs = self.db.query(StakeholderQuestion).filter(
            StakeholderQuestion.project_id == self.project_id,
            StakeholderQuestion.answer.isnot(None),
        ).all()
        if stakeholder_qs:
            sections.append("\n=== STAKEHOLDER INPUT ===")
            for sq in stakeholder_qs:
                sections.append(f"Q: {sq.question}")
                sections.append(f"A ({sq.answered_by or 'stakeholder'}): {sq.answer}\n")

        sections.append("\n=== YOUR TASK ===")
        sections.append("Synthesize ALL agent outputs into a unified Grand Strategy and Multi-Channel Plan.")
        sections.append("Every recommendation must trace back to evidence from prior agents.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
