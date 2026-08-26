# 官方公开源自动获取 — 规划缩刀任务书

- 编号：`327-stage2-official-open-source-auto-ingest-plan-tasking-20260826`
- 前置：用户 2026-08-26 裁定：**不再等用户投喂**；产品两目标=①自动检索官方公开数据 ②结构化呈现
- 用户裁定：**D**；覆盖此前「仅用户投递 O1」等待策略
- 对齐 PRD §9（来源登记 / 原始不可变 / 哈希）+ docs/00 §3 红线 7（**不绕验证码、付费墙、技术限制**）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 写 **`docs/52`**：官方**公开**源自动获取规划——(1) 允许：source_registry 登记的公开下载包 / 开放 API / 无登录公开页面的稳定文件 URL；(2) 禁止：绕验证码/付费墙/登录、伪造、Stage0 式全国市县盲爬；(3) 首批 1–3 个试点源（建议：国家统计局公开数据 / 江苏统计公开表，以 registry 可核验为准）；(4) 流水线：discover→download→sha256→archive→extract→observation（is_demo=false 仅当真实文件哈希入仓）；(5) 与 docs/48 intake / docs/51 关系：用户投递仍可用，**不再是唯一路径**；(6) 验收清单与下一刀（首个 connector 落地）边界 |
| 本刀不做 | 实装全量爬虫；绕验证码；伪造样本；宣布 Gate/O1 PASS；改 CF |
| 禁止 | Gate PASS；绕验证码/付费墙；登录绕过；伪造 SHA；盲爬全国市县 |

## NOW

1. 落地 `docs/52` 规划
2. 补 pack → 回执 **`328`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不绕验证码/付费墙；不伪造；不盲爬；本刀只规划。
