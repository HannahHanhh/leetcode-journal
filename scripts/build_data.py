#!/usr/bin/env python3
"""Build static data files for the docs/ Pages site.

Reads:
  plan/hot100.md      -- topic-grouped problem list
  review/schedule.json -- SM-2 state

Writes:
  docs/hot100.json
  docs/schedule.json (copy)
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "plan" / "hot100.md"
SCHEDULE = ROOT / "review" / "schedule.json"
DOCS = ROOT / "docs"

TOPIC_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*\(\d+\)\s*$")
ITEM_RE = re.compile(r"^-\s+\[[ x]\]\s+(\d+)\s+(.+?)\s+(🟢|🟡|🔴)")
DIFFICULTY_MAP = {"🟢": "easy", "🟡": "medium", "🔴": "hard"}


def parse_hot100() -> list[dict]:
    topics: list[dict] = []
    current: dict | None = None
    seen_ids: set[str] = set()

    for line in PLAN.read_text().splitlines():
        m = TOPIC_RE.match(line)
        if m:
            current = {"name": m.group(1), "problems": []}
            topics.append(current)
            continue
        m = ITEM_RE.match(line)
        if m and current is not None:
            pid = m.group(1)
            if pid in seen_ids:
                continue  # skip duplicates across topics (e.g. 76)
            seen_ids.add(pid)
            current["problems"].append({
                "id": pid,
                "title": m.group(2).strip(),
                "difficulty": DIFFICULTY_MAP[m.group(3)],
            })
    return topics


def main() -> None:
    DOCS.mkdir(exist_ok=True)

    topics = parse_hot100()
    (DOCS / "hot100.json").write_text(
        json.dumps(topics, indent=2, ensure_ascii=False) + "\n"
    )

    if SCHEDULE.exists():
        shutil.copy(SCHEDULE, DOCS / "schedule.json")
    else:
        (DOCS / "schedule.json").write_text("{}\n")

    total = sum(len(t["problems"]) for t in topics)
    print(f"Wrote {len(topics)} topics, {total} problems -> docs/hot100.json")
    print(f"Copied schedule.json -> docs/schedule.json")


if __name__ == "__main__":
    main()
