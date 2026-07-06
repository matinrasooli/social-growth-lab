from app.schemas.content import ContentScoreRequest
from app.services.scoring import score_content


def test_score_content_returns_all_fields():
    req = ContentScoreRequest(
        niche="fitness",
        target_audience="beginners",
        business_goal="grow followers",
        content_idea="A quick morning stretch routine",
        hook="The one stretch nobody tells you about",
        caption="Try this before your next workout.",
        cta="save this",
        content_type="reel",
    )
    result = score_content(req)
    assert 0 <= result.overall_score <= 10
    assert result.method in ("rules", "blended")
    assert result.retention_risk in ("low", "medium", "high")
    assert isinstance(result.improvement_suggestions, list)
    assert len(result.improvement_suggestions) > 0


def test_score_content_flags_missing_hook_as_higher_risk():
    req_no_hook = ContentScoreRequest(content_idea="Just a post about fitness", content_type="reel")
    req_with_hook = ContentScoreRequest(
        content_idea="Just a post about fitness",
        hook="Why nobody talks about this fitness mistake",
        content_type="reel",
    )
    result_no_hook = score_content(req_no_hook)
    result_with_hook = score_content(req_with_hook)
    assert result_no_hook.hook_score <= result_with_hook.hook_score


def test_score_content_penalizes_urgency_language_in_cta():
    req_urgent = ContentScoreRequest(content_idea="Limited offer post", cta="hurry, limited time now", content_type="reel")
    req_normal = ContentScoreRequest(content_idea="Limited offer post", cta="save this", content_type="reel")
    urgent_result = score_content(req_urgent)
    normal_result = score_content(req_normal)
    assert urgent_result.cta_score < normal_result.cta_score


def test_score_content_never_reaches_over_ten_or_under_zero():
    req = ContentScoreRequest(content_idea="x", hook="x" * 200, cta="hurry now limited last chance", content_type="reel")
    result = score_content(req)
    for field in [
        "hook_score", "clarity_score", "novelty_score", "audience_fit_score", "emotional_pull_score",
        "usefulness_score", "shareability_score", "saveability_score", "trust_score", "cta_score",
        "overall_score",
    ]:
        val = getattr(result, field)
        assert 0 <= val <= 10
