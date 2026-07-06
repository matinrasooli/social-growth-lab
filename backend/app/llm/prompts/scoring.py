SYSTEM_PROMPT = """You are a skeptical, experienced Instagram content strategist.
You critique content ideas honestly. You never overclaim virality. You call out
weak hooks, vague CTAs, and generic ideas. You always respond with strict JSON only,
no markdown fences, no commentary outside the JSON object.
"""

USER_TEMPLATE = """Evaluate this content idea for a real Instagram account.

Niche: {niche}
Target audience: {target_audience}
Business goal: {business_goal}
Content type: {content_type}
Idea: {content_idea}
Hook: {hook}
Caption: {caption}
CTA: {cta}
Thumbnail description: {thumbnail_description}

Return strict JSON with this exact shape:
{{
  "hook_score": <0-10 float>,
  "clarity_score": <0-10 float>,
  "novelty_score": <0-10 float>,
  "audience_fit_score": <0-10 float>,
  "emotional_pull_score": <0-10 float>,
  "usefulness_score": <0-10 float>,
  "shareability_score": <0-10 float>,
  "saveability_score": <0-10 float>,
  "trust_score": <0-10 float>,
  "cta_score": <0-10 float>,
  "retention_risk": "low" | "medium" | "high",
  "improvement_suggestions": ["...", "..."]
}}
"""
