# S2.0.2 — 真实 SHA 样本 / 探针真实化 规划任务书

- 编号：`154-stage2-s202-real-sha-probe-planning-tasking-20260825`
- 前置：`153` S2.0.1 PASS；`docs/34` §4.1 序 2；用户裁定 **C**
- 范围：**规划 only**

## 背景

- S1.18 已交 `is_demo`；真实 SHA-locked 江苏样本仍 **OPEN**（本地曾零文件）
- S1.17 URL probe 默认 mock/不联外；「真实化」须钉死上限（不爬业务数据）

## NOW（CC 交付）

1. 起草 **`docs/35-stage2-s202-real-sha-probe-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - 本地/用户上传样本路径（复用 S1.13 admin；**不爬网**）
   - `compute_file_sha` / `replace_demo_with_real`（或等价）最小设计；无文件时诚实失败
   - 前端：真实 SHA 时 `DemoBadge` 隐藏 / live API 串联验收
   - URL probe「真实化」范围（可选 HEAD 实探 vs 仍 mock；须钉死与 docs/32 红线）
   - 与 S2.0.1 / S1.18 边界；不宣布 Gate PASS
3. 规划 only — 实现另开；回执 **`155`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate 1/2 PASS；不伪造 SHA；不爬网；不改 `gate_thresholds.json`；Cursor 不写 `docs/35` 正文。
