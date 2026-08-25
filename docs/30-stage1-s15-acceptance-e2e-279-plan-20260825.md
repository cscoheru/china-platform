# 30 — Stage 1 / S1.15 — docs/10 §2.7–2.9 e2e 验收测试规划（279）

- 编号：`30-stage1-s15-acceptance-e2e-279-plan-20260825`
- 作者：CC（规划 only；实现另开任务书）
- 前置：Cursor `111` S1.14 PASS；`112` 任务书；`docs/27` §4.1 缺口 3（"2.7-2.9 e2e 自动化测试缺失"）；用户裁定 A
- 范围：**规划 only** — 本文档定义 §2.7/§2.8/§2.9 三组 e2e 验收测试的判定语义、所需 schema 增量、测试落点与清单。不写代码、不改 schema、不跑实现。

---

## §0. 目标与判定语义（对齐 docs/10）

| # | docs/10 定义 | 判定语义（e2e 可执行形式） |
|---|---|---|
| 2.7 | 行政区划有效期：`observation.geo_version` 必须在 period 当时有效（巢湖 2011 拆分例） | 对每条 observation：其 `geo_code_version` 的 `[valid_from, valid_to]` 必须覆盖 `calendar_period` 的 `[start_date, end_date]`；覆盖失败 = 违规 |
| 2.8 | OCR 置信度：`confidence < 0.7` 必须入复核队列、不入正式表 | OCR 提取（`extraction_method ∈ {PDF_OCR, IMAGE_OCR}`）且 `confidence < 0.70` 的单元格：**不得**进入 `observation`（DB 硬门），**必须**落入复核队列表 |
| 2.9 | 缺失值不补零：缺失写 NULL + `missing_reason`，不得写 0 | `value=0` 与 `missing_reason IS NOT NULL` 不得共存（DB CHECK 已有）；`raw_value` 为缺失占位符（`…`/`—`）时 `value` 必须为 NULL 不得为 0 |

**阈值来源声明**：
- §2.8 的 `0.70` 是 **docs/10 §2.8 的验收常量**（0–1 标度，`observation.confidence CHECK 0-1`）。
- `spikes/04-scanned-pdf/gate_thresholds.json` 是 **spike-04 OCR 质量评测**的 gate 文件（0–100 标度、450 格分母、BLOCKED 判定），与本 e2e 是**两个不同构件**。本刀**只读不写**该文件；红线「不改 gate_thresholds.json」完整适用。

---

## §1. §2.7 行政区划有效期 — 现状与设计

### §1.1 现状（已有，无需新 schema）

- `geo_code_version(valid_from DATE NOT NULL, valid_to DATE NULL)` + `EXCLUDE USING gist` 同实体区间不重叠（`schema/01-core.sql:160-177`）
- `observation.geo_code_version_id NOT NULL` FK + `calendar_period(start_date, end_date)`
- **缺口**：DB 不校验「版本区间覆盖 period」——错误配对可以插入成功。docs/10 §2.7 的 e2e 是**检出型**测试（查询发现违规），insert 时硬拦截属 Stage 2 触发器（见 §7）。

### §1.2 e2e 设计

判定查询（pytest 内执行，断言违规数）：

```sql
SELECT o.id, gcv.geo_entity_id, cp.start_date, gcv.valid_from, gcv.valid_to
FROM cegr.observation o
JOIN cegr.geo_code_version gcv ON gcv.id = o.geo_code_version_id
JOIN cegr.calendar_period cp    ON cp.id  = o.calendar_period_id
WHERE cp.start_date >= gcv.valid_from            -- 覆盖下界
  AND (gcv.valid_to IS NULL OR cp.end_date <= gcv.valid_to)  -- 覆盖上界（开放式版本恒有效）
```
→ 迁移测试中取**补集**断言违规数。fixture 用巢湖模式：实体「巢湖市（2011 拆分）」版本 `valid_from=2000-01-01, valid_to=2011-07-31`；2010 年 observation 合法、2012 年 observation 引用旧版本 = 违规 1 条。

---

## §2. §2.8 OCR 置信度分流 — 需 schema 增量

### §2.1 现状

- `observation.confidence NUMERIC CHECK (0..1)`；`extraction_method` 枚举含 `PDF_OCR`/`IMAGE_OCR`
- **无复核队列表**；spike-04 OCR 全量 BLOCKED（numeric 0%），其 `extracted.json` 从未加载进 `observation`
- 现库中 OCR 路径 observation 行数 = 0（见 §5 空表诚实）

