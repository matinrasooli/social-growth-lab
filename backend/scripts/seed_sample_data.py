"""
Generates demo/sample data for Social Growth Lab.

This produces entirely synthetic, fabricated data -- no real Instagram data,
no scraping, no real accounts. It's meant to (a) let you explore the product
immediately, and (b) double as an example of the Insights CSV/JSON import format.

Run with: python scripts/seed_sample_data.py
Output goes to ../sample_data relative to this script.
"""
import csv
import json
import os
import random
from datetime import date, timedelta

random.seed(42)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "sample_data"))
os.makedirs(OUT_DIR, exist_ok=True)

TOPICS = ["morning routine", "meal prep", "budgeting basics", "home workout",
          "productivity tips", "skincare routine", "travel packing", "side hustle ideas"]
HOOK_STYLES = ["curiosity", "pain_point", "contrarian", "proof", "personal_story",
               "before_and_after", "mistake", "list", "authority", "direct_benefit"]
CTA_TYPES = ["save this", "share with a friend", "comment with a real opinion",
             "visit profile", "click link in bio", "ask a question"]
CAMPAIGNS = ["spring_launch", "q2_growth_push", "product_launch_2026", "evergreen", "collab_series"]


def make_post(i: int, content_type: str, start_date: date) -> dict:
    topic = random.choice(TOPICS)
    hook_style = random.choice(HOOK_STYLES)
    cta = random.choice(CTA_TYPES)
    post_date = start_date + timedelta(days=i)

    base_reach = {
        "reel": random.randint(3000, 40000),
        "story": random.randint(800, 6000),
        "carousel": random.randint(1500, 15000),
        "static": random.randint(500, 8000),
    }[content_type]

    engagement_multiplier = random.uniform(0.5, 1.6)
    likes = int(base_reach * random.uniform(0.03, 0.12) * engagement_multiplier)
    comments = int(base_reach * random.uniform(0.002, 0.02) * engagement_multiplier)
    shares = int(base_reach * random.uniform(0.001, 0.02) * engagement_multiplier)
    saves = int(base_reach * random.uniform(0.005, 0.05) * engagement_multiplier)
    profile_visits = int(base_reach * random.uniform(0.01, 0.05))
    follows = int(profile_visits * random.uniform(0.02, 0.15))
    unfollows = int(follows * random.uniform(0, 0.3))

    row = {
        "date": post_date.isoformat(),
        "content type": content_type,
        "topic": topic,
        "caption": f"A {topic} post exploring {hook_style.replace('_', ' ')} style messaging.",
        "hook": f"{hook_style.replace('_', ' ').title()} hook about {topic}",
        "reach": base_reach,
        "impressions": int(base_reach * random.uniform(1.1, 1.8)),
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "profile visits": profile_visits,
        "follows": follows,
        "unfollows": unfollows,
        "campaign": random.choice(CAMPAIGNS),
        "cta type": cta,
        "hook style": hook_style,
    }

    if content_type in ("reel", "story"):
        completion = round(random.uniform(0.2, 0.85), 2)
        row.update({
            "watch time": round(base_reach * completion * random.uniform(4, 20), 1),
            "average watch duration": round(random.uniform(2, 25), 1),
            "completion rate": completion,
            "retention at 3 seconds": round(random.uniform(0.4, 0.95), 2),
            "retention at 50 percent": round(random.uniform(0.2, 0.7), 2),
            "retention at 95 percent": round(completion, 2),
        })
    if content_type == "story":
        row.update({
            "story exits": int(base_reach * random.uniform(0.05, 0.3)),
            "story taps forward": int(base_reach * random.uniform(0.1, 0.4)),
            "story taps back": int(base_reach * random.uniform(0.01, 0.1)),
            "story replies": int(base_reach * random.uniform(0.005, 0.05)),
        })
    row["link clicks"] = int(base_reach * random.uniform(0.001, 0.03))
    return row


def generate_insights_csv():
    plan = [("reel", 20), ("story", 20), ("carousel", 10), ("static", 10)]
    start_date = date.today() - timedelta(days=90)
    rows = []
    i = 0
    for content_type, count in plan:
        for _ in range(count):
            rows.append(make_post(i, content_type, start_date))
            i += 3  # spread posts out over ~90 days

    all_fieldnames = []
    for row in rows:
        for key in row:
            if key not in all_fieldnames:
                all_fieldnames.append(key)

    out_path = os.path.join(OUT_DIR, "instagram_insights_sample.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} rows to {out_path}")
    return rows


def generate_insights_json(rows):
    out_path = os.path.join(OUT_DIR, "instagram_insights_sample.json")
    with open(out_path, "w") as f:
        json.dump({"data": rows[:15]}, f, indent=2)
    print(f"Wrote sample JSON export (15 rows) to {out_path}")


