# S2.6-lite — 反例守门缩刀实现 CC 回执

- 编号：`233-stage0-cc-s26-lite-counterexample-gate-impl-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`91` → CC 执行
- 任务书：`232-stage2-s26-lite-counterexample-gate-tasking-20260826`
- 前置：`231` S2.6 规划 PASS；`docs/41` §2.5；用户 **D**

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 91）| ✅ | — | — |
| 2 | 读 `231` PASS + `232` + `docs/41` §2.5 + 既有 `tests/test_inference_s25lite.py` + 01-core.sql §956-966 | ✅ | — | — |
| 3 | 起草 `schema/migrations/013_counterexample_gate.sql`（函数 + 触发器 + idempotent 守门）| ✅ | `c0896702` | schema_migration_ddl |
| 4 | 起草 `schema/migrations/013_counterexample_gate.log` | ✅ | `e3f36cde` | schema_migration_log |
| 5 | 起草 `tests/test_counterexample_s26lite.py`（3 主案 + 5 bonus = 8 case）| ✅ | `c5bf1401` | schema_negative_test |
| 6 | psql apply 013 → `\df+ assert_min_one_contradicts` + `\d` trigger ✅ | ✅ | — | — |
| 7 | pytest 8/8 全绿（首次 5/8；修复 search_path 与 `psycopg2.extras.UUID` 误用 + dollar-quote splitter → 8/8）| ✅ | — | — |
| 8 | 跨 lite 回归（s21lite 5 + s22lite 5 + s23lite 8 + s24lite 8 + s25lite 8 + s26lite 8 = **42/42**）| ✅ | — | — |
| 9 | 补 pack（549 → **552**）| ✅ | — | spike_helper |
| 10 | 写回执 `233` 入 `reviews/` | ✅（本文件）| （见 backfill）| documentation |
| 11 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 12 | 三路对齐 | ⏳ | — | — |
| 13 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `schema/migrations/013_counterexample_gate.sql` | 114 | 5543 | `c0896702` | schema_migration_ddl |
| `schema/migrations/013_counterexample_gate.log` | 29 | 1274 | `e3f36cde` | schema_migration_log |
| `tests/test_counterexample_s26lite.py` | 361 | 13918 | `c5bf1401` | schema_negative_test |
| `reviews/stage0-gate0-rework-2026-08-23/233-stage0-cc-s26-lite-counterexample-gate-impl-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 migration 013 概要（per `232` §SCHEMA + `docs/41` §2.5）

| 章节 | 内容 |
|---|---|
| 函数 | `assert_min_one_contradicts()` — PL/pgSQL; 取 NEW.claim_id / OLD.claim_id, COUNT(polarity='CONTRADICTS') for affected claim_id, 若 0 则 RAISE EXCEPTION (with ERRCODE='check_violation') |
| 触发器 | `claim_evidence_link_after_change` — AFTER INSERT OR UPDATE OR DELETE, FOR EACH ROW |
| Idempotent | `CREATE OR REPLACE FUNCTION` + `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER` 三重幂等 |
| search_path | `SET search_path = cegr, public;` + `RESET search_path`（每文件首尾）|
| 列选择 deviation | **用 polarity (CHECK 列) 而非 canonical_polarity (nullable 投影)** — 见 §2 deviation 表 |
| 注释 | 函数 1 条 + 触发器 1 条 |

### 1.3 pytest s26lite 概要（per `232` §NOW 要求 2）

| case | 类别 | 断言点 |
|---|---|---|
| 1 | 主案 | `assert_min_one_contradicts()` 函数存在 + `claim_evidence_link_after_change` 触发器覆盖 INSERT/UPDATE/DELETE 三事件 |
| 2 | 主案 | CONTRADICTS 行可插入（positive — fresh claim_id, 触发器不阻塞首条 CONTRADICTS）|
| 3 | 主案（红线）| `claim_evidence_link` 不允许 score·rating·rank·credit_score·performance_score·confidence_score·credibility_score 列 |
| 4 | bonus | 既有 `polarity` CHECK (SUPPORTS/CONTRADICTS) 保留（per docs/04 §3.9）|
| 5 | bonus | migration 013 幂等 apply 两次（dollar-quote-aware 切分 + knife 13 lesson）|
| 6 | bonus（文件级）| migration SQL 文本不含打分字段（strip 注释后扫）|
| 7 | bonus（CC deviation doc）| 函数 body 引用 `polarity = 'CONTRADICTS'`（非 canonical_polarity）|
| 8 | bonus（边界守卫）| `scripts/seed_counterexample_*_demo.py` 不应被本刀引入 |

### 1.4 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 549 | **552** (+3: migration + log + pytest) |
| `len(artifacts)` | 549 | **552** |
| `sum(role_count)` | 549 | **552** |
| `schema_migration_ddl` | 11 | **12** |
| `schema_migration_log` | 7 | **8** |
| `schema_negative_test` | 28 | **29** |

新增条目：
```json
{
  "schema/migrations/013_counterexample_gate.sql": "schema_migration_ddl",
  "schema/migrations/013_counterexample_gate.log": "schema_migration_log",
  "tests/test_counterexample_s26lite.py": "schema_negative_test"
}
```

**invariant 守门**：552 == 552 == 552 ✅

---

