# 122 — Stage 0 / CC / S1.16 Impl Receipt

**Tasking**: Cursor 121 §NOW（审计 `120` PASS；计划 `docs/31`）
**Date (UTC)**: 2026-08-25
**Commit (origin)**: bff23a8
**Branch**: main
**Pack**: artifact_count=497, sum(role_count)=497 ✓ invariant
**Sub-pack delta**: 492 → 497 (+5)

---

## §NOW items completed (tasking 121)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 121-1 | `.venv-dbt`（python3.11）+ 钉版本 requirements；`dbt run` 绿 | ✅ | `.venv-dbt/bin/dbt --version` → `Core: 1.12.3 / postgres: 1.11.0`；`requirements-dbt.txt` 钉版本；`dbt run --select +mart_source_disagreement --full-refresh` 返回码 0 |
| 121-2a | 落地 singular test（含 S0↔S0 过滤） | ✅ | `dbt/tests/test_cross_source_consistency_threshold.sql`；WHERE 含 `source_a_level='S0' AND source_b_level='S0'`（不是 Jinja 占位） |
| 121-2b | pytest wrapper：干净 / PENDING 红 / RESOLVED 绿 / S0↔S1 不断言 | ✅ | `tests/test_r03_cross_source_dbt.py` 5/5 PASS（27.76s） |
| 121-3 | 回归：`test_source_disagreement_s141` 仍绿 | ✅ | 9/9 PASS（0.82s） |
| 121-4 | commit → origin → 回执 `122` 进 `reviews/` | ✅ | origin push `a665024..bff23a8`；本回执路径 reviews/ |
| 121-5 | → `84` POLL | ✅ | job 50a7c596 持续武装（180s，session-only） |

---

## §1 — Deliverables

| Path | Status | Role | sha256[:12] |
|------|--------|------|-------------|
| `.gitignore` | modified (+1 line) | — | — |
| `dbt/models/marts/mart_source_disagreement.sql` | modified（latent S1.14 fix） | spike_helper | d3518b113472 |
| `dbt/packages.yml` | new | documentation | 3135a8533b62 |
| `dbt/package-lock.yml` | new（`dbt deps` 锁定 dbt_utils 版本） | documentation | a4d6f0312e87 |
| `dbt/tests/test_cross_source_consistency_threshold.sql` | new | spike_helper | 72ebf50b5c48 |
| `requirements-dbt.txt` | new（钉 dbt-core==1.12.3 / dbt-postgres==1.11.0） | documentation | db73c34251af |
| `tests/test_r03_cross_source_dbt.py` | new（5 用例） | schema_negative_test | 991ec9d5e418 |

---

## §2 — 实现关键决策（供审计定位）

1. **dbt 3.14 不可用**：`dbt-core` 1.12 在 Python 3.14 下 mashumaro 编译失败；解法 = `.venv-dbt`（python3.11 创）+ `requirements-dbt.txt` 钉版本；venv 不入 pack（`.venv-dbt/` 加 .gitignore）。
2. **dbt singular test 范围**：WHERE 仅 S0↔S0；NEEDS_REVIEW+resolution='PENDING' 出现即失败；与 S1/S2 的差异由 mart 落表记录但不阻塞（docs/10 §2.4 分层语义）。
3. **dbt incremental 不重建表**：mart SQL 加列后，incremental run 不动 schema；本刀 `--full-refresh` 强制重建 26 列（22→26：source_a_level/source_a_basis/source_b_level/source_b_basis 落地）。
4. **S0↔S1 fixture 不走 UPDATE**：`source_document_immutable()` trigger 禁 UPDATE；fixture 一次性种子化 DOC_C（source_level='S1'）+ SRC_C + LOC_C，`_insert_pair(doc_b=DOC_C, loc_b=LOC_C)` 直接选已 seed 的 S1 文档。
5. **dbt 1.12 dropped `python -m dbt`**：CLI 入口为 `.venv-dbt/bin/dbt`（不再是包）。
6. **Mart latent bug fix**：原 `NOW()` 作为 outer SELECT 字面量导致 `surrogate_key` 引用 `detected_at` 在 CTE 外不存在；CTE 现暴露 `NOW() AS detected_at`，outer SELECT 引用列引用——severity 分类逻辑零变更。

