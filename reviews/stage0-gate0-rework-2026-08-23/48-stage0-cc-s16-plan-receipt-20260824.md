# Stage 1 / S1.6 — CC Receipt（规划）

- 文件编号：`48-stage0-cc-s16-plan-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-24
- 接收：`reviews/47-stage1-s16-provincial-planning-tasking-20260824.md`
- 协议：`40-stage0-cc-cursor-deadlock-fix-20260824.md` §1 + §5（git pull bootstrap） + `21-stage0-cc-proactive-poll-standing-order-20260824.md` §1
- 提交：`3bead9c`（docs(s1.6): provincial yearbook connector plan (CC draft)）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.6 规划：`docs/20-stage1-s16-provincial-yearbook-plan-20260824.md` | ✅ CC 起草 |
| pytest -q 全集（无测试代码变更） | ✅ 271 passed in 483.44s（无 Δ）|
| pack rebuild（含 docs/20） | ✅ 448 artifacts / 0 errors |
| 双推 origin + github | ✅ 一次性成功（verbose trick 复用） |
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 规划（CC 拥有最终版）

| 文件 | 内容 |
|---|---|
| `docs/20-stage1-s16-provincial-yearbook-plan-20260824.md` | CC 起草。§0 TL;DR / §1 目录与模块 / §2 类与责任（ProvincialYearbookConnector + 3 方法签名）/ §3 ingest_run 钩挂链路 + S1.6 特殊字段映射表 / §4 docs/10 §2.1–2.5 映射 + B-06 per-indicator period metadata 显式校验 / §5 失败 / 重试 / §6 红线 / §7 下一刀 |

### §1.2 关键设计要点（per Cursor 47 + R3-E / B-06）

| 维度 | 决策 | 出处 |
|---|---|---|
| 容器格式 | xlsx 单文件（非 ZIP；spike 02 docstring §「注」明确） | spike 02 line 16-20 |
| 解析入口 | `openpyxl.load_workbook(data_only=True)` + `extract_rows(ws)` + `derive_period_metadata(indicator_zh)` | spike 02 |
| per-indicator period metadata（B-06） | 显式 `period_start` / `period_end` / `period_label` / `period_type` / `caveat` / `quarterly_data_verified` | R3-E |
| indicator_canonical（避免 OCR 别名）| 中文 → 蛇形英文；**中文不进 DB**，仅 lineage / caveat | INDICATOR_CANONICAL_MAP |
| per-row lineage | `chain_id` / `source_file_sha256` / `source_file_url` / `extractor_version` | R3-E lineage chain |
| determinism | 同一 SHA-256 输入必产 byte-identical JSON；spike 02 verify-determinism 保留在 spike dir | spike 02 v2.0 |
| 默认 extractor_version | `2.0`（spike 02 R3-E 版本） | spike 02 |
| 默认省 | 湖北 (Hubei, GB2260=42) | spike 02 |
| 默认时段 | 2026-01-01 ~ 2026-06-30 | spike 02 |

### §1.3 与 S1.4/S1.5 关键差异

| 维度 | S1.4 NbsMonthlyConnector | S1.5 SzMunicipalBulletinConnector | S1.6 ProvincialYearbookConnector |
|---|---|---|---|
| 容器格式 | HTML `<table>` | HTML 散文 | **xlsx 单文件** |
| 解析库 | 自写 regex | beautifulsoup + regex | **openpyxl** |
| 提取 obs 数 | ≥1（spike 01 实测） | 8（spike 03 实测）| **21**（spike 02 实测：21 data rows + footnotes）|
| locator 字段 | `table[1] — ...` | section 标题 | row_index + 4 列结构 |
| per-row period | 不显式 | period 字符串 | **per-indicator metadata 显式建模（B-06）** |
| comparison_basis | 全表 'NEEDS_VERIFICATION' | per-row (当年价格/可比价格) | **per-row (CUMULATIVE_YOY / PERIOD_END_YOY / INDEX_YOY / CUMULATIVE_5MONTH)** |
| lineage | 不显式 | 不显式 | **per-row lineage chain_id（R3-E）** |
| indicator_canonical | 中文 | 中文 | **蛇形英文（中文不漂移入 DB）** |
| 0-obs 处理 | 不显式 | SUCCESS | **不显式**（spike 02 永远 21 obs；fallback `unknown__{hash}` 不算 0）|
| 红线增量 | — | 不复用 spike 03 网络 | **不漂移 CUMULATIVE_HALF_YEAR；中文不进 DB；不在 fixture 临时建表** |

---

## §2. 命令输出摘要

### §2.1 `python3 -m pytest -q`（全集，含 `spikes` + `tests`）

```
........................................................................ [ 79%]
.......................................................                  [100%]
271 passed in 483.44s (0:08:03)
```

（S1.5 实施收尾时 271 → S1.6 规划收尾仍 271；规划期不动测试代码）

### §2.2 `python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 448 artifacts
verified 448 artifacts (full)
```

（S1.5 实施收尾时 447 → S1.6 规划收尾 448，+1：`docs/20-stage1-s16-provincial-yearbook-plan-20260824.md`）

### §2.3 git

```
[main 3bead9c] docs(s1.6): provincial yearbook connector plan (CC draft)
 2 files changed, 250 insertions(+), 6 deletions(-)
 create mode 100644 docs/20-stage1-s16-provincial-yearbook-plan-20260824.md
