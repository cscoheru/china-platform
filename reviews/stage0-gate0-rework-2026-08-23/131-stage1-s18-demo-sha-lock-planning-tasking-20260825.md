# S1.18 — DEMO SHA / 真实样本锁定 规划任务书

- 编号：`131-stage1-s18-demo-sha-lock-planning-tasking-20260825`
- 前置：`130` S1.17 PASS；用户裁定 **A**；`docs/27` §4 剩余演示诚实缺口
- 范围：**规划 only**

## 背景

- 江苏 GDP demo seed 已可 API 出序列，但 `source_file_sha256` 仍为 **DEMO placeholder**（`docs/27`）
- 工程自动化缺口（R03/R08/R12/§2.4/§2.7–2.9）已闭合；Gate 1 前须诚实处理「真实样本 vs DEMO」边界

## NOW（CC 交付）

1. 起草 **`docs/33-stage1-s18-demo-sha-lock-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - 现有 `data/seeds/jiangsu_gdp_*` / `seed_jiangsu_gdp_demo.py` 现状
   - SHA-256 锁定路径选项（本地已有 XLSX/PDF vs 仍标 DEMO；**不爬网**）
   - 与 S1.12 Gate prep pack / API 演示脚本的衔接
   - 空样本 / 无法取得真实文件时的诚实失败策略（不伪造 SHA）
3. 规划 only — 实现另开；回执 **`132`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不伪造 SHA；不改 `gate_thresholds.json`；Cursor 不写 `docs/33` 正文。
