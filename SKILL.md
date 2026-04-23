---
name: algocoach
description: AI algorithm practice tracker and coach. Tracks daily LeetCode/Luogu submissions, analyzes weaknesses from conversations and submissions, generates targeted daily practice plans.
version: 1.0.0
tags: [skill, algorithm, leetcode, practice, coaching]
---

# AlgoCoach

## Overview
Track algorithm practice, analyze weaknesses, and generate targeted daily plans. Learns from your questions during practice to identify knowledge gaps.

## Usage
When the user:
- Says they did a problem (e.g. "今天做了 LC 300", "I solved two-sum")
- Asks about algorithm concepts during practice (e.g. "为什么这题不能用贪心")
- Wants a daily practice plan (e.g. "给我出题", "what should I practice today")
- Asks about their progress or weaknesses (e.g. "我哪里比较弱", "show my stats")

## Instructions

### 1. Tracking Submissions

When the user mentions completing a problem, record it:

```bash
python3 scripts/fetcher.py add <title-slug> <AC|WA|TLE> [source]
```

Examples:
```bash
python3 scripts/fetcher.py add longest-increasing-subsequence AC
python3 scripts/fetcher.py add coin-change WA
python3 scripts/fetcher.py add P1001 AC luogu  # for Luogu problems
```

To sync recent LeetCode submissions automatically:
```bash
python3 scripts/fetcher.py
```

### 2. Logging Conversations (CRITICAL — do this automatically)

**Every time the user asks an algorithm question during practice**, silently log it with inferred knowledge gaps:

```bash
python3 scripts/analyzer.py log "<question>" "<topic_tags>" "<knowledge_gaps>"
```

You MUST infer the `knowledge_gaps` from the question. Examples:

| User asks | knowledge_gaps |
|-----------|---------------|
| "为什么这题不能用贪心？" | "DP vs 贪心的选择" |
| "什么时候用BFS什么时候用DFS？" | "BFS vs DFS选择" |
| "这个递归怎么改成迭代？" | "递归转迭代" |
| "时间复杂度怎么分析？" | "复杂度分析" |
| "为什么要用单调栈？" | "单调栈适用场景" |

After logging, answer the user's question normally. The logging is silent background work.

### 3. Analyzing Weaknesses

```bash
python3 scripts/analyzer.py
```

Returns a JSON weakness profile with:
- `from_submissions`: tags with high WA ratio
- `from_conversations`: knowledge gaps asked about ≥2 times
- `tag_stats`: overall tag distribution

Present this to the user in a friendly format, e.g.:
```
📊 你的弱点分析：
- 提交数据显示：BFS 类题目 100% WA，DP 类 33% WA
- 对话分析显示：你反复问到 "DP vs 贪心的选择"（2次），说明这个知识点需要系统强化
```

### 4. Generating Daily Plans

```bash
python3 scripts/planner.py
```

Generates 5 problems (1 Easy + 3 Medium + 1 Hard) targeting weak areas. Present like:
```
📋 今日题单（针对你的薄弱环节）
🎯 重点：Dynamic Programming, BFS

1. [Easy] Climbing Stairs — 热身
   https://leetcode.com/problems/climbing-stairs/
2. [Medium] Coin Change — DP 基础
   https://leetcode.com/problems/coin-change/
...
```

### 5. Showing Status

```bash
python3 coach.py status
```

### Conversation Flow Example

```
User: 今天做了 longest-increasing-subsequence，想了20分钟没思路看了题解

Agent: [runs: fetcher.py add longest-increasing-subsequence AC]
       [runs: analyzer.py log "想了20分钟没思路看了题解" "Dynamic Programming" "LIS类DP建模"]
       
       记录了！LIS 是经典的 DP 题。你在 DP 子序列类型上已经是第 3 次需要看题解了。
       需要我讲解一下 LIS 的思路吗？

User: 为什么不能用贪心？

Agent: [runs: analyzer.py log "为什么LIS不能用贪心" "DP,Greedy" "DP vs 贪心的选择"]
       
       因为 LIS 需要全局最优解...（正常回答问题）

User: 给我出明天的题

Agent: [runs: analyzer.py (update weaknesses)]
       [runs: planner.py]
       
       📋 明日题单...
```

## Data Location

All data stored in `data/profile.json` relative to this skill's path. Sync this file across machines for cross-platform use.

## Deterministic Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fetcher.py` | LeetCode API sync + manual problem add |
| `scripts/fetcher.py add <slug> <status>` | Add single problem |
| `scripts/analyzer.py` | Build weakness profile |
| `scripts/analyzer.py log "<q>" "<tags>" "<gaps>"` | Log conversation |
| `scripts/planner.py` | Generate daily plan |
| `coach.py status` | Show progress summary |
