# /public-extracts 四轨 CSV 下载 — 缩刀任务书

- 编号：`403-stage2-public-extracts-csv-download-tasking-20260826`
- 前置：`402` PASS；JSON 下载已齐（`389`）；CC 报「无 §NOW，等任务书」
- 用户裁定：**C** + **D**；Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 由既有 4 fixture **确定性**生成 CSV（列序=首行键序，不重命名）→ `frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv`；(2) overview 表「下载 JSON」旁增 CSV 链（或同列第二链）；(3) ≥2 pytest（CSV 行数=fixture 行数；表头一致）+ smoke 针；(4) 回执 **`404`**（`-cc-`）|
| 本刀不做 | 改 fixture JSON 字节；Gate/O1 PASS；服务端动态导出 |
| 禁止 | 谎称 CSV=权威库；破坏 JSON 下载 |

## NOW

1. CSV 生成脚本或 build-time 一步（可 `scripts/` 小工具 + commit 产物）+ 页面链 + 测
2. pack → 回执 **`404`**
3. **双推** → `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；CSV 必须与 fixture 行数一致；做完**必须 push**。
