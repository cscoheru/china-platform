# 首个公开源 connector — 缩刀任务书

- 编号：`330-stage2-first-public-source-connector-tasking-20260826`
- 前置：`329` docs/52 PASS；用户裁定：不再等投喂 + AUTH 遇阻报告用户
- 用户裁定：**D**；试点优先 NBS `NATIONAL_BULLETIN`（registry 公开；无需授权）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 写 `scripts/auto_ingest_public_source.py`：按 `source_registry/registry.csv` 筛 `enabled=TRUE` + 公开源 → **discover→download→sha256→archive→extract→observation**（最小可跑；本刀仅接通 **1** 个试点：`stats.gov.cn` / `NATIONAL_BULLETIN` / `https://www.stats.gov.cn/sj/zxfb/`）；(2) WORM 归档目录 `data/public_archives/{YYYY-MM}/stats.gov.cn/`（git 可忽略大文件；小样本可入仓或只写 lineage JSON）；(3) lineage：`intake_status=O1_AUTO_INTAKED` 仅当真 SHA + 与 registry 一致；否则保持 demo/WAITING；(4) AUTH：遇 401/403/登录墙/验证码/付费/反爬 → **停止**，写 `reviews/…auth-blocked…md`（5 字段），**不绕过**；(5) `tests/test_auto_ingest_public_source_s52.py` ≥12 pytest（含：registry 过滤、SHA、AUTH 触发假响应、禁止 headless、不碰未登记源）；(6) 回执 **`331`** |
| 本刀不做 | 全量爬虫；湖北/深圳第二源；OCR/O3；改 CF；改 docs/48/51 契约；宣布 Gate/O1 PASS；伪造 SHA；headless browser |
| 禁止 | 绕验证码/付费墙/登录；静默失败；盲爬；把 spike fixture 当 live O1；Gate PASS 措辞 |

## NOW

1. 落地 script + tests；对 NBS zxfb **公开 GET**（curl/requests；有 rate limit；失败重试≤3）
2. 若 AUTH 触发 → 写 blocked 报告并停；若成功 → archive + lineage 证据进回执
3. 补 pack → 回执 **`331`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不绕 AUTH；不伪造；不盲爬；不 headless；本刀只 1 个公开 connector。
