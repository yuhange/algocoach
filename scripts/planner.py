#!/usr/bin/env python3
"""Generate daily practice plan based on weakness profile."""

import json, urllib.request, time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROFILE = DATA_DIR / "profile.json"
LC_COM = "https://leetcode.com/graphql"


def graphql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(LC_COM, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://leetcode.com",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def fetch_problems_by_tag(tag_slug, limit=50):
    """Fetch problems filtered by tag from LeetCode."""
    q = """query($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(categorySlug: $categorySlug, limit: $limit, skip: $skip, filters: $filters) {
            totalNum data { questionId title titleSlug difficulty topicTags { name slug } }
        }
    }"""
    data = graphql(q, {
        "categorySlug": "", "limit": limit, "skip": 0,
        "filters": {"tags": [tag_slug]}
    })
    return data.get("data", {}).get("problemsetQuestionList", {}).get("data", [])


def generate_plan(num_problems=5):
    """Generate a daily plan targeting weak areas."""
    profile = json.loads(PROFILE.read_text())
    weaknesses = profile.get("weaknesses", {})
    done_slugs = {p["titleSlug"] for p in profile["progress"]}

    # Collect target tags: from submissions first, then conversations
    target_tags = []
    for w in weaknesses.get("from_submissions", []):
        target_tags.append(w["tag"])
    for g in weaknesses.get("from_conversations", []):
        target_tags.append(g["gap"])

    # Fallback: use least-practiced tags
    if not target_tags:
        stats = weaknesses.get("tag_stats", {})
        if stats:
            target_tags = [t for t, _ in sorted(stats.items(), key=lambda x: x[1])[:3]]
        else:
            target_tags = ["Dynamic Programming", "Graph", "Binary Search"]

    # Fetch candidates and filter out already-done problems
    candidates = []
    seen_slugs = set()
    for tag in target_tags[:3]:
        tag_slug = tag.lower().replace(" ", "-")
        try:
            problems = fetch_problems_by_tag(tag_slug)
            for p in problems:
                if p["titleSlug"] not in done_slugs and p["titleSlug"] not in seen_slugs:
                    candidates.append(p)
                    seen_slugs.add(p["titleSlug"])
            time.sleep(0.3)
        except Exception:
            continue

    # Sort: mix difficulties — 1 Easy, 2-3 Medium, 1 Hard
    easy = [p for p in candidates if p["difficulty"] == "Easy"]
    medium = [p for p in candidates if p["difficulty"] == "Medium"]
    hard = [p for p in candidates if p["difficulty"] == "Hard"]
    plan = easy[:1] + medium[:3] + hard[:1]
    plan = plan[:num_problems]
    plan_output = {
        "date": time.strftime("%Y-%m-%d"),
        "target_tags": target_tags[:3],
        "problems": [{
            "id": p["questionId"],
            "title": p["title"],
            "titleSlug": p["titleSlug"],
            "difficulty": p["difficulty"],
            "tags": [t["name"] for t in p.get("topicTags", [])],
            "url": f"https://leetcode.com/problems/{p['titleSlug']}/",
        } for p in plan]
    }
    return plan_output


if __name__ == "__main__":
    plan = generate_plan()
    print(f"\n📋 Daily Plan for {plan['date']}")
    print(f"🎯 Focus areas: {', '.join(plan['target_tags'])}\n")
    for i, p in enumerate(plan["problems"], 1):
        print(f"  {i}. [{p['difficulty']}] {p['title']}")
        print(f"     {p['url']}")
        print(f"     Tags: {', '.join(p['tags'])}\n")
