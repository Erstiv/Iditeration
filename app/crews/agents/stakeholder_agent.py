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

        # Product Bible context
        sections.append(self.bible.to_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        # Pass ALL prior agent outputs — this agent runs last and needs to see everything
        agent_labels = {
            "research_agent": "Research Agent (External Research)",
            "intake_analyst": "Intake Analyst (Product Assessment)",
            "behavioral_scientist": "Behavioral Scientist (Behavioral Framework)",
            "psychometrics_expert": "Psychometrics Expert (Audience Segments)",
            "competitive_intelligence": "Competitive Intelligence (Competitor Landscape)",
            "social_strategist": "Social Strategist (Platform & Content Strategy)",
            "chief_strategist": "Chief Strategist (Grand Strategy)",
            "creative_director": "Creative Director (Campaign Concepts)",
        }
        for agent_key, label in agent_labels.items():
            if agent_key in prior_outputs:
                sections.append(f"=== OUTPUT FROM: {label.upper()} ===")
                sections.append(json.dumps(prior_outputs[agent_key], indent=2, default=str)[:20000])
                sections.append(f"=== END {agent_key.upper()} ===\n")

        # One-time rerun guidance (if provided)
        if self.agent_run.rerun_guidance:
            sections.append("=== ONE-TIME INSTRUCTION (from user) ===")
            sections.append(self.agent_run.rerun_guidance)
            sections.append("=== END INSTRUCTION ===\n")

        sections.append("=== YOUR TASK ===")
        sections.append("Analyze ALL agent outputs above. Identify knowledge gaps — things agents had to assume, guess, or skip.")
        sections.append("Generate targeted stakeholder interview questions that would fill those gaps.")
        sections.append("Focus on insider knowledge that can't be found through external research.")
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
