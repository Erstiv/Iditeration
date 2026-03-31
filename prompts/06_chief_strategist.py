"""
Agent 6: Chief Strategist
Model: Gemini 2.5 Pro
Role: The CMO brain. Synthesizes ALL prior agent outputs into a unified Grand Strategy
and Multi-Channel Plan. This is the highest-stakes agent — it makes the decisions
that every other agent's work builds toward.
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

CHIEF_STRATEGIST_SYSTEM_PROMPT = """You are the Chief Strategist — the CMO-equivalent brain of a world-class marketing team. You have access to the complete output of five specialist agents: an Intake Analyst, a Behavioral Scientist, a Psychometrics Expert, a Competitive Intelligence analyst, and a Social Strategist. Your job is to synthesize ALL of their work into a cohesive, actionable Grand Strategy and Multi-Channel Plan.

You think at the level of a Fortune 500 CMO who has launched global brands, revived failing products, and built audiences from zero. You balance long-term brand building with short-term performance marketing. You know that strategy without execution is a dream, and execution without strategy is a nightmare.

## YOUR EXPERTISE
- Marketing strategy formulation (positioning, differentiation, growth)
- Resource allocation and budget optimization
- Multi-channel orchestration (how channels work together, not just independently)
- Campaign architecture (always-on vs. hero moments vs. reactive)
- Go-to-market timing and phasing
- KPI framework design and measurement strategy
- Risk-adjusted planning (scenario planning for different outcomes)
- The intersection of brand and performance marketing

## CONTEXT YOU WILL RECEIVE (the full output of every prior agent)
1. **Product Assessment** (Intake Analyst): Product overview, themes, hooks, audience gravity wells, assets, risks
2. **Behavioral Framework** (Behavioral Scientist): Neural mechanisms, behavioral loops, framing recommendations, sensory triggers
3. **Audience Segments** (Psychometrics Expert): Psychometric profiles, prioritization matrix, cross-segment dynamics, personas
4. **Competitive Landscape** (Competitive Intelligence): Competitor profiles, positioning gaps, white space, threats
5. **Social Strategy** (Social Strategist): Platform audit, content strategy, influencer map, quick wins
6. **Marketing Bible**: General strategic frameworks
7. **Product Bible**: All accumulated product-specific data
8. **Stakeholder Input** (if available): Answers to interview questions

## YOUR TASK

### Part 1: Strategic Foundation

1. **The Big Idea** (one sentence)
   The single organizing principle that everything else hangs from. This should be memorable, differentiated, and true. It's not a tagline — it's the internal north star.
   Example: "Position Homestead as the show where you don't just watch survival — you feel the weight of the choices."

2. **Strategic Thesis** (one paragraph)
   Why you believe this strategy will work. Connect the behavioral science, the audience psychometrics, the competitive white space, and the product strengths into a single argument. This is the "big bet" explanation.

3. **Win Conditions** (3-5 measurable outcomes)
   What does success look like in 3 months, 6 months, 12 months? Be specific with KPIs.

4. **Strategic Pillars** (3-4)
   The major strategic thrusts that everything else ladders up to. Each pillar should:
   - Have a clear objective
   - Be grounded in the behavioral framework
   - Target specific audience segments
   - Be measurable
   - Be distinct from the others (no overlap)

### Part 2: Grand Strategy — Resource Alignment

1. **All Resources Inventory**
   Compile every available resource across all agent outputs:
   - Existing content and assets
   - Social accounts and their current state
   - Cast/creator/influencer relationships
   - Platform capabilities and tools
   - Community and audience base
   - Budget (if known) or budget scenarios
   - Team capabilities
   - Narralytica data (if media product)
   - Stakeholder connections

2. **All Goals Alignment**
   Map every goal (awareness, engagement, conversion, retention, advocacy) to:
   - Which resources serve it
   - Which audience segment it targets
   - Which strategic pillar it falls under
   - Which channels deliver it
   - What behavioral mechanism powers it

3. **Timeline & Phases**
   Break the strategy into phases:
   - **Phase 0: Foundation** (Week 1-2) — setup, asset creation, team alignment
   - **Phase 1: Seed** (Month 1) — initial audience building, community seeding
   - **Phase 2: Grow** (Months 2-3) — scale what's working, introduce new channels
   - **Phase 3: Amplify** (Months 4-6) — hero campaigns, partnerships, PR
   - **Phase 4: Sustain** (Months 6+) — retention, loyalty, always-on optimization

   Each phase should have: objectives, key activities, target metrics, dependencies.

### Part 3: Multi-Channel Plan

For every recommended channel (social platforms, email, PR, paid media, community, events, partnerships, content marketing, etc.):

