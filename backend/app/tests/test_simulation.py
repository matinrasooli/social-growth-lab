import pytest

from app.simulation.entities import generate_post
from app.simulation.engine import run_simulation
from app.simulation.network import build_network


NETWORK_STRUCTURES = [
    "random", "small_world", "influencer_hub", "niche_cluster",
    "dense_local_community", "sparse_network", "multi_community",
]


@pytest.mark.parametrize("structure", NETWORK_STRUCTURES)
def test_build_network_produces_valid_graph(structure):
    graph = build_network(structure, num_users=100, seed=42)
    assert len(graph) == 100
    for node, neighbors in graph.items():
        assert node not in neighbors  # no self-loops
        for neighbor in neighbors:
            assert node in graph[neighbor]  # symmetric


def test_build_network_rejects_unknown_structure():
    with pytest.raises(ValueError):
        build_network("not_a_real_structure", num_users=10)


def test_run_simulation_returns_expected_shape():
    post = generate_post(
        topic="fitness", hook_strength=0.7, visual_quality=0.6, emotional_intensity=0.5,
        usefulness=0.6, novelty=0.5, controversy=0.2, clarity=0.7, cta_strength=0.6,
        creator_trust=0.7, posting_hour=18,
    )
    result = run_simulation(network_structure="small_world", num_users=200, num_ticks=20, post=post, seed=1)
    assert "reach_curve" in result
    assert "engagement_curve" in result
    assert "final_reach" in result
    assert result["final_reach"] <= 200
    assert "why_content_spread" in result
    assert "why_content_stalled" in result
    assert "disclaimer" in result
    assert "does not use or predict real Instagram data" in result["disclaimer"]


def test_strong_hook_reaches_further_than_weak_hook():
    weak_post = generate_post(
        topic="fitness", hook_strength=0.05, visual_quality=0.3, emotional_intensity=0.2,
        usefulness=0.1, novelty=0.1, controversy=0.1, clarity=0.3, cta_strength=0.1,
        creator_trust=0.3, posting_hour=12,
    )
    strong_post = generate_post(
        topic="fitness", hook_strength=0.95, visual_quality=0.9, emotional_intensity=0.8,
        usefulness=0.8, novelty=0.7, controversy=0.2, clarity=0.9, cta_strength=0.8,
        creator_trust=0.9, posting_hour=18,
    )
    weak_result = run_simulation(network_structure="small_world", num_users=300, num_ticks=30, post=weak_post, seed=7)
    strong_result = run_simulation(network_structure="small_world", num_users=300, num_ticks=30, post=strong_post, seed=7)
    assert strong_result["final_reach"] >= weak_result["final_reach"]


def test_simulation_never_touches_network(monkeypatch):
    """Sanity check: the simulation module must not import any HTTP client."""
    import app.simulation.engine as engine_module
    import inspect
    source = inspect.getsource(engine_module)
    for banned in ["requests", "httpx", "urllib", "instagram"]:
        assert banned not in source.lower()
