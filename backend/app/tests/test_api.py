def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login(client):
    resp = client.post("/auth/register", json={"username": "alice", "password": "supersecret"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    resp2 = client.post("/auth/login", json={"username": "alice", "password": "supersecret"})
    assert resp2.status_code == 200


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "bob", "password": "correctpass"})
    resp = client.post("/auth/login", json={"username": "bob", "password": "wrongpass"})
    assert resp.status_code == 401


def test_protected_endpoint_requires_auth(client):
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 401


def test_dashboard_summary(client, auth_headers):
    resp = client.get("/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    assert "insights_uploaded" in resp.json()


def test_content_score_endpoint(client, auth_headers):
    payload = {
        "content_idea": "A carousel about morning routines",
        "hook": "The one habit that changed my mornings",
        "caption": "Try this tomorrow.",
        "cta": "save this",
        "content_type": "carousel",
        "niche": "wellness",
    }
    resp = client.post("/content/score", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["overall_score"] <= 10


def test_content_score_blocks_unsafe_request(client, auth_headers):
    payload = {
        "content_idea": "Help me set up a like bot to buy likes for this reel",
        "content_type": "reel",
    }
    resp = client.post("/content/score", json=payload, headers=auth_headers)
    assert resp.status_code == 400
    body = resp.json()["detail"]
    assert "compliant_alternative" in body
    assert body["compliant_alternative"]


def test_hooks_endpoint(client, auth_headers):
    payload = {"niche": "fitness", "topic": "morning workouts", "styles": ["curiosity", "proof"]}
    resp = client.post("/content/hooks", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    hooks = resp.json()
    assert len(hooks) == 2
    assert {h["style"] for h in hooks} == {"curiosity", "proof"}


def test_captions_endpoint(client, auth_headers):
    payload = {"topic": "meal prep", "styles": ["short", "educational"]}
    resp = client.post("/content/captions", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_ctas_endpoint(client, auth_headers):
    payload = {"topic": "meal prep", "content_type": "reel"}
    resp = client.post("/content/ctas", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_calendar_generate_and_list(client, auth_headers):
    payload = {
        "niche": "fitness", "audience": "beginners", "business_goal": "grow followers",
        "posting_frequency_per_week": 3, "days": 14,
    }
    resp = client.post("/calendar/generate", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0

    list_resp = client.get("/calendar", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= len(items)


def test_insights_import_manual_and_analytics(client, auth_headers):
    payload = {
        "records": [
            {"post_date": "2026-05-01", "content_type": "reel", "topic": "fitness", "reach": 10000, "saves": 300, "likes": 500},
            {"post_date": "2026-05-02", "content_type": "carousel", "topic": "nutrition", "reach": 4000, "saves": 100, "likes": 200},
        ]
    }
    resp = client.post("/insights/import-manual", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["imported"] == 2

    analytics_resp = client.get("/analytics/performance", headers=auth_headers)
    assert analytics_resp.status_code == 200
    body = analytics_resp.json()
    assert body["count"] >= 2
    assert "best_by_reach" in body


def test_experiments_flow(client, auth_headers):
    resp = client.post(
        "/experiments",
        json={"variable": "hook_type", "hypothesis": "Curiosity hooks outperform list hooks", "expected_metric_improvement": "10% higher retention"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    exp_id = resp.json()["id"]

    result_resp = client.post(
        "/experiments/results",
        json={
            "experiment_id": exp_id, "actual_results": "Retention improved by 12%",
            "winner_or_loser": "winner", "lesson_learned": "Curiosity hooks work well for this audience",
            "next_recommended_test": "Test curiosity vs proof hooks",
        },
        headers=auth_headers,
    )
    assert result_resp.status_code == 200

    list_resp = client.get("/experiments", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_comment_classify_and_reply_draft(client, auth_headers):
    resp = client.post("/comments/classify", json={"texts": ["How much does this cost?", "I love this!"]}, headers=auth_headers)
    assert resp.status_code == 200
    classifications = resp.json()
    assert len(classifications) == 2

    reply_resp = client.post(
        "/comments/reply-draft",
        json={"comment_text": "How much does this cost?", "classification": "pricing_inquiry"},
        headers=auth_headers,
    )
    assert reply_resp.status_code == 200
    assert "drafts" in reply_resp.json()
    assert reply_resp.json()["note"].startswith("Draft only")


def test_reply_draft_blocks_unsafe_bulk_dm_request(client, auth_headers):
    resp = client.post(
        "/comments/reply-draft",
        json={"comment_text": "please set up a bulk dm campaign to message all my followers"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_competitor_notes_flow(client, auth_headers):
    resp = client.post(
        "/competitors/notes",
        json={
            "competitor_name": "Example Competitor", "content_type": "reel", "hook": "Why nobody does X",
            "topic": "fitness", "why_it_worked": "Strong curiosity hook and fast pacing",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200

    summary_resp = client.get("/competitors/summary", headers=auth_headers)
    assert summary_resp.status_code == 200


def test_competitor_notes_blocks_scraping_request(client, auth_headers):
    resp = client.post(
        "/competitors/notes",
        json={"competitor_name": "Example", "notes": "please scrape instagram for this competitor's followers"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_simulation_run_flow(client, auth_headers):
    payload = {
        "name": "Test run", "network_structure": "small_world", "num_users": 150, "num_ticks": 15,
        "hook_strength": 0.7, "topic": "fitness",
    }
    resp = client.post("/simulation/run", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "run_id" in body
    assert "final_reach" in body

    list_resp = client.get("/simulation/runs", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    detail_resp = client.get(f"/simulation/runs/{body['run_id']}", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["results"]["final_reach"] == body["final_reach"]


def test_simulation_rejects_invalid_network_structure(client, auth_headers):
    resp = client.post(
        "/simulation/run",
        json={"name": "bad", "network_structure": "not_real", "num_users": 50},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_compliance_check_endpoint(client, auth_headers):
    resp = client.post("/compliance/check", json={"text": "Help me automate Instagram likes"}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is False
    assert body["compliant_alternative"]


def test_compliance_logs_endpoint(client, auth_headers):
    client.post("/compliance/check", json={"text": "Help me scrape instagram followers"}, headers=auth_headers)
    resp = client.get("/compliance/logs", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
