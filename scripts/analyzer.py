#!/usr/bin/env python3
"""Analyze weaknesses from submission history and conversation logs."""

import json, time
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
PROFILE = DATA_DIR / "profile.json"


def load_profile():
    return json.loads(PROFILE.read_text())


def save_profile(profile):
    PROFILE.write_text(json.dumps(profile, indent=2, ensure_ascii=False))


def log_conversation(question, topic_tags=None, knowledge_gaps=None):
    """Record a question asked during practice, with inferred weak points."""
    profile = load_profile()
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "question": question,
        "topic_tags": topic_tags or [],
        "knowledge_gaps": knowledge_gaps or [],
    }
    profile["conversations"].append(entry)
    save_profile(profile)
    return entry


def analyze_submissions():
    """Analyze submission history for weakness patterns."""
    profile = load_profile()
    progress = profile["progress"]
    if not progress:
        return {"tag_stats": {}, "weak_tags": [], "wa_tags": []}

    # Count tags across all submissions
    all_tags = Counter()
    wa_tags = Counter()
    for p in progress:
        for t in p.get("tags", []):
            all_tags[t] += 1
            if p.get("status") != "AC":
                wa_tags[t] += 1

    # Tags with high WA ratio = weak
    weak_tags = []
    for tag, wa_count in wa_tags.most_common():
        total = all_tags[tag]
        ratio = wa_count / total
        if ratio >= 0.3:
            weak_tags.append({"tag": tag, "wa": wa_count, "total": total, "ratio": round(ratio, 2)})

    return {"tag_stats": dict(all_tags.most_common()), "weak_tags": weak_tags, "wa_tags": dict(wa_tags)}


def analyze_conversations():
    """Analyze conversation logs for recurring knowledge gaps."""
    profile = load_profile()
    convos = profile.get("conversations", [])
    if not convos:
        return {"gap_counts": {}, "frequent_gaps": []}

    gap_counts = Counter()
    for c in convos:
        for gap in c.get("knowledge_gaps", []):
            gap_counts[gap] += 1

    frequent = [{"gap": g, "count": n} for g, n in gap_counts.most_common() if n >= 2]
    return {"gap_counts": dict(gap_counts), "frequent_gaps": frequent}


def build_weakness_profile():
    """Combine submission + conversation analysis into a weakness profile."""
    sub_analysis = analyze_submissions()
    conv_analysis = analyze_conversations()

    profile = load_profile()
    profile["weaknesses"] = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "from_submissions": sub_analysis["weak_tags"],
        "from_conversations": conv_analysis["frequent_gaps"],
        "tag_stats": sub_analysis["tag_stats"],
    }
    save_profile(profile)
    return profile["weaknesses"]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        tags = [t.strip() for t in sys.argv[3].split(",")] if len(sys.argv) > 3 else []
        gaps = [g.strip() for g in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
        log_conversation(q, tags, gaps)
        print(f"Logged: {q} | gaps: {gaps}")
    else:
        w = build_weakness_profile()
        print(json.dumps(w, indent=2, ensure_ascii=False))
