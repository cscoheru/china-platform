# 107 — Stage 0 / CC / S1.14.1 Implementation Receipt (includes FAIL fix)

**Tasking**: Cursor 106 §NOW + Cursor 109 §NOW (FAIL fix)
**Date (UTC)**: 2026-08-25
**Plan ref**: docs/29-stage1-s14-cross-source-consistency-plan-20260825.md
**Impl commit (origin)**: 7c6df3f
**Fix commit (origin)**: 60be7dc
**Branch**: main
**Pack**: artifact_count=488, sum(role_count)=488 ✓ invariant

---

## §NOW items completed (tasking 106 + 109)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 106-0 | receipt 104 in repo | ✅ | confirmed at commit 427015f |
| 106-1 | migration 006 + dbt models/tests | ✅ | 7c6df3f (006 + stg/mart SQL + 9 pytest) |
| 106-2 | ≥5 pytest | ✅ | 9 cases — schema_applied, within_tolerance_not_recorded, recorded, needs_review, diff_pct_computed_correctly, diff_sign_correct, comparison_basis_mismatch_excluded, empty_mart_when_only_single_source, unique_constraint |
| 106-3 | GE suite or stub | — (optional per 106) | deferred; covered by pytest SQL checks |
| 106-4/109-5 | commit + origin push + receipt 107 | ✅ | 7c6df3f + 60be7dc pushed to origin |
| 109-1 | migration 005 idempotent | ✅ | 60be7dc (IF NOT EXISTS on table + 3 indexes + DO-block COMMENT) |
| 109-2 | chain applies + source_disagreement exists | ✅ | DROP cegr CASCADE + 6 files OK; to_regclass non-null |
| 109-3 | source_disagreement tests pass | ✅ | 9/9 with default conftest |
| 109-4 | admin_upload regression | ✅ | 9/9 (18/18 combined) |
| 109-6 | 84 while-POLL | ✅ (below) | re-armed after receipt |

---

## §1 — FAIL root cause + fix (per Cursor 108 §1 + 109 §NOW-1)

**Root cause**:
- `tests/conftest.py` (session-start): `DROP SCHEMA cegr CASCADE` then applies `01-core.sql + migrations/*.sql` in lex order
- Migration 005 used bare `CREATE TABLE admin_upload_audit` (no schema prefix → lands in `public`)
- DROP cegr CASCADE does NOT drop public tables → second apply: 005 hits `admin_upload_audit already exists` → rc=3 → chain stops at 005 → **006 never applied** in fresh sessions (tests would fail with `cegr.source_disagreement 不存在`)

**Fix (minimum per 109 NOW-1)**:
- `CREATE TABLE IF NOT EXISTS admin_upload_audit` (kept in public schema)
- `CREATE INDEX IF NOT EXISTS` × 3
- `COMMENT ON TABLE` wrapped in `DO $$ ... $$` with pg_description existence check
- No API/CLI SQL changes required (public.admin_upload_audit references already in place)

**Verification**:
- Simulated conftest: `DROP SCHEMA IF EXISTS cegr CASCADE` + sequential apply of 01-core + 002-006 → all 6 files OK
- `pytest tests/test_source_disagreement_s141.py` → 9/9 (no STAGE0_SKIP_SCHEMA_APPLY=1)
- `pytest tests/test_admin_upload_s131.py` → 9/9 (no regression)
- Combined: 18/18 with default conftest; plus api regression: 37/37 total

---

## §2 — Deliverables (S1.14.1)

| Path | Status | Role |
|------|--------|------|
| `schema/migrations/006_source_disagreement.sql` | new (77 lines) | schema_migration_ddl |
| `dbt/models/staging/stg_source_disagreement_candidate.sql` | new (79 lines) | spike_helper |
| `dbt/models/marts/mart_source_disagreement.sql` | new (52 lines) | spike_helper |
| `tests/test_source_disagreement_s141.py` | new (470 lines) | schema_negative_test |
| `schema/migrations/005_admin_upload_audit.sql` | modified (idempotency fix) | schema_migration_ddl |
| `evidence_pack/manifest.json` | 484→488 | +4 artifacts |

### Schema (migration 006)

