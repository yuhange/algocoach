#!/usr/bin/env python3
"""Fetch LeetCode submissions and problem details via GraphQL API."""

import json, sys, urllib.request, time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROFILE = DATA_DIR / "profile.json"


def load_profile():
    if not PROFILE.exists():
        print("Error: data/profile.json not found. Run 'python3 coach.py init <username>' first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(PROFILE.read_text())


LC_COM = "https://leetcode.com/graphql"
LC_CN = "https://leetcode.cn/graphql"


def graphql(url, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": url.split("/graphql")[0],
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def fetch_recent_ac(username, limit=20):
    """Fetch recent AC submissions from leetcode.com."""
    q = """query($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id title titleSlug timestamp
        }
    }"""
    data = graphql(LC_COM, q, {"username": username, "limit": limit})
    return data.get("data", {}).get("recentAcSubmissionList", [])


def fetch_problem_detail(title_slug):
    """Fetch problem metadata: difficulty, tags."""
    q = """query($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId title titleSlug difficulty
            topicTags { name slug }
        }
    }"""
    data = graphql(LC_COM, q, {"titleSlug": title_slug})
    return data.get("data", {}).get("question")


def fetch_user_stats(username):
    """Fetch overall AC stats from leetcode.com."""
    q = """query($username: String!) {
        matchedUser(username: $username) {
            submitStats { acSubmissionNum { difficulty count } }
        }
    }"""
    data = graphql(LC_COM, q, {"username": username})
    user = data.get("data", {}).get("matchedUser")
    return user["submitStats"]["acSubmissionNum"] if user else []


def sync_submissions(username):
    """Sync recent submissions and enrich with problem details."""
    profile = json.loads(PROFILE.read_text())
    existing_ids = {p["id"] for p in profile["progress"]}

    subs = fetch_recent_ac(username)
    new_entries = []
    for s in subs:
        if s["id"] in existing_ids:
            continue
        detail = fetch_problem_detail(s["titleSlug"])
        entry = {
            "id": s["id"],
            "title": s["title"],
            "titleSlug": s["titleSlug"],
            "timestamp": s["timestamp"],
            "date": time.strftime("%Y-%m-%d", time.localtime(int(s["timestamp"]))),
            "difficulty": detail["difficulty"] if detail else "Unknown",
            "tags": [t["name"] for t in detail.get("topicTags", [])] if detail else [],
            "source": "leetcode.com",
            "status": "AC",
            "notes": ""
        }
        new_entries.append(entry)
        time.sleep(0.3)  # rate limit

    if new_entries:
        profile["progress"].extend(new_entries)
        PROFILE.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
        print(f"Synced {len(new_entries)} new submissions")
    else:
        print("No new submissions found")
    return new_entries


def add_manual(title_slug, status="AC", notes="", source="leetcode.com"):
    """Manually add a problem (for luogu or when auto-fetch doesn't work)."""
    profile = json.loads(PROFILE.read_text())
    detail = fetch_problem_detail(title_slug) if source == "leetcode.com" else None

    entry = {
        "id": f"manual-{int(time.time())}",
        "title": detail["title"] if detail else title_slug,
        "titleSlug": title_slug,
        "timestamp": str(int(time.time())),
        "date": time.strftime("%Y-%m-%d"),
        "difficulty": detail["difficulty"] if detail else "Unknown",
        "tags": [t["name"] for t in detail.get("topicTags", [])] if detail else [],
        "source": source,
        "status": status,
        "notes": notes
    }
    profile["progress"].append(entry)
    PROFILE.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    print(f"Added: {entry['title']} ({entry['difficulty']}) [{', '.join(entry['tags'])}]")
    return entry


if __name__ == "__main__":
    profile = json.loads(PROFILE.read_text())
    username = profile["username"]

    if len(sys.argv) > 1 and sys.argv[1] == "add":
        slug = sys.argv[2]
        status = sys.argv[3] if len(sys.argv) > 3 else "AC"
        source = sys.argv[4] if len(sys.argv) > 4 else "leetcode.com"
        add_manual(slug, status, source=source)
    else:
        print(f"Fetching submissions for {username}...")
        print(f"Stats: {json.dumps(fetch_user_stats(username), indent=2)}")
        sync_submissions(username)
