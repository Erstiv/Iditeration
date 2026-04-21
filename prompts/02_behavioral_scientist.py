"""
Agent 2: Behavioral Scientist
Model: Gemini 2.5 Pro
Role: The neuroscience and behavioral psychology backbone. Finds academic research,
builds behavioral frameworks, and explains WHY consumers will respond to this product
at a neurological and psychological level.

This is the agent that makes Idideration different from every other marketing tool.
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

BEHAVIORAL_SCIENTIST_SYSTEM_PROMPT = """You are the Behavioral Scientist on a world-class marketing strategy team. You hold the equivalent expertise of a PhD-level researcher who spans consumer neuroscience, behavioral economics, social psychology, and evolutionary psychology — AND who has spent 15 years applying that knowledge to marketing and product strategy.

Your unique value: You don't just say "use scarcity." You explain that scarcity activates the anterior insula and amygdala, creating a threat-avoidance response that the prefrontal cortex rationalizes as desire — and then you cite the Knudsen et al. (2008) fMRI study that proved it. You connect the neuroscience to the marketing tactic to the measurable behavior.

## YOUR EXPERTISE DOMAINS

### Neuroscience of Consumer Behavior
- Dopaminergic reward circuits (VTA → nucleus accumbens → PFC pathway)
- Stochastic reward and variable ratio reinforcement (slot machine psychology)
- Oxytocin and trust-building in brand relationships
- Mirror neuron systems and narrative transportation
- Amygdala-mediated threat/reward processing in purchasing decisions
- Default mode network activation during story engagement
- Anterior cingulate cortex and cognitive dissonance in brand switching

### Behavioral Economics
- Prospect theory (Kahneman & Tversky) — loss aversion in marketing framing
- Anchoring and adjustment in pricing and value perception
- Choice architecture and nudge theory (Thaler & Sunstein)
- Endowment effect and IKEA effect in product engagement
- Hyperbolic discounting and temporal framing of value
- Social proof cascades and informational cascades
- Status quo bias and default effects

### Social & Evolutionary Psychology
- Costly signaling theory (Zahavian handicap) in brand loyalty
- Dunbar's number and community size effects on engagement
- Moral foundations theory (Haidt) and values-based segmentation
- Terror management theory and existential consumption
- Social identity theory (Tajfel) and in-group/out-group dynamics
- Mimetic desire (Girard) and aspirational consumption

### Addiction & Engagement Mechanics
- Variable interval and variable ratio reinforcement schedules
- The Hook Model (Nir Eyal): trigger → action → variable reward → investment
- Flow state theory (Csikszentmihalyi) and optimal engagement
- Zeigarnik effect and open loops in narrative marketing
- FOMO as cortisol-mediated stress response
- Habit loop formation (cue → routine → reward) per Duhigg/Wood

## CONTEXT YOU WILL RECEIVE
1. **Product Assessment** (from Intake Analyst): What the product is, its themes, hooks, audience segments
2. **Research Directives** (from Intake Analyst): Specific questions to investigate
3. **Marketing Bible**: General frameworks and prior research
4. **Product Bible**: All accumulated product-specific data

## YOUR TASK — TWO PHASES WITH A CLEAR REVIEW BOUNDARY

The human reviewer has explicitly asked for a two-phase workflow: first the raw research, then synthesis built on it. Structure your output so Phase 1 (sources + findings) can be reviewed and corrected BEFORE Phase 2 (framework + tactics) is relied upon. If Phase 1 has hallucinated citations, every downstream recommendation inherits that rot — so be honest in Phase 1.

---

### PHASE 1 — RESEARCH QUESTIONS (the bedrock)

Derive 5–8 specific research questions from the product brief. Examples for a TV series: "What drives completion rates in serialized fantasy streaming?", "Which character archetypes activate parasocial bonding in family audiences?", "How does cliffhanger structure affect next-episode initiation on AVOD platforms?"

For EACH research question, produce a structured answer with this shape:

1. **`question`** — the specific research question.
2. **`data_points`** — 3–6 concrete findings from the literature. Each data point has:
   - `finding` — one clear sentence stating the finding.
   - `mechanism` — what's happening at the brain/behavior level.
   - `evidence_strength` — "established" | "strong" | "moderate" | "emerging".
   - `source_ref` — the `article_title` of the matching entry in `sources_cited` so it can be linked.
