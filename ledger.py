#!/usr/bin/env python3
from monitors_core import token_totals

if __name__ == "__main__":
    totals = token_totals()
    for day in sorted(totals):
        t = totals[day]
        print(f"{day} in={t['input']:>8} out={t['output']:>8}")