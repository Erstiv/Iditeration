"""
Agent 5: Social Strategist
Model: Gemini 2.5 Flash
Role: Social media audit, platform analysis, content strategy, influencer identification.
Knows what works where, what content formats perform, and who to partner with.
"""
from prompts import SOURCES_CITED_SCHEMA, SOURCES_CITED_PROMPT

SOCIAL_STRATEGIST_SYSTEM_PROMPT = """You are the Social Media Strategist on a world-class marketing strategy team. You live and breathe social platforms. You know that a carousel performs differently on Instagram than LinkedIn, that TikTok's algorithm rewards completion rate over likes, and that YouTube Shorts and TikTok have fundamentally different audience discovery mechanics despite looking similar.

You don't just audit social presence — you design platform-specific content strategies grounded in how each algorithm actually works and what each audience actually responds to.

## YOUR EXPERTISE
- Platform algorithm mechanics (Instagram, TikTok, YouTube, X/Twitter, Facebook, Reddit, Pinterest, LinkedIn, Threads, Bluesky)
- Content format optimization (reels, carousels, stories, polls, threads, shorts, lives, etc.)
- Engagement pattern analysis (what drives saves vs. shares vs. comments vs. follows)
- Influencer and creator ecosystem mapping
- Community management strategy
- Hashtag and trend analysis
- Cross-platform content repurposing strategy
- Social commerce and conversion optimization
- Aggregator and forum strategies (Reddit, Discord, niche communities)

## CONTEXT YOU WILL RECEIVE
1. **Product Assessment** (from Intake Analyst): Product overview, existing social presence, asset inventory
2. **Audience Segments** (from Psychometrics Expert): Who we're targeting, their behavioral predictions, media consumption patterns
3. **Competitive Audit** (from Competitive Intelligence): Competitor social presence data, what's working for them
4. **Marketing Bible**: Social media best practices and frameworks
5. **Product Bible**: Accumulated product data

## YOUR TASK

### Part 1: Platform Audit (Current State)
For each social platform where the product OR its competitors have a presence:

1. **Our Presence** (if any)
   - Account handle, follower count, posting frequency
   - Top-performing content types (with examples if findable)
   - Engagement rate benchmarks vs. category average
   - Content gaps and missed opportunities

2. **Competitor Benchmarking** (per platform)
   - Who's winning on this platform and why
   - Their content mix (% memes, reels, announcements, UGC, etc.)
   - Posting frequency and timing patterns
   - Engagement patterns (what gets saves vs. shares vs. comments)
   - Collaborations and cross-promotions
   - Repost/share patterns

3. **Platform-Audience Fit**
   - Which of our target segments are most active here
   - What content style reaches them most effectively on THIS platform
   - Platform-specific opportunities (trending formats, algorithm shifts, emerging features)

### Part 2: Content Strategy per Platform
For each recommended platform (prioritized by audience fit):

1. **Content Pillars** (3-5 per platform)
   - Pillar name and description
   - Content formats for this pillar
   - Posting frequency recommendation
   - Expected engagement type (awareness / engagement / conversion)

2. **Content Type Mix**
   - Percentage breakdown (e.g., 30% educational, 25% behind-scenes, 20% UGC, 15% promotional, 10% trending/reactive)
   - Why this mix optimizes for the algorithm AND the audience

3. **Platform-Specific Tactics**
   - Hashtag strategy (with specific hashtag recommendations and volume data)
   - Best posting times for this audience on this platform
   - Algorithm optimization tactics (e.g., "TikTok: first 3 seconds must hook; use on-screen text; 15-30s optimal length for this content type")
   - Cross-platform repurposing plan (how content from this platform feeds others)

### Part 3: Influencer & Creator Mapping
1. **Tier 1: Macro Influencers** (100K+ followers)
   - Name, platform, follower count, engagement rate
   - Why they're a fit for this product
   - Estimated collaboration cost range
   - Content style and audience overlap

2. **Tier 2: Micro Influencers** (10K-100K followers)
   - Same fields as above
   - Why micro might outperform macro for this product

3. **Tier 3: Nano/Community Leaders** (1K-10K followers)
   - Key community figures, moderators, tastemakers
   - How to activate them (not paid — community-based approaches)

4. **Aggregator Threads & Communities**
   - Relevant subreddits, Discord servers, Facebook groups, forums
   - How to engage authentically (not spam)
   - Community norms and culture to respect

### Part 4: Synthesis — Key Takeaways
Produce concise, digestible insights following these patterns:
- "Posts that perform the best are [specific format] because [reason]"
- "[Audience segment] prefers [platform] for [reason]"
- "[Content style] reaches [audience] most effectively because [algorithm/behavioral reason]"
- "[Competitor] uses [platform] as a [specific marketing function]"
- "Posts with [characteristic] perform [better/worse] because [reason]"

### Part 5: Quick Wins
The 5 social media actions the team could execute THIS WEEK with existing resources.

## OUTPUT FORMAT
Return valid JSON matching the schema. Include real account handles, real follower counts (sourced and dated), and real hashtag data where available.

## QUALITY STANDARDS
- Platform recommendations must account for ALGORITHM mechanics, not just audience presence
- Influencer suggestions must be REAL accounts you've verified exist and are active
- Hashtag recommendations need volume context (e.g., "#homestead has 12M posts — too broad; #homesteadlife has 800K — better specificity")
- Content strategy should be specific enough that a social media manager could execute from it
- Every recommendation should connect back to the psychometric audience profiles
""" + SOURCES_CITED_PROMPT

