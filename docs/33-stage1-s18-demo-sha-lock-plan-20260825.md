# Stage 1 / S1.18 — DEMO SHA / 真实样本锁定 规划

- 编号：`docs/33-stage1-s18-demo-sha-lock-plan-20260825`
- 前置：S1.17 PASS（Cursor `130`）；用户裁定 **A**；`docs/27` §4 剩余演示诚实缺口
- 范围：**规划 only**（实现另开；本文为 §NOW 交付物）

---

## §0. 背景与目标

**业务问题**：`docs/27-stage1-s12-gate1-prep-pack-20260825.md` §4.3 第 1 行已点名 — **「S1.13: 江苏 GDP seed 替换为真实 extraction（待 SHA-256-locked XLSX）」**。当前 demo 用手工 seed 跑通了 Gate 1 §1.5「近 5 年江苏 GDP 增长趋势」研究问题，但：

- `data/seeds/jiangsu_gdp_2020_2024.json` 的 `lineage.source_file_sha256` = 全零（`"00…00"` ×64）
- `scripts/seed_jiangsu_gdp_demo.py` 写入 `cegr.source_document.file_hash_sha256` 同样为全零
- `verification_status='UNVERIFIED'` + `caveat_text` 已注明 DEMO 性质
- 但任何按 `file_hash_sha256` 做去重 / 一致性 / 跨源 比对的 dbt 测试或 ingest 检查 **不会把全零识别为 DEMO**，会与真实 SHA 同池参与

**目标刀**：建立一条 **「真实文件 → 锁定 SHA-256」** 的受控路径，并给出 **「无真实文件 → 仍可演示但被识别为 DEMO」** 的诚实失败策略。**不爬网、不伪造 SHA、不批量 2020-2025**（红线继承自 `tasking 92` / `docs/09` / Cursor 红线）。

**目标边界**：

1. **真实样本路径**：当本地或用户上传（Stage 2 S1.17 admin/upload）已有真实 XLSX/PDF 时，`sha256(file_bytes)` 计算 → 写 `cegr.source_document.file_hash_sha256` → `verification_status` 从 UNVERIFIED → PENDING → VERIFIED（人工审校闭环）。
2. **DEMO 标识路径**：当仍只有手工 seed 时，把 `00…00` 升级为 **可识别的 DEMO sentinel**（如 `sha256("DEMO_SEED:"+seed_id)` 或保留全零 + 在 `lineage` JSONB 里加 `is_demo=true` 字段）— 这样任何下游按 `file_hash_sha256` 比对的代码都能 fail-closed 区分「真不存在」与「DEMO 故意留空」。
3. **诚实失败**：拿不到真实文件 → 不伪造 SHA；状态停留在 `UNVERIFIED`；Gate 1 仍以 demo 演示跑通，但 §4 缺口 §S1.18-1 「真实 SHA-locked 样本」**显式标记 OPEN**，不掩盖。

**与既有构件的衔接**：

- `seed_jiangsu_gdp_demo.py`：扩 `--load` 时按"是否有真实文件"分流；保留 `--status` / `--unload`。
- `cegr.source_document.file_hash_sha256`：现有 CHECK `source_doc_hash_format`（64 hex）继续生效；DEMO sentinel 必须同样满足 64 hex。
- `evidence_pack`：SHA-256 列表 +12。
- `dbt`：`mart_source_disagreement` 现有 S0/S1 比对逻辑不需要改；DEMO 行需在 dbt 投影里被识别为 DEMO，不进入跨源冲突候选池（详见 §3.2）。

---

## §1. 既有 demo 现状盘点

### §1.1 文件 + 库函数（已存在）

| 路径 | 角色 | 关键事实 |
|---|---|---|
| `data/seeds/jiangsu_gdp_2020_2024.json` | 演示数据源（5 行 2020-2024 江苏 GDP） | `metadata.seed_kind="DEMO_HANDCRAFTED"`；`lineage.source_file_sha256="00…00"`；`lineage.source_file_url="(DEMO_SEED_NO_FILE)"` |
| `scripts/seed_jiangsu_gdp_demo.py` | seed loader (`--load/--status/--unload`) | 写 `cegr.source_document.file_hash_sha256=00…00` + `verification_status='UNVERIFIED'` + `caveat_text`；行 schema 已稳定 UUID |
| `docs/27-stage1-s12-gate1-prep-pack-20260825.md` §2 | API 演示 step-by-step | 用 `seed_jiangsu_gdp_demo.py --load` → `GET /api/indicator/{id}/series` → `GET /api/source/{doc_id}` 演示 SHA-256 回溯；**当前 §2.4 步骤会看到全零 SHA** |

