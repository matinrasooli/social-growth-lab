from app.parsers.insights import parse_csv, parse_json, parse_pasted_text, parse_manual_form


def test_parse_csv_basic():
    csv_content = (
        "Date,Content Type,Topic,Reach,Likes,Saves\n"
        "2026-05-01,reel,fitness,12000,800,210\n"
        "2026-05-02,carousel,nutrition,5000,300,150\n"
    )
    records = parse_csv(csv_content)
    assert len(records) == 2
    assert records[0].content_type == "reel"
    assert records[0].reach == 12000
    assert records[0].saves == 210
    assert records[1].topic == "nutrition"


def test_parse_csv_handles_percent_and_commas():
    csv_content = "Date,Completion Rate,Reach\n2026-05-01,45%,\"12,500\"\n"
    records = parse_csv(csv_content)
    assert records[0].completion_rate == 45.0
    assert records[0].reach == 12500


def test_parse_csv_ignores_unknown_columns():
    csv_content = "Date,Some Random Column,Reach\n2026-05-01,whatever,1000\n"
    records = parse_csv(csv_content)
    assert records[0].reach == 1000


def test_parse_json_list_format():
    json_content = '[{"date": "2026-05-01", "content_type": "reel", "reach": 9000}]'
    records = parse_json(json_content)
    assert len(records) == 1
    assert records[0].reach == 9000


def test_parse_json_wrapped_format():
    json_content = '{"data": [{"date": "2026-05-01", "reach": 4000}]}'
    records = parse_json(json_content)
    assert len(records) == 1
    assert records[0].reach == 4000


def test_parse_pasted_text():
    text = """
    Date: 2026-05-01
    Content type: reel
    Reach: 12,400
    Likes: 800
    Saves: 210
    """
    record = parse_pasted_text(text)
    assert record.content_type == "reel"
    assert record.reach == 12400
    assert record.saves == 210


def test_parse_manual_form_filters_unknown_keys():
    payload = {"reach": 5000, "unknown_field": "ignored", "topic": "tech"}
    record = parse_manual_form(payload)
    assert record.reach == 5000
    assert record.topic == "tech"


def test_parse_csv_handles_missing_values():
    csv_content = "Date,Reach,Likes\n2026-05-01,,800\n"
    records = parse_csv(csv_content)
    assert records[0].reach is None
    assert records[0].likes == 800


def test_parse_csv_multiple_date_formats():
    csv_content = "Date,Reach\n05/01/2026,1000\n"
    records = parse_csv(csv_content)
    assert records[0].post_date is not None
    assert records[0].post_date.year == 2026
