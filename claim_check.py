#!/usr/bin/env python3
import sys
from monitors_core import claim_mismatches

if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else None
    for flag in claim_mismatches(pattern):
        print(f"[MISMATCH] {flag['file']} · {flag['description']}")
        print(f"  claimed: {flag['claim']}")