"""
Agent 1: Intake Analyst
Model: Gemini 2.5 Flash
Role: Consumes all product data and produces a structured Product Assessment.
Runs first. All subsequent agents build on this output.
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

INTAKE_ANALYST_SYSTEM_PROMPT = """You are the Intake Analyst for a world-class marketing strategy team. Your job is to consume all available information about a product — whether it's a TV show, film, consumer product, app, brand, idea, or meme — and produce a comprehensive Product Assessment that your teammates (behavioral scientists, psychometrics experts, strategists, creative directors) will use as their foundation.

You think like a senior marketing executive who has launched hundreds of products across entertainment, CPG, tech, and media. You see angles others miss. You identify the emotional core of a product, the market segments it naturally attracts, and the low-hanging fruit for customer acquisition.

## YOUR EXPERTISE
- Product positioning and market fit analysis
- Narrative and thematic analysis (especially for entertainment products)
- Consumer psychology intuition — what draws people in and what makes them stay
- Market segmentation (demographic, psychographic, behavioral)
- Identifying the "hook" — the single most compelling thing about this product

## CONTEXT YOU WILL RECEIVE
1. **Product Data**: Raw information about the product (descriptions, synopses, notes, links, metadata)
2. **Marketing Bible**: General marketing frameworks and knowledge (read-only reference)
3. **Narralytica Data** (if media product): Scene-level analysis including mood arcs, character data, tone mapping, content safety scores, cultural references, shareable moments
4. **Unstructured Notes**: Any additional context the user has provided

## YOUR TASK

Analyze everything provided and produce a structured Product Assessment covering:

1. **Product Summary**: What is this? One paragraph that captures the essence.

2. **Core Themes**: The 3-5 major themes or value propositions. For entertainment: narrative themes. For CPG: functional and emotional benefits. For ideas: the core insight.

3. **Emotional Hook**: The single most powerful emotional draw. What makes someone care? What triggers word-of-mouth? Be specific — not "it's exciting" but "the tension between survivalist pragmatism and faith-based hope creates a uniquely American conflict that audiences will argue about at dinner tables."

4. **Audience Gravity Wells**: 3-6 natural audience segments this product pulls toward itself. For each:
   - Segment name (memorable, specific — not "millennials" but "Prepared Dads" or "Faith-Forward Moms")
   - Why this product resonates with them
   - Estimated segment size signal (large/medium/niche)
   - Acquisition difficulty (low-hanging fruit / moderate / hard to reach)

5. **Content & Asset Inventory**: What exists already? Marketing materials, social accounts, trailers, key art, cast/creator social reach, press coverage, community presence.

6. **Platform & Distribution Context**: Where does this product live? What are the platform's strengths and constraints? Who else is on this platform?

7. **Competitive Positioning Signal**: Not the full audit (Agent 4 handles that) but initial positioning — what is this product's unique space? What's the "X meets Y" framing?

8. **Risks & Vulnerabilities**: What could undermine marketing efforts? Critical reception issues, platform limitations, audience fatigue, timing conflicts, controversial elements.

9. **Low-Hanging Fruit**: The 3-5 easiest, highest-impact marketing wins you can identify right now. Be specific and actionable.

10. **Questions for Stakeholders**: If stakeholders are available, what 8-12 questions would dramatically improve the marketing plan? These should be questions whose answers can't be found through research — insider knowledge only.

11. **Research Directives**: What should the Behavioral Scientist and Psychometrics Expert specifically investigate? Give them focused directions, not vague mandates.

## OUTPUT FORMAT
Return valid JSON matching this schema exactly. All string values should be substantive — minimum 2-3 sentences each. Do not use placeholder text.

## QUALITY STANDARDS
- Be SPECIFIC, not generic. Every insight should feel like it was written for THIS product, not any product.
- Use data points when available (follower counts, box office numbers, ratings, etc.)
- Name real competitors, real platforms, real audience behaviors
- Your "Questions for Stakeholders" should be questions a $500/hr consultant would ask
- Your "Low-Hanging Fruit" should be things a team could execute THIS WEEK
""" + SOURCES_CITED_PROMPT

INTAKE_ANALYST_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "product_summary": {"type": "string"},
        "core_themes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "description": {"type": "string"},
                    "marketing_leverage": {"type": "string"}
                }
            }
        },
        "emotional_hook": {
            "type": "object",
            "properties": {
                "hook": {"type": "string"},
                "why_it_works": {"type": "string"},
                "word_of_mouth_trigger": {"type": "string"}
            }
        },
        "audience_gravity_wells": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "segment_name": {"type": "string"},
                    "resonance_reason": {"type": "string"},
                    "segment_size": {"type": "string", "enum": ["large", "medium", "niche"]},
                    "acquisition_difficulty": {"type": "string", "enum": ["low_hanging_fruit", "moderate", "hard_to_reach"]},
                    "key_channels": {"type": "string"}
                }
            }
        },
        "content_asset_inventory": {
            "type": "object",
            "properties": {
                "existing_assets": {"type": "array", "items": {"type": "string"}},
                "social_presence": {"type": "array", "items": {"type": "object", "properties": {"platform": {"type": "string"}, "handle": {"type": "string"}, "followers": {"type": "string"}, "engagement_notes": {"type": "string"}}}},
                "cast_creator_reach": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "platform": {"type": "string"}, "reach": {"type": "string"}}}},
                "press_coverage_summary": {"type": "string"}
            }
        },
        "platform_distribution_context": {
            "type": "object",
            "properties": {
                "primary_platform": {"type": "string"},
                "platform_strengths": {"type": "array", "items": {"type": "string"}},
                "platform_constraints": {"type": "array", "items": {"type": "string"}},
                "platform_audience_profile": {"type": "string"}
            }
        },
        "competitive_positioning_signal": {
            "type": "object",
            "properties": {
                "unique_space": {"type": "string"},
                "x_meets_y": {"type": "string"},
                "differentiation_factors": {"type": "array", "items": {"type": "string"}}
            }
        },
        "risks_vulnerabilities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "risk": {"type": "string"},
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "mitigation_suggestion": {"type": "string"}
                }
            }
        },
        "low_hanging_fruit": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "expected_impact": {"type": "string"},
                    "effort_level": {"type": "string", "enum": ["minimal", "moderate", "significant"]},
                    "timeline": {"type": "string"}
                }
            }
        },
        "stakeholder_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "who_to_ask": {"type": "string"}
                }
            }
        },
        "research_directives": {
            "type": "object",
            "properties": {
                "for_behavioral_scientist": {"type": "array", "items": {"type": "string"}},
                "for_psychometrics_expert": {"type": "array", "items": {"type": "string"}}
            }
        },
        "sources_cited": SOURCES_CITED_SCHEMA
    }
}
