#!/usr/bin/env python3
"""One-shot migration: replay every card's history under the new
Anki-style SM-2 rules and overwrite review/schedule.json in place.

The history list itself (date + grade) is the source of truth; the
derived ef/reps/interval fields per step are recomputed from scratch.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "review" / "schedule.json"

DEFAULT_EF = 2.5
MIN_EF = 1.3

ANKI_FIRST_TWO = {
    (0, 3): 1, (0, 4): 3, (0, 5): 4,
    (1, 3): 3, (1, 4): 4, (1, 5): 6,
}


def replay(history: list[dict]) -> tuple[float, int, int, str, list[dict]]:
    ef = DEFAULT_EF
    reps = 0
    interval = 0
    last_date = ""
    new_history: list[dict] = []
    for h in history:
        q = int(h["grade"])
        last_date = h["date"]
        if q < 3:
            reps = 0
            interval = 1
        else:
            if reps < 2:
                interval = ANKI_FIRST_TWO[(reps, q)]
            else:
                interval = max(1, round(interval * ef))
            reps += 1
        ef = max(MIN_EF, ef + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_history.append({
            "date": last_date,
            "grade": q,
            "ef": round(ef, 3),
            "reps": reps,
            "interval": interval,
        })

    if last_date:
        due = (date.fromisoformat(last_date) + timedelta(days=interval)).isoformat()
    else:
        due = ""
    return ef, reps, interval, due, new_history


def main() -> None:
    data = json.loads(SCHEDULE.read_text())
    changed = 0
    for pid, card in data.items():
        before = (round(card["ef"], 3), card["reps"], card["interval"], card["due"])
        ef, reps, interval, due, new_history = replay(card["history"])
        card["ef"] = ef
        card["reps"] = reps
        card["interval"] = interval
        card["due"] = due
        card["history"] = new_history
        after = (round(ef, 3), reps, interval, due)
        if before != after:
            changed += 1
            print(f"  {pid:>4}  {before}  ->  {after}")

    SCHEDULE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"\nMigrated {changed}/{len(data)} cards. schedule.json overwritten.")


if __name__ == "__main__":
    main()
