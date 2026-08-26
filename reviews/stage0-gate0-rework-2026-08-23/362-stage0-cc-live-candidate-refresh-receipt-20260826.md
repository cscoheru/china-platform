# 362 — LIVE_CANDIDATE 一键刷新 · CC 回执

- 编号：`362-stage0-cc-live-candidate-refresh-receipt-20260826`
- 任务书：`361-stage2-live-candidate-refresh-cli-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<BACKFILL>`
- 日期：2026-08-26

---

## §NOW 对照

| 361 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `--refresh-live-candidate`：NBS live（过壳/deeplink）→ WORM → extract → 写 `NATIONAL_BULLETIN_LIVE_CANDIDATE.json` + 同步 `frontend/lib/public_extract_nbs_live_candidate.json` | ✅ flag 落在 `auto_ingest_public_source.py`：live 流水线照常跑（壳门→deeplink→重下载→SHA→WORM），随后 `write_live_candidate_files()` 双写——data 侧 `{domain}/{category}_LIVE_CANDIDATE.json` + NBS 前端 fixture **byte-verbatim 同步**（同一份 payload 写两处，形状同 knife 55：intake_status=LIVE_CANDIDATE / is_demo=true / deeplink+WORM+SHA provenance）。drift 与 match 两分支均挂钩（match 时照写候选轨，rc 语义不变） | `scripts/auto_ingest_public_source.py` |
| (2) 绝不改 sample JSON/fixture/registry sample 哈希 | ✅ 三重锁：函数只写 `*_LIVE_CANDIDATE.json` 命名空间 + fixture 名硬编码 candidate 专用；pytest 字节级前后对比（`test_refresh_does_not_touch_sample_track`）；跑测后 `git status data/ frontend/lib/ source_registry/` 全净 | 测试 + git status |
| (3) drift/AUTH/tech-blocked 路径照旧 | ✅ 早退路径（AUTH rc=3 / transport rc=5 / 壳或空内容 rc=7）在挂钩点之前 return，零改动；drift 分支 rc=4 语义不变（先报告/lineage，再候选双写）；refresh 未加 --live → rc=6 拒绝（refresh 即 live，同 confirm-live 授权纪律） | `test_refresh_tech_blocked_writes_no_candidate` / `test_refresh_requires_live_authorization` |
| (4) ≥4 pytest | ✅ **+4 case**（下表）；连跑 **92 passed** | 下文证据 |
| (5) 回执 `362`（`-cc-` 名） | ✅ 本文件名 | — |

## 新增测试 4 case

1. `test_refresh_writes_candidate_double_track` — in-process main（monkeypatch `download`+`REVIEWS_DIR`，tmp 三根：archive/extracts/frontend_lib）：drift 路径 rc=4 照旧；候选 JSON 落 tmp extracts 根（intake_status/is_demo/category/deeplink 尾段/row_count==len(rows)==2）；前端 fixture 落 tmp lib 根且与 data 侧**字节相同**（双写契约）
2. `test_refresh_does_not_touch_sample_track` — 真实三文件（sample extract / sample fixture / registry.csv）refresh 前后字节级不变
3. `test_refresh_tech_blocked_writes_no_candidate` — 小壳 blob → rc=7；tmp 根下无任何 `*LIVE_CANDIDATE*` 与 fixture
4. `test_refresh_requires_live_authorization` — 无 `--live` 的 refresh → rc=6

配套：autouse fixture 增 `CEGR_FRONTEND_LIB_ROOT` setenv（352 纪律延伸——护已提交前端 fixture）；connector 新增 `get_frontend_lib_root()` 调用时解析（env > 默认 `frontend/lib`）。

## 证据

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
92 passed in 2.11s          # 88 + 4

$ git status --porcelain data/ frontend/lib/ source_registry/
（空）                        # sample 三轨 + 候选轨全零污染

$ python3 scripts/auto_ingest_public_source.py --refresh-live-candidate
❌ --refresh-live-candidate requires --live --confirm-live=PATH (refresh IS
a live run; same authorization discipline, per tasking 361 §SCHEMA)

$ python3 frontend/smoke-check.py
=== ... smoke: PASS ===
```

（本刀未再跑真实 live 刷新——knife 54 刚跑过一次 NBS live 且 361 §SCHEMA 未要求重复网络探测；CLI 行为由 4 个 in-process case + rc=6 实测覆盖。真实一键刷新留待下一次 tasking 或用户直接执行。）

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `scripts/auto_ingest_public_source.py` | MODIFIED（flag + `write_live_candidate_files` + `get_frontend_lib_root` + rc=6 守卫 + drift/match 挂钩） | 已入 manifest（SKIP） |
| `tests/test_auto_ingest_public_source_s52.py` | MODIFIED（autouse +frontend env）+ 新增 4 case | 已入 manifest（SKIP） |
| `scripts/_knife56_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../362-stage0-cc-live-candidate-refresh-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife56_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **671 → 673**；`sum(role_count) == artifact_count == len(artifacts) == 673`。

## 红线自查

- ❌ 未覆盖 sample JSON/fixture；未改 registry sample 哈希（字节级测试锁）
- ❌ 未自动 O1 收口（drift 仍 rc=4 等用户裁定；match 路径 rc=0 语义原样）
- ❌ 未 headless；未绕 AUTH（refresh 强制 --live --confirm-live）
- ❌ 未 Gate/O1 PASS 宣言；未动 `00-CC-CURRENT.md` / `gate_thresholds.json`；未 --force；未索要 PAT
- ✅ 回执文件名含 `-cc-`

## 下一步

`./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 363）。
