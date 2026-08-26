# 公开源深链发现（无 headless）— 缩刀任务书（+ Cursor 代判）

- 编号：`339-stage2-public-source-deeplink-discover-tasking-20260826`
- 前置：`338` Hubei PASS；`341` Cursor 代判（用户授权「你自己判断」）
- 用户裁定：**D** + **源工程由 Cursor 代判**（仅 AUTH/付费打断用户）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) **deeplink discover**：index HTML 用 bs4/`re` 找同域 `.xlsx`/`.xls`（相对路径拼绝对）；**禁止 headless / 禁止执行 JS**；(2) 找到 → 下载附件 → sha/archive/extract；**真实附件**且非 JS 壳 → 可 `O1_AUTO_INTAKED` + `is_demo=false`，并 **更新 registry** 该行 `primary_url`+`file_hash_sha256`+`file_size_bytes`（per `341`）；(3) 0 条或 JS 壳（体积阈值）→ `reviews/…tech-blocked…md`，报告用户，不绕过；(4) 列表页本身仍只许 `CANDIDATE_AUTO`（per `341`）；(5) ≥6 pytest；(6) Hubei **再 live**；回执 **`340`** |
| 本刀不做 | headless；把列表页今日哈希当永久 pin；深圳全量；Gate PASS |
| 禁止 | 执行 JS；盲爬外域；JS 壳标 O1；不问用户就绕登录/付费 |

## NOW

1. 落地 deeplink + JS 壳检测 + tech-blocked；成功则 pin registry（`341`）
2. Hubei 再 live；证据入回执
3. 补 pack → 回执 **`340`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不 headless；不绕 AUTH；不伪造；列表页 ≠ O1。
