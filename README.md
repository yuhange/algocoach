# 🏋️ AlgoCoach

AI-powered algorithm practice tracker and coach. Tracks your LeetCode/Luogu submissions, analyzes weaknesses from your practice conversations, and generates targeted daily practice plans.

## Features

- **Auto-sync** LeetCode submissions via public GraphQL API (no login required)
- **Manual tracking** for any platform (Luogu, Codeforces, etc.)
- **Weakness analysis** from two signals:
  - Submission history (high WA/TLE ratio per tag)
  - Conversation logs (recurring questions → knowledge gaps)
- **Daily practice plans** — 5 problems (Easy → Medium → Hard) targeting your weak areas
- **AI agent integration** — works as a [Kiro](https://kiro.dev) skill for conversational coaching

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/algocoach.git
cd algocoach

# Initialize with your LeetCode username
python3 coach.py init <your_leetcode_username>

# Sync your recent submissions
python3 coach.py sync

# Get your first daily plan
python3 coach.py plan
```

## Usage

```bash
# Track a problem
python3 coach.py add two-sum AC
python3 coach.py add coin-change WA

# Track a Luogu problem (manual)
python3 coach.py add P1001 AC

# Log a question you asked during practice (with knowledge gaps)
python3 coach.py log "为什么这题不能用贪心？" "DP,Greedy" "DP vs 贪心的选择"

# View weakness analysis
python3 coach.py analyze

# Generate targeted daily plan
python3 coach.py plan

# Check overall progress
python3 coach.py status
```

## How Weakness Detection Works

AlgoCoach identifies your weak areas from two sources:

### 1. Submission Analysis
Tags with high WA/TLE ratio are flagged. If you WA on 3 out of 5 DP problems, "Dynamic Programming" gets marked as weak.

### 2. Conversation Analysis
When you ask questions during practice (via the AI agent or `coach.py log`), AlgoCoach extracts knowledge gaps. If you ask about "DP vs Greedy" twice, it knows you need systematic practice on that topic.

```
📊 Weakness Profile:
  ⚠️  From submissions: BFS (100% WA), DP (33% WA)
  🧠 From conversations: "DP vs 贪心的选择" (asked 2x)
```

The daily planner then pulls problems from LeetCode that target these specific weak areas.

## Use as AI Agent Skill

AlgoCoach includes a `SKILL.md` that makes it work as a [Kiro CLI](https://kiro.dev) agent skill. When integrated, the agent will:

1. **Automatically track** problems you mention in conversation
2. **Silently log** your algorithm questions and infer knowledge gaps
3. **Generate plans** when you ask "what should I practice today?"

## Cross-Platform Sync

All data lives in `data/profile.json`. To use across machines:
- Put it in a git repo and commit `profile.json` (remove it from `.gitignore`)
- Or sync via cloud storage (Dropbox, iCloud, etc.)

## Project Structure

```
algocoach/
├── coach.py                 # CLI entry point
├── SKILL.md                 # AI agent skill definition
├── data/
│   ├── profile.example.json # Template (copy to profile.json)
│   └── profile.json         # Your data (gitignored)
└── scripts/
    ├── fetcher.py           # LeetCode API + manual add
    ├── analyzer.py          # Weakness analysis + conversation logging
    └── planner.py           # Daily plan generation
```

## Requirements

- Python 3.7+
- No external dependencies (uses only stdlib `urllib`, `json`, `pathlib`)

## License

MIT
