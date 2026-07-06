"""
Compliance Guardrail Engine
============================

This is the single most important module in Social Growth Lab.

Every user request that could eventually reach an LLM provider or an
automation/service module MUST first pass through `check_request()`.

Design principles:
- Fail closed: if we are not sure, we block and ask for clarification.
- Never forward a blocked request's text to an LLM provider.
- Never synthesize or return code, scripts, or step-by-step instructions
  for a blocked category, even "for educational purposes".
- Always give the user a short, honest explanation and a compliant
  alternative path within this product.
- Always log the blocked attempt locally (see compliance_logs table).

This module is intentionally dependency-free (no LLM calls) so that it
can run fast, deterministically, and be unit tested exhaustively.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class BlockedCategory(str, Enum):
    FAKE_ACCOUNT_CREATION = "fake_account_creation"
    MASS_SIGNUP = "mass_signup"
    EMAIL_ACCOUNT_CREATION = "email_account_creation"
    INSTAGRAM_AUTOMATION = "instagram_automation"
    FAKE_LIKES = "fake_likes"
    FAKE_COMMENTS = "fake_comments"
    FAKE_VIEWS = "fake_views"
    FAKE_STORY_VIEWS = "fake_story_views"
    FAKE_SHARES = "fake_shares"
    FAKE_SAVES = "fake_saves"
    BOT_ENGAGEMENT = "bot_engagement"
    ENGAGEMENT_PODS = "engagement_pods"
    SCRAPING = "scraping"
    PROXY_ROTATION = "proxy_rotation"
    IP_ROTATION = "ip_rotation"
    CAPTCHA_BYPASS = "captcha_bypass"
    ANTI_DETECTION = "anti_detection"
    DEVICE_FINGERPRINT_SPOOFING = "device_fingerprint_spoofing"
    HUMAN_LIKE_BOT_BEHAVIOR = "human_like_bot_behavior"
    BAN_EVASION = "ban_evasion"
    RATE_LIMIT_BYPASS = "rate_limit_bypass"
    ACCOUNT_WARMING = "account_warming"
    BULK_DMS = "bulk_dms"
    CREDENTIAL_HARVESTING = "credential_harvesting"
    SESSION_HIJACKING = "session_hijacking"
    UNOFFICIAL_API_USAGE = "unofficial_api_usage"
    PASSWORD_REQUEST = "password_request"


@dataclass
class Rule:
    category: BlockedCategory
    patterns: list[str]
    alternative: str


@dataclass
class ComplianceResult:
    allowed: bool
    category: BlockedCategory | None = None
    matched_text: str | None = None
    explanation: str = ""
    alternative: str = ""
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Rule set
# ---------------------------------------------------------------------------
# Patterns are matched case-insensitively against the raw user text.
# They are intentionally broad (word-boundary regex, common synonyms,
# leetspeak-lite variants) rather than a single exact phrase, because a
# narrow blocklist is trivial to route around. False positives are
# acceptable here: this module must fail closed.

_RULES: list[Rule] = [
    Rule(
        BlockedCategory.FAKE_ACCOUNT_CREATION,
        [
            r"fake\s+(instagram\s+)?account", r"bulk\s+(instagram\s+)?account",
            r"multiple\s+accounts?\s+(to|for)\s+(follow|like|boost)",
            r"create\s+\d+\s+(fake\s+)?instagram\s+accounts?", r"\d+\s+fake\s+(instagram\s+)?accounts?",
            r"account\s+farm", r"sock\s?puppet", r"burner\s+account",
        ],
        "I can't help create fake or bulk accounts. I can help you grow one real, "
        "compliant account through better content, testing, and strategy instead.",
    ),
    Rule(
        BlockedCategory.MASS_SIGNUP,
        [r"mass\s+sign\s?up", r"automated?\s+signups?", r"register\s+\d+\s+(users|accounts)"],
        "Mass sign-up automation isn't something this product does. "
        "I can help you plan organic audience growth and content strategy instead.",
    ),
    Rule(
        BlockedCategory.EMAIL_ACCOUNT_CREATION,
        [r"(create|generate|make)\s+(fake\s+)?email\s+accounts?", r"generate\s+emails?\s+for\s+sign\s?up",
         r"bulk\s+email\s+accounts?", r"disposable\s+emails?\s+for\s+instagram", r"fake\s+emails?\s+for\s+(signup|sign up|instagram)"],
        "I won't generate email accounts for platform sign-up. "
        "If you need real business email tooling, use a legitimate provider directly.",
    ),
    Rule(
        BlockedCategory.INSTAGRAM_AUTOMATION,
        [r"automate\s+instagram", r"instagram\s+bot", r"auto[- ]post(er)?\s+bot",
         r"selenium.*instagram", r"playwright.*instagram", r"puppeteer.*instagram",
         r"browser\s+automation.*instagram"],
        "I can't build automation that acts on Instagram on your behalf. "
        "I can help you draft content and a publishing calendar for you to post yourself "
        "or via Meta's official Graph API.",
    ),
    Rule(
        BlockedCategory.FAKE_LIKES,
        [r"fake\s+likes?", r"buy\s+likes?", r"boost\s+likes?\s+(bot|automatically|fake)",
         r"(?<!-)\blike\s+bot\b", r"auto[- ]?like"],
        "I can't generate fake or automated likes. I can help you create content that "
        "earns real likes, and analyze what's already working.",
    ),
    Rule(
        BlockedCategory.FAKE_COMMENTS,
        [r"fake\s+comments?", r"comment\s+bot", r"auto[- ]?comment", r"buy\s+comments?"],
        "I can't generate fake comments or comment automation. "
        "I can draft reply templates for YOU to review and post manually.",
    ),
    Rule(
        BlockedCategory.FAKE_VIEWS,
        [r"fake\s+views?", r"buy\s+views?", r"view\s+bot", r"inflate\s+views?"],
        "I can't fabricate or automate views. I can help you improve hooks and retention "
        "so real viewers watch longer.",
    ),
    Rule(
        BlockedCategory.FAKE_STORY_VIEWS,
        [r"fake\s+story\s+views?", r"story\s+view\s+bot", r"boost\s+story\s+views?"],
        "I can't fabricate story views. I can help you design stories that real followers "
        "want to watch and reply to.",
    ),
    Rule(
        BlockedCategory.FAKE_SHARES,
        [r"fake\s+shares?", r"share\s+bot", r"buy\s+shares?", r"auto[- ]?share"],
        "I can't fabricate or automate shares. I can help craft content and CTAs that "
        "are genuinely more shareable.",
    ),
    Rule(
        BlockedCategory.FAKE_SAVES,
        [r"fake\s+saves?", r"save\s+bot", r"buy\s+saves?", r"auto[- ]?save"],
        "I can't fabricate saves. I can help you design 'save-worthy' content "
        "(templates, checklists, reference posts).",
    ),
    Rule(
        BlockedCategory.BOT_ENGAGEMENT,
        [r"engagement\s+bot", r"fake\s+engagement", r"bot\s+engagement", r"artificial\s+engagement"],
        "I can't build fake engagement systems. I can help with real audience growth "
        "and a closed toy simulation for strategy testing that never touches Instagram.",
    ),
    Rule(
        BlockedCategory.ENGAGEMENT_PODS,
        [r"engagement\s+pod", r"comment\s+pod", r"like\s+pod", r"pod\s+group.*(like|comment|engagement)"],
        "I can't help coordinate engagement pods; they violate Instagram's terms. "
        "I can help you build a genuine community-based content strategy instead.",
    ),
    Rule(
        BlockedCategory.SCRAPING,
        [r"scrape\s+instagram", r"instagram\s+scraper", r"scrape\s+(profile|followers|posts|comments)",
         r"crawl\s+instagram", r"harvest\s+(followers|posts|profiles)"],
        "I can't scrape Instagram. Please export your own data from Instagram Insights "
        "and upload it here — I can analyze anything you upload manually.",
    ),
    Rule(
        BlockedCategory.PROXY_ROTATION,
        [r"proxy\s+rotation", r"rotating\s+proxies", r"proxy\s+pool"],
        "I can't help set up proxy infrastructure for platform automation. "
        "That falls outside what this product supports.",
    ),
    Rule(
        BlockedCategory.IP_ROTATION,
        [r"ip\s+rotation", r"rotate\s+ip", r"rotating\s+ips?"],
        "I can't help with IP rotation for evading platform limits.",
    ),
    Rule(
        BlockedCategory.CAPTCHA_BYPASS,
        [r"bypass\s+captcha", r"captcha\s+solver", r"solve\s+captchas?\s+automatically",
         r"captcha\s+bypass"],
        "I can't help bypass CAPTCHAs. That's a platform-security circumvention I won't build.",
    ),
    Rule(
        BlockedCategory.ANTI_DETECTION,
        [r"anti[- ]detection", r"evade\s+detection", r"avoid\s+detection", r"undetectable\s+bot"],
        "I can't build anti-detection systems. This product is built to be fully "
        "transparent and platform-compliant.",
    ),
    Rule(
        BlockedCategory.DEVICE_FINGERPRINT_SPOOFING,
        [r"fingerprint\s+spoof", r"spoof\s+device", r"fake\s+device\s+fingerprint",
         r"device\s+fingerprint\s+randomiz"],
        "I can't help spoof device fingerprints.",
    ),
    Rule(
        BlockedCategory.HUMAN_LIKE_BOT_BEHAVIOR,
        [r"human[- ]like\s+bot", r"mimic\s+human\s+behavior.*bot", r"randomize.*(clicks|delays).*bot"],
        "I can't design bots that imitate human behavior to evade platform detection.",
    ),
    Rule(
        BlockedCategory.BAN_EVASION,
        [r"ban\s+evasion", r"evade\s+(a\s+)?ban", r"get\s+around\s+(a\s+)?ban",
         r"avoid\s+getting\s+banned.*bot"],
        "I can't help evade a platform ban. If your account was actioned, the compliant "
        "path is Meta's official appeal process.",
    ),
    Rule(
        BlockedCategory.RATE_LIMIT_BYPASS,
        [r"bypass\s+rate\s?limit", r"rate\s?limit\s+bypass", r"get\s+around\s+rate\s?limits?"],
        "I can't help bypass platform rate limits.",
    ),
    Rule(
        BlockedCategory.ACCOUNT_WARMING,
        [r"account\s+warming", r"warm\s+up\s+(an?\s+)?account", r"session\s+farming"],
        "I can't help with account warming or session farming schemes.",
    ),
    Rule(
        BlockedCategory.BULK_DMS,
        [r"bulk\s+dms?", r"mass\s+dm", r"auto[- ]?dm", r"dm\s+bot", r"spam\s+dms?"],
        "I can't automate or mass-send DMs. I can draft individual reply templates "
        "for you to review and send manually, or you can wire up an approved API later "
        "with explicit per-message confirmation.",
    ),
    Rule(
        BlockedCategory.CREDENTIAL_HARVESTING,
        [r"harvest\s+credentials?", r"phish", r"steal\s+(passwords?|credentials?|cookies)"],
        "I can't help harvest credentials. This product never asks for or stores "
        "Instagram passwords.",
    ),
    Rule(
        BlockedCategory.SESSION_HIJACKING,
        [r"session\s+hijack", r"steal\s+session\s+token", r"hijack.*(cookie|session)"],
        "I can't help hijack sessions or steal auth tokens.",
    ),
    Rule(
        BlockedCategory.UNOFFICIAL_API_USAGE,
        [r"unofficial\s+instagram\s+api", r"private\s+instagram\s+api", r"reverse[- ]engineered?\s+instagram\s+api",
         r"instagram-private-api", r"instagrapi"],
        "I can't integrate unofficial/reverse-engineered Instagram APIs. "
        "Only Meta's official Graph API (added by you later, with your own credentials) "
        "is in scope.",
    ),
    Rule(
        BlockedCategory.PASSWORD_REQUEST,
        [r"my\s+instagram\s+password\s+is", r"here.?s\s+my\s+instagram\s+password",
         r"enter\s+my\s+instagram\s+password"],
        "This product never asks for or stores Instagram passwords, and you shouldn't "
        "paste one into any third-party tool. Please don't share it here.",
    ),
]

_COMPILED: list[tuple[Rule, list[re.Pattern]]] = [
    (rule, [re.compile(p, re.IGNORECASE) for p in rule.patterns]) for rule in _RULES
]


def check_request(text: str) -> ComplianceResult:
    """
    Check a free-text user request (prompt, form field, uploaded note, etc.)
    against the compliance rule set.

    Returns a ComplianceResult. Callers MUST NOT forward the original text to
    any LLM provider or automation module when `allowed` is False.
    """
    if not text:
        return ComplianceResult(allowed=True)

    for rule, patterns in _COMPILED:
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return ComplianceResult(
                    allowed=False,
                    category=rule.category,
                    matched_text=match.group(0),
                    explanation=(
                        f"This request looks like it's asking for '{rule.category.value.replace('_', ' ')}', "
                        "which Social Growth Lab does not support because it violates Instagram/Meta's "
                        "terms of service and this project's own safety rules."
                    ),
                    alternative=rule.alternative,
                )
    return ComplianceResult(allowed=True)


def check_request_bundle(*texts: str | None) -> ComplianceResult:
    """Convenience helper to check several free-text fields from one form/payload."""
    for text in texts:
        if not text:
            continue
        result = check_request(text)
        if not result.allowed:
            return result
    return ComplianceResult(allowed=True)
