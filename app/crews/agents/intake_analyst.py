"""Agent 1: Intake Analyst — Product assessment and initial analysis."""
import json
import httpx
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import Project, BibleScope
from app.config import NARRALYTICA_API_URL

_p = load_prompt_module("01_intake_analyst")


class IntakeAnalystAgent(BaseAgent):
    agent_name = "intake_analyst"
    system_prompt = _p.INTAKE_ANALYST_SYSTEM_PROMPT
    output_schema = _p.INTAKE_ANALYST_OUTPUT_SCHEMA

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []
        project = self.db.query(Project).filter(Project.id == self.project_id).first()

        sections.append("=== PRODUCT DATA ===")
        sections.append(f"Product Name: {project.name}")
        sections.append(f"Product Type: {project.project_type.value}")
        if project.description:
            sections.append(f"Description: {project.description}")
        if project.raw_data:
            sections.append(f"\nRaw Product Data / Notes:\n{project.raw_data}")

        if project.narralytica_show_id:
            nd = self._fetch_narralytica(project.narralytica_show_id)
            if nd:
                sections.append("\n=== NARRALYTICA CONTENT INTELLIGENCE ===")
                sections.append(json.dumps(nd, indent=2, default=str)[:20000])

        sections.append(self.bible.to_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))
        sections.append("\n=== YOUR TASK ===\nProduce your Product Assessment as valid JSON. Return ONLY valid JSON.")
        return "\n\n".join(sections)

    def _fetch_narralytica(self, show_id: int) -> dict | None:
        try:
            with httpx.Client(timeout=30) as c:
                show = c.get(f"{NARRALYTICA_API_URL}/library/shows/{show_id}").json()
                eps = c.get(f"{NARRALYTICA_API_URL}/episodes/", params={"show_id": show_id}).json()
                analytics = {}
                for ep in eps[:5]:
                    eid = ep.get("id")
                    if eid:
                        r = c.get(f"{NARRALYTICA_API_URL}/analytics/mood-timeline/{eid}")
                        if r.status_code == 200:
                            analytics[f"episode_{eid}"] = r.json()
                r = c.get(f"{NARRALYTICA_API_URL}/analytics/screen-time/{show_id}")
                if r.status_code == 200:
                    analytics["screen_time"] = r.json()
                return {"show": show, "episodes": eps, "analytics": analytics}
        except Exception:
            return None