### §1.2 真实样本检索结果（**本地零文件**）

```bash
$ ls data/raw/                     # 仅 .gitkeep + 空 02-provincial-yearbook/
$ find data -name "*.xlsx" -o -name "*.pdf" -o -name "*.docx"  # 0 hit
$ grep -l "江苏\|Jiangsu\|JIANGSU" data/extracts/*/extracted.json
  data/extracts/00-national-yearbook-table/extracted.json  # 仅作为 indicator 列表中的一项提及，非真实数据
```

**结论**：本地**无**任何可计算 SHA-256 的江苏 GDP 文件。data/extracts 下唯一带 SHA 的表 (`00-provincial-yearbook-table`) 是 **Hubei 2025** 年鉴表 (`file_name=0109-地区生产总值.xls`, `file_hash_sha256=076b41ab…`)，与江苏 2020-2024 demo 主题无关。

### §1.3 Stage 2 衔接点

- S1.17 `scripts/admin_upload.py`（已交）：人工上传入口 — Stage 2 接通后，用户上传真实 Jiangsu 年鉴 XLSX → 计算 SHA-256 → 写 `cegr.source_document` → 替换 demo 的 UNVERIFIED + 全零 SHA。
- S1.13 后端 admin/upload 路由（per `docs/28`）：尚未接通；S1.18 不依赖其完成。

---

## §2. SHA-256 锁定路径选项

### §2.1 路径 A：保留全零 + 加 `is_demo` 标记（**最小改动，推荐**）

**做法**：

1. `data/seeds/jiangsu_gdp_2020_2024.json` 的 `lineage` JSONB 增加 `"is_demo": true` 与 `"demo_reason": "no real source file fetched; hand-crafted per tasking 92 §1.1"`；`source_file_sha256` 仍为 `00…00`（**不变**，避免破坏现有 124 行引用该值的测试与回执）。
2. `scripts/seed_jiangsu_gdp_demo.py` 写 `cegr.source_document` 时同步把 `is_demo` 透传到 `lineage` JSONB 列（observation 表已有 `lineage jsonb` 列）。
3. 新增 dbt 投影列 `mart_source_disagreement.is_demo`（= `source_document.lineage->>'is_demo' = 'true'`），并在跨源比对 CTE 里 `WHERE NOT is_demo` 过滤掉 DEMO 行 — 这样 DEMO 不参与 R03 跨源冲突候选池。
4. 新增 pytest 单测：
   - `tests/test_demo_sha_sentinel.py`：断言 `file_hash_sha256='00…00'` 的 demo 行 `verification_status='UNVERIFIED'` 且 lineage 含 `is_demo=true`，下游按 `is_demo` 过滤后行数=0（不污染跨源）。
   - 端到端：load seed → 跑 mart → 验证 mart 中**不出现**这条 demo 来源。

**优点**：不动 `gate_thresholds.json` / 不动现有 dbt 测试 / 改动局部（一个 JSONB 字段 + 一个 dbt CTE 过滤）；诚实信号强（`is_demo=true` 与 `verification_status='UNVERIFIED'` 双重信号）。

**缺点**：仍占一行的 `source_document` 与 5 个 `observation`；`file_hash_sha256='00…00'` 字符串仍在库中（需明确写入说明：`source_doc_hash_format` CHECK 只查 64 hex，全零满足格式 → 不需修改 CHECK）。

### §2.2 路径 B：DEMO sentinel SHA（计算式而非字面 `00…00`）

**做法**：`source_file_sha256 = sha256("DEMO_SEED:jiangsu-gdp-2020-2024:v1")`，可在 seed loader 里 `_demo_sha()` 函数计算。这样：

- `file_hash_sha256` 仍为合法 64 hex（满足 CHECK）
- 任何按 SHA 比对的代码会自然把不同 DEMO seed 的 sentinel 区分开（避免所有 DEMO 共占一个 `00…00` 哈希值）
- 与真实 SHA 在同一列中形态一致，下游不必特判 `00…00`

**优点**：与真实 SHA 形态对齐；不同 DEMO 自动分开。

**缺点**：`00…00` 是 DEMO 业内常识，全零 → sentinel 替换需要 dbt / 测试 / 文档 / 回执四处同步改；任何读 SHA 的下游测试可能把全零当 sentinel 显式断言（需要全部改 → 风险更大）。

**评估**：相对路径 A 收益小、改动大，**不推荐**作为主路径。可作为路径 A 实施一段时间后的「可选」远期清理。

### §2.3 路径 C：把 demo 行迁出 `source_document` 主表

