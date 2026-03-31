"""Agent 8: Stakeholder Agent — Interview question generation and answer processing."""
import json
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope, StakeholderQuestion
from datetime import datetime, timezone

_p = load_prompt_module("08_stakeholder_agent")


class StakeholderAgent(BaseAgent):
    agent_name = "stakeholder_agent"
    system_prompt = _p.STAKEHOLDER_AGENT_SYSTEM_PROMPT_GENERATE
    output_schema = _p.STAKEHOLDER_GENERATE_OUTPUT_SCHEMA

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        if "intake_analyst" in prior_outputs:
            sections.append("=== PRODUCT ASSESSMENT (from Intake Analyst) ===")
            sections.append(json.dumps(prior_outputs["intake_analyst"], indent=2, default=str)[:25000])

        sections.append("\n=== YOUR TASK ===")
        sections.append("Generate stakeholder interview questions based on the product assessment.")
        sections.append("Focus on questions whose answers can't be found through research.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)

    def _write_bible_entries(self, output: dict):
        """Override: also save generated questions to StakeholderQuestion table."""
        super()._write_bible_entries(output)

        framework = output.get("interview_framework", {})
        all_questions = []

        # Universal questions
        for q in framework.get("universal_questions", []):
            all_questions.append({
                "question": q.get("question", ""),
                "purpose": q.get("purpose", ""),
                "target_role": "all",
            })

        # Role-specific questions
        for role_set in framework.get("role_specific_questions", []):
            role = role_set.get("role", "general")
            for q in role_set.get("questions", []):
                all_questions.append({
                    "question": q.get("question", ""),
                    "purpose": q.get("what_it_reveals", q.get("purpose", "")),
                    "target_role": role,
                })

        # Gap-filling questions
        for q in framework.get("gap_filling_questions", []):
            all_questions.append({
                "question": q.get("question", ""),
                "purpose": q.get("strategic_impact_if_answered", ""),
                "target_role": "key_stakeholder",
            })

        # Provocative questions
        for q in framework.get("provocative_questions", []):
            all_questions.append({
                "question": q.get("question", ""),
                "purpose": q.get("what_it_surfaces", ""),
                "target_role": "leadership",
            })

        # Save to database
        for qdata in all_questions:
            sq = StakeholderQuestion(
                project_id=self.project_id,
                question=qdata["question"],
                purpose=qdata["purpose"],
                target_role=qdata["target_role"],
                is_generated=True,
            )
            self.db.add(sq)

        self.db.commit()


class StakeholderProcessAgent(BaseAgent):
    """Second mode: processes stakeholder answers back into the Product Bible."""
    agent_name = "stakeholder_agent"
    system_prompt = _p.STAKEHOLDER_AGENT_SYSTEM_PROMPT_PROCESS
    output_schema = _p.STAKEHOLDER_PROCESS_OUTPUT_SCHEMA

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        # Gather all answered questions
        answered = self.db.query(StakeholderQuestion).filter(
            StakeholderQuestion.project_id == self.project_id,
            StakeholderQuestion.answer.isnot(None),
        ).all()

        if answered:
            sections.append("=== STAKEHOLDER RESPONSES ===")
            for sq in answered:
                sections.append(f"Role: {sq.target_role}")
                sections.append(f"Q: {sq.question}")
                sections.append(f"A ({sq.answered_by or 'stakeholder'}): {sq.answer}\n")

        sections.append("\n=== YOUR TASK ===")
        sections.append("Extract all strategically relevant information from stakeholder answers.")
        sections.append("Write findings to the Product Bible.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
