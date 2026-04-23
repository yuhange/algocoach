#!/usr/bin/env python3
"""AlgoCoach — AI algorithm practice tracker and coach.

Usage:
  python3 coach.py init <leetcode_username>   # First-time setup
  python3 coach.py sync                       # Sync LeetCode submissions
  python3 coach.py add <slug> [WA|TLE]        # Manually add a problem
  python3 coach.py plan                       # Generate daily practice plan
  python3 coach.py analyze                    # Show weakness analysis
  python3 coach.py log "<question>" "<tags>" "<gaps>"  # Log a conversation
  python3 coach.py status                     # Show overall progress
"""

import json, sys, shutil
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
PROFILE = DATA_DIR / "profile.json"
EXAMPLE = DATA_DIR / "profile.example.json"

sys.path.insert(0, str(ROOT))
from scripts.fetcher import sync_submissions, add_manual, fetch_user_stats
from scripts.analyzer import build_weakness_profile, log_conversation
from scripts.planner import generate_plan


def load_profile():
    if not PROFILE.exists():
        print("Error: Not initialized. Run 'python3 coach.py init <username>' first.")
        sys.exit(1)
    return json.loads(PROFILE.read_text())


def cmd_init(username):
    DATA_DIR.mkdir(exist_ok=True)
    if PROFILE.exists():
        print(f"Already initialized for '{load_profile()['username']}'. Delete data/profile.json to reinit.")
        return
    profile = json.loads(EXAMPLE.read_text()) if EXAMPLE.exists() else {
        "username": "", "platforms": {"leetcode_com": True, "leetcode_cn": False},
        "progress": [], "weaknesses": {}, "conversations": []
    }
    profile["username"] = username
    PROFILE.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    print(f"✅ Initialized for '{username}'. Run 'python3 coach.py sync' to fetch submissions.")


def cmd_status():
    p = load_profile()
    progress = p["progress"]
    ac = sum(1 for x in progress if x["status"] == "AC")
    wa = len(progress) - ac
    print(f"\n👤 {p['username']}")
    print(f"📊 Tracked: {len(progress)} problems ({ac} AC, {wa} WA/TLE)")
    if progress:
        tags = Counter(t for x in progress for t in x.get("tags", []))
        print(f"🏷️  Top tags: {', '.join(f'{t}({n})' for t, n in tags.most_common(5))}")
    w = p.get("weaknesses", {})
    if w.get("from_submissions"):
        weak = [f"{x['tag']}({x['ratio']*100:.0f}% WA)" for x in w["from_submissions"]]
        print(f"⚠️  Weak areas: {', '.join(weak)}")
    if w.get("from_conversations"):
        gaps = [f"{x['gap']}(×{x['count']})" for x in w["from_conversations"]]
        print(f"🧠 Knowledge gaps: {', '.join(gaps)}")
    print()


def cmd_log(question, tags_str="", gaps_str=""):
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
    gaps = [g.strip() for g in gaps_str.split(",") if g.strip()] if gaps_str else []
    log_conversation(question, tags, gaps)
    print(f"📝 Logged: {question}")
    if gaps:
        print(f"   Gaps: {', '.join(gaps)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) < 3:
            print("Usage: python3 coach.py init <leetcode_username>")
            sys.exit(1)
        cmd_init(sys.argv[2])
    elif cmd == "sync":
        p = load_profile()
        sync_submissions(p["username"])
    elif cmd == "add":
        slug = sys.argv[2]
        status = sys.argv[3] if len(sys.argv) > 3 else "AC"
        add_manual(slug, status)
    elif cmd == "plan":
        build_weakness_profile()
        plan = generate_plan()
        print(f"\n📋 Daily Plan for {plan['date']}")
        print(f"🎯 Focus: {', '.join(plan['target_tags'])}\n")
        for i, p in enumerate(plan["problems"], 1):
            print(f"  {i}. [{p['difficulty']}] {p['title']}")
            print(f"     {p['url']}")
    elif cmd == "analyze":
        w = build_weakness_profile()
        print(json.dumps(w, indent=2, ensure_ascii=False))
    elif cmd == "log":
        cmd_log(sys.argv[2] if len(sys.argv) > 2 else "",
                sys.argv[3] if len(sys.argv) > 3 else "",
                sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "status":
        cmd_status()
    else:
        print(__doc__)