**做法**：新增 `cegr.source_document_demo` 表，DEMO seed 写这里而非主表；`cegr.observation` 的 `source_id` 不再 FK 到 demo 表。

**优点**：物理隔离，R03 / 一致性 / 监控 SQL 一行 `WHERE source_id IN (SELECT id FROM cegr.source_document WHERE verification_status='VERIFIED')` 即天然过滤。

**缺点**：schema migration（trigger / FK / dbt models 全要审）；S1.13 之后若真实样本上链，需要把所有引用 demo 表的 ETL 改回主表；复杂度过高，**不推荐**。

### §2.4 决策记录

**本刀采用路径 A**：

- 改动最小（JSONB 字段 + 一处 dbt CTE 过滤 + 一组 pytest）
- 不动 schema、不动 `gate_thresholds.json`、不动现有 dbt 测试
- 路径 B 作为后续远期清理候选（§9）
- 路径 C 否决（成本/收益不匹配）

---

## §3. 实现设计

### §3.1 seed JSON + loader 改动

**`data/seeds/jiangsu_gdp_2020_2024.json`**：在 `lineage` 顶层加：

```json
"is_demo": true,
"demo_reason": "no real source file fetched; hand-crafted per tasking 92 §1.1",
"demo_sentinel_sha256": "00…00 (literal zeros; do not interpret as a real hash)"
```

5 行 observation 的 `lineage` 也对应同步加 `is_demo=true`（保证 mart 投影可定位到行级）。

**`scripts/seed_jiangsu_gdp_demo.py`**：

- 写 `cegr.source_document` 不变（`file_hash_sha256` 仍为 `00…00`、`verification_status='UNVERIFIED'`、`caveat_text` 沿用）。
- 写 `cegr.observation.lineage` 时，lineage JSONB 中包含 `is_demo=true` 与 `chain_id`。
- 新增 `--status` 输出多一行：`is_demo_markers: N rows tagged (expected: 5)`，便于人工快速核对。

### §3.2 dbt mart 投影

**`dbt/models/marts/mart_source_disagreement.sql`**：在现有 26 列基础上，加一列：

```sql
sd.is_demo AS is_demo,
```

并在 CTE `disagreement_pairs` 的 WHERE 子句加：

```sql
WHERE NOT COALESCE(sd.is_demo, false)
```

—— 这样 DEMO 行不进 cross-source pair 比较池。**注意**：仍可在 mart 主查询 SELECT 中保留 `is_demo` 列以便 Stage 2 替换时筛出 DEMO 行做清理。**完整保留行**，只**过滤跨源冲突**。

### §3.3 pytest

新增 **`tests/test_demo_sha_sentinel.py`**（≈ 6 用例）：

1. `test_seed_json_has_is_demo`：直接读 `data/seeds/jiangsu_gdp_2020_2024.json` 断言 `lineage.is_demo=true`。
2. `test_demo_load_writes_is_demo_in_observation_lineage`：`seed_jiangsu_gdp_demo.py --load` 后查 `cegr.observation.lineage->>'is_demo' = 'true'` 行数 = 5。
3. `test_unverifed_status_for_demo`：写后 `verification_status='UNVERIFIED'`、`file_hash_sha256='00…00'`。
4. `test_demo_excluded_from_mart_cross_source`：load 后跑 dbt mart；断言 mart 中**不出现**该 `source_document_id` 作为 S0↔S1 pair 的参与者。
5. `test_unload_clears_demo_rows`：`--unload` 后 `cegr.observation` 中 `lineage->>'is_demo' = 'true'` 行数 = 0。
6. `test_existing_ingest_monitor_unchanged`：回归 `tests/test_ingest_monitor.py` 12 用例仍绿（确认 ingest monitor 不读 `is_demo`，避免下游监控被过滤逻辑误伤）。

### §3.4 evidence_pack

`evidence_pack/manifest.json`：

- `scripts/seed_jiangsu_gdp_demo.py` 的 role 不变（seed_loader）
- `tests/test_demo_sha_sentinel.py` 新增 role=`schema_negative_test`
- pack 计数 `+1`

### §3.5 与 S1.12 Gate prep pack / API 演示脚本的衔接

`docs/27-stage1-s12-gate1-prep-pack-20260825.md` §2.4 「1 跳回溯到 source_document + SHA-256」步骤 — 当前演示能看到 `file_hash_sha256="00…00"`；S1.18 后应**追加一段**：

> **S1.18 起**：DEMO 行还会在 `lineage.is_demo=true` 上被识别；调用方应在拿到 `file_hash_sha256='00…00'` 时再查 `lineage.is_demo` 字段确认是否为 demo（非真实文件）；生产下游（监控 / 跨源 / 一致性）应 `WHERE NOT is_demo` 过滤。