### §2.2 设计（migration `007_ocr_review_queue.sql`，实现另开）

**(a) 新表 `cegr.ocr_review_queue`**（单元格级停车场）：

```sql
CREATE TABLE IF NOT EXISTS cegr.ocr_review_queue (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id  UUID NOT NULL REFERENCES cegr.source_document(id) ON DELETE RESTRICT,
    ingestion_run_id    UUID REFERENCES cegr.ingestion_run(id),
    indicator_id        UUID REFERENCES cegr.indicator_definition(id),   -- 复核确认映射前可空
    geo_entity_id       UUID REFERENCES cegr.geo_entity(id),
    calendar_period_id  UUID REFERENCES cegr.calendar_period(id),
    raw_ocr_text        TEXT,                       -- 原始单元格文本（含不可解析）
    parsed_value        NUMERIC,                    -- 复核前解析值（可能是错的）
    confidence          NUMERIC NOT NULL CHECK (confidence >= 0 AND confidence < 0.70),
    locator_page        INTEGER,
    locator_bbox        JSONB,
    review_status       TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (review_status IN ('PENDING','ACCEPTED','REJECTED','REEXTRACT')),
    resolution_note     TEXT,
    reviewed_by         TEXT,
    reviewed_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ocr_review_queue_status ON cegr.ocr_review_queue (review_status);
CREATE INDEX IF NOT EXISTS idx_ocr_review_queue_doc    ON cegr.ocr_review_queue (source_document_id);
```

**(b) `observation` 加硬门 CHECK**（docs/10「不入正式表」的 DB 级不可绕过形式）：

```sql
ALTER TABLE cegr.observation ADD CONSTRAINT observation_ocr_confidence_floor CHECK (
    extraction_method NOT IN ('PDF_OCR','IMAGE_OCR')
    OR confidence IS NULL        -- 非 OCR 语义路径
    OR confidence >= 0.70        -- docs/10 §2.8 常量；open-ended：恰好 0.70 通过（定义是 <0.7）
);
```

> 幂等性教训（S1.14 FAIL 复盘）：007 落 `cegr.` schema，随 conftest `DROP SCHEMA cegr CASCADE` 自然清理，无 005 式 public 残留问题；`ADD CONSTRAINT` 用 `IF NOT EXISTS` 守卫（PG 不支持直接 IF NOT EXISTS，用 DO 块查 pg_constraint）。

### §2.3 与 ingest / upload 的衔接（边界，不实现）

```
connector 提取单元格 (S1.10 路径)
   │  extraction_method ∈ {PDF_OCR, IMAGE_OCR}?
   ├─ confidence ≥ 0.70 → INSERT observation            ← 正常路径
   └─ confidence < 0.70 → INSERT ocr_review_queue       ← 分流（应用层路由 + (b) DB 硬门双保险）
S1.13 /admin/upload → 只登记 source_document；上传路径不做 OCR、不产生 queue 行
复核 ACCEPT → 人工以 MANUAL_UPLOAD 重新提取入 observation（不改 confidence 粉饰）
```

---

## §3. §2.9 缺失值不补零 — 现状与设计

### §3.1 现状（`01-core.sql:488-495` 已有 DB 约束，无需新 schema）

```sql
observation_missing_consistency CHECK (
    (value IS NULL AND missing_reason IS NOT NULL) OR
    (value IS NOT NULL AND missing_reason IS NULL) OR
    (value IS NULL AND is_imputed = TRUE) )
```
即：`value` 与 `missing_reason` 互斥；补零（value=0 + reason）**已被 DB 拒绝**。

### §3.2 e2e 设计（检出 + 负例）

1. **正例**：`value=NULL, missing_reason='NOT_PUBLISHED', is_imputed=FALSE, unit=NULL`（unit CHECK 允许 value 为 NULL 时空）→ 插入成功且读回保持 NULL。
2. **负例 A**：`value=0, missing_reason='NOT_PUBLISHED'` → CheckViolation（「不写 0」的 DB 证据）。
3. **负例 B**：`value=123, missing_reason='SUPPRESSED'` → CheckViolation（有值不得挂缺失因）。
4. **检出查询**（CHECK 管不到的灰区）：`raw_value` 为缺失占位符（`…`、`—`、空串）而 `value=0` 的行 = 补零污染。CHECK 只挡 reason 非空的行；**reason 漏填的补零**只能靠此检出查询。真 0（`raw_value='0'`）合法。