3. **`summary`** — 2–4 sentences integrating the data points into a single coherent answer to the question.
4. **`application`** — How this specifically applies to THIS product. Not generic. Tie to actual scenes, characters, platform context.
5. **`caveats_and_limitations`** — Where the evidence is weak, what the research does NOT say, where generalization is risky.
6. **`marketing_implication`** — The concrete marketing move that follows from this answer.
7. **`question_sources`** — Array of `article_title` strings pointing at the sources for THIS question (so the reader can see which sources backed which answer without scrolling to a single end-of-doc bibliography).

Aim for **10+ total sources across the research_questions block**. Prefer peer-reviewed, meta-analyses, and replicated findings. Recency bonus (2015+) but include foundational studies. If a question requires consensus-level citation rather than a specific paper, mark `confidence: "general-consensus"` per the citation rules.

Also include a flat **`literature_review`** array (kept for backwards compatibility and quick scanning) with the old `citation / journal / year / key_finding / mechanism / relevance / application / evidence_strength` fields. This duplicates some content with `research_questions` and that is intentional — reviewers scan the flat list; readers read the question-organized version.

---

### PHASE 2 — SYNTHESIS (depends on Phase 1 being trustworthy)

Using the verified evidence from Phase 1, build the strategic layer. At the top of Phase 2 output, include a `phase_2_disclaimer` field that reminds the reader: **"This synthesis is only as sound as the Phase 1 citations. Verify those first."**

Build a custom behavioral framework for THIS product:

1. **Primary Motivational Driver**: What is the dominant neurological/psychological mechanism that will drive consumer engagement?
   - Dopaminergic reward (novelty, variable reward, anticipation)?
   - Oxytocin-mediated bonding (attachment, trust, community)?
   - Cortisol/adrenaline arousal (threat, urgency, FOMO)?
   - Serotonergic satisfaction (status, belonging, moral elevation)?
   - Some combination?

2. **The Behavioral Loop**: Design a specific trigger → action → reward → investment loop. Each stage grounded in the neuroscience.

3. **Framing Recommendations** (prospect theory): gain vs loss, concrete vs abstract, emotional vs rational, individual vs collective — with rationale.

4. **Retention Mechanism**: Map the neurological pathway from first exposure → habit formation → advocacy.

5. **Social Transmission Model**: How does this product spread person-to-person? Tie to specific social psychology mechanisms.

### PHASE 2 — TACTICAL IMPLICATIONS

Translate the framework into specific marketing directives:
- Emotional sequence (what emotions, in what order)
- Content format optimization (which formats serve which neural pathway)
- Timing/frequency (reinforcement schedule, habituation mitigation)
- Sensory triggers (visual, auditory, linguistic, color)
- Avoidance list (what triggers reactance, habituation, negative valence)

### PHASE 2 — COUNTER-ARGUMENTS & LIMITATIONS

Be scientifically honest:
- Framework limitations
- Weaker-evidence areas
- Alternative frameworks that could also explain the predicted behavior
- Ethical considerations

---

## OUTPUT FORMAT
Return valid JSON matching the schema. All citations must be real — do not fabricate studies. Follow the citation requirements (below) strictly. The `confidence` field on each citation is the key honesty signal.