回执中标注 `docs/27` 需在 S1.18 实现刀后由 Cursor 增量更新（Cursor 拥有 `docs/27` 写作权 — per 红线）。

`scripts/seed_jiangsu_gdp_demo.py --status` 的输出格式更新（§3.1）。

### §3.6 真实样本路径（前置条件 — Stage 2 接通后启用）

不属本刀实施范围，仅规划接口：

- `scripts/compute_file_sha.py --path <file>`：CLI 算 SHA-256 + 文件大小 + 行数（CSV/XLSX）；stdout 一行 JSON。
- `scripts/replace_demo_with_real.py --source-doc-id <UUID> --file <path>`：把 demo source_document 的 `file_hash_sha256` 替换为真实 SHA、`verification_status='PENDING'`、写 audit trail。
- 此两 CLI 在 S1.18 实现刀**不交付**，留待 Stage 2 S1.17 admin/upload 通路接通后另开 §1.19 / §1.20。

---

## §4. 空样本 / 无真实文件时的诚实失败策略

按 S1.18 实施后状态分三种：

| 状态 | `file_hash_sha256` | `verification_status` | `lineage.is_demo` | 下游处理 |
|---|---|---|---|---|
| 真实样本已 SHA-locked | 真 SHA-256 | `VERIFIED` | NULL/false | 正常路径 |
| 真实样本已上传待人工审 | 真 SHA-256 | `PENDING` | NULL/false | 监控告警；不参与跨源 |
| DEMO（手工 seed） | `00…00` | `UNVERIFIED` | `true` | `WHERE NOT is_demo` 过滤；监控旁路 |

**fail-closed 规则**：

1. **任何 ingest / 一致性 / 跨源 SQL 必须显式过滤 DEMO**：dbt mart 已加 `WHERE NOT is_demo`；ingest_monitor 检查失败率时 `triggered_by='url_health_probe'` 已存在，不与 demo 冲突。
2. **真实样本出现但 SHA 计算失败 → 整个 ingest 失败**：`compute_file_sha.py` 返回非 0 → `replace_demo_with_real.py` 退出非 0 → 不写库（不静默吞错）。
3. **真实样本 SHA 与已存在的 PENDING/VERIFIED 行碰撞**：`source_registry` UNIQUE on `primary_url` 类似约束需复用；新 SHA 命中老 SHA → 走"复用老 source_document"路径（不创建新行；避免 N 份同一文件）。
4. **Gate 1 §4 缺口 §S1.18-1 「真实 SHA-locked 样本」状态：OPEN** — 本刀不宣称闭合；S1.18 仅闭合「DEMO 与真实样本的区分机制」，真实样本仍待 Stage 2 S1.17 admin/upload 接通后人工上传替换。

---

## §5. 红线（沿用 `docs/09` + tasking 131）

- ❌ **不宣布 Stage 0 / Gate 1 PASS**
- ❌ **不批量 2020-2025**（沿用 S1.12 红线）
- ❌ **不 HTTP 爬源站**（江苏统计局站点等真实源站不爬；真实样本路径仅消费本地或人工上传文件）
- ❌ **不降 OCR 门槛**（S1.18 不涉及 OCR）
- ❌ **不把 1909 代表中国 / 不把陕西标为门控**
- ❌ **不擅自 `--force` / `--force-with-lease`**
- ❌ **不替用户下裁定**
- ❌ **不在聊天复述 Cursor 长文；不索要 PAT**
- ❌ **不改 `gate_thresholds.json`**
- ❌ **不伪造 SHA**（路径 A 仍保留全零但用 `is_demo` 双重信号；路径 B/C 已否决）
- ❌ **Cursor 不写本文件正文**（per `tasking 131` §红线）
- ❌ **不替 demo 伪造 `verification_status='VERIFIED'`**

---

## §6. 一条命令手动复验

实现刀交付后，下列命令应一次跑通：