---

## §4. 测试落点与用例清单

**落点决策**：
- **pytest**：`tests/test_acceptance_e2e_s15.py`（单文件，~14 用例；复用 conftest 全链 apply + S1.14.1 式 fixture 骨架）
- **dbt**：不用 — §2.7–2.9 是摄取时门禁 + 行级性质断言，非跨行分析（与 S1.14 的 2.4 跨源一致性性质不同）
- **GE**：不新增 suite — S1.12 数据契约 suite 已覆盖表形状；本刀用例全部落 pytest

| 组 | 用例（实现时逐条落） | 断言 |
|---|---|---|
| §2.7 ×4 | `valid_version_covers_period`（2010 巢湖） | 检出查询违规数 = 0 |
| | `expired_version_detected`（2012 引旧版本） | 违规数 = 1 且指向该实体 |
| | `overlapping_versions_rejected` | 同实体区间重叠 → ExclusionViolation |
| | `open_ended_version_always_valid`（valid_to NULL） | 任意后期 period 违规数 = 0 |
| §2.8 ×6 | `queue_schema_applied` | 007 表 + 2 索引存在 |
| | `low_confidence_routed_to_queue`（0.65） | queue 1 行 / observation 0 行 |
| | `high_confidence_passes`（0.85） | observation 1 行 / queue 0 行 |
| | `boundary_070_passes`（恰 0.70） | 通过（定义 `<0.7` 才分流） |
| | `ocr_floor_check_rejects`（直插 0.65 OCR 行） | CheckViolation |
| | `non_ocr_unaffected`（EXCEL_PARSE, confidence NULL） | 正常插入 |
| §2.9 ×4 | `missing_row_persists_null` | 读回 value IS NULL + reason 保留 |
| | `zero_with_reason_rejected` | CheckViolation |
| | `value_with_reason_rejected` | CheckViolation |
| | `zero_marker_detection`（value=0 + raw_value='…'） | 检出查询命中；`raw_value='0'` 不命中 |

合计 14 用例（≥ docs/27 §4.1-3 的覆盖要求）。

---

## §5. 空表诚实声明

- 现库 `observation` 只有 S1.12 demo seed（江苏 GDP，EXCEL_PARSE/API 路径）；**PDF_OCR/IMAGE_OCR 行数 = 0**。
- spike-04 OCR gate **BLOCKED**（numeric 0% / char 3.7%），其结果从未入 `observation`；1909 样本代表性待用户书面裁定（`gate_thresholds.json.user_decision_required`）。
- 因此 §2.8 的生产路径 e2e 只能以 **fixture 注入**证明（路由 + DB 硬门）；真实扫描源落库后的 e2e 属后续刀（依赖用户裁定）。
- §2.7/§2.9 同理：当前无真实巢湖类拆分数据与真实缺失行，用例全部 fixture 驱动。

## §6. 与 S1.12 / S1.13 / S1.14 边界

| 刀 | 边界 |
|---|---|
| S1.12 | `docs/27` demo seed 与其 manifest 不动；本刀实现后其 §4.1-3 缺口方可闭 |
| S1.13 | `/admin/upload` 路由、CLI、migration 005（public schema）**零改动**；§2.8 只消费其登记的 source_document |
| S1.14 | `source_disagreement` / migration 006 / 2%/5% 阈值不动；0.70 与 2%/5% 是不同域常量，互不牵连 |

## §7. 红线遵守

❌ 不 Gate 1 PASS（裁定权在用户 + Cursor 审计）；❌ 不 DSH；❌ 不爬网；❌ 不改 `gate_thresholds.json`（只读引用）；❌ 本刀只规划，不改 schema / 不写测试代码。

## §8. 诚实缺口与 Stage 2 建议

1. §2.7 无 insert 时触发器拦截（仅检出）→ Stage 2 可加 trigger 或摄取层校验
2. `ocr_review_queue` 无复核 UI / API（Stage 2；表先行）
3. 0.70 常量在 CHECK 与路由两处出现 → Stage 2 与 2%/5% 一并参数化（dbt var / 环境变量），改动须过用户
4. 真实扫描源 e2e 被 1909 裁定阻塞（不催促、不替代裁定）
5. `review_status='REEXTRACT'` 的回灌链路未设计（复核 ACCEPT 走 MANUAL_UPLOAD 是最小闭环）

— CC @ queue_rev 38，S1.15 规划（docs/30）—