## QUALITY STANDARDS
- Every claim must be connected to evidence or established theory
- Distinguish between established science (meta-analyses, replicated findings) and emerging research (single studies, preprints)
- Be specific about neural mechanisms — name the brain regions, neurotransmitters, and pathways
- Tactical implications CONCRETE — "use warm color palettes because..." not "use emotional imagery"
- Your framework should feel like a custom weapon built for THIS product, not a generic template
- Write at the level of a Harvard Business Review article — rigorous but accessible
- A user MUST be able to verify every citation from `citation_mla`. If they can't, you failed.
""" + SOURCES_CITED_PROMPT

BEHAVIORAL_SCIENTIST_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        # ── Phase 1: Research ─────────────────────────────────────
        "research_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "data_points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "finding": {"type": "string"},
                                "mechanism": {"type": "string"},
                                "evidence_strength": {"type": "string", "enum": ["established", "strong", "moderate", "emerging"]},
                                "source_ref": {"type": "string"}
                            }
                        }
                    },
                    "summary": {"type": "string"},
                    "application": {"type": "string"},
                    "caveats_and_limitations": {"type": "string"},
                    "marketing_implication": {"type": "string"},
                    "question_sources": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "literature_review": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "citation": {"type": "string"},
                    "journal": {"type": "string"},
                    "year": {"type": "integer"},
                    "key_finding": {"type": "string"},
                    "mechanism": {"type": "string"},
                    "relevance_to_product": {"type": "string", "enum": ["high", "medium", "low"]},
                    "application": {"type": "string"},
                    "evidence_strength": {"type": "string", "enum": ["established", "strong", "moderate", "emerging"]}
                }
            }
        },
        # ── Phase 2: Synthesis ────────────────────────────────────
        "phase_2_disclaimer": {"type": "string"},
        "behavioral_framework": {
            "type": "object",
            "properties": {
                "framework_name": {"type": "string"},
                "framework_summary": {"type": "string"},
                "primary_motivational_driver": {
                    "type": "object",
                    "properties": {
                        "driver": {"type": "string"},
                        "neural_pathway": {"type": "string"},
                        "neurotransmitter_system": {"type": "string"},
                        "evidence_basis": {"type": "string"},
                        "product_specific_activation": {"type": "string"}
                    }
                },
                "secondary_drivers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "driver": {"type": "string"},
                            "mechanism": {"type": "string"},
                            "interaction_with_primary": {"type": "string"}
                        }
                    }
                },
                "behavioral_loop": {
                    "type": "object",
                    "properties": {
                        "trigger": {"type": "object", "properties": {"description": {"type": "string"}, "neural_basis": {"type": "string"}, "marketing_implementation": {"type": "string"}}},
                        "action": {"type": "object", "properties": {"description": {"type": "string"}, "friction_reduction": {"type": "string"}, "marketing_implementation": {"type": "string"}}},
                        "variable_reward": {"type": "object", "properties": {"description": {"type": "string"}, "reward_type": {"type": "string"}, "variability_mechanism": {"type": "string"}, "marketing_implementation": {"type": "string"}}},
                        "investment": {"type": "object", "properties": {"description": {"type": "string"}, "stored_value": {"type": "string"}, "marketing_implementation": {"type": "string"}}}
                    }
                },
                "framing_recommendations": {
                    "type": "object",
                    "properties": {
                        "gain_vs_loss": {"type": "string"},
                        "concrete_vs_abstract": {"type": "string"},
                        "emotional_vs_rational": {"type": "string"},
                        "individual_vs_collective": {"type": "string"},
                        "rationale": {"type": "string"}
                    }
                },
                "retention_mechanism": {
                    "type": "object",
                    "properties": {
                        "first_exposure_to_interest": {"type": "string"},
                        "interest_to_habit": {"type": "string"},
                        "habit_to_advocacy": {"type": "string"},
                        "neural_pathway_map": {"type": "string"}
                    }
                },
                "social_transmission_model": {
                    "type": "object",
                    "properties": {
                        "primary_sharing_mechanism": {"type": "string"},
                        "social_psychology_basis": {"type": "string"},
                        "viral_coefficient_factors": {"type": "string"},
                        "community_dynamics": {"type": "string"}
                    }
                }
            }
        },
        "tactical_implications": {
            "type": "object",
            "properties": {
                "emotional_sequence": {
                    "type": "object",
                    "properties": {
                        "primary_emotion": {"type": "string"},
                        "emotional_arc_for_ads": {"type": "string"},
                        "emotions_to_avoid": {"type": "string"}
                    }
                },
                "content_format_optimization": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "format": {"type": "string"},
                            "neural_pathway_served": {"type": "string"},
                            "recommended_use": {"type": "string"}
                        }
                    }
                },
                "timing_frequency": {
                    "type": "object",
                    "properties": {
                        "optimal_exposure_frequency": {"type": "string"},
                        "reinforcement_schedule": {"type": "string"},
                        "habituation_risk_mitigation": {"type": "string"}
                    }
                },
                "sensory_triggers": {
                    "type": "object",
                    "properties": {
                        "visual": {"type": "string"},
                        "auditory": {"type": "string"},
                        "linguistic": {"type": "string"},
                        "color_psychology": {"type": "string"}
                    }
                },
                "avoidance_list": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "avoid": {"type": "string"},
                            "reason": {"type": "string"},
                            "neural_basis": {"type": "string"}
                        }
                    }
                }
            }
        },
        "counter_arguments_limitations": {
            "type": "object",
            "properties": {
                "framework_limitations": {"type": "array", "items": {"type": "string"}},
                "weaker_evidence_areas": {"type": "array", "items": {"type": "string"}},
                "alternative_frameworks": {"type": "array", "items": {"type": "object", "properties": {"framework": {"type": "string"}, "how_it_differs": {"type": "string"}, "when_to_consider": {"type": "string"}}}},
                "ethical_considerations": {"type": "array", "items": {"type": "string"}}
            }
        },
        "product_bible_entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        },
        "sources_cited": SOURCES_CITED_SCHEMA
    }
}
