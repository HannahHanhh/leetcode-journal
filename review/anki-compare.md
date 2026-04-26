# SM-2 vs Anki 规则对照表

对每张卡按 Anki 风格规则重放历史，对比当前 `schedule.json` 的最终状态。
**未改动真实数据**。

Anki 规则差异：
- reps=0（首次通过）：q=3→1d, q=4→3d, q=5→4d
- reps=1：q=3→3d, q=4→4d, q=5→6d
- reps≥2 同 SM-2：`round(interval * EF)`
- q<3 同 SM-2：reps 重置, interval=1

| | ID | Title | Old EF/reps/int/due | New EF/reps/int/due | Δdue (days) |
|---|---:|---|---|---|---:|
|  | 1 | Two Sum | 2.38 / 2 / 6d / 2026-05-02 | 2.38 / 2 / 6d / 2026-05-02 | 0 |
| 🔸 | 3 | Longest Substring Without Repeating Characters | 2.22 / 2 / 6d / 2026-04-28 | 2.22 / 2 / 3d / 2026-04-25 | -3 |
|  | 11 | Container With Most Water | 2.14 / 2 / 6d / 2026-04-30 | 2.14 / 2 / 6d / 2026-04-30 | 0 |
| 🔸 | 15 | 3Sum | 1.82 / 2 / 6d / 2026-05-02 | 1.82 / 2 / 4d / 2026-04-30 | -2 |
|  | 41 | First Missing Positive | 2.36 / 1 / 1d / 2026-04-27 | 2.36 / 1 / 1d / 2026-04-27 | 0 |
|  | 42 | Trapping Rain Water | 2.60 / 2 / 6d / 2026-04-28 | 2.60 / 2 / 6d / 2026-04-28 | 0 |
|  | 49 | Group Anagrams | 2.04 / 1 / 1d / 2026-04-27 | 2.04 / 1 / 1d / 2026-04-27 | 0 |
| 🔸 | 53 | Maximum Subarray | 2.28 / 1 / 1d / 2026-04-27 | 2.28 / 1 / 4d / 2026-04-30 | +3 |
|  | 54 | Spiral Matrix | 1.70 / 0 / 1d / 2026-04-28 | 1.70 / 0 / 1d / 2026-04-28 | 0 |
| 🔸 | 56 | Merge Intervals | 2.04 / 2 / 6d / 2026-05-02 | 2.04 / 2 / 4d / 2026-04-30 | -2 |
|  | 73 | Set Matrix Zeroes | 1.86 / 0 / 1d / 2026-04-28 | 1.86 / 0 / 1d / 2026-04-28 | 0 |
|  | 76 | Minimum Window Substring | 1.82 / 1 / 1d / 2026-04-27 | 1.82 / 1 / 1d / 2026-04-27 | 0 |
|  | 128 | Longest Consecutive Sequence | 2.04 / 1 / 1d / 2026-04-27 | 2.04 / 1 / 1d / 2026-04-27 | 0 |
|  | 189 | Rotate Array | 2.60 / 2 / 6d / 2026-05-02 | 2.60 / 2 / 6d / 2026-05-02 | 0 |
|  | 238 | Product of Array Except Self | 2.80 / 3 / 16d / 2026-05-12 | 2.80 / 3 / 16d / 2026-05-12 | 0 |
|  | 239 | Sliding Window Maximum | 1.82 / 1 / 1d / 2026-04-27 | 1.82 / 1 / 1d / 2026-04-27 | 0 |
| 🔸 | 283 | Move Zeroes | 2.08 / 3 / 13d / 2026-05-04 | 2.08 / 3 / 7d / 2026-04-28 | -6 |
| 🔸 | 438 | Find All Anagrams in a String | 1.82 / 2 / 6d / 2026-05-02 | 1.82 / 2 / 4d / 2026-04-30 | -2 |
| 🔸 | 560 | Subarray Sum Equals K | 2.36 / 2 / 6d / 2026-05-02 | 2.36 / 2 / 4d / 2026-04-30 | -2 |

**7 / 19 卡片在 Anki 规则下会有不同状态。**

🔸 标记代表新旧规则结果不同。
