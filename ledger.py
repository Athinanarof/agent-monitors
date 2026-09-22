#!/usr/bin/env python3
import json, glob, collections
from pathlib import Path

totals = collections.defaultdict(lambda: {"input": 0, "output": 0})

pattern = str(Path.home() / ".claude/projects/*/*.jsonl")
for path in glob.glob(pattern):
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            usage = entry.get("message", {}).get("usage")
            if not usage:
                continue
            day = entry.get("timestamp", "")[:10] or "unknown"
            totals[day]["input"] += usage.get("input_tokens", 0)
            totals[day]["output"] += usage.get("output_tokens", 0)

for day in sorted(totals):
    t = totals[day]
    print(f"{day} in={t['input']:>8} out={t['output']:>8}")

# optional: every day at 8am
# 0 8 * * * /usr/bin/python3 ~/ledger.py >> ~/ledger.log