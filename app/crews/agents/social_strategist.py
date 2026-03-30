"""Agent 5: Social Strategist — Platform audit, content strategy, influencer mapping."""
import json
import re
from app.crews.agents.base import BaseAgent
from app.crews.agents._load_prompt import load_prompt_module
from app.models import BibleScope

_p = load_prompt_module("05_social_strategist")


def _flex_get(d: dict, key: str, default=None):
    """Get a value from a dict, matching keys case/format-insensitively.

    Normalizes both the target key and dict keys by lowercasing and stripping
    all non-alphanumeric characters, so 'product_summary', 'Product Summary',
    and 'productSummary' all match each other.
    """
    if not isinstance(d, dict):
        return default
    norm = re.sub(r"[^a-z0-9]", "", key.lower())
    for k, v in d.items():
        if re.sub(r"[^a-z0-9]", "", k.lower()) == norm:
            return v
    return default


class SocialStrategistAgent(BaseAgent):
    agent_name = "social_strategist"
    system_prompt = _p.SOCIAL_STRATEGIST_SYSTEM_PROMPT

    def _build_prompt(self, prior_outputs: dict[str, dict]) -> str:
        sections = []

        sections.append(self.bible.to_prompt_text(BibleScope.GLOBAL))
        sections.append(self.bible.to_prompt_text(BibleScope.PROJECT))

        if "intake_analyst" in prior_outputs:
            sections.append("=== PRODUCT ASSESSMENT (from Intake Analyst) ===")
            intake = prior_outputs["intake_analyst"]
            sections.append(json.dumps({
                "product_summary": _flex_get(intake, "product_summary"),
                "content_asset_inventory": _flex_get(intake, "content_asset_inventory"),
                "audience_gravity_wells": _flex_get(intake, "audience_gravity_wells"),
                "platform_distribution_context": _flex_get(intake, "platform_distribution_context"),
            }, indent=2, default=str))

        if "psychometrics_expert" in prior_outputs:
            sections.append("\n=== AUDIENCE SEGMENTS (from Psychometrics Expert) ===")
            psych = prior_outputs["psychometrics_expert"]
            # Segments live under varying keys — try known variants
            seg_list = (
                _flex_get(psych, "audience_segments")
                or _flex_get(psych, "part1_psychometric_audience_map")
                or _flex_get(psych, "part1_psychometricAudienceMap")
                or []
            )
            segments = []
            for seg in seg_list:
                segments.append({
                    "segment_name": (
                        _flex_get(seg, "segment_name")
                        or _flex_get(seg, "segment_identity")
                    ),
                    "one_line_description": _flex_get(seg, "one_line_description"),
                    "behavioral_predictions": _flex_get(seg, "behavioral_predictions"),
                    "messaging_dna": _flex_get(seg, "messaging_dna"),
                    "psychometric_profile": _flex_get(seg, "psychometric_profile"),
                })
            sections.append(json.dumps(segments, indent=2, default=str))

        if "competitive_intelligence" in prior_outputs:
            sections.append("\n=== COMPETITIVE AUDIT (from Competitive Intelligence) ===")
            comp = prior_outputs["competitive_intelligence"]
            # Profiles may be top-level or nested under 'competitive_analysis'
            profiles = (
                _flex_get(comp, "deep_profiles")
                or _flex_get(comp, "deep_competitor_profiles")
            )
            if not profiles:
                nested = _flex_get(comp, "competitive_analysis")
                if isinstance(nested, dict):
                    profiles = (
                        _flex_get(nested, "deep_profiles")
                        or _flex_get(nested, "deep_competitor_profiles")
                        or []
                    )
            social_data = []
            for profile in (profiles or []):
                social_data.append({
                    "name": _flex_get(profile, "name"),
                    "social_presence": _flex_get(profile, "social_presence"),
                })
            sections.append(json.dumps(social_data, indent=2, default=str))

        sections.append("\n=== YOUR TASK ===")
        sections.append("Conduct social media audit and build platform-specific content strategies.")
        sections.append("Find real influencers with real follower counts.")
        sections.append("Return ONLY valid JSON.")
        return "\n\n".join(sections)
