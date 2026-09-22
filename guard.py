#!/usr/bin/env python3
import json, re, sys

DENYLIST = [
    r"rm\s+-rf\s+/",
    r"git\s+push\s+.*--force",
    r"curl[^|]*\|\s*sh",
    r"\.ssh/|\.aws/|\.env",
]

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")


for pattern in DENYLIST:
    if re.search(pattern, command):
        print(f"Blocked: matched `{pattern}`", file=sys.stderr)
        sys.exit(2)

sys.exit(0)