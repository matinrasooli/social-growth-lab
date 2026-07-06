# Compliance Philosophy

Social Growth Lab is built around one non-negotiable rule: **it never automates
or fabricates anything on Instagram.** Growth has to come from better content,
better testing, and a better understanding of a real audience -- not from
bots, scraping, or fake engagement.

## Why this matters

Fake engagement and automation schemes:

- Violate Instagram/Meta's Terms of Service and can get real accounts banned.
- Produce misleading data that leads to worse business decisions, not better ones.
- Erode trust between creators/brands and their actual audience.
- Are frequently illegal in the jurisdictions that regulate deceptive
  advertising and platform manipulation.

## How the guardrail works

Every endpoint that accepts free-text input from a user (a content idea, a
hypothesis, a competitor note, a comment to classify, etc.) routes through
`app/compliance/guardrail.py` **before** anything is persisted or sent to an
LLM provider. See `check_request()` and `check_request_bundle()`.

The guardrail:

1. Matches the input against an explicit, documented list of blocked
   categories (fake accounts, scraping, bot engagement, CAPTCHA bypass, and
   so on -- see the module for the full list).
2. If blocked, returns a short, specific explanation and a compliant
   alternative **without** ever generating code, scripts, or instructions
   for the blocked behavior.
3. Logs every check -- allowed or blocked -- to the `compliance_logs` table,
   visible in the Compliance Logs page.
4. Fails closed: ambiguous or unclear phrasing that looks unsafe is blocked
   rather than allowed through.

This is intentionally a fast, deterministic, dependency-free regex/keyword
engine rather than an LLM classifier, so it:

- Never depends on an external API being configured or reachable.
- Is fully unit-testable (see `app/tests/test_compliance_guardrail.py`).
- Can't be talked out of its rules by clever prompting of an LLM, because
  it runs before any LLM is ever invoked.

## What's structurally impossible in this codebase

Beyond the guardrail, several categories of harm are prevented by the
architecture itself, not just by pattern matching:

- **No Instagram credentials anywhere.** There is no field, model, or form
  for an Instagram password. Nothing in this codebase authenticates to
  Instagram.
- **No browser automation.** Selenium/Playwright/Puppeteer are not
  dependencies of this project and nothing here drives a real browser
  against Instagram.
- **No outbound send path for replies.** `ReplyDraft.sent` always evaluates
  to `False`; there is no code path that transmits a drafted reply anywhere.
  Sending would require a future, explicit integration with Meta's official
  Graph API plus a human confirming each individual message.
- **Competitor data is manual-only.** `CompetitorNote` records are created
  from a form the user fills in; there is no fetch/scrape function anywhere
  in `app/services` or `app/parsers` that reaches out to Instagram.
- **The virality simulator is fully synthetic.** `app/simulation` generates
  its own fake users and a fake social graph in memory. It has no HTTP
  client, no dependency on `requests`/`httpx` for simulation logic, and
  cannot read or write real platform data.

## Correlation vs. causation

The Analytics and Strategy Recommendation features are deliberately written
to hedge: small sample sizes produce an explicit low-confidence note, and
recommendations are phrased as directional, testable hypotheses ("try this
next") rather than guarantees. See `app/services/strategy.py` and
`app/services/analytics.py`.

## If you disagree with a block

The guardrail is a broad, deliberately over-inclusive keyword/regex matcher,
so it will sometimes flag legitimate phrasing (for example, discussing a
competitor's use of engagement pods in the abstract, as analysis rather than
as a request to build one). If that happens, rephrase the request to make
the intent clear, or open an issue describing the false positive so the
pattern can be refined without weakening the underlying rule.