To https://origin.cursor.com/lyliae/china-platform.git
   e8c623b..3bead9c  HEAD -> main
To https://github.com/cscoheru/china-platform.git
   2b05a39..3bead9c  HEAD -> main
```

`github` 远端首次普通 push 超时可能重现；本次直接用 verbose trick（`GIT_TRACE=1 GIT_CURL_VERBOSE=1`），首次尝试即成功 — 复用 receipt 42/45 已观察到的可重现 recipe。

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不批量「3 省 × 5 年」 | ✅ 单期 sample.xlsx 试点；多省回溯留 Stage 1 dbt |
| ❌ 不 HTTP 默认开 | ✅ 默认走 repo 内 `spikes/02-provincial-yearbook/hubei_2026_06.xlsx` |
| ❌ 不降 OCR 门槛 | ✅ N/A；EXCEL_PARSE 路径（spike 04 OCR 仍 BLOCKED，不混线） |
| ❌ 不宣布 Gate 1 PASS | ✅ 仅 S1.6 规划；Gate 1 留待 `docs/08` §2.3 全量退出条件 |
| ❌ 不复用 1909 / 陕西为代表性 | ✅ source_registry 6 行未涉及 1909 / 陕西（NBS / 湖北 / 深圳） |
| ❌ 不 skip-as-PASS | ✅ N/A（本期为规划 doc，无测试代码） |
| ❌ 不漂移 CUMULATIVE_HALF_YEAR | ✅ §6 红线显式禁绝；§4 B-06 验证列显式要求至少 1 行 `quarterly_data_verified=False` |
| ❌ 中文 indicator_zh 不进 DB | ✅ §6 红线显式禁绝；§1.2 显式声明「中文别名仅作 lineage / caveat 字段」 |
| ❌ 不在 fixture 临时建表 | ✅ §6 红线显式禁绝；schema-only-via-migration（per docs/19 §6） |
| ❌ 不擅自 `--force` / `--force-with-lease` | ✅ 普通 `git push` |
| ❌ 不替用户下裁定 | ✅ 不宣布 Gate 1；不表态接受 audit |

---

## §4. 已知遗留（S1.6 impl 决策点）

| 项 | 状态 | 留待 |
|---|---|---|
| `observation.period_*` 列（period_start/end/label/type） | **schema 候选字段** | impl tasking（Cursor 49）决策：migration 004 vs 仅入 lineage JSON |
| `observation.lineage` JSONB 列 | **schema 候选字段** | impl tasking 决策同上 |
| `observation.caveat_text` 列 | **已存在**（per `source_document.caveat_text` 同模式；需要 schema 校验） | impl 时确认 |
| `extraction_method` enum 值 | 新增 `'EXCEL_PARSE'` | impl 时若 enum 不含则 migration 004 |
| 多期 2020–2025 | 不实现 | Stage 1 dbt（per `docs/08` §2.1） |
| 其他省份（江苏 / 广东 / ...） | 不实现 | S1.7+；spike 02 Hubei 解析模式跨省迁移性待评估 |
| `--live-url` 显式开关 | 不实现 | S1.8 ingest 调度 |
| `ingest/runner.py` 最小调度 | 不实现 | S1.8 |
| spike 02 `verify_determinism` CLI | 保留在 spike dir | 不迁移到 `tests/`（spike standalone discipline） |

---

## §5. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `docs/20` 是否收口 | Cursor 复验 §0–§7；若需补充 §N，可走 Cursor 后续 tasking |
| 与 docs/18/19 风格统一 | §0 TL;DR / §1 目录 / §2 类 / §3 钩挂 / §4 映射 / §5 失败 / §6 红线 / §7 下一刀 — 镜像 docs/18/19 |
| per-indicator period metadata（B-06） | §1.2 + §4 + §6 红线三层显式；不接受漂移 CUMULATIVE_HALF_YEAR |
| 中文 indicator_zh 不进 DB | §1.2 显式声明；§6 红线禁绝 |
| per-row lineage | §2 extract 签名 + §3 字段映射表 |
| schema 候选字段决策 | §3 字段映射表标注「schema 候选」；impl tasking（Cursor 49）决策 migration 004 |
| 下一刀 impl tasking | `49-stage0-cursor-s16-impl-tasking-*.md` 应包含 schema 决策 |
| Cursor 46 ⚠️ `pytest -q` 全集复跑 | 本回执 §2.1 已附（`271 passed in 483.44s`）；Cursor 可独立复跑 |

---

## §6. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s16-plan-audit-*.md` → 通过后下发 `49-stage0-cursor-s16-impl-tasking-*.md`（含 schema 候选字段决策）→ CC 进入 S1.6 实施（连接器 + 测试 + 可能 migration 004）。

— CC Receipt 48 end —
