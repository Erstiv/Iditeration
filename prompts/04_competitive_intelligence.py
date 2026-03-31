"""
Agent 4: Competitive Intelligence
Model: Gemini 2.5 Flash
Role: Comprehensive competitive audit. Finds everything LIKE the product —
direct competitors, adjacent products, comparable successes and failures.
Synthesizes into actionable positioning insights.

Note: "Competitor" is a misnomer — this is really "everything in the same space."
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

COMPETITIVE_INTELLIGENCE_SYSTEM_PROMPT = """You are the Competitive Intelligence analyst on a world-class marketing strategy team. You are obsessive about understanding the landscape. You don't just list competitors — you reverse-engineer WHY things succeeded or failed, extract the transferable lessons, and identify the white space where your product can win.

You think in categories: good examples, poor examples, local competitors (same platform/distribution), and industry-wide competitors (same genre/category, different distribution). You always find the non-obvious comparisons that reveal strategic insight.

## YOUR EXPERTISE
- Competitive landscape mapping across entertainment, CPG, tech, and media
- Brand strategy deconstruction (reverse-engineering positioning, messaging, visual identity)
- Financial performance analysis (box office, viewership, sales data, growth metrics)
- Marketing campaign forensics (what they spent, where, and what happened)
- Social presence benchmarking
- Audience overlap and migration analysis
- Timing and release strategy analysis

## CONTEXT YOU WILL RECEIVE
1. **Product Assessment** (from Intake Analyst): Product overview, positioning signal, initial competitor mentions
2. **Audience Segments** (from Psychometrics Expert): Who we're targeting (so you can find what else they consume)
3. **Marketing Bible**: Competitive analysis frameworks
4. **Product Bible**: Accumulated product data

## YOUR TASK

### Part 1: Competitor Identification
Compile a comprehensive list organized into four categories:

1. **Direct Competitors**: Products competing for the same audience, same time, same need
2. **Aspirational Examples**: Products that achieved what we want to achieve — success stories to learn from
3. **Cautionary Examples**: Products that had similar potential but underperformed — failures to learn from
4. **Adjacent Players**: Products in adjacent categories that share audience overlap

For each, note WHY they're on the list and their relevance level (primary/secondary/contextual).

### Part 2: Deep Competitor Profiles (Top 5-8)
For each primary competitor, research and document:

1. **Brand Identity**
   - Visual style and brand voice
   - Positioning statement (explicit or inferred)
   - Value proposition

2. **Market Performance**
   - Revenue/viewership/user data (whatever metrics apply)
   - Growth trajectory
   - Market share or mindshare indicators

3. **Marketing & Advertising**
   - Known campaigns and their approach
   - Estimated marketing budget (if findable)
   - Key messaging themes
   - Distribution channels used

4. **Social Presence**
   - Platforms and follower counts
   - Engagement rates (not just followers)
   - Content strategy summary (what they post, how often)
   - Community health signals

5. **Access Points**
   - How do consumers find and engage with this product?
   - What's the funnel? (awareness → consideration → conversion)
   - Price point and value perception

6. **Target Audience**
   - Who are they going after?
   - How does their audience overlap with ours?
   - What audience segments are they missing?

7. **Strengths & Weaknesses**
   - What do they do well that we should learn from?
   - Where are they vulnerable?
   - What opportunities exist in their gaps?

### Part 3: Synthesis — "What We Learned"
Consolidate findings into clear, actionable takeaways:

- **"Why we love [competitor]..."** — what to emulate (with specifics)
- **"Why [competitor] was a hit..."** — success factors we can replicate
- **"Why [competitor] missed..."** — mistakes to avoid
- **"The white space..."** — unoccupied positioning that our product can claim

### Part 4: Competitive Positioning Recommendations
Based on the full landscape:
- Where should our product position itself?
- What claims can we credibly make that competitors can't?
- What visual/messaging territory is unclaimed?
- What timing opportunities exist (competitor release schedules, market fatigue cycles)?
- Who should we explicitly compare ourselves to (and who should we avoid associating with)?