def generate_competitor_notes():
    notes = [
        {
            "competitor_name": "Wellness Creator A", "profile_reference": "instagram.com/example-wellness-a (manually noted, not scraped)",
            "content_type": "reel", "hook": "The morning mistake ruining your energy",
            "topic": "morning routine", "offer": "free 5-day energy reset guide",
            "visual_style": "bright, minimal, text overlay top third",
            "estimated_engagement": "high (visually estimated from public post)",
            "notes": "Posts consistently at 7am, uses the same intro shot style across reels.",
            "why_it_worked": "Strong pain-point hook paired with a low-friction free offer.",
        },
        {
            "competitor_name": "Budget Coach B", "profile_reference": "instagram.com/example-budget-b (manually noted)",
            "content_type": "carousel", "hook": "3 budgeting rules nobody follows",
            "topic": "budgeting basics", "offer": "budgeting template",
            "visual_style": "clean slides, single accent color",
            "estimated_engagement": "medium-high", "notes": "List-style carousels seem to get more saves.",
            "why_it_worked": "List format is scannable and highly saveable.",
        },
        {
            "competitor_name": "Home Fitness C", "profile_reference": "instagram.com/example-fitness-c (manually noted)",
            "content_type": "reel", "hook": "Before and after: 1 exercise change",
            "topic": "home workout", "offer": "workout program link in bio",
            "visual_style": "high energy, fast cuts, upbeat music",
            "estimated_engagement": "high", "notes": "Before/after framing used almost every week.",
            "why_it_worked": "Visual proof format builds credibility quickly.",
        },
        {
            "competitor_name": "Skincare Creator D", "profile_reference": "instagram.com/example-skincare-d (manually noted)",
            "content_type": "story", "hook": "Ask me anything about routines",
            "topic": "skincare routine", "offer": "n/a",
            "visual_style": "casual, selfie-style, text sticker heavy",
            "estimated_engagement": "medium", "notes": "Uses story Q&A stickers weekly to drive replies.",
            "why_it_worked": "Interactive stickers boost reply rate and feel personal.",
        },
        {
            "competitor_name": "Side Hustle Creator E", "profile_reference": "instagram.com/example-hustle-e (manually noted)",
            "content_type": "carousel", "hook": "I made $2k with this side hustle",
            "topic": "side hustle ideas", "offer": "free notion template",
            "visual_style": "bold typography, dark background",
            "estimated_engagement": "high", "notes": "Proof-style hooks with specific numbers seem to outperform vague claims.",
            "why_it_worked": "Specificity in the hook builds curiosity and trust simultaneously.",
        },
    ]
    out_path = os.path.join(OUT_DIR, "competitor_notes_sample.json")
    with open(out_path, "w") as f:
        json.dump(notes, f, indent=2)
    print(f"Wrote {len(notes)} competitor notes to {out_path}")


def generate_experiments():
    variables = ["hook_type", "posting_time", "caption_style", "video_length", "cta_type",
                 "thumbnail_style", "topic", "music_choice", "talking_head_vs_broll", "text_overlay_style"]
    experiments = []
    for i, variable in enumerate(variables):
        experiments.append({
            "variable": variable,
            "hypothesis": f"Changing {variable.replace('_', ' ')} will improve retention or save rate.",
            "expected_metric_improvement": f"+{random.randint(5, 20)}% on the primary metric for this variable",
            "status": random.choice(["planned", "running", "complete"]),
        })
    out_path = os.path.join(OUT_DIR, "experiments_sample.json")
    with open(out_path, "w") as f:
        json.dump(experiments, f, indent=2)
    print(f"Wrote {len(experiments)} experiments to {out_path}")


def generate_calendar_campaigns():
    campaigns = [
        {"name": "spring_launch", "niche": "wellness", "goal": "product launch awareness", "weeks": 2},
        {"name": "q2_growth_push", "niche": "fitness", "goal": "follower growth", "weeks": 4},
        {"name": "product_launch_2026", "niche": "budgeting app", "goal": "waitlist signups", "weeks": 3},
        {"name": "evergreen", "niche": "general lifestyle", "goal": "steady engagement", "weeks": 8},
        {"name": "collab_series", "niche": "cross-niche", "goal": "audience cross-pollination", "weeks": 2},
    ]
    out_path = os.path.join(OUT_DIR, "content_calendar_campaigns_sample.json")
    with open(out_path, "w") as f:
        json.dump(campaigns, f, indent=2)
    print(f"Wrote {len(campaigns)} campaign definitions to {out_path}")


if __name__ == "__main__":
    rows = generate_insights_csv()
    generate_insights_json(rows)
    generate_competitor_notes()
    generate_experiments()
    generate_calendar_campaigns()
    print(
        "\nNote: the 300 simulated users for the Virality Simulator are generated "
        "live at simulation run time (see app/simulation/entities.py) and are not "
        "persisted as static sample data, since they're meant to be regenerated "
        "per experiment/network structure."
    )
