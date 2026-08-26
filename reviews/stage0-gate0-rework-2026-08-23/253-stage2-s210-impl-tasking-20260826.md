# S2.10 落地刀 任务书（CC-authored; 用户 override "继续S2.10 落地刀"）

- 编号：`253-stage2-s210-impl-tasking-20260826`
- 前置：`252` docs/45 索引 PASS；`docs/44` 规划；`docs/10` §3.1-3.5
- 触发：**用户 override** — "继续S2.10 落地刀"（2026-08-26；直接授权，绕过 queue_rev=98 协议自造刀限制）
- 用户裁定：**D**（缩刀节奏）+ Stage 2 **C**

> ⚠ 本刀由 CC 在用户直接 override 下起草；00-CC-CURRENT.md 仍 `phase=POLL`。
> 严格意义上，tasking 仍属 Cursor 拥有（per AGENTS.md）。
> 此处仅作 audit trail：记录用户 override + 本刀实际范围。

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | 5 个 pytest 文件（§3.1 + §3.5 real + §3.2-§3.4 xfail stub）+ bump script + receipt 253 |
| 路径 | `tests/test_*_s210.py`（per docs/44 §7 + docs/45 §4）|
| **禁止** | 落地刀不出 dbt / 不出 migration / 不出 UI（per tasking 250 §SCHEMA + 用户 D）|
| **禁止** | 不宣布 Gate 2 PASS（per docs/34 §1 + §8 #8 + §133）|

## NOW

1. 落地 5 个 pytest 文件（`test_peer_selection_justified_s210.py` + `test_attribution_language_labels_s210.py` + 3 xfail stubs）
2. 跑通 §3.1 + §3.5 case；§3.2-§3.4 留 xfail stub + reason "Stage 3 收口"
3. 补 pack → commit → origin → 回执 **`253`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不伪造 SHA；不动 Cursor 拥有 doc；不写 heartbeat 到磁盘。