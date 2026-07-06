"""
Synthetic social-graph generators for the closed virality simulator.

Everything here is entirely local, in-memory, and synthetic. No real user
data, no real platform data, no network calls.
"""
from __future__ import annotations

import random


def build_network(structure: str, num_users: int, seed: int | None = None) -> dict[int, set[int]]:
    """
    Return an adjacency mapping {user_index: set(neighbor_indices)}.
    """
    rng = random.Random(seed)
    graph: dict[int, set[int]] = {i: set() for i in range(num_users)}

    def connect(a: int, b: int):
        if a != b:
            graph[a].add(b)
            graph[b].add(a)

    if structure == "random":
        edge_prob = min(0.02, 8 / max(num_users, 1))
        for i in range(num_users):
            for j in range(i + 1, num_users):
                if rng.random() < edge_prob:
                    connect(i, j)

    elif structure == "small_world":
        k = 4  # each node connects to k nearest neighbors in a ring, then rewires
        for i in range(num_users):
            for offset in range(1, k // 2 + 1):
                connect(i, (i + offset) % num_users)
        rewire_prob = 0.1
        for i in range(num_users):
            for neighbor in list(graph[i]):
                if rng.random() < rewire_prob:
                    graph[i].discard(neighbor)
                    graph[neighbor].discard(i)
                    new_target = rng.randrange(num_users)
                    connect(i, new_target)

    elif structure == "influencer_hub":
        num_hubs = max(1, num_users // 50)
        hubs = rng.sample(range(num_users), num_hubs)
        for i in range(num_users):
            if i in hubs:
                continue
            connect(i, rng.choice(hubs))
            if rng.random() < 0.1:
                connect(i, rng.randrange(num_users))

    elif structure == "niche_cluster":
        num_clusters = max(2, num_users // 40)
        clusters = [[] for _ in range(num_clusters)]
        for i in range(num_users):
            clusters[i % num_clusters].append(i)
        for cluster in clusters:
            for i in cluster:
                for j in cluster:
                    if i < j and rng.random() < 0.15:
                        connect(i, j)
        # Sparse bridges between clusters
        for _ in range(num_clusters):
            a, b = rng.sample(range(num_clusters), 2) if num_clusters > 1 else (0, 0)
            if clusters[a] and clusters[b]:
                connect(rng.choice(clusters[a]), rng.choice(clusters[b]))

    elif structure == "dense_local_community":
        community_size = max(5, num_users // 10)
        for start in range(0, num_users, community_size):
            members = list(range(start, min(start + community_size, num_users)))
            for i in members:
                for j in members:
                    if i < j and rng.random() < 0.4:
                        connect(i, j)

    elif structure == "sparse_network":
        for i in range(num_users):
            if rng.random() < 0.5:
                connect(i, rng.randrange(num_users))

    elif structure == "multi_community":
        num_communities = max(3, num_users // 30)
        communities = [[] for _ in range(num_communities)]
        for i in range(num_users):
            communities[i % num_communities].append(i)
        for community in communities:
            for i in community:
                for j in community:
                    if i < j and rng.random() < 0.2:
                        connect(i, j)
        for i in range(num_users):
            if rng.random() < 0.03:
                connect(i, rng.randrange(num_users))

    else:
        raise ValueError(f"Unknown network structure: {structure}")

    return graph
