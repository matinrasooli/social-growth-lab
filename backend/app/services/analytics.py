from __future__ import annotations

from collections import defaultdict
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import InstagramInsight
from app.schemas.misc import AnalyticsFilter


def _apply_filters(query, filt: AnalyticsFilter):
    if filt.account_id is not None:
        query = query.filter(InstagramInsight.account_id == filt.account_id)
    if filt.date_from:
        query = query.filter(InstagramInsight.post_date >= filt.date_from)
    if filt.date_to:
        query = query.filter(InstagramInsight.post_date <= filt.date_to)
    if filt.content_type:
        query = query.filter(InstagramInsight.content_type == filt.content_type)
    if filt.topic:
        query = query.filter(InstagramInsight.topic == filt.topic)
    if filt.campaign:
        query = query.filter(InstagramInsight.campaign == filt.campaign)
    if filt.hook_style:
        query = query.filter(InstagramInsight.hook_style == filt.hook_style)
    if filt.cta_type:
        query = query.filter(InstagramInsight.cta_type == filt.cta_type)
    return query


def _safe_rate(numerator: int | None, denominator: int | None) -> float | None:
    if not denominator:
        return None
    return round((numerator or 0) / denominator * 100, 2)


def get_performance_summary(db: Session, filt: AnalyticsFilter) -> dict:
    query = select(InstagramInsight)
    query = _apply_filters(query, filt)
    rows = db.execute(query).scalars().all()

    if not rows:
        return {
            "count": 0,
            "message": "No insights data uploaded yet for this filter. Upload Instagram Insights exports to see analytics.",
        }

    reach_over_time = sorted(
        [{"date": r.post_date.isoformat() if r.post_date else None, "reach": r.reach or 0} for r in rows],
        key=lambda x: x["date"] or "",
    )
    follower_growth_over_time = sorted(
        [{"date": r.post_date.isoformat() if r.post_date else None,
          "net_follows": (r.follows or 0) - (r.unfollows or 0)} for r in rows],
        key=lambda x: x["date"] or "",
    )

    def top_by(metric: str, n: int = 5, reverse: bool = True):
        scored = [(getattr(r, metric) or 0, r) for r in rows]
        scored.sort(key=lambda x: x[0], reverse=reverse)
        return [
            {
                "id": r.id, "topic": r.topic, "content_type": r.content_type,
                "post_date": r.post_date.isoformat() if r.post_date else None,
                metric: val,
            }
            for val, r in scored[:n]
        ]

    def group_avg(key_fn, metric_fn, min_count: int = 1):
        buckets: dict = defaultdict(list)
        for r in rows:
            key = key_fn(r)
            if key is None:
                continue
            val = metric_fn(r)
            if val is not None:
                buckets[key].append(val)
        return sorted(
            [{"key": k, "avg": round(mean(v), 2), "n": len(v)} for k, v in buckets.items() if len(v) >= min_count],
            key=lambda x: x["avg"], reverse=True,
        )

    content_type_comparison = group_avg(lambda r: r.content_type, lambda r: r.reach)
    hook_style_comparison = group_avg(lambda r: r.hook_style, lambda r: r.reach)
    topic_comparison = group_avg(lambda r: r.topic, lambda r: r.reach)
    cta_comparison = group_avg(lambda r: r.cta_type, lambda r: r.reach)

    posting_day_perf = group_avg(
        lambda r: r.post_date.strftime("%A") if r.post_date else None, lambda r: r.reach
    )
    posting_hour_perf = []  # Insights exports rarely include hour; left empty unless present in future schema.

    caption_len_buckets: dict = defaultdict(list)
    for r in rows:
        if not r.caption:
            continue
        n_words = len(r.caption.split())
        bucket = "short (<20w)" if n_words < 20 else "medium (20-60w)" if n_words <= 60 else "long (>60w)"
        if r.reach is not None:
            caption_len_buckets[bucket].append(r.reach)
    caption_length_comparison = [
        {"key": k, "avg_reach": round(mean(v), 2), "n": len(v)} for k, v in caption_len_buckets.items()
    ]

    total_reach = sum(r.reach or 0 for r in rows)
    total_saves = sum(r.saves or 0 for r in rows)
    total_shares = sum(r.shares or 0 for r in rows)
    total_comments = sum(r.comments or 0 for r in rows)
    total_follows = sum(r.follows or 0 for r in rows)
    total_profile_visits = sum(r.profile_visits or 0 for r in rows)

    worst_retention = sorted(
        [r for r in rows if r.retention_50pct is not None], key=lambda r: r.retention_50pct
    )[:5]

    return {
        "count": len(rows),
        "reach_over_time": reach_over_time,
        "follower_growth_over_time": follower_growth_over_time,
        "best_by_reach": top_by("reach"),
        "best_by_saves": top_by("saves"),
        "best_by_shares": top_by("shares"),
        "best_by_comments": top_by("comments"),
        "worst_by_retention": [
            {"id": r.id, "topic": r.topic, "content_type": r.content_type, "retention_50pct": r.retention_50pct}
            for r in worst_retention
        ],
        "best_posting_days": posting_day_perf,
        "best_posting_hours": posting_hour_perf,
        "content_type_comparison": content_type_comparison,
        "hook_style_comparison": hook_style_comparison,
        "topic_comparison": topic_comparison,
        "cta_comparison": cta_comparison,
        "caption_length_comparison": caption_length_comparison,
        "save_rate_pct": _safe_rate(total_saves, total_reach),
        "share_rate_pct": _safe_rate(total_shares, total_reach),
        "comment_rate_pct": _safe_rate(total_comments, total_reach),
        "follow_conversion_rate_pct": _safe_rate(total_follows, total_profile_visits),
        "data_confidence_note": (
            "Directional only" if len(rows) < 20 else "Reasonable sample size, still monitor over time"
        ) + " -- correlations here are not guarantees of causation.",
    }
