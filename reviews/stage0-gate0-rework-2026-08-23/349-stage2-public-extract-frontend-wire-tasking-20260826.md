# 公开提取 → 前端结构化呈现 — 缩刀任务书

- 编号：`349-stage2-public-extract-frontend-wire-tasking-20260826`
- 前置：`348` PASS；`data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` 63 行；产品目标②结构化呈现
- 用户裁定：**D** + Cursor 代判源工程

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 前端可读 `public_extracts`（或生成 `frontend` fixture 自该 JSON，构建期/运行期二选一，优先简单可测）；(2) 首页或专用区块展示 NBS 提取表（≥若干行可见）；**显式标注** `REGISTRY_SAMPLE` / demo，非 live O1；(3) 保留现有 mart demo 旗标逻辑，不谎称真收口；(4) ≥1 测或 build 证据；(5) 回执 **`350`** |
| 本刀不做 | 宣布 O1/Gate PASS；HTTP pin 深圳；headless；改 CF |
| 禁止 | 把 sample 标成 live 真数据；绕 AUTH |

## NOW

1. 接线 NBS extract → UI（sample 标）
2. 补 pack → 回执 **`350`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；sample ≠ live；不伪造。
