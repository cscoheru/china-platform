# 368 — 深圳样本表抽取修复 · CC 回执

- 编号：`368-stage0-cc-shenzhen-extract-fix-receipt-20260826`
- 任务书：`367-stage2-shenzhen-sample-extract-fix-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<待回填>`
- 日期：2026-08-26

---

## §NOW 对照

| 367 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 修 `extract_html_tables` / `MUNICIPAL_BULLETIN` 抽取，使 `spikes/03-municipal-bulletin/sample.html` → **≥1 行**（保留 NBS 63 行回归） | ✅ 新增 `extract_municipal_tables()` 并改 `extract_tables` 路由（MUNICIPAL_BULLETIN → 新抽取器；NBS 路由与 `extract_html_tables` 首表语义**零改动**）。**根因**：深圳公报正文纯散文、数据表全部以 PNG 图片嵌入（`nfw-cms-img`），页面唯一 `<table>` 是 JS 填充的空搜索壳（`tbody#rdsslist`，快照时 0 行）→ 原 first-table walker 恒 0 行。**修法（零伪造）**：先全表遍历（每张 `<table>` 用 NBS header/row 逻辑，空壳贡献 0 行），无表行时回退散文抽取——`news_cont_d_wrap` 容器内每个非空 `<p>` 一行 `{section, paragraph}`，中文序号节标（一、…十二、）作 running section。真实样本 → **71 行 / 12 节标**；NBS 回归 63 行 keys 不变 | 下文证据 |
| (2) 重跑 `--from-local-sample` 写 `data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json`（可增前端 fixture 小节，标 REGISTRY_SAMPLE） | ✅ 真实重跑 rc=0：71 行 / sha `d5e2c731…`（registry 锚吻合）/ WORM `data/public_archives/2026-08/sz.gov.cn/sample.html`（幂等未变）/ lineage JSONL `REGISTRY_SAMPLE_INTAKED`（is_demo=true）。前端 fixture 小节 = 可选项未做（缩刀 D；/public-extracts 已有 NBS sample+live 双轨范式，深圳 preview 留后续刀，如需用户明示） | 文件 + lineage |
| (3) ≥3 pytest（深圳 ≥1 行 + NBS 不回归） | ✅ **+5 case**（Section 15）；连跑 **97 passed**（92+5） | 下文证据 |
| (4) 回执 `368`（`-cc-` 名） | ✅ 本文件名 | — |

## 新增测试 5 case

1. `test_municipal_extract_real_sample_prose_rows` — 真实样本 ≥1 行；每行恰 `{section, paragraph}` 且非空；12 个节标齐；GDP 针 `36801.87` 落「一、综合」
2. `test_municipal_extract_prefers_embedded_tables` — 合成页（空壳表 + 真 2 列表 + 散文）：真表行胜出、散文不混入、空壳贡献 0 行
3. `test_nbs_extract_no_regression_63_rows` — NBS sample → 63 行 + 首行 keys `["指 标","7月","1—7月"]` 不变
4. `test_sz_delivered_extract_json_shape` — 交付产物落盘形状：row_count==len(rows)≥1、sha `d5e2c731…`、WORM 尾段、sample 路径
5. `test_municipal_dispatch_routes_prose_fallback` — dispatcher 级：纯散文页（无表）MUNICIPAL_BULLETIN 仍出行

## 事故与处置（诚实记录）

- 首次跑 `--from-local-sample` 时漏带 `--pilot-domain/--pilot-category`，误重跑了 NBS 默认 pilot：`data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` 仅 `extracted_at` 一行变化（rows 字节全同），WORM 幂等未动，lineage 只进了误命名 JSONL，无 DB 写。处置：`git checkout --` 还原 NBS sample（已验 `git status data/` 全净）、删除误命名 lineage 文件、带 pilot 参数重跑深圳成功。sample 轨零净污染。

## 证据

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
97 passed in 2.25s          # 92 + 5

$ python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=sz.gov.cn --pilot-category=MUNICIPAL_BULLETIN \
    --from-local-sample --confirm-live=reviews/.../20260826-local-sample-\
sz-gov-cn-MUNICIPAL_BULLETIN.jsonl
OK archived: data/public_archives/2026-08/sz.gov.cn/sample.html
OK extract JSON: data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json
OK REGISTRY_SAMPLE_INTAKED (is_demo=true)          rc=0

$ python3 -c "…" # 交付产物核验
rows: 71 | sha: d5e2c73196b43cec | 12 节标 | GDP 针落一、综合

$ python3 frontend/smoke-check.py
=== … smoke: PASS ===

$ git status --porcelain data/ frontend/lib/ source_registry/
M data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json   # 仅深圳（0→71 行）
（NBS sample/fixture/registry 零改动）
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `scripts/auto_ingest_public_source.py` | MODIFIED（`extract_municipal_tables` + dispatcher 路由） | 已入 manifest（SKIP） |
| `tests/test_auto_ingest_public_source_s52.py` | MODIFIED + 新增 5 case | 已入 manifest（SKIP） |
| `data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json` | git MODIFIED（0 行→71 行）→ pack NEW | `data_contract_suite` |
| `reviews/.../20260826-local-sample-sz-gov-cn-MUNICIPAL_BULLETIN.jsonl` | NEW（lineage，git 跟踪） | 不入 pack（_knife47/48 先例） |
| `scripts/_knife58_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../368-stage0-cc-shenzhen-extract-fix-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife58_manifest_bump.py`：NEW_ARTIFACTS +3（sz extract + bump + receipt）→ **676 → 679**；`sum(role_count) == artifact_count == len(artifacts) == 679`。

## 红线自查

- ❌ 未伪造行（每行 = 真实内容段落；PNG 表不解析不捏造）
- ❌ 未破坏 NBS 双轨（63 行契约测试锁 + sample 字节还原 + fixture/registry 零改动）
- ❌ 未做深圳 HTTPS live（SSL 仍暂缓，per 367 §不做）；未 headless
- ❌ 未 Gate/O1 PASS 宣言；未动 `00-CC-CURRENT.md` / `gate_thresholds.json`；未 --force；未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 369）。
