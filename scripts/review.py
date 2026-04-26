#!/usr/bin/env python3
"""
LeetCode SM-2 review scheduler.

Commands:
  review.py today              List problems due today (or earlier).
  review.py upcoming [N]       Show next N days of reviews (default 7).
  review.py log <id> <grade>   Log a review session. grade: 0-5.
  review.py add <id> <title>   Add a new problem (first-time scheduled today).
  review.py stats              Show overall progress.
  review.py list               List every tracked problem with state.

SM-2 algorithm (Anki-style variant):
  - Each item has: repetitions n, easiness factor EF (>= 1.3), interval I (days).
  - After a grade q in [0..5]:
      if q < 3:  n = 0, I = 1                (failure: restart repetitions)
      else:      based on reps BEFORE incrementing,
                   reps=0:  q=3->1d  q=4->3d  q=5->4d
                   reps=1:  q=3->3d  q=4->4d  q=5->6d
                   reps>=2: I = round(I_prev * EF)
                 then n += 1
      EF := max(1.3, EF + (0.1 - (5-q)*(0.08 + (5-q)*0.02)))
      (EF is updated on every grade, including failures.)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "review" / "schedule.json"

DEFAULT_EF = 2.5
MIN_EF = 1.3

# (reps_before_pass, q) -> interval in days
ANKI_FIRST_TWO = {
    (0, 3): 1, (0, 4): 3, (0, 5): 4,
    (1, 3): 3, (1, 4): 4, (1, 5): 6,
}


@dataclass
class Card:
    id: str
    title: str
    ef: float = DEFAULT_EF
    reps: int = 0
    interval: int = 0
    due: str = ""          # ISO date, YYYY-MM-DD
    added: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)

    def grade(self, q: int, today: date) -> None:
        if not 0 <= q <= 5:
            raise ValueError("grade must be in 0..5")
        if q < 3:
            self.reps = 0
            self.interval = 1
        else:
            if self.reps < 2:
                self.interval = ANKI_FIRST_TWO[(self.reps, q)]
            else:
                self.interval = max(1, round(self.interval * self.ef))
            self.reps += 1
        self.ef = max(MIN_EF, self.ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
        self.due = (today + timedelta(days=self.interval)).isoformat()
        self.history.append({
            "date": today.isoformat(),
            "grade": q,
            "ef": round(self.ef, 3),
            "reps": self.reps,
            "interval": self.interval,
        })


def load() -> dict[str, Card]:
    if not SCHEDULE.exists():
        return {}
    raw = json.loads(SCHEDULE.read_text())
    return {k: Card(**v) for k, v in raw.items()}


def save(cards: dict[str, Card]) -> None:
    SCHEDULE.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE.write_text(json.dumps(
        {k: asdict(v) for k, v in cards.items()},
        indent=2, ensure_ascii=False,
    ) + "\n")


def cmd_add(cards: dict[str, Card], pid: str, title: str) -> None:
    today = date.today()
    if pid in cards:
        print(f"Problem {pid} already tracked: {cards[pid].title}")
        return
    cards[pid] = Card(
        id=pid,
        title=title,
        added=today.isoformat(),
        due=today.isoformat(),
    )
    print(f"Added {pid} ({title}), due today.")


def cmd_log(cards: dict[str, Card], pid: str, grade: int) -> None:
    if pid not in cards:
        print(f"Problem {pid} not tracked. Use `add` first.")
        sys.exit(1)
    card = cards[pid]
    card.grade(grade, date.today())
    print(f"[{pid}] {card.title}")
    print(f"  grade: {grade}  ->  EF={card.ef:.2f}  reps={card.reps}  "
          f"interval={card.interval}d  next={card.due}")


def cmd_today(cards: dict[str, Card]) -> None:
    today = date.today()
    due = [c for c in cards.values() if c.due and c.due <= today.isoformat()]
    due.sort(key=lambda c: c.due)
    if not due:
        print("Nothing due today. ✨")
        return
    print(f"Due today or earlier ({len(due)}):")
    for c in due:
        overdue = (today - date.fromisoformat(c.due)).days
        tag = f"(overdue {overdue}d)" if overdue > 0 else "(today)"
        print(f"  {c.id:>5}  {c.title:<40}  EF={c.ef:.2f}  reps={c.reps}  {tag}")


def cmd_upcoming(cards: dict[str, Card], days: int) -> None:
    today = date.today()
    horizon = today + timedelta(days=days)
    upcoming = [
        c for c in cards.values()
        if c.due and today.isoformat() < c.due <= horizon.isoformat()
    ]
    upcoming.sort(key=lambda c: c.due)
    if not upcoming:
        print(f"No reviews in the next {days} days.")
        return
    print(f"Upcoming {days} days ({len(upcoming)}):")
    for c in upcoming:
        print(f"  {c.due}  {c.id:>5}  {c.title:<40}  EF={c.ef:.2f}")


def cmd_stats(cards: dict[str, Card]) -> None:
    if not cards:
        print("No problems tracked yet.")
        return
    today = date.today().isoformat()
    total = len(cards)
    due = sum(1 for c in cards.values() if c.due and c.due <= today)
    mastered = sum(1 for c in cards.values() if c.reps >= 3 and c.ef >= 2.5)
    struggling = sum(1 for c in cards.values() if c.ef < 2.0)
    reviews = sum(len(c.history) for c in cards.values())
    print(f"Tracked problems : {total}")
    print(f"Due now          : {due}")
    print(f"Mastered         : {mastered}  (reps>=3 & EF>=2.5)")
    print(f"Struggling       : {struggling}  (EF<2.0)")
    print(f"Total reviews    : {reviews}")


def cmd_list(cards: dict[str, Card]) -> None:
    if not cards:
        print("No problems tracked yet.")
        return
    items = sorted(cards.values(), key=lambda c: c.id)
    print(f"{'ID':>5}  {'TITLE':<40}  {'EF':>4}  {'REPS':>4}  {'INT':>4}  DUE")
    for c in items:
        print(f"{c.id:>5}  {c.title:<40}  {c.ef:>4.2f}  {c.reps:>4}  "
              f"{c.interval:>4}  {c.due}")


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = argv[1]
    cards = load()

    if cmd == "today":
        cmd_today(cards)
    elif cmd == "upcoming":
        days = int(argv[2]) if len(argv) > 2 else 7
        cmd_upcoming(cards, days)
    elif cmd == "log":
        if len(argv) != 4:
            print("usage: review.py log <id> <grade 0-5>")
            sys.exit(1)
        cmd_log(cards, argv[2], int(argv[3]))
        save(cards)
    elif cmd == "add":
        if len(argv) < 4:
            print("usage: review.py add <id> <title>")
            sys.exit(1)
        cmd_add(cards, argv[2], " ".join(argv[3:]))
        save(cards)
    elif cmd == "stats":
        cmd_stats(cards)
    elif cmd == "list":
        cmd_list(cards)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
