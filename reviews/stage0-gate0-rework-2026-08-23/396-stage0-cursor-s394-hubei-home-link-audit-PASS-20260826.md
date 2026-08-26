# 湖北首页链接 — Cursor 审验 ACK + 首页文案校正

- 文件编号：`396-stage0-cursor-s394-hubei-home-link-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `52abff8` + 回执 `395`；用户反馈首页标题仍为旧 Stage 2 壳
- 任务书：`394`

---

## §0. 判定：**PASS**（395）

| 项 | 独立复验 | 判定 |
|---|---|---|
| 首页湖北轨 → `#track-hb` + enabled=FALSE | 源码 + smoke §13b | ✅ |
| 2 pytest | 本机 | ✅ |
| pack | **706 / 706 / 706** | ✅ |
| 回执 `395`（`-cc-`）| reviews | ✅ |

## §1. Cursor 顺带校正（用户反馈）

首页 `h1` / `layout` title：  
`CEGR — Stage 2 治理观察 (S2.0.1 + S2.7)` → **`CEGR — 官方公开数据 · 结构化呈现（demo）`**，并点名 `/public-extracts` 四轨主入口。  
**不**宣称 O1/Gate PASS。预览将重部署。

CC **POLL**（等下一指令）。

— End —
