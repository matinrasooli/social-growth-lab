from __future__ import annotations

import re

from app.llm.client import call_llm_json
from app.llm.prompts.scoring import SYSTEM_PROMPT, USER_TEMPLATE
from app.schemas.content import ContentScoreRequest, ContentScoreResponse

_WEAK_WORDS = {"nice", "cool", "amazing", "good", "great", "awesome", "stuff", "thing"}
_URGENCY_WORDS = {"now", "hurry", "limited", "today only", "last chance"}
_CURIOSITY_MARKERS = {"why", "how", "what happens", "nobody tells you", "secret", "mistake"}


def _rules_based_scores(req: ContentScoreRequest) -> dict:
    """
    Cheap, deterministic heuristic scoring that works even with zero LLM
    access. This is intentionally simple and transparent -- it is one input
    into the blended score, not a substitute for real performance data.
    """
    idea = (req.content_idea or "").lower()
    hook = (req.hook or "").lower()
    caption = (req.caption or "").lower()
    cta = (req.cta or "").lower()

    def word_count(s: str) -> int:
        return len(s.split())

    hook_score = 5.0
    if hook:
        hook_score += 1.5 if any(m in hook for m in _CURIOSITY_MARKERS) else 0
        hook_score += 1.0 if word_count(hook) <= 14 else -0.5
        hook_score -= 1.5 if any(w in hook for w in _URGENCY_WORDS) else 0
    hook_score = max(0.0, min(10.0, hook_score))

    clarity_score = 6.0
    if idea:
        clarity_score += 1.0 if word_count(idea) >= 6 else -1.0
    clarity_score -= sum(1 for w in _WEAK_WORDS if w in idea) * 0.5
    clarity_score = max(0.0, min(10.0, clarity_score))

    novelty_score = 5.0 if idea else 4.0
    audience_fit_score = 6.0 if req.target_audience else 4.5
    emotional_pull_score = 5.5 if hook or caption else 4.0
    usefulness_score = 6.0 if req.business_goal else 5.0
    shareability_score = 5.0
    saveability_score = 5.0 + (1.0 if "how to" in idea or "checklist" in idea or "list" in idea else 0)
    trust_score = 6.0 - (1.5 if any(w in caption for w in _URGENCY_WORDS) else 0)
    cta_score = 5.0
    if cta:
        cta_score += 1.5 if word_count(cta) <= 8 else 0
        cta_score -= 2.0 if any(w in cta for w in _URGENCY_WORDS) else 0
    cta_score = max(0.0, min(10.0, cta_score))

    saveability_score = max(0.0, min(10.0, saveability_score))
    trust_score = max(0.0, min(10.0, trust_score))

    retention_risk = "low"
    if not hook or word_count(hook) > 20:
        retention_risk = "high"
    elif hook_score < 5:
        retention_risk = "medium"

    return {
        "hook_score": round(hook_score, 1),
        "clarity_score": round(clarity_score, 1),
        "novelty_score": round(novelty_score, 1),
        "audience_fit_score": round(audience_fit_score, 1),
        "emotional_pull_score": round(emotional_pull_score, 1),
        "usefulness_score": round(usefulness_score, 1),
        "shareability_score": round(shareability_score, 1),
        "saveability_score": round(saveability_score, 1),
        "trust_score": round(trust_score, 1),
        "cta_score": round(cta_score, 1),
        "retention_risk": retention_risk,
        "improvement_suggestions": _rules_based_suggestions(req, hook_score, clarity_score, cta_score),
    }


def _rules_based_suggestions(req: ContentScoreRequest, hook_score, clarity_score, cta_score) -> list[str]:
    suggestions = []
    if not req.hook:
        suggestions.append("Add an explicit hook for the first 1-3 seconds; posts without one tend to lose viewers early.")
    elif hook_score < 6:
        suggestions.append("Sharpen the hook: lead with curiosity, a pain point, or a clear promise instead of a general statement.")
    if clarity_score < 6:
        suggestions.append("Tighten the core idea into one clear sentence before scripting.")
    if not req.cta or cta_score < 6:
        suggestions.append("Use one specific, low-friction CTA (e.g. 'save this' or 'comment your answer') rather than none or several.")
    if not req.target_audience:
        suggestions.append("Specify a target audience so the idea can be scored for audience fit.")
    if not suggestions:
        suggestions.append("Solid foundation -- consider A/B testing this against a different hook style.")
    return suggestions


def score_content(req: ContentScoreRequest, provider_name: str | None = None) -> ContentScoreResponse:
    rules = _rules_based_scores(req)

    llm_result = call_llm_json(
        system=SYSTEM_PROMPT,
        prompt=USER_TEMPLATE.format(
            niche=req.niche or "unspecified",
            target_audience=req.target_audience or "unspecified",
            business_goal=req.business_goal or "unspecified",
            content_type=req.content_type,
            content_idea=req.content_idea,
            hook=req.hook or "none provided",
            caption=req.caption or "none provided",
            cta=req.cta or "none provided",
            thumbnail_description=req.thumbnail_description or "none provided",
        ),
        provider_name=provider_name,
    )

    method = "rules"
    blended = dict(rules)

    if llm_result.get("ok") and isinstance(llm_result.get("data"), dict):
        llm_data = llm_result["data"]
        method = "blended"
        numeric_fields = [
            "hook_score", "clarity_score", "novelty_score", "audience_fit_score",
            "emotional_pull_score", "usefulness_score", "shareability_score",
            "saveability_score", "trust_score", "cta_score",
        ]
        for field in numeric_fields:
            llm_val = llm_data.get(field)
            if isinstance(llm_val, (int, float)):
                blended[field] = round((rules[field] + float(llm_val)) / 2, 1)
        if llm_data.get("retention_risk") in {"low", "medium", "high"}:
            # Be conservative: take the higher-risk of the two assessments.
            risk_order = {"low": 0, "medium": 1, "high": 2}
            blended["retention_risk"] = max(
                rules["retention_risk"], llm_data["retention_risk"], key=lambda r: risk_order[r]
            )
        if isinstance(llm_data.get("improvement_suggestions"), list):
            combined = list(dict.fromkeys(rules["improvement_suggestions"] + llm_data["improvement_suggestions"]))
            blended["improvement_suggestions"] = combined[:6]

    overall = round(
        sum(blended[f] for f in [
            "hook_score", "clarity_score", "novelty_score", "audience_fit_score",
            "emotional_pull_score", "usefulness_score", "shareability_score",
            "saveability_score", "trust_score", "cta_score",
        ]) / 10,
        1,
    )

    return ContentScoreResponse(
        overall_score=overall,
        method=method,
        **{k: v for k, v in blended.items() if k != "overall_score"},
    )
