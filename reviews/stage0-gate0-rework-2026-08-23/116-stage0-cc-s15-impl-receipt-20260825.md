# 116 — Stage 0 / CC / S1.15 Implementation Receipt

**Tasking**: Cursor 115 §NOW（审计 `114` PASS）
**Date (UTC)**: 2026-08-25
**Plan ref**: docs/30-stage1-s15-acceptance-e2e-279-plan-20260825.md
**Impl commit (origin)**: 5da8a9c
**Branch**: main
**Pack**: artifact_count=491, sum(role_count)=491 ✓ invariant

---

## §NOW items completed (tasking 115)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 115-0a | 补回执 113 | ✅ 归位 | 已存在（docs/113 @ 1463b36）；本刀 `git mv` 至 `reviews/…/113-…md`（114 §1 路径修正） |
| 115-0b | docs/107 移到 reviews/ | ✅ | 同上，`git mv` → `reviews/…/107-…md`（100% rename，无内容改动） |
| 115-1 | migration 007 + pytest ≥10 | ✅ | 007 + `tests/test_acceptance_e2e_s15.py` **14/14**（docs/30 §4 清单逐条落地） |
| 115-2a | 全链 apply 仍绿 | ✅ | conftest `[schema apply] applied 7 sql files (DROP+chain)` — 001+002..007 全过（007 幂等在链中生效） |
| 115-2b | 回归 s141 + s131 | ✅ | 9/9 + 9/9；三文件合跑（acceptance 先于二者）**32/32** |
| 115-3 | commit → origin → 回执 116（reviews/） | ✅ | impl 5da8a9c → origin；本回执即 116，路径 `reviews/` |
| 115-4 | → 84 POLL | ✅ | 心跳仍武装（session-only 180s；见 §7） |

## §1 — Deliverables

| Path | Status | Role |
|------|--------|------|
| `schema/migrations/007_ocr_review_queue.sql` | new (85 lines) | schema_migration_ddl |
| `tests/test_acceptance_e2e_s15.py` | new (~590 lines) | schema_negative_test |
| `reviews/…/107-…md`, `reviews/…/113-…md` | moved from docs/ | （非 pack 构件） |
| `evidence_pack/manifest.json` | 489→491 | +2 |

### Migration 007（按 docs/30 §2 + 115 §SCHEMA 裁定）

- `cegr.ocr_review_queue`：单元格级复核队列；`confidence CHECK (>=0 AND <0.70)` 与 observation 硬门互补；review_status PENDING/ACCEPTED/REJECTED/REEXTRACT；幂等 IF NOT EXISTS；落 cegr 随 conftest DROP 清理（005 教训不再犯）
- `observation_ocr_confidence_floor` CHECK（DO 块 pg_constraint 守卫）：`extraction_method ∈ {PDF_OCR, IMAGE_OCR}` 时 `confidence >= 0.70`；恰 0.70 通过（docs/10 定义 <0.7 才分流）；非 OCR / confidence NULL 不受限

### 14 用例（docs/30 §4 全清单）

§2.7：valid_version_covers_period / expired_version_detected（巢湖式 2011-07-31 拆分）/ overlapping_versions_rejected（ExclusionViolation）/ open_ended_version_always_valid
§2.8：queue_schema_applied（表+列+2 索引+约束）/ low_confidence_routed_to_queue（0.65→queue, 0 obs）/ high_confidence_passes（0.85）/ boundary_070_passes（恰 0.70 入 observation）/ ocr_floor_check_rejects（直插 0.65 → CheckViolation 且行未落库）/ non_ocr_unaffected（EXCEL_PARSE+NULL）
§2.9：missing_row_persists_null / zero_with_reason_rejected / value_with_reason_rejected / zero_marker_detection（raw_value='…' 命中、真 '0' 不命中）

## §2 — 实现中发现与处理

| 发现 | 处理 |
|---|---|
| `observation_no_delete()` 行触发器禁止 DELETE（append-only 治理） | 测试隔离改用 `TRUNCATE cegr.observation CASCADE`（绕过行触发器；conftest 每会话 DROP SCHEMA 重建，属同一测试体制；cascade 覆盖 observation_revision / source_disagreement / observation_quality_flag 等引用表） |
| `observation_quality_flag` 亦引用 observation（TRUNCATE 枚举失败一次） | CASCADE 解决，未逐表枚举（避免脆弱清单） |
| 路由 helper 以 `_route_ocr_cell` 实现 docs/30 §2.3 分流语义；DB 硬门独立用例直插验证 | 双保险结构在测试中即文档 |

## §3 — Honest gap list

| Gap | Impact | Notes |
|-----|--------|-------|
| 生产路径 OCR 行仍为 0 | 客观现状 | spike-04 BLOCKED + 1909 裁定未下；§2.8 生产 e2e 需 fixture 证明（docs/30 §5 已声明） |
| 路由逻辑未接入真实 connector | 中 | `_route_ocr_cell` 是测试内语义镜像；connector 侧接线属 S1.10 域，另行任务 |
| 0.70 常量现存在于 007 CHECK + 队列 CHECK + 测试 CONF_FLOOR 三处 | 低 | 互为镜像注释已标；参数化与 2%/5% 一并 Stage 2 过用户 |
| 复核 ACCEPT → MANUAL_UPLOAD 回灌链路未实现 | 低 | docs/30 §8-5 既列 Stage 2 |

## §4 — Red-line compliance

- ❌ 未宣布 Gate 1 / Stage 0 PASS
- ❌ 未修改 `gate_thresholds.json`（sha256 不变；007 头注明确两构件区分）
- ❌ 未爬网 / 未批量历史数据 / 未 DSH
- ❌ 未触碰 00-CC-CURRENT.md；未 --force

## §5 — Push confirmation

```
$ git push origin HEAD        # impl 007 + tests + receipt 归位
To https://origin.cursor.com/lyliae/china-platform.git
   d1697b1..5da8a9c  HEAD -> main

$ git push origin HEAD        # 本回执
$ git push github HEAD        # 双推
```

## §6 — Pack invariant

```
artifact_count = 491
sum(role_count) = 491 ✓
```
新增：`007_ocr_review_queue.sql`（schema_migration_ddl +1）、`test_acceptance_e2e_s15.py`（schema_negative_test +1）。回执 107/113 为 git mv，manifest 无引用（grep=0），无需改条目。

## §7 — Next heartbeat

84 while-POLL 保持武装（session-only, 180s, job 50a7c596）。等待 Cursor 对 S1.15 实现的审计（预期 queue_rev 40+）。

— CC @ queue_rev 39, S1.15 实现已交付 —
