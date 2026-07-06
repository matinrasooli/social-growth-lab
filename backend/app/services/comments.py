from __future__ import annotations

import re

from app.llm.client import call_llm_json
from app.llm.prompts import generation as prompts

_CLASSIFICATION_KEYWORDS = {
    "pricing_inquiry": [r"how much", r"price", r"cost", r"\$"],
    "complaint": [r"broken", r"terrible", r"worst", r"refund", r"disappointed", r"never again"],
    "praise": [r"love this", r"amazing", r"great job", r"awesome", r"so good"],
    "question": [r"\?"],
    "spam": [r"http[s]?://", r"dm me for", r"click my bio", r"free followers"],
    "troll": [r"cringe", r"fake", r"scam", r"trash"],
    "partnership": [r"collab", r"partnership", r"sponsor", r"work together"],
    "customer_support": [r"not working", r"help me", r"issue with", r"support"],
    "product_feedback": [r"suggestion", r"feature request", r"wish it had"],
    "lead": [r"interested", r"sign me up", r"where can i buy", r"link please"],
}


def _rules_classify(text: str) -> str:
    lowered = text.lower()
    for category, patterns in _CLASSIFICATION_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                return category
    return "question" if "?" in text else "praise"


def classify_comments(texts: list[str], provider_name: str | None = None) -> list[dict]:
    llm_result = call_llm_json(
        system=prompts.COMMENT_CLASSIFY_SYSTEM_PROMPT,
        prompt=prompts.COMMENT_CLASSIFY_USER_TEMPLATE.format(messages=texts),
        provider_name=provider_name,
    )
    if llm_result.get("ok") and isinstance(llm_result["data"], dict) and llm_result["data"].get("classifications"):
        results = llm_result["data"]["classifications"]
        if len(results) == len(texts):
            return results

    return [{"text": t, "classification": _rules_classify(t)} for t in texts]


_TONE_TEMPLATES = {
    "friendly": "Thanks so much for this! {body}",
    "concise": "{body}",
    "professional": "Thank you for reaching out. {body}",
    "founder_style": "Hey, it's the founder here -- {body}",
    "playful": "Ha, love this! {body}",
    "support_focused": "Sorry about that -- {body} Let us know if you need anything else.",
    "sales_focused": "{body} Happy to share more details if useful.",
}

_CLASS_BODY = {
    "pricing_inquiry": "pricing details are on our profile link, happy to answer specifics too.",
    "complaint": "we hear you and want to make this right.",
    "praise": "really appreciate you saying that!",
    "question": "great question -- here's the short answer.",
    "spam": "thanks for the comment.",
    "troll": "appreciate the feedback either way.",
    "partnership": "would love to hear more about what you have in mind.",
    "customer_support": "let's get this sorted for you.",
    "product_feedback": "that's really helpful, thank you for sharing it.",
    "lead": "thanks for the interest, more info is coming your way.",
}


def draft_replies(comment_text: str, classification: str | None, tones: list[str] | None,
                   provider_name: str | None = None) -> list[dict]:
    tones = tones or ["friendly", "concise", "professional"]
    llm_result = call_llm_json(
        system=prompts.REPLY_DRAFT_SYSTEM_PROMPT,
        prompt=prompts.REPLY_DRAFT_USER_TEMPLATE.format(
            comment_text=comment_text, classification=classification or "unclassified", tones=tones,
        ),
        provider_name=provider_name,
    )
    if llm_result.get("ok") and isinstance(llm_result["data"], dict) and llm_result["data"].get("drafts"):
        drafts = llm_result["data"]["drafts"]
        if drafts:
            return drafts

    body = _CLASS_BODY.get(classification or "question", "thanks for reaching out.")
    return [{"tone": tone, "text": _TONE_TEMPLATES.get(tone, "{body}").format(body=body)} for tone in tones]
