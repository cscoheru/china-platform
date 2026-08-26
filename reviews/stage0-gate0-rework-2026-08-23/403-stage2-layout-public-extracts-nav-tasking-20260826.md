# 全站顶栏链到 /public-extracts — 缩刀任务书

- 编号：`403-stage2-layout-public-extracts-nav-tasking-20260826`
- 前置：`402` PASS；CC 报「无 §NOW」— Cursor 续刀
- 用户裁定：**C** + **D**；不等人裁定除非卡住

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `frontend/app/layout.tsx` 顶栏（`mode-banner` 内或紧接下方）增**全站常驻**链：`/public-extracts`（文案含「四轨 demo / 非 O1」）；(2) banner 文案补一句：主演示入口 = 公开提取四轨（不改 mock/mart 免责逻辑）；(3) ≥1 smoke/pytest 针；(4) 回执 **`404`**（`-cc-`）|
| 本刀不做 | 改 extract/fixture；Gate/O1 PASS；大改导航 IA |
| 禁止 | 谎称四轨=O1；去掉 demo 免责 |

## NOW

1. layout 顶栏链 + 测
2. pack → 回执 **`404`**
3. **双推** → `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不碰 fixture 字节。
