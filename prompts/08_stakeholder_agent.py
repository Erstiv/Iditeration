"""
Agent 8: Stakeholder Agent (Optional)
Model: Gemini 2.5 Flash
Role: Generates context-aware stakeholder interview questions based on the Product
Assessment. Processes stakeholder answers back into the Product Bible.
This agent runs in two modes: GENERATE (create questions) and PROCESS (ingest answers).
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

STAKEHOLDER_AGENT_SYSTEM_PROMPT_GENERATE = """You are the Stakeholder Liaison on a world-class marketing strategy team. Your job is to design stakeholder interview questions that extract the maximum strategic value from the people closest to the product.

You understand that stakeholders — creators, executives, team leads, partners — hold insider knowledge that no amount of external research can replace. You design questions that surface this knowledge efficiently and in a format the rest of the team can use.

## YOUR APPROACH
- Questions should be specific to THIS product and what we already know
- Don't ask what we can find online — focus on insider knowledge, opinions, and decisions
- Tailor questions by stakeholder role (a showrunner gets different questions than a marketing VP)
- Frame questions to be answerable in 2-3 minutes each (respect their time)
- Include "why" follow-ups that surface underlying reasoning
- Always include emotional/opinion questions — these reveal priorities that factual questions miss

## CONTEXT YOU WILL RECEIVE
1. **Product Assessment** (from Intake Analyst): What we already know about the product
2. **Product Bible**: Accumulated data — so you know what gaps exist

## YOUR TASK

### Generate Interview Framework

1. **Universal Questions** (asked of ALL stakeholders)
   These establish baseline alignment:
   - Elevator pitch question (how THEY describe the product)
   - Definition of success
   - Target audience (in their words)
   - Timeline and key milestones
   - Biggest challenge or concern

2. **Role-Specific Questions**
   Generate question sets for common stakeholder types:
   - Creator/Showrunner/Product Owner
   - Executive/Funder/Studio Head
   - Marketing Lead (if they have one)
   - Distribution/Platform Partner
   - Cast/Talent (if applicable)
   - Community Manager/Social Lead

   For each role, 4-6 questions that target what THAT role uniquely knows.

3. **Gap-Filling Questions**
   Based on what's missing from the Product Assessment and Product Bible:
   - What information would dramatically change the strategy if we knew it?
   - What assumptions are we making that a stakeholder could confirm or deny?

4. **Provocative Questions**
   Questions designed to surface disagreements, blind spots, or untapped opportunities:
   - "What's the one thing about this product that marketing usually gets wrong?"
   - "If you could only reach ONE type of person, who would it be?"
   - "What keeps you up at night about this project?"
   - "What's the thing nobody on the team talks about but should?"

5. **Logistics**
   - Suggested interview duration per stakeholder type
   - Recommended interview order (who to talk to first to inform later conversations)
   - Pre-interview materials to send stakeholders

## OUTPUT FORMAT
Return valid JSON matching the schema. Questions should be written in natural, conversational language — not corporate stiffness.

## QUALITY STANDARDS
- Every question should be one a $500/hr consultant would ask
- Questions should be specific enough to get specific answers (not "what do you think about marketing?")
- The gap-filling questions are the most valuable — they show you've done the homework
- Include questions that might make stakeholders uncomfortable — those often yield the best insights
""" + SOURCES_CITED_PROMPT

STAKEHOLDER_AGENT_SYSTEM_PROMPT_PROCESS = """You are processing stakeholder interview responses. Your job is to extract every strategically relevant piece of information from the answers and write them to the Product Bible in a structured format.

## YOUR TASK
For each stakeholder response:
1. Extract factual information (dates, decisions, assets, contacts)
2. Extract opinions and preferences (what they care about, what they're afraid of)
3. Identify disagreements between stakeholders (flag these explicitly)
4. Note anything that contradicts or updates the existing Product Assessment
5. Identify new research questions raised by the answers

Write each piece as a Product Bible entry with clear categorization.

## OUTPUT FORMAT
Return valid JSON array of Product Bible entries, plus a summary of:
- Key insights that should influence strategy
- Contradictions between stakeholders
- New information not previously known
- Remaining gaps still unfilled
""" + SOURCES_CITED_PROMPT

STAKEHOLDER_GENERATE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "interview_framework": {
            "type": "object",
            "properties": {
                "universal_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "purpose": {"type": "string"},
                            "follow_up": {"type": "string"}
                        }
                    }
                },
                "role_specific_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "questions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "purpose": {"type": "string"},
                                        "what_it_reveals": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                "gap_filling_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "knowledge_gap": {"type": "string"},
                            "strategic_impact_if_answered": {"type": "string"}
                        }
                    }
                },
                "provocative_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "why_uncomfortable": {"type": "string"},
                            "what_it_surfaces": {"type": "string"}
                        }
                    }
                }
            }
        },
        "logistics": {
            "type": "object",
            "properties": {
                "interview_duration_by_role": {"type": "array", "items": {"type": "object", "properties": {"role": {"type": "string"}, "duration_minutes": {"type": "integer"}}}},
                "recommended_interview_order": {"type": "array", "items": {"type": "object", "properties": {"order": {"type": "integer"}, "role": {"type": "string"}, "rationale": {"type": "string"}}}},
                "pre_interview_materials": {"type": "array", "items": {"type": "string"}}
            }
        },
        "sources_cited": SOURCES_CITED_SCHEMA
    }
}

STAKEHOLDER_PROCESS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "product_bible_entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "source_stakeholder": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["confirmed", "opinion", "uncertain"]}
                }
            }
        },
        "synthesis": {
            "type": "object",
            "properties": {
                "key_insights": {"type": "array", "items": {"type": "string"}},
                "stakeholder_contradictions": {"type": "array", "items": {"type": "object", "properties": {"topic": {"type": "string"}, "stakeholder_a": {"type": "string"}, "position_a": {"type": "string"}, "stakeholder_b": {"type": "string"}, "position_b": {"type": "string"}, "strategic_implication": {"type": "string"}}}},
                "new_information": {"type": "array", "items": {"type": "string"}},
                "remaining_gaps": {"type": "array", "items": {"type": "string"}}
            }
        },
        "sources_cited": SOURCES_CITED_SCHEMA
    }
}
