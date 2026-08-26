# S2.3-lite — idempotent pytest 修复 CC 回执

- 编号：`208-stage0-cc-s23-lite-idempotent-pytest-fix-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`84` → CC 执行
- 任务书：`207-stage2-s23-lite-idempotent-pytest-fix-tasking-20260825`
- 前置：`206` FAIL（`test_migration_010_idempotent`）
- 用户裁定：`211` 续跑 `207`，不重启 CC（`212` ACK）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main`（queue_rev 83→84）| ✅ | — | — |
| 2 | 读 `207` + `206` + 既有 `tests/test_project_event_s23lite.py` | ✅ | — | — |
| 3 | 修 `test_migration_010_idempotent`：quote-aware 切分 + 注释剥离 | ✅ | （既有路径，sha 变化）| `schema_negative_test` |
| 4 | `python3 -m pytest tests/test_project_event_s23lite.py -v` | ✅ **8 passed / 0 failed** | — | — |
| 5 | 写回执 `208` 入 `reviews/` | ✅（本文件） | `c2f6a30c` | documentation |
| 6 | 补 pack（534 → **535**）| ✅ | — | spike_helper |
| 7 | commit → origin 优先 → github | ⏳ 待推 | — | — |
| 8 | 三路对齐 | ⏳ | — | — |
| 9 | → `84` POLL | ⏳ re-arm | — | — |

---

## §1. 根因 + 修法（per Cursor 206）

### 1.1 双重根因

原 `test_migration_010_idempotent` 用 `migration_sql.split(";")` 切分 DDL 块。问题：

1. **trailing 注释陷阱**：migration 文件末行 `-- End of migration 010.` 在 `;` 之后被切出，`.strip()` 非空，被当成正式语句 → psycopg2 提交后只剩注释 → `can't execute an empty query`（这就是 206 报告的失败点）。
2. **字符串里 `;` 陷阱**：`COMMENT ON COLUMN ... IS '...; ...'`（11 条全部如此）的字符串字面量里有 `;`，naive 切分会从字符串中间砍断 → `unterminated quoted string` 的 `SyntaxError`。原代码之所以只暴 1 个错，是因为第一个 trailing empty-query 错就提前 abort 了整个事务，后续 COMMENT 块根本没机会跑。

### 1.2 修法（仅测试层）

| 层 | 处理 |
|---|---|
| 1 | 先用 regex 把 `--...\n` 行注释与 `/* ... */` 块注释剥掉 → trailing `-- End...` 自然消失 |
| 2 | 自实现 `_split_quote_aware(sql)` 状态机：进入 `'...'` 切到 `in_quote=True`，遇 `''` 当转义 quote 消费 2 字符，遇 `;` 仅当 `not in_quote` 才视为语句分隔 |
| 3 | 空 / 纯空白语句丢弃 |

`ALTER TABLE ... ADD COLUMN IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS` / `RESET search_path` 都不含字符串字面量，全部走默认路径切分。`COMMENT ON COLUMN` 在 quote-aware 切分后整块进入 `cur.execute`，落地 11 行 COMMENT 元数据。两次 apply（首跑 + idempotent 第二遍）皆由 `IF NOT EXISTS` 守门，安全无副作用。

---

## §2. pytest 结果

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2
configfile: pytest.ini
collected 8 items

tests/test_project_event_s23lite.py::test_migration_010_columns_present PASSED [ 12%]
tests/test_project_event_s23lite.py::test_project_event_table_exists PASSED [ 25%]
tests/test_project_event_s23lite.py::test_no_score_like_fields_on_project_event PASSED [ 37%]
tests/test_project_event_s23lite.py::test_lineage_column_jsonb_on_project_event PASSED [ 50%]
tests/test_project_event_s23lite.py::test_migration_010_idempotent PASSED [ 62%]
tests/test_project_event_s23lite.py::test_migration_010_indexes_present PASSED [ 75%]
tests/test_project_event_s23lite.py::test_migration_file_has_no_score_fields PASSED [ 87%]
tests/test_project_event_s23lite.py::test_seed_loader_module_loadable PASSED [100%]

============================== 8 passed in 0.92s ===============================
```

8/8 全绿 ✅（含 206 失败点 `test_migration_010_idempotent`）。

---

## §3. manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 534 | **535** (+1: receipt 208) |
| `len(artifacts)` | 534 | **535** |
| `sum(role_count)` | 534 | **535** |
| `documentation` | 46 | **47** |

新增条目：
```json
{
  "path": "reviews/stage0-gate0-rework-2026-08-23/208-stage0-cc-s23-lite-idempotent-pytest-fix-receipt-20260826.md",
  "role": "documentation"
}
```

注：`tests/test_project_event_s23lite.py` 仅修改内容，路径不变，pack 不重数（仅 sha256 更新 — 不在 manifest 字段中体现）。

**invariant 守门**：535 == 535 == 535 ✅

---

## §4. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅修测试 + 写回执 |
| ❌ 不批量爬项目公告 | ✅ 无关 |
| ❌ 不做官员评分/总分/排名 | ✅ 测试仍守门 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ |
| ❌ 不改 1909 / 陕西代表中国 | ✅ |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 用户已回 `211`；本回执仅执行 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不改 migration `010` SQL | ✅（per 207 §SCHEMA 钉死）|
| ❌ 不扩 scope | ✅ 仅 `test_migration_010_idempotent` 一个用例 |
| ✅ pack invariant 守门 | ✅ 534 → 535 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 8/8 全绿 | ✅ |

---

## §5. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 84 ✅ |
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 535 == 535 == 535 |
| pytest | `python3 -m pytest tests/test_project_event_s23lite.py -v` | ✅ 8/8 |
| commit | `git add … && git commit -m "fix(test): s23lite idempotent split — quote-aware state machine (per 206/207)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

---

## §6. 下次 heartbeat 预期

- `queue_rev 84` 完成后：Cursor 收 `208` → 下发 `209-stage0-cursor-s23-lite-idempotent-fix-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.3 落地刀（tasking 210+）— `seed` + `dbt` + UI 接 EvidenceChain
- 若 FAIL：`208-correction` 回合（修测试 + re-commit）

— End of `208` —