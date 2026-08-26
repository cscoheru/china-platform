# 真 SHA 投递上线缩刀 — S2.0.2-live / O1 intake

- 编号：`290-stage2-real-sha-intake-live-tasking-20260826`
- 前置：`289` dbt mart skel PASS；`docs/35` §4；`scripts/compute_file_sha.py` + `replace_demo_with_real.py` 已交
- 用户裁定：**D**；自主推进；**尽快真实数据**；**O1 无材料则不得伪造 / 不爬网**
- 动机：骨架已齐；真数据卡点=合法持有文件投递。本刀把「有文件 → SHA → 清 is_demo → seed」打成可执行单路径。

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | ① 写 **`docs/48`** 投递手册（路径 allowlist：`/tmp/cegr_uploads/` 或 `data/seed_archives/`；一步命令；无文件时诚实失败）② 落地 **`scripts/intake_real_sha_if_present.py`**（复用 `compute_file_sha` allowlist；发现文件则算真 SHA、组装 `is_demo!=true` lineage、可选调用既有 seed/replace 契约；无文件 → 非零 rc + 明确 `WAITING_FILE`）③ 最小 pytest：无文件 → skip/xfail 诚实；用 allowlist 下**临时**控制流文件验证「非零 SHA + is_demo 清除契约」（禁止把控制流文件冒充江苏政府样本/禁止宣布 O1 收口）④ 若投递目录**已有**用户文件：跑通 SHA+lineage 并写入回执（仍不擅自标 O1 CLOSED，除非用户明示该文件即 O1）|
| 本刀不做 | HTTP 爬取；伪造非零 SHA；把 demo/mock 冒充真实；宣布 Gate / O1 PASS；改 CF/nginx |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；无文件硬造样本 |

## NOW

1. 落地 `docs/48` + `scripts/intake_real_sha_if_present.py` + pytest
2. 检查 allowlist 是否已有用户文件 → 有则跑通并记入回执；无则 `WAITING_FILE`（**不算红线 FAIL**）
3. 补 pack → commit → 回执 **`291`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不伪造 SHA/样本；不爬网；无文件必须诚实 `WAITING_FILE`；不擅自宣布 O1 收口。
