# Agent Traffic Monitors

Scripts that watch your Claude Code sessions: token usage, blocked commands, subagents that claim tests pass without running any. Plus a dashboard that shows them together.

Everything reads from files Claude Code already writes under `~/.claude/`. Nothing here talks to a network or an API.

## What's in here

| File | What it does |
|---|---|
| `guard.py` | A `PreToolUse` hook. Blocks dangerous bash commands (`rm -rf /`, force pushes, `curl \| sh`, touching `.ssh`/`.aws`/`.env`) and logs every block to `~/.claude/hooks/blocked.log`. |
| `ledger.py` | Prints input/output token totals per day, read from `~/.claude/projects/*/*.jsonl`. |
| `claim_check.py` | Scans subagent transcripts (`~/.claude/projects/*/*/subagents/agent-*.jsonl`) for a `SubagentHandback` claiming tests pass with no test command anywhere in its Bash history, and flags the mismatch. |
| `monitors_core.py` | The shared logic behind all three: `token_totals()`, `blocked_commands()`, `claim_mismatches()`. `ledger.py`, `claim_check.py`, and `server.py` import from here instead of duplicating it. |
| `server.py` | A FastAPI backend that exposes the same logic as one endpoint, `/api/stats`. |
| `monitor-ui/` | A React + TypeScript (Vite) frontend that polls `/api/stats` every 3 seconds. |
| `agent-fixture123.jsonl` / `.meta.json` | A hand-built test fixture, a fake subagent transcript with a false claim, used to check `claim_check.py`'s logic. Not real session data. |

## Setup

Requires Python 3 and Node.js (`node --version` to check).

```bash
python -m venv venv
source venv/Scripts/activate      # Git Bash on Windows
pip install -r requirements.txt
```

`guard.py` only runs if it's wired into Claude Code as a hook. Add it to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python /path/to/guard.py" }]
      }
    ]
  }
}
```

## Running the CLI monitors

```bash
python ledger.py          # token totals by day
python claim_check.py     # flagged subagent claims
```

## Running the dashboard

Two terminals, both stay open:

```bash
# terminal 1, backend
source venv/Scripts/activate
uvicorn server:app --reload --port 8787

# terminal 2, frontend
cd monitor-ui
npm install
npm run dev
```

Then open the URL Vite prints, usually `http://localhost:5173`.

## Notes

`guard.py` doesn't import from `monitors_core.py` on purpose. It only writes to `blocked.log` and doesn't read from any of the shared functions, so there's nothing to extract.

The dashboard's default file patterns only look inside `~/.claude/projects/`. The fixture files in this repo won't show up there unless copied into a matching `projects/<any>/<any>/subagents/` path. They're for testing `claim_check.py` on its own.
