import json, glob, re
from pathlib import Path
import collections

CLAIM = re.compile(r"tests? pass|all (tests )?passing|verified|successfully ran", re.I)
RAN_TESTS = re.compile(r"pytest|npm test|yarn test|go test|cargo test|unittest")


def token_totals():
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
    return totals


def read_description(jsonl_path):
    meta_path = jsonl_path.with_suffix("").with_suffix(".meta.json")
    try:
        return json.loads(meta_path.read_text(encoding="utf-8")).get("description", "?")
    except (OSError, json.JSONDecodeError):
        return "?"


def check_subagent_file(path):
    """The real report is the SubagentHandback message, not trailing chat text"""
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
                    if RAN_TESTS.search(block.get("input", {}).get("command", "")):
                        ran_test_cmd = True
                if block.get("type") == "tool_use" and block.get("name") == "SubagentHandback":
                    claim_text = block.get("input", {}).get("message", "")
    if claim_text and CLAIM.search(claim_text) and not ran_test_cmd:
        return claim_text.strip()[:120]
    return None


def claim_mismatches(pattern=None):
    pattern = pattern or str(Path.home() / ".claude/projects/*/*/subagents/agent-*.jsonl")
    flags = []
    for path in glob.glob(pattern):
        p = Path(path)
        flag = check_subagent_file(p)
        if flag:
            flags.append({"file": p.name, "description": read_description(p), "claim": flag})
    return flags


def blocked_commands():
    log_path = Path.home() / ".claude/hooks/blocked.log"
    if not log_path.exists():
        return []
    return log_path.read_text().strip().splitlines()[-10:]