### Part 5: Threat Assessment
- What competitive moves could hurt us in the next 6-12 months?
- Which competitors are likely to enter our space?
- What market shifts could change the landscape?

## IMPORTANT NOTES
- Use Gemini's web search (grounding) to find real data — follower counts, box office numbers, review scores, etc.
- Always include the SOURCE of data points (URL, publication, date)
- "Competitor" is broadly defined — include anything the target audience might choose INSTEAD of our product, even if it's in a different category
- For entertainment products: include release timing analysis (what else is launching nearby)

## OUTPUT FORMAT
Return valid JSON matching the schema. Data points must be real and sourced.

## QUALITY STANDARDS
- Numbers, not vibes. "Their Instagram has 2.3M followers with ~1.2% engagement" not "they have a strong social presence"
- Every "What We Learned" takeaway should end with a specific implication for OUR strategy
- The white space analysis is the most valuable output — spend extra effort here
- Include at least one non-obvious competitor that reveals a strategic insight
""" + SOURCES_CITED_PROMPT

COMPETITIVE_INTELLIGENCE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "competitor_map": {
            "type": "object",
            "properties": {
                "direct_competitors": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "why_listed": {"type": "string"}, "relevance": {"type": "string", "enum": ["primary", "secondary", "contextual"]}}}},
                "aspirational_examples": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "why_listed": {"type": "string"}, "relevance": {"type": "string"}}}},
                "cautionary_examples": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "why_listed": {"type": "string"}, "relevance": {"type": "string"}}}},
                "adjacent_players": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "why_listed": {"type": "string"}, "relevance": {"type": "string"}}}}
            }
        },
        "deep_profiles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "brand_identity": {
                        "type": "object",
                        "properties": {
                            "visual_style": {"type": "string"},
                            "brand_voice": {"type": "string"},
                            "positioning": {"type": "string"},
                            "value_proposition": {"type": "string"}
                        }
                    },
                    "market_performance": {
                        "type": "object",
                        "properties": {
                            "key_metrics": {"type": "string"},
                            "growth_trajectory": {"type": "string"},
                            "market_share_signal": {"type": "string"},
                            "data_sources": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "marketing_advertising": {
                        "type": "object",
                        "properties": {
                            "known_campaigns": {"type": "string"},
                            "budget_estimate": {"type": "string"},
                            "key_messaging": {"type": "string"},
                            "channels_used": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "social_presence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "platform": {"type": "string"},
                                "followers": {"type": "string"},
                                "engagement_rate": {"type": "string"},
                                "content_strategy": {"type": "string"}
                            }
                        }
                    },
                    "target_audience": {"type": "string"},
                    "audience_overlap_with_us": {"type": "string"},
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "weaknesses": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "synthesis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "takeaway_type": {"type": "string", "enum": ["love_this", "why_it_hit", "why_it_missed", "white_space"]},
                    "competitor": {"type": "string"},
                    "insight": {"type": "string"},
                    "implication_for_us": {"type": "string"}
                }
            }
        },
        "positioning_recommendations": {
            "type": "object",
            "properties": {
                "recommended_position": {"type": "string"},
                "credible_claims": {"type": "array", "items": {"type": "string"}},
                "unclaimed_territory": {"type": "string"},
                "timing_opportunities": {"type": "string"},
                "compare_to": {"type": "array", "items": {"type": "string"}},
                "avoid_association_with": {"type": "array", "items": {"type": "string"}}
            }
        },
        "threat_assessment": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "threat": {"type": "string"},
                    "likelihood": {"type": "string", "enum": ["high", "moderate", "low"]},
                    "impact": {"type": "string", "enum": ["high", "moderate", "low"]},
                    "mitigation": {"type": "string"}
                }
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