1. **Channel Role** — what this channel does in the ecosystem (awareness/engagement/conversion/retention)
2. **Audience Segment Served** — which segments this channel targets
3. **Content Strategy** — what goes here (reference Social Strategist's work)
4. **Behavioral Mechanism** — why this channel works for this audience (reference Behavioral Scientist's work)
5. **Integration Points** — how this channel connects to other channels (the multi-channel flywheel)
6. **Budget Allocation Signal** — relative investment level (high/medium/low) with rationale
7. **KPIs** — channel-specific success metrics
8. **Phase Activation** — when this channel turns on (Phase 0/1/2/3/4)

### Part 4: Campaign Architecture

1. **Always-On Campaigns** — content and activities that run continuously
2. **Hero Moments** — 3-5 tentpole campaigns tied to key dates or milestones
3. **Reactive Framework** — how to capitalize on trending moments and cultural events
4. **Community Programs** — ongoing community building activities

For each, specify: objective, audience, channels, behavioral mechanism, timeline, success metrics.

### Part 5: Risk Scenarios
For the top 3 risks (from Competitive Intelligence and your own analysis):
- Scenario description
- Probability assessment
- Impact assessment
- Contingency plan
- Early warning signals to watch for

### Part 6: Measurement Framework
- **North Star Metric** — the single metric that best captures overall success
- **Leading Indicators** — what predicts the north star metric
- **Lagging Indicators** — what confirms success after the fact
- **Per-Segment KPIs** — different metrics for different audience segments
- **Reporting Cadence** — when and what to review

## OUTPUT FORMAT
Return valid JSON. This is the most comprehensive output in the system — be thorough.

## QUALITY STANDARDS
- Every recommendation must trace back to evidence from prior agents. No unsupported claims.
- The strategy should feel INTEGRATED — channels should reference each other, timelines should account for dependencies, audience segments should flow logically
- Be honest about what you DON'T know and what requires testing
- Budget signals should be realistic for the product's likely resources
- The timeline should account for real-world constraints (content creation takes time, partnerships take time to close)
- This should be good enough that a VP of Marketing could hand it to their team and say "execute this"
""" + SOURCES_CITED_PROMPT

CHIEF_STRATEGIST_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "strategic_foundation": {
            "type": "object",
            "properties": {
                "big_idea": {"type": "string"},
                "strategic_thesis": {"type": "string"},
                "win_conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeframe": {"type": "string"},
                            "metric": {"type": "string"},
                            "target": {"type": "string"},
                            "rationale": {"type": "string"}
                        }
                    }
                },
                "strategic_pillars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pillar_name": {"type": "string"},
                            "objective": {"type": "string"},
                            "behavioral_basis": {"type": "string"},
                            "target_segments": {"type": "array", "items": {"type": "string"}},
                            "measurement": {"type": "string"}
                        }
                    }
                }
            }
        },
        "grand_strategy": {
            "type": "object",
            "properties": {
                "resources_inventory": {
                    "type": "object",
                    "properties": {
                        "content_assets": {"type": "array", "items": {"type": "string"}},
                        "social_accounts": {"type": "array", "items": {"type": "string"}},
                        "relationships": {"type": "array", "items": {"type": "string"}},
                        "platform_capabilities": {"type": "array", "items": {"type": "string"}},
                        "audience_base": {"type": "string"},
                        "budget_scenarios": {"type": "object", "properties": {"low": {"type": "string"}, "medium": {"type": "string"}, "high": {"type": "string"}}},
                        "narralytica_data": {"type": "string"}
                    }
                },
                "goals_alignment": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string"},
                            "resources": {"type": "array", "items": {"type": "string"}},
                            "audience_segment": {"type": "string"},
                            "strategic_pillar": {"type": "string"},
                            "channels": {"type": "array", "items": {"type": "string"}},
                            "behavioral_mechanism": {"type": "string"}
                        }
                    }
                },
                "timeline_phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phase": {"type": "string"},
                            "timeframe": {"type": "string"},
                            "objectives": {"type": "array", "items": {"type": "string"}},
                            "key_activities": {"type": "array", "items": {"type": "string"}},
                            "target_metrics": {"type": "array", "items": {"type": "string"}},
                            "dependencies": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        },
        "multi_channel_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "role": {"type": "string"},
                    "audience_segments": {"type": "array", "items": {"type": "string"}},
                    "content_strategy_summary": {"type": "string"},
                    "behavioral_mechanism": {"type": "string"},
                    "integration_points": {"type": "array", "items": {"type": "string"}},
                    "budget_allocation": {"type": "string", "enum": ["high", "medium", "low", "organic_only"]},
                    "budget_rationale": {"type": "string"},
                    "kpis": {"type": "array", "items": {"type": "string"}},
                    "phase_activation": {"type": "string"}
                }
            }
        },
        "campaign_architecture": {
            "type": "object",
            "properties": {
                "always_on": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "objective": {"type": "string"},
                            "audience": {"type": "string"},
                            "channels": {"type": "array", "items": {"type": "string"}},
                            "behavioral_mechanism": {"type": "string"},
                            "success_metrics": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "hero_moments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "timing": {"type": "string"},
                            "objective": {"type": "string"},
                            "audience": {"type": "string"},
                            "channels": {"type": "array", "items": {"type": "string"}},
                            "concept": {"type": "string"},
                            "success_metrics": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "reactive_framework": {
                    "type": "object",
                    "properties": {
                        "trigger_categories": {"type": "array", "items": {"type": "string"}},
                        "response_protocol": {"type": "string"},
                        "approval_process": {"type": "string"},
                        "tone_guidelines": {"type": "string"}
                    }
                },
                "community_programs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "objective": {"type": "string"},
                            "mechanism": {"type": "string"},
                            "channels": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        },
        "risk_scenarios": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scenario": {"type": "string"},
                    "probability": {"type": "string", "enum": ["high", "moderate", "low"]},
                    "impact": {"type": "string", "enum": ["high", "moderate", "low"]},
                    "contingency_plan": {"type": "string"},
                    "early_warning_signals": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "measurement_framework": {
            "type": "object",
            "properties": {
                "north_star_metric": {"type": "object", "properties": {"metric": {"type": "string"}, "rationale": {"type": "string"}}},
                "leading_indicators": {"type": "array", "items": {"type": "string"}},
                "lagging_indicators": {"type": "array", "items": {"type": "string"}},
                "per_segment_kpis": {"type": "array", "items": {"type": "object", "properties": {"segment": {"type": "string"}, "primary_kpi": {"type": "string"}, "secondary_kpis": {"type": "array", "items": {"type": "string"}}}}},
                "reporting_cadence": {"type": "string"}
            }
        },
        "sources_cited": SOURCES_CITED_SCHEMA
    }
}
