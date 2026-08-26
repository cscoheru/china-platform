# 359 — live WORM 提取 + 前端 LIVE_CANDIDATE · CC 回执

- 编号：`359-stage0-cc-live-worm-frontend-candidate-receipt-20260826`
- 任务书：`358-stage2-live-worm-extract-frontend-candidate-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<BACKFILL>`
- 日期：2026-08-26

---

## §NOW 对照

| 358 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 从已归档 `zxfb` 跑 extract → `NATIONAL_BULLETIN_LIVE_CANDIDATE.json`（sha/path/row_count/rows；live candidate 语义） | ✅ 复用 connector `extract_tables(blob, category=NATIONAL_BULLETIN)` 对 WORM `data/public_archives/2026-08/stats.gov.cn/zxfb`（435,469 B，`sha=0b85212f…`）一次性提取：**60 行**（2026年8月中旬流通领域重要生产资料市场价格变动情况，t20260821_1965093 文章）；`intake_status=LIVE_CANDIDATE`；`is_demo="true"`（沿 knife 333 CANDIDATE_AUTO 候选惯例）；含 `source_deeplink_url`/`source_archive_path`/`source_sha256`/`row_count`/`rows`/`extracted_at` | `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN_LIVE_CANDIDATE.json`（13,025 B） |
| (2) 禁止覆盖 sample 与 sample fixture | ✅ 分轨双锁：`NATIONAL_BULLETIN.json`（63 行 / `dea13b8a…`）与 `frontend/lib/public_extract_nbs.json` 零改动（git status 无 M；pytest `test_sample_track_not_overwritten` + smoke §12c 交叉检查 registry SHA 锚定不变） | git diff 为空 + 测试 |
| (3) 前端 `/public-extracts` 增 LIVE_CANDIDATE 区块（显式非 O1，同页分节） | ✅ `frontend/lib/public_extract_nbs_live_candidate.json`（byte-verbatim 快照）+ 页面第二区块「Live 候选提取 — NBS 2026-08-21 文章 (drift)」：DemoBadge（demo_reason 注明 drift 候选/非 O1/分轨）+ 8 字段 provenance（含 source_deeplink_url、drift SHA）+ 60 行全量表；sample 区块注同步修正（355 后 live 已过壳门，非「仍 rc=7」） | `frontend/app/public-extracts/page.tsx` |
| (4) ≥3 pytest + smoke/build 证据 | ✅ **+4 case**，`test_public_extract_frontend_fixture.py` 11 passed；连跑 88 passed；smoke §12c gate 新增并 PASS；`npm run build` exit 0（/public-extracts 静态 ○） | 下文证据 |
| (5) 回执 `359`（`-cc-` 名） | ✅ 本文件名 | — |

## 新增测试 4 case

1. `test_live_candidate_extract_shape` — intake_status/is_demo/domain/archive 尾段/deeplink 前缀/row_count==len(rows)；**SHA 双锚定**：记录 sha == WORM 文件实算 sha == knife 54 回执实录前缀 `0b85212f70055c38…`
2. `test_live_candidate_fixture_mirrors_extract` — 前端 fixture 与 data 侧提取 dict 全等（352 已护 extracts 不被测改写，快照对比不再假性失败）
3. `test_sample_track_not_overwritten` — §红线分轨：sample data 侧 63 行/`dea13b8a…`、sample fixture 同锚、live SHA ≠ sample SHA（分轨存在意义）
4. `test_page_renders_live_candidate_track` — 页面 import live fixture、LIVE_CANDIDATE 标注、source_deeplink_url、非 O1 收口免责、无 O1_AUTO_INTAKED

## 证据

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
88 passed in 1.93s          # 84 + 4

$ git status --porcelain data/
?? data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN_LIVE_CANDIDATE.json
（仅新增候选文件;sample / archive 零 M）

$ python3 frontend/smoke-check.py
✅ public_extract_nbs_live_candidate.json: LIVE_CANDIDATE fixture 在位 (60 行)
✅ public-extracts/page.tsx: LIVE_CANDIDATE 分轨区块 + 非 O1 免责
=== ... smoke: PASS ===

$ cd frontend && npm run build
build-rc=0                  # /public-extracts ○ (Static) prerendered
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN_LIVE_CANDIDATE.json` | NEW（13,025 B，60 行候选提取） | `data_contract_suite` |
| `frontend/lib/public_extract_nbs_live_candidate.json` | NEW（byte-verbatim fixture） | `data_contract_suite` |
| `frontend/app/public-extracts/page.tsx` | MODIFIED（LIVE_CANDIDATE 区块 + sample 注修正） | 已入 manifest（SKIP） |
| `tests/test_public_extract_frontend_fixture.py` | MODIFIED + 新增 4 case | 已入 manifest（SKIP） |
| `frontend/smoke-check.py` | MODIFIED（§12c gate：候选 fixture 在位/页面标注/分轨不覆盖交叉检查） | 已入 manifest（SKIP） |
| `scripts/_knife55_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../359-stage0-cc-live-worm-frontend-candidate-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife55_manifest_bump.py`：NEW_ARTIFACTS +4（候选提取 + 前端 fixture + bump + receipt）→ **667 → 671**；`sum(role_count) == artifact_count == len(artifacts) == 671`。

## 红线自查

- ❌ 未覆盖 `NATIONAL_BULLETIN.json` sample / `public_extract_nbs.json` fixture（分轨双锁）
- ❌ 未改 registry sample 哈希；未写 O1_AUTO_INTAKED；未宣称 O1/Gate PASS（LIVE_CANDIDATE 语义 = drift 候选，等用户裁定）
- ❌ 未 headless；未伪造；未动 `00-CC-CURRENT.md` / `gate_thresholds.json`；未 --force；未索要 PAT
- ✅ 回执文件名含 `-cc-`；静态路由无 `params.*` 分支；禁词扫描前先剥注释

## 下一步

`./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 360）。
