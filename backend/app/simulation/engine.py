"""
Closed virality simulation engine.

This models a small synthetic social network to help reason about how
different hooks, posting times, topics, CTAs, and network structures
*might* affect spread -- entirely offline, with fabricated users and posts.
It is a strategy-testing sandbox, not a prediction of real Instagram results,
and never reads or writes real platform data.
"""
from __future__ import annotations

import random
from dataclasses import asdict

from app.simulation.entities import SimUser, SimPost, generate_users, generate_post
from app.simulation.network import build_network


def _feed_rank_score(user: SimUser, post: SimPost, tick: int, early_engagement: float, share_velocity: float) -> float:
    interest_match = 0.7 if user.interest_category == post.topic else 0.3
    recency = max(0.0, 1.0 - tick * 0.02)
    trust = post.creator_trust * (1 - user.trust_sensitivity * 0.3)
    quality = (post.visual_quality + post.clarity) / 2
    fatigue_penalty = user.fatigue_level * 0.3

    score = (
        0.25 * interest_match +
        0.2 * early_engagement +
        0.15 * recency +
        0.15 * trust +
        0.1 * quality +
        0.1 * share_velocity +
        0.05 * (1 - fatigue_penalty)
    )
    return max(0.0, min(1.0, score))


def run_simulation(
    network_structure: str,
    num_users: int,
    num_ticks: int,
    post: SimPost,
    seed: int | None = None,
) -> dict:
    rng = random.Random(seed)
    num_clusters = max(3, num_users // 30)
    users = generate_users(num_users, num_clusters, seed=seed)
    graph = build_network(network_structure, num_users, seed=seed)

    exposed: set[int] = set()
    engaged_like: set[int] = set()
    engaged_comment: set[int] = set()
    engaged_save: set[int] = set()
    engaged_share: set[int] = set()
    negative_feedback: set[int] = set()

    reach_curve = []
    engagement_curve = []
    cascade_edges: list[tuple[int, int, int]] = []  # (from, to, tick)

    # Seed: a handful of random users see the post organically at tick 0
    seed_size = max(1, num_users // 100)
    frontier = set(rng.sample(range(num_users), min(seed_size, num_users)))
    exposed |= frontier

    for tick in range(num_ticks):
        if not frontier:
            break

        early_engagement = len(engaged_like) / max(len(exposed), 1)
        share_velocity = len(engaged_share) / max(tick + 1, 1)

        next_frontier: set[int] = set()

        for user_index in frontier:
            user = users[user_index]
            rank_score = _feed_rank_score(user, post, tick, early_engagement, share_velocity)

            if rng.random() > rank_score * post.hook_strength * 1.3:
                continue  # scrolled past

            user.seen_count += 1
            user.fatigue_level = min(1.0, user.fatigue_level + 0.05)

            watch_roll = rng.random()
            watched = watch_roll < user.watch_prob * (0.5 + 0.5 * post.clarity)
            if not watched:
                continue

            if rng.random() < user.like_prob * post.emotional_intensity:
                engaged_like.add(user_index)
            if rng.random() < user.comment_prob * (post.controversy * 0.5 + post.usefulness * 0.5):
                engaged_comment.add(user_index)
            if rng.random() < user.save_prob * post.usefulness:
                engaged_save.add(user_index)
            share_chance = user.share_prob * post.cta_strength * (1 + post.novelty * user.novelty_sensitivity)
            if rng.random() < share_chance:
                engaged_share.add(user_index)
                for neighbor in graph.get(user_index, set()):
                    if neighbor not in exposed:
                        next_frontier.add(neighbor)
                        cascade_edges.append((user_index, neighbor, tick + 1))

            negative_roll = rng.random()
            if negative_roll < (post.controversy * 0.15) and post.usefulness < 0.4:
                negative_feedback.add(user_index)

        exposed |= next_frontier
        frontier = next_frontier

        reach_curve.append({"tick": tick, "cumulative_reach": len(exposed)})
        engagement_curve.append({
            "tick": tick,
            "likes": len(engaged_like),
            "comments": len(engaged_comment),
            "saves": len(engaged_save),
            "shares": len(engaged_share),
        })

    clusters_reached = sorted({users[i].community_cluster for i in exposed})
    saturation_point = next((r["tick"] for r in reach_curve if r["cumulative_reach"] >= 0.9 * max(len(exposed), 1)), None)

    total_engaged = len(engaged_like | engaged_comment | engaged_save | engaged_share)
    stalled = len(exposed) < num_users * 0.05
    spread_reason = []
    stall_reason = []

    if post.hook_strength > 0.65:
        spread_reason.append("Strong hook kept viewers watching long enough to engage.")
    if post.cta_strength > 0.6:
        spread_reason.append("Clear CTA drove a meaningful share rate.")
    if network_structure in ("influencer_hub", "small_world"):
        spread_reason.append(f"'{network_structure}' network structure allowed fast cross-cluster spread.")
    if not spread_reason:
        spread_reason.append("Spread stayed mostly organic and slow within the seed cluster.")

    if post.hook_strength < 0.4:
        stall_reason.append("Weak hook likely caused early scroll-past before engagement could occur.")
    if post.usefulness < 0.3 and post.novelty < 0.3:
        stall_reason.append("Low usefulness and novelty gave viewers little reason to save or share.")
    if network_structure in ("sparse_network", "niche_cluster") and stalled:
        stall_reason.append(f"'{network_structure}' limits cross-cluster reach without a strong share trigger.")
    if not stall_reason:
        stall_reason.append("No major stall detected in this run.")

    return {
        "reach_curve": reach_curve,
        "engagement_curve": engagement_curve,
        "share_cascade_edges": cascade_edges[:500],  # cap payload size
        "user_clusters_reached": clusters_reached,
        "saturation_point_tick": saturation_point,
        "final_reach": len(exposed),
        "final_engagement": {
            "likes": len(engaged_like),
            "comments": len(engaged_comment),
            "saves": len(engaged_save),
            "shares": len(engaged_share),
            "negative_feedback": len(negative_feedback),
        },
        "why_content_spread": spread_reason,
        "why_content_stalled": stall_reason if stalled else [],
        "simulated_follower_conversion_estimate": round(len(engaged_share) * 0.05 + len(engaged_save) * 0.02, 1),
        "disclaimer": (
            "This is a synthetic, closed-network simulation for strategy testing only. "
            "It does not use or predict real Instagram data."
        ),
    }


def sensitivity_analysis(base_kwargs: dict, vary_field: str, values: list[float], seed: int | None = None) -> list[dict]:
    """Run the same simulation multiple times varying one post attribute, for comparison experiments."""
    results = []
    for value in values:
        kwargs = dict(base_kwargs)
        post_kwargs = dict(kwargs["post_kwargs"])
        post_kwargs[vary_field] = value
        kwargs["post_kwargs"] = post_kwargs
        post = generate_post(**post_kwargs)
        result = run_simulation(
            network_structure=kwargs["network_structure"],
            num_users=kwargs["num_users"],
            num_ticks=kwargs["num_ticks"],
            post=post,
            seed=seed,
        )
        results.append({vary_field: value, "final_reach": result["final_reach"], "final_engagement": result["final_engagement"]})
    return results
