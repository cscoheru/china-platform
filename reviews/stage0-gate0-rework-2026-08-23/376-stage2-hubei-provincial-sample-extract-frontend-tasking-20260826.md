# 湖北省级 REGISTRY_SAMPLE 抽取 + 前端分节 — 缩刀任务书

- 编号：`376-stage2-hubei-provincial-sample-extract-frontend-tasking-20260826`
- 前置：`375` PASS；三轨已齐；用户 2026-08-26：**不要等我裁定，除非卡住了，继续自行决定往下走**
- 用户裁定：**C** 自主 + **D** 缩刀；Cursor 代判；仅登录/验证码/付费/技术死墙 escalate

## SCHEMA / 裁定（Cursor 代判）

| 决策点 | 裁定 |
|---|---|
| 为何湖北 | registry 已有 `spikes/02-provincial-yearbook/hubei_2026_06.xlsx`（SHA `c5cf5a…`）；connector 已有 `extract_xlsx_tables`；**live 仍 FALSE**（JS-shell / 341 暂缓）— 本刀只走 **local-sample** |
| 本刀做 | (1) `--from-local-sample --allow-disabled-local-sample --pilot-domain=tjj.hubei.gov.cn --pilot-category=PROVINCIAL_BULLETIN` 写出 extract ≥1 行（期望 ≈19）；(2) `frontend/lib/public_extract_hubei.json` 快照 + `/public-extracts` **第四分节**（显式 REGISTRY_SAMPLE / demo；注明 live `enabled=FALSE` 暂缓，**非** live）；(3) 不覆盖 NBS 三轨既有 fixture；(4) ≥3 pytest（湖北 ≥1 行 + NBS/深圳不回归）+ smoke 针；(5) 回执 **`377`**（`-cc-`）|
| 本刀不做 | 湖北 live HTTPS/headless；改 `enabled=TRUE`；Gate/O1 PASS；改 NBS/深圳字节 |
| 禁止 | headless；伪造行；把 disabled 源谎称 live |

## NOW

1. local-sample intake（带 `--allow-disabled-local-sample` + `--confirm-live=PATH` lineage）
2. fixture + 页面第四分节 + 测
3. pack → 回执 **`377`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不启用湖北 live；不绕 JS-shell；不破坏既有三轨。
