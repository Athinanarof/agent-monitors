#!/usr/bin/env python3
import json, glob, re, sys
from pathlib import Path

CLAIM = re.compile(r"tests? pass|all (tests )?passing|verified|successfully ran", re.I)
RAN_TESTS = re.compile(r"pytest|npm test|yarn test|go test|cargo test|unittest")

pattern = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / ".claude/projects/*/*/subagents/agent-*.jsonl")

def read_description(jsonl_path):
    meta_path = jsonl_path.with_suffix("").with_suffix(".meta.json")
    try:
        return json.loads(meta_path.read_text(encoding="utf-8")).get("description", "?")
    except (OSError, json.JSONDecodeError):
        return "?"


def check_subagent_file(path):
    """The real report is the SubagentHandback message, not tralling chat text"""
    claim_text, ran_test_cmd = None, False
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            for block in entry.get("message", {}).get("content", []) or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use" and block.get("name") == "Bash":
                    cmd = block.get("input", {}).get("command", "")
                    if RAN_TESTS.search(cmd):
                        ran_test_cmd = True
                if block.get("type") == "tool_use" and block.get("name") == "SubagentHandback":
                        claim_text = block.get("input", {}).get("message", "")
    if claim_text and CLAIM.search(claim_text) and not ran_test_cmd:
        return claim_text.strip()[:120]
    return None

for path in glob.glob(pattern):
    p = Path(path)
    flag = check_subagent_file(p)
    if flag:
        print(f"[MISTMATCH] {p.name} ·  {read_description(p)}")
        print(f"  claimed: {flag}")

# python claim_check.py fixtures/agent-fixture123.jsonl