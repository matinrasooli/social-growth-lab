from __future__ import annotations

from datetime import date, timedelta

from app.llm.client import call_llm_json
from app.llm.prompts import generation as prompts
from app.schemas.content import (
    HookGenerateRequest, HookResult,
    CaptionGenerateRequest, CaptionResult,
    CTAGenerateRequest, CTAResult,
    CalendarGenerateRequest, CalendarItemOut,
)

ALL_HOOK_STYLES = [
    "curiosity", "pain_point", "contrarian", "proof", "personal_story",
    "before_and_after", "mistake", "list", "authority", "direct_benefit",
    "emotional", "educational",
]

ALL_CAPTION_STYLES = [
    "short", "founder_style", "educational", "storytelling", "premium_brand",
    "casual_human", "direct_sales", "soft_cta", "comment_bait_authentic", "community_building",
]

_HOOK_TEMPLATES = {
    "curiosity": "The one thing nobody tells you about {topic}...",
    "pain_point": "Struggling with {topic}? Here's what's actually going wrong.",
    "contrarian": "Everyone says do X for {topic}. Here's why that's backwards.",
    "proof": "We tried this {topic} approach for 30 days -- here's what happened.",
    "personal_story": "I almost quit {topic} until this happened.",
    "before_and_after": "This is what {topic} looked like before vs. after one change.",
    "mistake": "The #1 mistake people make with {topic}.",
    "list": "3 things about {topic} I wish I knew sooner.",
    "authority": "After years working in {topic}, here's what actually matters.",
    "direct_benefit": "Do this and improve your {topic} in one week.",
    "emotional": "Nobody talks about how hard {topic} really is.",
    "educational": "Here's how {topic} actually works, in under 60 seconds.",
}

_CAPTION_TEMPLATES = {
    "short": "{topic} -- simpler than it looks.",
    "founder_style": "We built this because {topic} shouldn't be this complicated.",
    "educational": "Here's a quick breakdown of {topic} and what actually matters.",
    "storytelling": "A few months ago, {topic} felt impossible. Here's what changed.",
    "premium_brand": "Considered. Deliberate. {topic}, done properly.",
    "casual_human": "Ok so {topic}... let's talk about it.",
    "direct_sales": "If {topic} is on your list, this is worth a look.",
    "soft_cta": "Save this if {topic} is something you're working on.",
    "comment_bait_authentic": "What's your honest take on {topic}? Curious what's worked for you.",
    "community_building": "Tag someone who needs to see this take on {topic}.",
}

_CTA_LIBRARY = [
    ("save this", "consideration"),
    ("share with a friend", "awareness"),
    ("comment with a real opinion", "consideration"),
    ("visit profile", "conversion"),
    ("click link in bio", "conversion"),
    ("ask a question", "consideration"),
    ("join waitlist", "conversion"),
    ("book a call", "conversion"),
    ("try the product", "conversion"),
    ("reply to story", "retention"),
]


def generate_hooks(req: HookGenerateRequest, provider_name: str | None = None) -> list[HookResult]:
    styles = req.styles or ALL_HOOK_STYLES
    llm_result = call_llm_json(
        system=prompts.HOOK_SYSTEM_PROMPT,
        prompt=prompts.HOOK_USER_TEMPLATE.format(
            niche=req.niche, topic=req.topic, audience=req.audience or "general audience", styles=styles,
        ),
        provider_name=provider_name,
    )

    if llm_result.get("ok") and isinstance(llm_result["data"], dict) and llm_result["data"].get("hooks"):
        results = []
        for item in llm_result["data"]["hooks"]:
            try:
                results.append(HookResult(**{
                    "style": item.get("style", "unknown"),
                    "text": item.get("text", ""),
                    "expected_strength": float(item.get("expected_strength", 5)),
                    "rationale": item.get("rationale", ""),
                    "visual_opening": item.get("visual_opening", ""),
                    "matching_caption": item.get("matching_caption", ""),
                    "matching_cta": item.get("matching_cta", ""),
                }))
            except (TypeError, ValueError):
                continue
        if results:
            return results

    # Deterministic fallback (also what runs under the mock provider / offline mode)
    fallback = []
    for style in styles:
        template = _HOOK_TEMPLATES.get(style, "Here's something worth knowing about {topic}.")
        fallback.append(HookResult(
            style=style,
            text=template.format(topic=req.topic),
            expected_strength=6.5,
            rationale=f"Template-based {style.replace('_', ' ')} hook; test against real audience data.",
            visual_opening="Close-up on speaker or product, direct to camera.",
            matching_caption=f"Let's talk about {req.topic}.",
            matching_cta="save this",
        ))
    return fallback


