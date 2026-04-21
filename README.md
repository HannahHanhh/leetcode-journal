# LeetCode Journal

个人刷题日志 + 基于 **SM-2 遗忘曲线**的复习调度。目标：**LeetCode 热题 100**。

## 日常工作流

1. **看今天要复习什么**
   ```bash
   python scripts/review.py today
   ```
2. **去 LeetCode 做题**（复习旧题优先，再刷新题）。
3. **记录结果**
   ```bash
   # 新题首刷
   python scripts/review.py add 1 "Two Sum"
   python scripts/review.py log 1 4

   # 已加入的题复习
   python scripts/review.py log 1 5
   ```
4. **写题记**：在 `problems/<id>-<slug>.md` 里用自己的话记思路、易错点、复杂度。
5. **Git commit**：让 Claude 按规范写 commit message。

## SM-2 评分标准（0-5）

| 分 | 含义 | 效果 |
|---|---|---|
| 5 | 完美回忆，秒解 | EF↑，间隔按 EF 放大 |
| 4 | 有犹豫但答对 | EF 略升 |
| 3 | 吃力答对 | EF 略降，仍继续推进 |
| 2 | 错了，看答案觉得熟悉 | **重置 reps**，间隔回到 1 天 |
| 1 | 错了，勉强想起一点 | 重置，EF 下降更多 |
| 0 | 完全不记得 | 重置，EF 下降最多 |

规则：**q<3 失败**（reps 归零，间隔=1d，但 EF 保留更新）；**q≥3 通过**（reps+1，间隔按 1d → 6d → prev·EF 递增）。EF 下限 1.3。

## 目录结构

```
leetcode-journal/
├── plan/hot100.md       # 热题 100 学习路径（按专题）
├── problems/            # 一题一 markdown：思路 + 易错点 + 复杂度
├── review/schedule.json # SM-2 调度数据（脚本自动维护）
├── scripts/review.py    # 调度脚本
├── CLAUDE.md            # 给 Claude 的项目规则
└── README.md
```

## 脚本命令速查

```bash
review.py today              # 今日/过期的复习题
review.py upcoming 7         # 未来 7 天复习计划
review.py add <id> <title>   # 新题入队（首次刷完后）
review.py log <id> <0-5>     # 记录本次评分
review.py list               # 所有题的状态
review.py stats              # 总体进度
```

## Commit 规范

- `solve: 0001 two-sum (hash)` — 新题首刷
- `review: 0001 grade=5` — 复习一次
- `note: 0001 add alt solution with two-pointer` — 补充题记
- `plan: reorder dp section` — 改计划文档
