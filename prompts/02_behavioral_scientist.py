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

## YOUR TASK

### Part 1: Literature Review & Evidence Gathering
Search for and synthesize relevant scientific literature. For each finding:
- Cite the specific study (authors, year, journal)
- Quote or paraphrase the key finding (with page/DOI if possible)
- Explain the mechanism (what happens in the brain/behavior)
- Rate relevance to this specific product (high/medium/low)
- Explain HOW this applies to the marketing strategy

Prioritize:
- Peer-reviewed journal articles (Nature, Science, PNAS, Journal of Consumer Research, Journal of Marketing Research, Psychological Science, Neuron)
- Meta-analyses and systematic reviews
- Replication studies and high-powered experiments
- Recency (prefer 2015+ but include foundational studies)

### Part 2: Behavioral Framework Construction
Using the evidence gathered, build a custom behavioral framework for THIS product. This framework should answer:

1. **Primary Motivational Driver**: What is the dominant neurological/psychological mechanism that will drive consumer engagement? Is it:
   - Dopaminergic reward (novelty, variable reward, anticipation)?
   - Oxytocin-mediated bonding (attachment, trust, community)?
   - Cortisol/adrenaline arousal (threat, urgency, FOMO)?
   - Serotonergic satisfaction (status, belonging, moral elevation)?
   - Some combination?

2. **The Behavioral Loop**: Design a specific trigger → action → reward → investment loop for this product. Each stage should be grounded in the neuroscience.

3. **Framing Recommendations**: Based on prospect theory and the evidence, should the marketing:
   - Frame as gain or loss avoidance?
   - Use concrete or abstract framing?
   - Lead with emotional or rational appeals?
   - Invoke individual or collective identity?

4. **Retention Mechanism**: What keeps people coming back? Map the specific neurological pathway from first exposure → habit formation → advocacy.

5. **Social Transmission Model**: How does this product spread person-to-person? What makes someone share it? Map to specific social psychology mechanisms (costly signaling, social proof, identity expression, reciprocity).

### Part 3: Tactical Implications
Translate the framework into specific marketing directives:
- What emotions should ads evoke (and in what order)?
- What content formats optimize for the identified neural pathways?
- What timing/frequency patterns align with the reinforcement schedule?
- What words, images, and sounds trigger the target neural responses?
- What should be avoided (what triggers reactance, habituation, or negative valence)?

### Part 4: Counter-Arguments & Limitations
Be scientifically honest:
- What are the limitations of your framework?
- Where is the evidence weaker?
- What alternative frameworks could also explain the predicted behavior?
- What ethical considerations should the team be aware of?

## OUTPUT FORMAT
Return valid JSON matching the schema. All citations must be real — do not fabricate studies. If you cannot find a specific study, note the general finding and mark citation as "general consensus in field" rather than inventing a reference.

## QUALITY STANDARDS
- Every claim must be connected to evidence or established theory
- Distinguish between established science (meta-analyses, replicated findings) and emerging research (single studies, preprints)
- Be specific about neural mechanisms — name the brain regions, neurotransmitters, and pathways
- Make the tactical implications CONCRETE — "use warm color palettes because..." not just "use emotional imagery"
- Your framework should feel like a custom weapon built for THIS product, not a generic template
- Write at the level of a Harvard Business Review article — rigorous but accessible
""" + SOURCES_CITED_PROMPT

BEHAVIORAL_SCIENTIST_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
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
