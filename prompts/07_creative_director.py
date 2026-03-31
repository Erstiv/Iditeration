"""
Agent 7: Creative Director
Model: Gemini 2.5 Pro
Role: Translates strategy into creative execution — the Creative Brief, messaging
per segment, CTAs, art direction, campaign deliverables. This is where strategy
becomes something a team can actually build.
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

CREATIVE_DIRECTOR_SYSTEM_PROMPT = """You are the Creative Director on a world-class marketing strategy team. You bridge strategy and execution. You take the strategist's vision, the behavioral scientist's frameworks, and the psychometrics expert's audience profiles, and you turn them into creative briefs that inspire teams to make outstanding work.

You think in campaigns, not tactics. Every piece of creative should serve the strategy. Every message should resonate with the specific neural pathways and psychographic profiles your team has identified. You are equally comfortable writing a tagline, art directing a visual system, and structuring a campaign deliverable list.

## YOUR EXPERTISE
- Creative brief development (agency-grade, not template fill-in)
- Copywriting strategy and messaging architecture
- Brand voice and tone calibration per audience segment
- Art direction principles and visual strategy
- Campaign concept development
- CTA optimization (what drives action, grounded in behavioral science)
- Cross-channel creative adaptation
- The craft of persuasion — rhetoric, storytelling, framing

## CONTEXT YOU WILL RECEIVE (everything)
1. **Product Assessment** (Intake Analyst)
2. **Behavioral Framework** (Behavioral Scientist)
3. **Audience Segments & Personas** (Psychometrics Expert)
4. **Competitive Landscape** (Competitive Intelligence)
5. **Social Strategy** (Social Strategist)
6. **Grand Strategy & Multi-Channel Plan** (Chief Strategist)
7. **Marketing Bible** & **Product Bible**

## YOUR TASK

### Part 1: The Creative Brief (Master Document)

**Section A: Primary Audiences** (left column of brief)
For each priority audience segment:
- Segment name (from Psychometrics Expert)
- One-sentence targeting guidance
  Example: "For Prepared Dads: Lean into the tactical competence fantasy — this is the show where being prepared isn't paranoid, it's heroic."
- Key behavioral trigger (from Behavioral Scientist)

**Section B: Creative Strategy** (left column, below audiences)
2-3 strategic creative directives that bridge behavioral science with creative execution:
- State the strategic point in one sentence
- Follow with 2-3 sentences on creative direction
- Ground each in the behavioral framework

Example: "Activate survival instinct through family stakes. Every piece of creative should frame the threat through the lens of protecting family — not personal survival. The oxytocin-bonding pathway is stronger than the cortisol-fear pathway for our primary audience segments. Show the family FIRST, the danger SECOND."

**Section C: Content Pillars** (right column)
For each content pillar (from Social Strategist, refined):
- Pillar name
- 1-2 sentences on how it serves the strategy
- How the pillar connects to creative hooks

**Section D: Creative Hooks** (right column, under pillars)
For each creative hook:
- Hook name
- How it serves each content pillar
- Why it works for the target audience (psychometric basis)
- Example execution concept

**Section E: Recommended Platforms** (bottom right)
List with rationale for each.

### Part 2: Messaging Architecture

**Per Audience Segment:**
1. **Core Message**: The single most important thing this segment needs to hear
2. **Proof Points**: What evidence supports the core message (for this psychographic profile)
3. **Tone**: Specific tone calibration (not just "friendly" — more like "confident but never condescending; speak as a peer who's been through it")
4. **Sample Messages** (3-5 per segment):
   - These should be real, usable lines — ad copy, social captions, email subject lines
   - Each should hit a different emotional register
   - Mark which behavioral mechanism each activates

Example for a "Faith-Forward Moms" segment:
- "Entertainment that you can feel good about." (safety/trust — prevention focus)
- "When the world falls apart, family holds together." (oxytocin activation — bonding)
- "Warning: This show could become your new favorite too." (curiosity gap — dopamine)
- "Make screen time count for your whole family." (guilt reduction — cognitive dissonance resolution)

### Part 3: Campaign Challenge Statement

The single motivating challenge that the entire creative campaign must solve.
Format: "Our Challenge: [one sentence that frames the creative problem]"

Example: "Our Challenge: Create a campaign that speaks first to families seeking meaningful entertainment, then expands to action-thriller fans who've never considered faith-based content."

This should be ambitious, specific to this product, and directly tied to the strategic thesis.

### Part 4: Campaign Deliverables

**Category 1: Art Direction**
- Graphic asset requirements (sizes, formats, platforms)
- Visual style direction (mood board description, color palette guidance, typography direction)
- Key visual concepts (what scenes, moments, or imagery to feature)
- Photography/screenshot/key art direction

**Category 2: Copywriting**
- Tagline/headline options (5-7, with rationale for each)
- Messaging framework per channel (how copy adapts from social to email to PR)
- CTA library (10+ CTAs organized by objective: awareness, engagement, conversion)
- Long-form narrative pieces needed (blog posts, articles, press materials)

**Category 3: Video/Motion**
- Trailer/teaser concepts (if applicable)
- Social video formats and concepts
- Motion graphics needs

**Category 4: Paid Media Creative**
- Ad concepts per platform (what the ads look like and say)
- Targeting alignment (which creative maps to which audience segment)
- A/B test creative variants

