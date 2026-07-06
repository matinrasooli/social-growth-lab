"""
Parsers that normalize manually-exported/uploaded Instagram Insights data
(CSV, JSON, or pasted text) into the common `InsightRecord` schema.

These parsers only ever operate on files/text the user has uploaded
themselves. They never fetch or scrape anything from Instagram.
"""
from __future__ import annotations

import csv
import io
import json
import re
from datetime import date, datetime

from app.schemas.misc import InsightRecord

# Map many possible column header spellings to our normalized field names.
_HEADER_ALIASES: dict[str, str] = {
    "date": "post_date",
    "post date": "post_date",
    "publish date": "post_date",
    "content type": "content_type",
    "type": "content_type",
    "topic": "topic",
    "caption": "caption",
    "hook": "hook",
    "reach": "reach",
    "impressions": "impressions",
    "likes": "likes",
    "comments": "comments",
    "shares": "shares",
    "saves": "saves",
    "profile visits": "profile_visits",
    "follows": "follows",
    "unfollows": "unfollows",
    "watch time": "watch_time_seconds",
    "watch time (seconds)": "watch_time_seconds",
    "avg watch time": "average_watch_duration",
    "average watch duration": "average_watch_duration",
    "completion rate": "completion_rate",
    "retention 3s": "retention_3s",
    "retention at 3 seconds": "retention_3s",
    "retention 50%": "retention_50pct",
    "retention at 50 percent": "retention_50pct",
    "retention 95%": "retention_95pct",
    "retention at 95 percent": "retention_95pct",
    "story exits": "story_exits",
    "story taps forward": "story_taps_forward",
    "story taps back": "story_taps_back",
    "story replies": "story_replies",
    "link clicks": "link_clicks",
    "campaign": "campaign",
    "cta type": "cta_type",
    "cta": "cta_type",
    "hook style": "hook_style",
}

_INT_FIELDS = {
    "reach", "impressions", "likes", "comments", "shares", "saves",
    "profile_visits", "follows", "unfollows", "story_exits",
    "story_taps_forward", "story_taps_back", "story_replies", "link_clicks",
}
_FLOAT_FIELDS = {
    "watch_time_seconds", "average_watch_duration", "completion_rate",
    "retention_3s", "retention_50pct", "retention_95pct",
}


def _normalize_header(header: str) -> str | None:
    key = header.strip().lower()
    return _HEADER_ALIASES.get(key)


def _coerce_value(field: str, raw: str):
    raw = (raw or "").strip()
    if raw == "":
        return None
    if field == "post_date":
        return _parse_date(raw)
    if field in _INT_FIELDS:
        try:
            return int(float(raw.replace(",", "")))
        except ValueError:
            return None
    if field in _FLOAT_FIELDS:
        try:
            cleaned = raw.replace("%", "").replace(",", "")
            return float(cleaned)
        except ValueError:
            return None
    return raw


def _parse_date(raw: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_csv(content: bytes | str) -> list[InsightRecord]:
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    records: list[InsightRecord] = []
    for row in reader:
        normalized: dict = {}
        for header, value in row.items():
            if header is None:
                continue
            field = _normalize_header(header)
            if not field:
                continue
            normalized[field] = _coerce_value(field, value)
        if normalized:
            records.append(InsightRecord(**normalized))
    return records


def parse_json(content: bytes | str) -> list[InsightRecord]:
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    payload = json.loads(content)
    rows = payload if isinstance(payload, list) else payload.get("data", payload.get("records", []))
    records: list[InsightRecord] = []
    for row in rows:
        normalized: dict = {}
        for key, value in row.items():
            field = _normalize_header(key) or (key if key in InsightRecord.model_fields else None)
            if not field:
                continue
            if isinstance(value, str):
                value = _coerce_value(field, value)
            normalized[field] = value
        if normalized:
            records.append(InsightRecord(**normalized))
    return records


_TEXT_LINE_PATTERN = re.compile(r"([A-Za-z][A-Za-z0-9 %()]+?)\s*[:\-]\s*([\w.,%/ -]+)")


def parse_pasted_text(content: str) -> InsightRecord:
    """
    Best-effort parse of a single post's insights pasted as free text, e.g.:

        Date: 2026-05-01
        Content type: reel
        Reach: 12,400
        Likes: 800
        Saves: 210
    """
    normalized: dict = {}
    for match in _TEXT_LINE_PATTERN.finditer(content):
        header, value = match.group(1), match.group(2)
        field = _normalize_header(header)
        if field:
            normalized[field] = _coerce_value(field, value)
    return InsightRecord(**normalized)


def parse_manual_form(payload: dict) -> InsightRecord:
    """Manual form entry: payload keys are already close to our schema."""
    normalized = {k: v for k, v in payload.items() if k in InsightRecord.model_fields}
    return InsightRecord(**normalized)