---

## §3 — Test evidence

```
$ .venv-dbt/bin/dbt run --select +mart_source_disagreement --full-refresh
Done. PASS=2 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=2

$ /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest tests/test_r03_cross_source_dbt.py -v
collected 5 items
tests/test_r03_cross_source_dbt.py::test_dbt_env_available                  PASSED [ 20%]
tests/test_r03_cross_source_dbt.py::test_dbt_run_then_test_clean            PASSED [ 40%]
tests/test_r03_cross_source_dbt.py::test_dbt_test_fails_on_pending_needs_review PASSED [ 60%]
tests/test_r03_cross_source_dbt.py::test_dbt_test_passes_when_resolved      PASSED [ 80%]
tests/test_r03_cross_source_dbt.py::test_s0_s1_pair_not_asserted            PASSED [100%]
============================== 5 passed in 27.76s ==============================

$ ... pytest tests/test_source_disagreement_s141.py -v
============================== 9 passed in 0.82s ==============================
```

---

## §4 — Run instructions (clean clone)

```bash
# 1. dbt venv
python3.11 -m venv .venv-dbt
.venv-dbt/bin/pip install -r requirements-dbt.txt

# 2. dbt deps
cd dbt && DBT_PROFILES_DIR=. ../.venv-dbt/bin/dbt deps

# 3. mart 重建 + 测试
DBT_PROFILES_DIR=. ../.venv-dbt/bin/dbt run --select +mart_source_disagreement --full-refresh
DBT_PROFILES_DIR=. ../.venv-dbt/bin/dbt test --select test_cross_source_consistency_threshold

# 4. 自动化入口 (缺 .venv-dbt → skip, 不 fail)
pytest tests/test_r03_cross_source_dbt.py
```

---

## §5 — Honest gap list

| Gap | Impact | Notes |
|-----|--------|-------|
| 真实双 S0 源对仍缺 | 客观现状 | 自动化语义全由 fixture 证明；真实 e2e Stage 2 |
| 2%/5% 常量 mart+test 两处镜像 | 低 | 参数化（dbt var）与 S1.15 的 0.70 一并 Stage 2 过用户 |
| dbt `--full-refresh` 在 wrapper 内每次跑 | 低（耗时 ~5s/test） | S1.16 自动化定义可接受；CI 接入后改为 selective |
| CI 接入未交付 | 设计内 | docs/31 §3.3 建议项，Stage 2 基础设施裁定 |

---

## §6 — Red-line compliance

- ❌ 未宣布 Gate 1 / Stage 0 PASS；❌ 未 DSH；❌ 未爬网
- ❌ 未修改 `gate_thresholds.json`（sha256 不变；docs/10 §2.4 阈值常量未引用）
- ❌ 未改 S1.14 mart 行为（severity 分类逻辑零变更；仅 fix latent `detected_at` 引用）
- ❌ 未触碰 00-CC-CURRENT.md；未 --force；未替用户下裁定

---

## §7 — Push confirmation

```
$ git push origin HEAD        # bff23a8
To https://origin.cursor.com/lyliae/china-platform.git
   a665024..bff23a8  HEAD -> main

$ git push github HEAD        # 双推（origin 优先，github retry 20s/45s/90s）
```

---

## §8 — Pack invariant

```
artifact_count = 497
sum(role_count) = 497 ✓
```

Delta breakdown (492→497 = +5):
- +3 documentation: `dbt/packages.yml`, `dbt/package-lock.yml`, `requirements-dbt.txt`
- +1 spike_helper: `dbt/tests/test_cross_source_consistency_threshold.sql`
- +1 schema_negative_test: `tests/test_r03_cross_source_dbt.py`
- modified: `dbt/models/marts/mart_source_disagreement.sql` (sha256 改；role_count 不变)
- modified: `.gitignore` (不入 pack)

---

## §9 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 50a7c596）。等待 Cursor 对 S1.16 实现的审计（预期 queue_rev 42+）。

— CC @ queue_rev 41, S1.16 实现已交付 —