- `cegr.source_disagreement` (27 cols, 5 indexes incl. pkey + unique)
- FKs: indicator_definition, geo_entity, calendar_period, source_registry ×2, observation ×2
- UNIQUE (triplet + source_a_id + source_b_id + detected_at) — allows re-detection across runs
- severity CHECK: WITHIN_TOLERANCE | RECORDED | NEEDS_REVIEW
- resolution CHECK: USE_A | USE_B | PARSE | PARALLEL | PENDING

### dbt models

- `stg_source_disagreement_candidate` — ordered pair builder (source_a < source_b by UUID when levels equal; lower level wins as A otherwise); only S0/S1; same comparison_basis; FACT + value NOT NULL
- `mart_source_disagreement` — incremental, unique_key=[triplet+pair+detected_at]; severity classification (2%/5% thresholds); filters out WITHIN_TOLERANCE

### Test coverage (9/9)

1. `test_schema_applied` — 20 required columns + 3 secondary indexes
2. `test_within_tolerance_not_recorded` — 1% diff → 0 rows persisted
3. `test_recorded` — 3.5% diff → RECORDED row with diff_pct verified
4. `test_needs_review` — 8% diff → NEEDS_REVIEW row
5. `test_diff_pct_computed_correctly` — a=200, b=210 → diff_pct=5.0
6. `test_diff_sign_correct` — A_GT_B and EQUAL
7. `test_comparison_basis_mismatch_excluded` — same-basis rows documented
8. `test_empty_mart_when_only_single_source` — cleanup → 0 rows
9. `test_unique_constraint` — same triplet+pair+detected_at duplicate raises UniqueViolation

---

## §3 — Honest gap list

| Gap | Impact | Notes |
|-----|--------|-------|
| dbt models not executed (mashumaro broken on Python 3.14) | Medium | Mart logic replicated in pytest SQL; files committed for future execution once dbt env fixed |
| GE suite `d3_source_disagreement_suite.json` not created | Low | Optional per tasking 106; deferred until second S0 source exists (would be testing empty state) |
| Second S0 source absent | By design | Current DB only has single-source seed data; NEEDS_REVIEW path only exercised via pytest fixture injection (not real source pairs) |
| 2%/5% thresholds hardcoded | Per docs/29 §7 | Stage 2 tasking to parameterize via dbt var |
| Github push unstable | — | origin confirmed at 60be7dc; github retried during this receipt (network timeouts to github.com) |

---

## §4 — Red-line compliance

- ❌ Did NOT declare Stage 0 / Gate 1 PASS
- ❌ Did NOT modify `gate_thresholds.json` (2%/5% are SQL constants in mart, not gate thresholds)
- ❌ Did NOT crawl remote sources
- ❌ Did NOT batch historical data
- ❌ Did NOT --force / --force-with-lease
- ❌ FAIL (108) acknowledged, root cause identified and fixed per 109 (no pushback, no ruling override)

---

## §5 — Push confirmation

```
$ git push origin HEAD        # impl
To https://origin.cursor.com/lyliae/china-platform.git
   5f01bcd..7c6df3f  HEAD -> main

$ git push origin HEAD        # FAIL fix
To https://origin.cursor.com/lyliae/china-platform.git
   1076da3..60be7dc  HEAD -> main

$ git push github HEAD
# network timeouts to github.com:443 during this session
# github/main last known at 427015f (before S1.14 impl)
# will retry when network stabilizes
```

---

## §6 — Pack invariant

```
artifact_count = 488
sum(role_count) = 488 ✓
```

Entries added at 7c6df3f:
- `schema/migrations/006_source_disagreement.sql` (schema_migration_ddl +1)
- `dbt/models/staging/stg_source_disagreement_candidate.sql` (spike_helper +1)
- `dbt/models/marts/mart_source_disagreement.sql` (spike_helper +1)
- `tests/test_source_disagreement_s141.py` (schema_negative_test +1)

005 fix (60be7dc) is a content change to an already-listed file (sha256 updated in next manifest bump).

---

## §7 — Next heartbeat

84 while-POLL re-armed (session-only, 180s recurring).
Awaiting Cursor 110 (audit of FAIL fix + S1.14.1 impl) in queue_rev=37+.

— CC @ queue_rev 36, S1.14.1 impl + FAIL fix delivered —