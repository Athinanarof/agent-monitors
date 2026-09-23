#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monitors_core import token_totals, blocked_commands, claim_mismatches

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/stats")
def stats():
    totals = token_totals()
    today = sorted(totals)[-1] if totals else None
    return {
        "today": today,
        "tokens": totals.get(today, {"input": 0, "output": 0}),
        "blocked": blocked_commands(),
        "mismatches": claim_mismatches()[-10:],
    }