def generate_captions(req: CaptionGenerateRequest, provider_name: str | None = None) -> list[CaptionResult]:
    styles = req.styles or ALL_CAPTION_STYLES
    llm_result = call_llm_json(
        system=prompts.CAPTION_SYSTEM_PROMPT,
        prompt=prompts.CAPTION_USER_TEMPLATE.format(
            topic=req.topic, niche=req.niche or "general", brand_voice=req.brand_voice or "neutral", styles=styles,
        ),
        provider_name=provider_name,
    )
    if llm_result.get("ok") and isinstance(llm_result["data"], dict) and llm_result["data"].get("captions"):
        results = []
        for item in llm_result["data"]["captions"]:
            if item.get("style") and item.get("text"):
                results.append(CaptionResult(style=item["style"], text=item["text"]))
        if results:
            return results

    return [
        CaptionResult(style=style, text=_CAPTION_TEMPLATES.get(style, "{topic}").format(topic=req.topic))
        for style in styles
    ]


def generate_ctas(req: CTAGenerateRequest, provider_name: str | None = None) -> list[CTAResult]:
    llm_result = call_llm_json(
        system=prompts.CTA_SYSTEM_PROMPT,
        prompt=prompts.CTA_USER_TEMPLATE.format(
            topic=req.topic, content_type=req.content_type,
            funnel_stage=req.funnel_stage or "unspecified", audience_intent=req.audience_intent or "unspecified",
        ),
        provider_name=provider_name,
    )
    if llm_result.get("ok") and isinstance(llm_result["data"], dict) and llm_result["data"].get("ctas"):
        results = []
        for item in llm_result["data"]["ctas"]:
            if item.get("text"):
                results.append(CTAResult(
                    text=item["text"],
                    funnel_stage=item.get("funnel_stage", req.funnel_stage or "consideration"),
                    content_type=item.get("content_type", req.content_type),
                    audience_intent=item.get("audience_intent", req.audience_intent),
                ))
        if results:
            return results

    return [
        CTAResult(text=text, funnel_stage=req.funnel_stage or stage, content_type=req.content_type,
                  audience_intent=req.audience_intent)
        for text, stage in _CTA_LIBRARY[:5]
    ]


def generate_calendar(req: CalendarGenerateRequest, provider_name: str | None = None) -> list[CalendarItemOut]:
    start = req.start_date or date.today()
    llm_result = call_llm_json(
        system=prompts.CALENDAR_SYSTEM_PROMPT,
        prompt=prompts.CALENDAR_USER_TEMPLATE.format(
            niche=req.niche, audience=req.audience, business_goal=req.business_goal,
            product=req.product or "n/a", brand_voice=req.brand_voice or "neutral",
            posting_frequency=req.posting_frequency_per_week, days=req.days,
            important_dates=req.important_dates or [], campaigns=req.campaigns or [],
        ),
        provider_name=provider_name,
        max_tokens=3000,
    )

    if llm_result.get("ok") and isinstance(llm_result["data"], dict) and llm_result["data"].get("items"):
        items = []
        for raw in llm_result["data"]["items"]:
            try:
                items.append(CalendarItemOut(
                    date=start + timedelta(days=int(raw.get("day_offset", 0))),
                    content_type=raw.get("content_type", "reel"),
                    topic=raw.get("topic", req.niche),
                    hook=raw.get("hook", ""),
                    caption_outline=raw.get("caption_outline", ""),
                    cta=raw.get("cta", "save this"),
                    asset_needed=raw.get("asset_needed", "n/a"),
                    production_difficulty=raw.get("production_difficulty", "medium"),
                    expected_outcome=raw.get("expected_outcome", "estimate not available"),
                    experiment_tag=raw.get("experiment_tag"),
                    status="idea",
                ))
            except (TypeError, ValueError):
                continue
        if items:
            return items

    # Deterministic fallback calendar
    content_types = ["reel", "carousel", "story", "static"]
    hook_styles = ALL_HOOK_STYLES
    items = []
    posts_planned = round(req.posting_frequency_per_week * req.days / 7)
    interval = max(1, req.days // max(posts_planned, 1))
    for i in range(0, req.days, interval):
        ct = content_types[(i // interval) % len(content_types)]
        style = hook_styles[(i // interval) % len(hook_styles)]
        items.append(CalendarItemOut(
            date=start + timedelta(days=i),
            content_type=ct,
            topic=f"{req.niche} - {style.replace('_', ' ')} angle",
            hook=_HOOK_TEMPLATES.get(style, "Hook about {topic}").format(topic=req.niche),
            caption_outline=f"Open with the hook, deliver one clear point about {req.niche}, close with a CTA.",
            cta="save this" if ct != "static" else "comment with a real opinion",
            asset_needed="video" if ct in ("reel", "story") else "image set",
            production_difficulty="medium",
            expected_outcome="Directional test -- validate against real Insights data before scaling.",
            experiment_tag=f"hook_style:{style}",
            status="idea",
        ))
    return items
