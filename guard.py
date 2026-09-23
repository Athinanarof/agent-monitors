#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
from datetime import datetime

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
        log_path = Path.home() / ".claude/hooks/blocked.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as log:
            log.write(f"{datetime.now().isoformat(timespec='seconds')} {command}\n")
        sys.exit(2)

sys.exit(0)