```bash
# 1. load demo
python3 scripts/seed_jiangsu_gdp_demo.py --load
python3 scripts/seed_jiangsu_gdp_demo.py --status
# 期望: observations=5 + is_demo_markers: 5 rows tagged (expected: 5)

# 2. dbt mart 重建
.venv-dbt/bin/dbt run --select +mart_source_disagreement --full-refresh \
  --profiles-dir dbt
# 期望: 27 列（含 is_demo），PASS

# 3. pytest 全跑
python3 -m pytest tests/test_demo_sha_sentinel.py \
  tests/test_ingest_monitor.py \
  tests/test_url_health_probe.py \
  tests/test_monitor_ingest_cli.py \
  tests/test_source_disagreement_s141.py \
  tests/test_r03_cross_source_dbt.py -v
# 期望: 6 (S1.18) + 12 (S1.8) + 6 (S1.17) + 6 (S1.17) + 9 (S1.14) + 5 (S1.16) = 44 PASS

# 4. 跨源验证（DEMO 不污染）
psql "$CEGR_DSN" -c "
SELECT COUNT(*) FROM cegr_staging.mart_source_disagreement
WHERE is_demo = TRUE;"
# 期望: 0（mart WHERE 已过滤；DEMO 行只在主表 cegr.source_document/observation 中存在）
```

---

## §7. 与既有 dbt / 测试的边界声明

| 既有构件 | 责任 | 本刀动作 |
|---|---|---|
| `seed_jiangsu_gdp_demo.py` | DEMO seed loader | **改**：JSONB 字段透传 `is_demo` + `--status` 输出格式扩展 |
| `data/seeds/jiangsu_gdp_2020_2024.json` | 演示数据源 | **改**：`lineage` 加 `is_demo=true` + `demo_reason` + `demo_sentinel_sha256` 注释 |
| `dbt/models/marts/mart_source_disagreement.sql` | 跨源冲突 mart | **改**：加 `is_demo` 列 + `WHERE NOT is_demo` 过滤 |
| `dbt/tests/test_cross_source_consistency_threshold.sql` | R03 阈值 singular test | **不动**：阈值逻辑不变；DEMO 行被前置过滤掉，断言不变 |
| `tests/test_source_disagreement_s141.py` | S1.14 回归 | **不动** |
| `tests/test_r03_cross_source_dbt.py` | S1.16 回归 | **不动** |
| `tests/test_ingest_monitor.py` | S1.8 回归 | **不动** |
| `tests/test_url_health_probe.py` / `tests/test_monitor_ingest_cli.py` | S1.17 回归 | **不动** |
| `gate_thresholds.json` | 阈值构件 | **不动** |
| `docs/27-stage1-s12-gate1-prep-pack-20260825.md` | S1.12 prep pack | **不动**（Cursor 拥有；S1.18 实现刀后 Cursor 增量更新 §2.4） |

**唯一新增构件**（实现刀）：
- `tests/test_demo_sha_sentinel.py`：6 用例

**migration**：**无 schema migration**。`is_demo` 进 `lineage` JSONB，无新列、无新表、无 trigger 改。

---

## §8. 诚实缺口（本刀后剩余）

| Gap ID | 描述 | 闭合路径 | 状态 |
|---|---|---|---|
| §S1.18-1 | 真实 SHA-locked 江苏 GDP XLSX/PDF 未到位（本地零文件） | Stage 2 S1.17 admin/upload 接通后人工上传 → 跑 `replace_demo_with_real.py` | **OPEN** |
| §S1.18-2 | `compute_file_sha.py` / `replace_demo_with_real.py` CLI 未交付 | §3.6 远期；与 S1.17 admin/upload 同步 | OPEN |
| §S1.18-3 | `docs/27` §2.4 增量更新（S1.18 后追加 is_demo 说明）由 Cursor 拥有 | Cursor 在 S1.18 PASS 后增量 | OPEN（依赖 Cursor） |
| §S1.18-4 | 路径 B（计算式 DEMO sentinel SHA）未采纳 | 远期清理（如决定治理全零 SHA 习惯） | 候选（非阻塞） |

---

## §9. 后续刀（Stage 1 候选 / Stage 2 触发）

- **§1.19**: `scripts/compute_file_sha.py` + `scripts/replace_demo_with_real.py` 实施（Stage 2 触发：S1.17 admin/upload 通路接通后）。
- **§1.20**: 真实江苏年鉴 XLSX 上链 → 重跑 demo → 把 `verification_status` 从 UNVERIFIED → VERIFIED → 从 mart CTE `WHERE NOT is_demo` 移除 → 真实样本正式进入跨源候选池。
- **远期**：路径 B 全零 → 计算式 DEMO sentinel；非阻塞。

---

## §10. 回执归属

- 实现刀 → 回执 `132-stage0-cc-s18-impl-receipt-20260825.md` 进 `reviews/stage0-gate0-rework-2026-08-23/`
- Cursor 审验 → `133-stage0-cursor-s18-impl-audit-PASS-20260825.md`（Cursor 拥有）
- 唤醒 `134` → 启动 S1.19 规划（如 §9 §1.19 候选在 S1.18 PASS 后由用户裁定）

— End — (CC @ S1.18 规划)
