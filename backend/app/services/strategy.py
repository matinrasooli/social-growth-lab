from __future__ import annotations

from app.llm.client import call_llm_json
from app.llm.prompts import generation as prompts


def analyze_competitor_notes(notes: list[dict], provider_name: str | None = None) -> dict:
    """
    Notes here are always manually entered by the user (never scraped).
    """
    llm_result = call_llm_json(
        system=prompts.COMPETITOR_SYSTEM_PROMPT,
        prompt=prompts.COMPETITOR_USER_TEMPLATE.format(notes=notes),
        provider_name=provider_name,
        max_tokens=1500,
    )
    if llm_result.get("ok") and isinstance(llm_result["data"], dict):
        return llm_result["data"]

    # Deterministic fallback summary
    topics = sorted({n.get("topic") for n in notes if n.get("topic")})
    hooks = sorted({n.get("hook") for n in notes if n.get("hook")})
    return {
        "patterns": [f"Recurring topic: {t}" for t in topics[:5]] or ["Not enough notes yet to detect patterns."],
        "gaps": ["Add more notes with 'why it may have worked' filled in for sharper gap analysis."],
        "ideas_to_test": [f"Try a post in the style of hook: '{h}'" for h in hooks[:3]] or ["Add more competitor hooks to compare."],
        "positioning_opportunities": ["Differentiate on a topic none of your tracked competitors cover yet."],
        "differentiated_angles": ["Combine two competitor angles into one original post."],
    }


def generate_strategy_recommendations(summary: dict, provider_name: str | None = None) -> dict:
    llm_result = call_llm_json(
        system=prompts.STRATEGY_SYSTEM_PROMPT,
        prompt=prompts.STRATEGY_USER_TEMPLATE.format(summary=summary),
        provider_name=provider_name,
        max_tokens=1500,
    )
    if llm_result.get("ok") and isinstance(llm_result["data"], dict):
        return llm_result["data"]

    count = summary.get("count", 0)
    confidence = "low" if count < 10 else "moderate" if count < 40 else "reasonable"
    return {
        "post_more": [row["key"] for row in summary.get("topic_comparison", [])[:3]] or ["Not enough data yet"],
        "stop_posting": [row["key"] for row in summary.get("topic_comparison", [])[-2:]] if summary.get("topic_comparison") else [],
        "best_hooks": [row["key"] for row in summary.get("hook_style_comparison", [])[:3]] or ["Not enough data yet"],
        "best_ctas": [row["key"] for row in summary.get("cta_comparison", [])[:3]] or ["Not enough data yet"],
        "best_content_length": "Not enough data to determine yet" ,
        "best_posting_windows": [row["key"] for row in summary.get("best_posting_days", [])[:3]] or ["Not enough data yet"],
        "best_topics": [row["key"] for row in summary.get("topic_comparison", [])[:3]] or ["Not enough data yet"],
        "best_content_pillars": [row["key"] for row in summary.get("topic_comparison", [])[:3]] or ["Not enough data yet"],
        "next_experiments": [
            "Test two hook styles on the same topic",
            "Test posting the same content type at two different times",
        ],
        "weekly_summary": f"Based on {count} uploaded posts, confidence in these patterns is {confidence}.",
        "data_confidence_note": (
            "This is correlational, not causal. Small sample sizes can look like patterns by chance -- "
            "keep testing before committing budget or a full content pivot."
        ),
    }
