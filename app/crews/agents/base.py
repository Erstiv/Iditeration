"""
Base Agent class — all Idideration agents inherit from this.
Handles Gemini API calls, context assembly, output parsing, and token tracking.
Mirrors Cassian's crew agent pattern.
"""
import json
import re
import time
from datetime import datetime, timezone
from typing import Optional
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from app.config import GEMINI_API_KEY, AGENT_MODELS, AGENT_TEMPERATURE, AGENT_MAX_TOKENS
from app.models import AgentRun, RunStatus, BibleCategory
from app.crews.marketing_bible import MarketingBibleTool, BibleScope


class BaseAgent:
    """Base class for all marketing crew agents."""

    agent_name: str = ""  # Override in subclass
    system_prompt: str = ""  # Override in subclass
    output_schema: dict = {}  # Override in subclass

    def __init__(self, db: Session, project_id: int, agent_run: AgentRun):
        self.db = db
        self.project_id = project_id
        self.agent_run = agent_run
        self.bible = MarketingBibleTool(db, project_id)
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = AGENT_MODELS.get(self.agent_name, "gemini-2.5-flash")

    def run(self, prior_outputs: dict[str, dict]) -> dict:
        """Execute the agent. Returns parsed JSON output."""
        self.agent_run.status = RunStatus.RUNNING
        self.agent_run.started_at = datetime.now(timezone.utc)
        self.agent_run.model_used = self.model
        self.db.commit()

        try:
            # Build the full prompt
            prompt = self._build_prompt(prior_outputs)
            self.agent_run.input_prompt = prompt[:50000]  # Store first 50K chars
            self.db.commit()

            # Call Gemini
            response = self._call_gemini(prompt)

            # Parse output
            output = self._parse_json_output(response.text)

            # Write any product bible entries the agent generated
            self._write_bible_entries(output)

            # Update run record
            self.agent_run.output_json = output
            self.agent_run.output_raw = response.text
            self.agent_run.status = RunStatus.COMPLETED
            self.agent_run.completed_at = datetime.now(timezone.utc)

            # Token tracking
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = response.usage_metadata
                self.agent_run.input_tokens = getattr(usage, "prompt_token_count", 0) or 0
                self.agent_run.output_tokens = getattr(usage, "candidates_token_count", 0) or 0
                self.agent_run.total_tokens = self.agent_run.input_tokens + self.agent_run.output_tokens
                self.agent_run.cost_usd = self._estimate_cost(
                    self.agent_run.input_tokens, self.agent_run.output_tokens
                )

            self.db.commit()
            return output

        except Exception as e:
            self.agent_run.status = RunStatus.FAILED
            self.agent_run.error_message = str(e)
            self.agent_run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            raise

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        """Assemble the full prompt with context. Override in subclass for custom context."""
        sections = []

        # Marketing Bible context (global knowledge)
        marketing_bible = self.bible.to_prompt_text(BibleScope.GLOBAL)
        sections.append(marketing_bible)

        # Product Bible context (project-specific)
        product_bible = self.bible.to_prompt_text(BibleScope.PROJECT)
        sections.append(product_bible)

        # Prior agent outputs
        for agent_name, output in prior_outputs.items():
            sections.append(f"=== OUTPUT FROM: {agent_name.upper()} ===")
            sections.append(json.dumps(output, indent=2, default=str)[:30000])
            sections.append(f"=== END {agent_name.upper()} ===\n")

        # Task instruction
        sections.append("=== YOUR TASK ===")
        sections.append("Analyze all the context above and produce your output as valid JSON.")
        sections.append("Follow the instructions in your system prompt exactly.")
        sections.append("Return ONLY valid JSON — no markdown, no explanation, just the JSON object.")

        return "\n\n".join(sections)

    def _call_gemini(self, prompt: str, max_retries: int = 4) -> object:
        """Make the Gemini API call with exponential backoff for rate limits."""
        import logging
        log = logging.getLogger("idideration.base_agent")

        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        temperature=AGENT_TEMPERATURE,
                        max_output_tokens=AGENT_MAX_TOKENS,
                        response_mime_type="application/json",
                    ),
                )
                return response
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "rate" in err_str or "quota" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < max_retries:
                    wait = 2 ** attempt * 5  # 5s, 10s, 20s, 40s
                    log.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}), waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise

    def _parse_json_output(self, text: str) -> dict:
        """Parse JSON from model output, with multiple fallback strategies."""
        cleaned = text.strip()
        # Strip markdown code fences
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        # Attempt 1: Direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Attempt 2: Fix common issues — trailing commas, unescaped newlines in strings
        fixed = re.sub(r",\s*([}\]])", r"\1", cleaned)  # trailing commas
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Attempt 3: Find the outermost JSON object
        brace_start = cleaned.find("{")
        brace_end = cleaned.rfind("}")
        if brace_start != -1 and brace_end != -1:
            subset = cleaned[brace_start:brace_end + 1]
            fixed_subset = re.sub(r",\s*([}\]])", r"\1", subset)
            try:
                return json.loads(fixed_subset)
            except json.JSONDecodeError:
                pass

        # Attempt 4: Ask Gemini to fix its own JSON (self-repair)
        import logging
        logging.getLogger("idideration.base_agent").warning(
            f"JSON parse failed after all attempts. Raw length: {len(cleaned)}. "
            f"Attempting Gemini self-repair..."
        )
        repair_response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"The following text was supposed to be valid JSON but has syntax errors. "
                     f"Fix it and return ONLY the corrected JSON, nothing else:\n\n{cleaned[:60000]}",
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=65536,
                response_mime_type="application/json",
            ),
        )
        repaired = repair_response.text.strip()
        repaired = re.sub(r"^```(?:json)?\s*\n?", "", repaired)
        repaired = re.sub(r"\n?```\s*$", "", repaired)
        return json.loads(repaired.strip())

    def _write_bible_entries(self, output: dict):
        """If the agent output includes product_bible_entries, write them."""
        entries = output.get("product_bible_entries") or []
        if isinstance(entries, list) and len(entries) > 0:
            try:
                self.bible.add_entries_bulk(entries, source=f"agent:{self.agent_name}")
            except Exception as e:
                import logging
                logging.getLogger("idideration.base_agent").warning(
                    f"Failed to write bible entries: {e}"
                )

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD based on model pricing (approximate 2025 rates)."""
        if "pro" in self.model:
            # Gemini 2.5 Pro pricing (approximate)
            input_cost = (input_tokens / 1_000_000) * 1.25
            output_cost = (output_tokens / 1_000_000) * 10.00
        else:
            # Gemini 2.5 Flash pricing (approximate)
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
        return round(input_cost + output_cost, 4)
