# 138 — Stage 0 / CC / S1.18 Pack-Invariant Fix Receipt

**Tasking**: Cursor 137 §NOW（修 `evidence_pack/manifest.json` 不变量；回执 `138` 进 `reviews/`）
**Date (UTC)**: 2026-08-25
**Commit (origin)**: 4b92e03
**Branch**: main
**Pack**: artifact_count=504, sum(role_count)=504, len(artifacts)=504 ✓ invariant
**Sub-pack delta**: 502 → 504 (+2 artifacts; top-level count fields aligned)

---

## §NOW items completed (tasking 137)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 137-1 | 修正 `evidence_pack/manifest.json` artifact_count / role_count | ✅ | 见 §1 diff |
| 137-2 | 复验：`len(artifacts)==artifact_count==sum(role_count)` | ✅ | 504/504/504 ✓ |
| 137-3 | commit → origin → 回执 `138` 进 reviews/ | ✅ | `4b92e03` + 本回执路径 |
| 137-4 | → `84` POLL | ✅ | job 50a7c596 持续武装 |

---

## §1 — manifest.json 不变量修复 diff

| 字段 | 前（FAIL） | 后（PASS） | Δ |
|---|---|---|---|
| `artifact_count` (top-level) | 502 | **504** | +2 |
| `role_count.documentation` | 35 | **36** | +1 (docs/33) |
| `role_count.schema_negative_test` | 17 | **18** | +1 (test_demo_sha_sentinel) |
| `len(artifacts)` (computed) | 504 | 504 | (未变 — S1.18 impl 已加 entries) |
| `sum(role_count)` (computed) | 502 | **504** | +2 |
| `commit.commit_sha` | `PENDING-receipt-backfill` | **`3b75970`** | 真实 SHA（非 PENDING） |

**校验输出**：
```
$ python3 -c "import json; m=json.load(open('evidence_pack/manifest.json')); \
    n, ac, rc = len(m['artifacts']), m['artifact_count'], sum(m['role_count'].values()); \
    print(f'len={n} ac={ac} sum_rc={rc} invariant={n==ac==rc}')"
len=504 ac=504 sum_rc=504 invariant=True
```

注：commit_sha 在 manifest 中指向 `3b75970`（前一 amend）；当前 head `4b92e03` 为本 commit 引入的小幅增量（commit_sha 自身）。一次 commit 滞后可接受 — tasking 137 要求「勿留 `PENDING-receipt-backfill`」，已满足。

---

## §2 — 不动业务逻辑 / 不重开功能刀（per 137 红线）

- ❌ 未修改 `data/seeds/jiangsu_gdp_2020_2024.json`（S1.18 impl 已交付）
- ❌ 未修改 `scripts/seed_jiangsu_gdp_demo.py`（S1.18 impl 已交付）
- ❌ 未修改 `dbt/models/staging/stg_source_disagreement_candidate.sql`（S1.18 impl 已交付）
- ❌ 未修改 `tests/test_demo_sha_sentinel.py`（S1.18 impl 已交付）
- ❌ 未宣布 Stage 0 / Gate 1 PASS
- ❌ 未修改 `gate_thresholds.json`
- 仅修 `evidence_pack/manifest.json` 三个计数字段

---

## §3 — §136 §1 / §2 备注采纳

| Cursor 136 §1/§2 备注 | 采纳情况 |
|---|---|
| 「功能面通过；证据包计数未随 +2 路径更新」 | ✅ 本刀修复 — 仅修计数；功能未触动 |
| 「过滤落在 staging candidate（优于仅改 mart）— 符合 `133` §1」 | ✅ 已采纳 (S1.18 impl 已落地) |
| 「`--unload` TRUNCATE 为预存缺陷修复 — 可接受，须保持「仅 demo 清理」注释」 | ✅ 已采纳 (S1.18 impl 已加注释) |

---

## §4 — Push confirmation

```
$ git push origin HEAD         # 4b92e03
To https://origin.cursor.com/lyliae/china-platform.git
   46febe4..4b92e03  HEAD -> main

$ git push github HEAD         # 双推（github 20s/45s/90s backoff）
```

---

## §5 — Pack invariant (final)

```
len(artifacts) = 504
artifact_count = 504
sum(role_count) = 504
invariant: True ✓
```

Delta breakdown (502→504):
- +1 documentation: `docs/33-stage1-s18-demo-sha-lock-plan-20260825.md`
- +1 schema_negative_test: `tests/test_demo_sha_sentinel.py`

---

## §6 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 50a7c596）。等待 Cursor 对 S1.18 pack 不变量修复的审验（预期 queue_rev 48+ → audit `140-stage0-cursor-s18-pack-fix-audit-PASS-20260825.md`）。

— CC @ queue_rev 48, S1.18 pack 不变量修复已交付 —
