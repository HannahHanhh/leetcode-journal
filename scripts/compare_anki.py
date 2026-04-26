#!/usr/bin/env python3
"""Replay every card's history under an Anki-style SM-2 variant
and print a side-by-side comparison against the current schedule.

Does NOT modify schedule.json.

Anki-style rule changes (relative to classic SM-2):
  reps=0 (just-passed first time)
    q=3 -> 1d   q=4 -> 3d   q=5 -> 4d
  reps=1
    q=3 -> 3d   q=4 -> 4d   q=5 -> 6d
  reps>=2
    interval = round(prev_interval * EF)   (same as classic)
  q<3
    reps=0, interval=1                     (same as classic)

EF formula is unchanged:
  EF := max(1.3, EF + 0.1 - (5-q)*(0.08 + (5-q)*0.02))
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "review" / "schedule.json"

DEFAULT_EF = 2.5
MIN_EF = 1.3

# (reps_before_pass, q) -> interval
ANKI_FIRST_TWO = {
    (0, 3): 1, (0, 4): 3, (0, 5): 4,
    (1, 3): 3, (1, 4): 4, (1, 5): 6,
}


def replay_anki(history: list[dict]) -> tuple[float, int, int, str]:
    """Return final (ef, reps, interval, due) after replaying history with Anki rules."""
    ef = DEFAULT_EF
    reps = 0
    interval = 0
    last_date = ""
    for h in history:
        q = h["grade"]
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

    if last_date:
        due = (date.fromisoformat(last_date) + timedelta(days=interval)).isoformat()
    else:
        due = ""
    return round(ef, 3), reps, interval, due


OUT = ROOT / "review" / "anki-compare.md"


def main() -> None:
    data = json.loads(SCHEDULE.read_text())
    rows = []
    for pid, card in data.items():
        old_ef = round(card["ef"], 3)
        old_reps = card["reps"]
        old_interval = card["interval"]
        old_due = card["due"]
        new_ef, new_reps, new_interval, new_due = replay_anki(card["history"])
        rows.append({
            "id": pid,
            "title": card["title"],
            "old": (old_ef, old_reps, old_interval, old_due),
            "new": (new_ef, new_reps, new_interval, new_due),
        })

    rows.sort(key=lambda r: int(r["id"]))

    lines = [
        "# SM-2 vs Anki 规则对照表",
        "",
        "对每张卡按 Anki 风格规则重放历史，对比当前 `schedule.json` 的最终状态。",
        "**未改动真实数据**。",
        "",
        "Anki 规则差异：",
        "- reps=0（首次通过）：q=3→1d, q=4→3d, q=5→4d",
        "- reps=1：q=3→3d, q=4→4d, q=5→6d",
        "- reps≥2 同 SM-2：`round(interval * EF)`",
        "- q<3 同 SM-2：reps 重置, interval=1",
        "",
        "| | ID | Title | Old EF/reps/int/due | New EF/reps/int/due | Δdue (days) |",
        "|---|---:|---|---|---|---:|",
    ]
    for r in rows:
        oef, orep, oi, od = r["old"]
        nef, nrep, ni, nd = r["new"]
        old_str = f"{oef:.2f} / {orep} / {oi}d / {od}"
        new_str = f"{nef:.2f} / {nrep} / {ni}d / {nd}"
        delta = ""
        if od and nd:
            d = (date.fromisoformat(nd) - date.fromisoformat(od)).days
            delta = f"{d:+d}" if d != 0 else "0"
        marker = "" if r["old"] == r["new"] else "🔸"
        lines.append(
            f"| {marker} | {r['id']} | {r['title']} | {old_str} | {new_str} | {delta} |"
        )

    diffs = sum(1 for r in rows if r["old"] != r["new"])
    lines += [
        "",
        f"**{diffs} / {len(rows)} 卡片在 Anki 规则下会有不同状态。**",
        "",
        "🔸 标记代表新旧规则结果不同。",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({diffs}/{len(rows)} cards differ)")


if __name__ == "__main__":
    main()