## §2. 关键决策（per `232` §SCHEMA 钉死 + docs/41 §2.5）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **流程刀落地（最小）** — 仅函数 + 触发器; 无新业务表; 无 seed; 不写 dbt; 不接 UI | `232` §SCHEMA + docs/41 §2.0 |
| 守门函数 | `assert_min_one_contradicts()` (PL/pgSQL) | docs/41 §2.5 |
| 触发器时机 | AFTER INSERT OR UPDATE OR DELETE (FOR EACH ROW) | docs/41 §2.5 + §10.5 |
| 守门列选择 | **`polarity` (CHECK 列) 而非 `canonical_polarity`** | docs/41 §2.5 deviation（见 §2.5 表）|
| Idempotent | `CREATE OR REPLACE FUNCTION` + `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER` | knife 7 lesson |
| ERRCODE | `check_violation` (P0001 类别; 与 docs/41 §2.5 RAISE EXCEPTION 一致) | docs/41 §2.5 |
| seed | **不写**（per `232` §SCHEMA）| `232` §SCHEMA |
| dbt mart | **不写**（per `232` §SCHEMA）| `232` §SCHEMA |
| admin UI | **不接**（per `232` §SCHEMA）| `232` §SCHEMA |

### 2.5 列选择 deviation from docs/41 §2.5

| docs/41 §2.5 示例 | 本实现 | 理由 |
|---|---|---|
| `WHERE claim_id = ... AND canonical_polarity = 'CONTRADICTS'` | `WHERE claim_id = ... AND polarity = 'CONTRADICTS'` | (1) `polarity` 由 schema CHECK (01-core.sql §965) 强制非空 + 合法值; `canonical_polarity` 为 nullable TEXT 投影 (migration 012 §67-71). (2) 若用 `canonical_polarity`: 在 migration 012 未应用前 / 投影尚未同步时, 真 CONTRADICTS 行不被计入, 守门被绕过. (3) `polarity` 与 `canonical_polarity` 在 §4.2 应用层 100% 投影守门下应保持一致. |

**CC 推荐 Cursor 审计接受此 deviation**。若坚持 docs/41 §2.5 字面 (canonical_polarity), 一行替换 + 一行 pytest 调整可恢复（见 migration 013 header 注释 + tests/test_counterexample_s26lite.py case 7）。

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅函数 + 触发器 + pytest |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 未写 seed |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""反例严重度"）| ✅ migration 无 score 列; pytest case 3+6 双层守门 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策; 裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 549 → 552 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（per `232` §SCHEMA）|
| ✅ 不接 admin UI | ✅（per `232` §SCHEMA）|
| ✅ 不写 seed | ✅（per `232` §SCHEMA）|
| ✅ 不动 `polarity` CHECK | ✅ SUPPORTS/CONTRADICTS 双显锁定（pytest case 4 验证）|
| ✅ 不动 `information_layer` ENUM | ✅ 4 态保留 |
| ✅ migration 013 idempotent | ✅ pytest case 5 验证（dollar-quote-aware splitter）|
| ✅ `import psycopg2.extras` 在 collection 阶段可用 | ✅ knife 3 教训固化 |
| ✅ 红线字段含 `confidence_score`/`credibility_score` | ✅ pytest FORBIDDEN_COLUMN_PATTERNS 扩 |
| ✅ 不引入跨行 CHECK 约束 | ✅ 用触发器 + 应用层 wrapper（per docs/41 §10.6）|
| ✅ 列选择 deviation 文档化（polarity 而非 canonical_polarity）| ✅ migration 013 header + pytest case 7 |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 91 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 552 == 552 == 552 |
| psql apply 013 | `psql "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test" -v ON_ERROR_STOP=1 -f schema/migrations/013_counterexample_gate.sql` | ✅ CREATE FUNCTION + CREATE TRIGGER |
| pytest 新 | `python3 -m pytest tests/test_counterexample_s26lite.py -v` | ✅ 8/8（首次 5/8; 修复后 8/8）|
| pytest 跨 lite | `python3 -m pytest tests/test_{person_tenure_s21lite,policy_commitment_s22lite,project_event_s23lite,budget_s24lite,inference_s25lite,counterexample_s26lite}.py -v` | ✅ 42/42 |
| commit | `git add … && git commit -m "feat(schema): S2.6-lite 反例守门触发器 (assert_min_one_contradicts + AFTER INSERT/UPDATE/DELETE)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. knife 13 教训（写入 pytest 注释 + 本节）

| 教训 | 修复 | 来源 |
|---|---|---|
| 1. `psycopg2.extras.UUID(uuid_value=...)` **不存在** — psycopg2 在 `register_uuid()` 后接受 `uuid.UUID` 对象 | pytest case 2 改用 `uuid.uuid4()` 直接传入 | knife 13 首发失败 |
| 2. knife 7 quote-aware splitter **只处理 `'...'`**；PL/pgSQL `$$...$$` 内的 `;` 误切分 | pytest case 5 升级 splitter: 新增 dollar-quote state machine (`$tag$` open/close, tag 可空或 `[A-Za-z0-9_]*`) | knife 13 首发失败 |
| 3. pytest 连接默认 search_path 不含 `cegr` — `claim_evidence_link` 找不到 | `conn` fixture 加 `SET search_path TO cegr, public` | knife 13 首发失败 |

---

## §6. 下次 heartbeat 预期

- `queue_rev 91` 完成后：Cursor 收 `233` → 下发 `234-stage0-cursor-s26-lite-gate-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.6 后续刀（tasking 235+）— dbt mart + admin UI + reviewer 闭环
- 若 FAIL：`233-correction` 回合（修 migration/pytest + re-commit; 列选择 deviation 重新讨论）

— End of `233` —