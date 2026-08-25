# S1.11 — Great Expectations 数据契约实现任务书

- 编号：`86-stage1-s11-data-contracts-impl-tasking-20260825`
- 前置：`85` 规划通过；`docs/25`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 范围 | **`ge/`** 按 `docs/25` §3：5 suites + checkpoints + `ge_run.sh` + README |
| DSN | `CEGR_GE_DSN` → `CEGR_API_DSN` → `CEGR_DSN` → `DATABASE_URL`（与规划一致） |
| 空表 | **不得**因 row_count=0 而 FAIL；PASS / PASS_WITH_WARN / FAIL 三态 |
| mostly | PK/FK 关键用 `0.99`；禁止把空表当成硬失败 |
| 数据源 | **`cegr_staging`** dbt views（D1–D5） |
| CI | `.github/workflows/ge-check.yml` + Makefile targets（§8） |

## NOW

1. 实现 `ge/` 脚手架 + **5** expectation suites（D1–D5）
2. checkpoints（ci/dev）+ `scripts/ge_run.sh` + `ge/README.md`
3. **≥3** loadable/smoke tests（`ge/tests/` 或 `tests/test_ge_*`）
4. 本地跑通空表诚实路径 + 有种子时非空路径（能跑则跑）
5. pack → commit → **origin 优先** → 回执 **`87-stage0-cc-s11-impl-receipt-*.md`**
6. → **立即再进 `84` while-POLL**

## 红线

不 Gate 1 PASS；不 DSH；不批量爬取；不改 `gate_thresholds.json`。