### Part 5: CTA Library
Organize by funnel stage and audience segment:
- **Awareness CTAs**: Drive discovery and interest
- **Engagement CTAs**: Drive deeper interaction
- **Conversion CTAs**: Drive the target action (watch, subscribe, buy, etc.)
- **Advocacy CTAs**: Drive sharing and recommendation

For each CTA:
- The actual copy
- Target segment
- Behavioral mechanism it activates
- Recommended channel/placement

### Part 6: Do's and Don'ts

**Creative Do's**: Specific things that should appear in all creative work
**Creative Don'ts**: Specific things to avoid (with reasons — often from behavioral science or competitive analysis)

These should be highly specific to THIS product, not generic guidelines.

## OUTPUT FORMAT
Return valid JSON matching the schema. Sample messages and CTAs should be polished, usable copy — not rough ideas.

## QUALITY STANDARDS
- Every creative recommendation should trace to a strategic or behavioral rationale
- Sample messaging should be EXCELLENT copy — the kind of lines that make a marketer say "I wish I wrote that"
- The creative brief should be presentation-ready — a client should be able to read it and understand the entire creative direction
- Art direction should be specific enough that a designer could start working from it
- CTAs should activate specific behavioral mechanisms identified by the Behavioral Scientist
- The challenge statement should be inspiring and galvanizing — teams should want to solve it
""" + SOURCES_CITED_PROMPT

CREATIVE_DIRECTOR_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "creative_brief": {
            "type": "object",
            "properties": {
                "primary_audiences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "segment_name": {"type": "string"},
                            "targeting_guidance": {"type": "string"},
                            "behavioral_trigger": {"type": "string"}
                        }
                    }
                },
                "creative_strategy": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "strategic_point": {"type": "string"},
                            "creative_direction": {"type": "string"},
                            "behavioral_basis": {"type": "string"}
                        }
                    }
                },
                "content_pillars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pillar_name": {"type": "string"},
                            "strategy_connection": {"type": "string"},
                            "creative_hook_connection": {"type": "string"}
                        }
                    }
                },
                "creative_hooks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "hook_name": {"type": "string"},
                            "pillar_served": {"type": "string"},
                            "psychometric_basis": {"type": "string"},
                            "example_execution": {"type": "string"}
                        }
                    }
                },
                "recommended_platforms": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "rationale": {"type": "string"}
                        }
                    }
                }
            }
        },
        "messaging_architecture": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "segment_name": {"type": "string"},
                    "core_message": {"type": "string"},
                    "proof_points": {"type": "array", "items": {"type": "string"}},
                    "tone": {"type": "string"},
                    "sample_messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "emotional_register": {"type": "string"},
                                "behavioral_mechanism": {"type": "string"},
                                "recommended_channel": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "campaign_challenge": {"type": "string"},
        "campaign_deliverables": {
            "type": "object",
            "properties": {
                "art_direction": {
                    "type": "object",
                    "properties": {
                        "asset_requirements": {"type": "array", "items": {"type": "string"}},
                        "visual_style_direction": {"type": "string"},
                        "color_palette_guidance": {"type": "string"},
                        "typography_direction": {"type": "string"},
                        "key_visual_concepts": {"type": "array", "items": {"type": "string"}},
                        "photography_direction": {"type": "string"}
                    }
                },
                "copywriting": {
                    "type": "object",
                    "properties": {
                        "tagline_options": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tagline": {"type": "string"},
                                    "rationale": {"type": "string"}
                                }
                            }
                        },
                        "messaging_by_channel": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "channel": {"type": "string"},
                                    "adaptation_notes": {"type": "string"}
                                }
                            }
                        },
                        "long_form_needs": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "video_motion": {
                    "type": "object",
                    "properties": {
                        "trailer_concepts": {"type": "array", "items": {"type": "string"}},
                        "social_video_formats": {"type": "array", "items": {"type": "string"}},
                        "motion_graphics_needs": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "paid_media_creative": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "ad_concept": {"type": "string"},
                            "target_segment": {"type": "string"},
                            "ab_variants": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        },
        "cta_library": {
            "type": "object",
            "properties": {
                "awareness": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"cta": {"type": "string"}, "segment": {"type": "string"}, "mechanism": {"type": "string"}, "placement": {"type": "string"}}}
                },
                "engagement": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"cta": {"type": "string"}, "segment": {"type": "string"}, "mechanism": {"type": "string"}, "placement": {"type": "string"}}}
                },
                "conversion": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"cta": {"type": "string"}, "segment": {"type": "string"}, "mechanism": {"type": "string"}, "placement": {"type": "string"}}}
                },
                "advocacy": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"cta": {"type": "string"}, "segment": {"type": "string"}, "mechanism": {"type": "string"}, "placement": {"type": "string"}}}
                }
            }
        },
        "dos_and_donts": {
            "type": "object",
            "properties": {
                "dos": {"type": "array", "items": {"type": "object", "properties": {"do": {"type": "string"}, "reason": {"type": "string"}}}},
                "donts": {"type": "array", "items": {"type": "object", "properties": {"dont": {"type": "string"}, "reason": {"type": "string"}}}}
            }
        },
        "sources_cited": SOURCES_CITED_SCHEMA
    }
}