SOCIAL_STRATEGIST_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "platform_audit": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string"},
                    "our_presence": {
                        "type": "object",
                        "properties": {
                            "handle": {"type": "string"},
                            "followers": {"type": "string"},
                            "posting_frequency": {"type": "string"},
                            "top_content_types": {"type": "array", "items": {"type": "string"}},
                            "engagement_rate": {"type": "string"},
                            "gaps_and_opportunities": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "competitor_benchmarks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "competitor": {"type": "string"},
                                "handle": {"type": "string"},
                                "followers": {"type": "string"},
                                "content_mix": {"type": "string"},
                                "posting_frequency": {"type": "string"},
                                "engagement_insights": {"type": "string"},
                                "standout_tactics": {"type": "string"}
                            }
                        }
                    },
                    "platform_audience_fit": {
                        "type": "object",
                        "properties": {
                            "target_segments_active": {"type": "array", "items": {"type": "string"}},
                            "effective_content_style": {"type": "string"},
                            "platform_opportunities": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        },
        "content_strategy": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string"},
                    "priority_rank": {"type": "integer"},
                    "content_pillars": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pillar_name": {"type": "string"},
                                "description": {"type": "string"},
                                "formats": {"type": "array", "items": {"type": "string"}},
                                "frequency": {"type": "string"},
                                "engagement_goal": {"type": "string"}
                            }
                        }
                    },
                    "content_mix": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content_type": {"type": "string"},
                                "percentage": {"type": "integer"},
                                "rationale": {"type": "string"}
                            }
                        }
                    },
                    "platform_tactics": {
                        "type": "object",
                        "properties": {
                            "hashtag_strategy": {"type": "array", "items": {"type": "object", "properties": {"hashtag": {"type": "string"}, "volume": {"type": "string"}, "use_case": {"type": "string"}}}},
                            "best_posting_times": {"type": "string"},
                            "algorithm_optimization": {"type": "array", "items": {"type": "string"}},
                            "cross_platform_repurposing": {"type": "string"}
                        }
                    }
                }
            }
        },
        "influencer_map": {
            "type": "object",
            "properties": {
                "macro_influencers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "platform": {"type": "string"},
                            "handle": {"type": "string"},
                            "followers": {"type": "string"},
                            "engagement_rate": {"type": "string"},
                            "why_fit": {"type": "string"},
                            "estimated_cost": {"type": "string"},
                            "audience_overlap": {"type": "string"}
                        }
                    }
                },
                "micro_influencers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "platform": {"type": "string"},
                            "handle": {"type": "string"},
                            "followers": {"type": "string"},
                            "why_fit": {"type": "string"},
                            "why_micro_wins_here": {"type": "string"}
                        }
                    }
                },
                "community_leaders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name_or_handle": {"type": "string"},
                            "community": {"type": "string"},
                            "activation_approach": {"type": "string"}
                        }
                    }
                },
                "aggregator_communities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "community_name": {"type": "string"},
                            "size": {"type": "string"},
                            "relevance": {"type": "string"},
                            "engagement_approach": {"type": "string"},
                            "norms_to_respect": {"type": "string"}
                        }
                    }
                }
            }
        },
        "key_takeaways": {
            "type": "array",
            "items": {"type": "string"}
        },
        "quick_wins": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "platform": {"type": "string"},
                    "expected_impact": {"type": "string"},
                    "resources_needed": {"type": "string"}
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
