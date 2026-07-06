from __future__ import annotations

import random
from dataclasses import dataclass, field

INTEREST_CATEGORIES = [
    "fitness", "food", "tech", "fashion", "finance", "travel", "beauty", "gaming", "parenting", "business",
]


@dataclass
class SimUser:
    index: int
    interest_category: str
    activity_hour: int
    like_prob: float
    comment_prob: float
    save_prob: float
    share_prob: float
    watch_prob: float
    trust_sensitivity: float
    novelty_sensitivity: float
    community_cluster: int
    fatigue_level: float
    seen_count: int = field(default=0)


@dataclass
class SimPost:
    topic: str
    hook_strength: float
    visual_quality: float
    emotional_intensity: float
    usefulness: float
    novelty: float
    controversy: float
    clarity: float
    cta_strength: float
    creator_trust: float
    posting_hour: int


def generate_users(num_users: int, num_clusters: int, seed: int | None = None) -> list[SimUser]:
    rng = random.Random(seed)
    users = []
    for i in range(num_users):
        users.append(SimUser(
            index=i,
            interest_category=rng.choice(INTEREST_CATEGORIES),
            activity_hour=rng.randint(0, 23),
            like_prob=rng.uniform(0.2, 0.8),
            comment_prob=rng.uniform(0.02, 0.2),
            save_prob=rng.uniform(0.05, 0.35),
            share_prob=rng.uniform(0.01, 0.15),
            watch_prob=rng.uniform(0.3, 0.9),
            trust_sensitivity=rng.uniform(0.2, 0.9),
            novelty_sensitivity=rng.uniform(0.2, 0.9),
            community_cluster=i % max(num_clusters, 1),
            fatigue_level=0.0,
        ))
    return users


def generate_post(topic: str, hook_strength: float, visual_quality: float, emotional_intensity: float,
                   usefulness: float, novelty: float, controversy: float, clarity: float,
                   cta_strength: float, creator_trust: float, posting_hour: int) -> SimPost:
    return SimPost(
        topic=topic, hook_strength=hook_strength, visual_quality=visual_quality,
        emotional_intensity=emotional_intensity, usefulness=usefulness, novelty=novelty,
        controversy=controversy, clarity=clarity, cta_strength=cta_strength,
        creator_trust=creator_trust, posting_hour=posting_hour,
    )
