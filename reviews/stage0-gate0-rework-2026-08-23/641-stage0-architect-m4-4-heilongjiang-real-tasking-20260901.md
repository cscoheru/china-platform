# 641 — M4.4 黑龙江政策真实化 spike（架构师 tasking）

> **刀号**: 641
> **Milestone**: M4.4（政策项目子刀 4/4）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**:
> - `docs/60-m4-3-policy-demo-20260901.md` §5（架构师推荐 641 = M4.4 黑龙江政策真实化 spike）
> - 640 receipt §8（用户接受 640 → 进入 641; "604接受，继续641"）
> - `docs/33 §3.2 sentinel`（lineage JSONB 是 is_demo 唯一落点;不新写 016 migration）
> - 638 / 639 / 640 demo 阶段累积;**641 是首次真实化 spike**——首次 INSERT 真实行到 cegr.policy_document 等
> - 640 关键反发现: 6 REACHABLE 任免源中仅 1 省 (黑龙江) 政策承载路径真正可达
> **用户接收**：`604接受，继续641`（2026-09-01）
> **不宣布** Gate / O1 / M2 / M4 PASS。

---

## 0. 范围（一句话）

641 落地 5 件：**(A1)** 黑龙江 `/zwgk/zfwj/` 真实政策样本抓取（≤3 条真实样本; curl 一次 + grep 解析; 不入库; **不爬网**(只抓首页 + 1-3 条详情页,共 ≤4 次 HTTP)）；**(A2)** `scripts/seed_m4_4_heilongjiang_real.sql` 真实化版本（1 source_registry 真实 + 1 source_document 真实（真实 SHA 计算）+ 6 政策表 × **1 真实样本 each**；lineage `is_demo='false'`；与 640 demo SHA `0…02` 区分；复用 640 lineage JSONB sentinel）；**(A3)** `docs/61-m4-4-heilongjiang-real-20260901.md` §1-§6 架构师级审查；**(B)** `tests/test_m4_4_heilongjiang_real.py` ≥ 6 用例；**全套 pytest ≥ 77/77 green**；**(C)** 回执 + commit + 双推；**架构师推荐 642 = M5 WAF spike（解决 5 BLOCKED 省根因; WAF 网防G01 假设进一步验证）或 642 = M4.5 任免真实化（复用 639 6 REACHABLE 任免源）**。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 641-A.1 | `scripts/fetch_heilongjiang_policy_v1_2024.py` + `evidence_pack/m4_4_heilongjiang_real_20260901.json` | DONE | 黑龙江 /zwgk/zfwj/ 真实政策样本抓取 (≤3 条);curl + grep + SHA256 计算;不写 cegr |
| 641-A.2 | `scripts/seed_m4_4_heilongjiang_real.sql` | DONE | 1 source_document 真实 (file_hash_sha256 = 真实 SHA) + 6 政策表 × 1 真实样本 each; lineage `is_demo='false'` 真实化; 复用 640 lineage JSONB sentinel (不新写 016 migration) |
| 641-A.3 | `docs/61-m4-4-heilongjiang-real-20260901.md` | DONE | §1-§6：M4.4 落地终态 / 黑龙江真实抓取数据 / 真实化 demo SQL 结构 / lineage 真实化 sentinel / 642 下一步 / 不宣称 PASS |
| 641-A.5 | `docs/reports/m4_4_heilongjiang_real_20260901.md` + `evidence_pack/m4_4_heilongjiang_real_20260901.json` | DONE | 真实抓取报告 + 证据包 |
| 641-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev67 → 641 tasking OPEN · 等 CC 落地 (即签即自交付;rev67 同时落地) |
| 641-B | `tests/test_m4_4_heilongjiang_real.py` | DONE | ≥ 6 用例：抓取报告存在 + 顶层裁定 / evidence JSON parses / seed SQL 6表×1 真实 each / seed lineage is_demo='false' / seed 真实 SHA ≠ demo SHA 0…02 / docs/61 六段 / docs/61 不宣称 PASS |
| 641-C | 回执 + commit + 双推 | DONE | `reviews/stage0-gate0-rework-2026-08-23/641-stage0-cc-m4-4-heilongjiang-real-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 641-A 详细

### 641-A.1 黑龙江政策真实抓取

**目标 URL**: `https://www.hlj.gov.cn/zwgk/zfwj/` (640 二次 probe REACHABLE 200; 仅 1 试点省政策可达)

**抓取边界 (硬性红线)**:
- ≤4 次 HTTP（首页 + ≤3 条详情页） — 架构师明确不爬网
- curl only (no JavaScript / no headless browser)
- 仅 grep title / publication_date / doc_type / url（不抓全文，不存档）
- 真实 SHA256 计算：每条详情页 HTML 的 SHA256
- 写入 `evidence_pack/m4_4_heilongjiang_real_20260901.json`
- **不写** cegr.* 表

**`scripts/fetch_heilongjiang_policy_v1_2024.py`**:

```python
# 仅探可达性 + 解析 ≤3 条政策样本,不算爬网
HEILONGJIANG_POLICY_INDEX = "https://www.hlj.gov.cn/zwgk/zfwj/"
FETCH_LIMIT = 3  # ≤3 条详情页
TIMEOUT = 15

def fetch_index() -> bytes:
    """curl 1 次首页; 解析 ≤3 条政策 URL."""
    ...

def fetch_detail(url: str) -> tuple[str, str, str, str, str]:
    """curl 1 次详情页; 返回 (title, publication_date, publisher, doc_type, sha256)."""
    ...

def main() -> int:
    """FETCH_LIMIT=3 次 HTTP; 写 evidence JSON."""
    ...
```

**关键约束**:
- 复用 `_probe_http_helpers.fetch()` (现有 helper)
- 不修改 helper 4 (avoid side effect on other probes)
- 脚本幂等（no time.sleep / no random; only curl + sha256）
- 不静默硬编码任何值（policy text 来自 curl 解析）

### 641-A.2 真实化 demo SQL

**架构师裁定（关键; 641 与 638/639/640 demo 阶段不同）**:
- **沿用 docs/33 §3.2 sentinel**: lineage JSONB 是 is_demo 唯一落点;**不新写 016 migration**
- 009 + 010 已在 6 政策表加 `lineage JSONB`
- demo 数据写 `lineage = {"chain_id": "demo_640", ...}` (is_demo='true')
- **真实数据写 `lineage = {"chain_id": "real_641_heilongjiang", "source_file_sha256": "<real SHA>", "source_file_url": "<real URL>", "extractor_version": "v1.0", "is_demo": "false"}`** — R3-E provenance 真实填充
- 真实 SHA 用 `641-A.1` 抓取的详情页 HTML SHA256 (脚本输出); demo SHA `0…02` 与 640 demo SHA 不混淆
- **真实行 INSERT 到 cegr.policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event** — 首次真实化

**`scripts/seed_m4_4_heilongjiang_real.sql`** 结构:

```sql
-- 641 / M4.4: 黑龙江政策真实化 spike (knife 641)
-- 沿用 docs/33 §3.2 sentinel (lineage JSONB is_demo='false' 真实化)
-- 真实 SHA = 641-A.1 抓取的详情页 SHA256 (calc on fetch)
-- 真实 URL = 641-A.1 抓取的黑龙江 /zwgk/zfwj/ 详情页

BEGIN;

-- 1. 1 个真实 source_registry (黑龙江政府网官方;与既有 registry 行兼容)
INSERT INTO source_registry (
    id, domain, organization, category, primary_url,
    update_frequency, auth_note, access_method,
    historical_coverage, stability_note, failure_handling, enabled
) VALUES (
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'www.hlj.gov.cn',
    '黑龙江省人民政府',
    'government',
    'https://www.hlj.gov.cn/zwgk/zfwj/',
    'daily',
    'official government site; no auth required',
    'HTTP_CURL',
    '2024 policy docs',
    'site stable; 640 probe REACHABLE 2/12 = 1 province only',
    'retry 3x; WAF 网防G01 may block subpath',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- 2. 1 个真实 source_document (real SHA = 641-A.1 计算; UNVERIFIED 待人工核验)
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, file_format, file_size_bytes,
    language, extraction_method, caveat_text,
    uploader_id
) VALUES (
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'S1',                                   -- S1 = 政府官方源 (per docs/34 §6 源等级)
    'UNVERIFIED',                           -- 真实化 spike; 待人工核验 (人工裁定门)
    '<real title from 641-A.1>',
    '黑龙江省人民政府',
    '<real publication_date from 641-A.1>',
    '<real detail URL from 641-A.1>',
    '<real SHA256 from 641-A.1>',           -- 真实 SHA (calc on fetch)
    'html',
    <real file_size>,
    'zh',
    'HTTP_CURL',
    'first real policy document from 黑龙江 /zwgk/zfwj/; lineage.is_demo=false',
    'm4_4_heilongjiang_real'
) ON CONFLICT (id) DO NOTHING;

-- 3. 1 个真实 policy_document (lineage.is_demo='false')
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES (
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'NOTICE',
    '<real title>', '黑龙江省人民政府', '<real date>',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'NOTICE', 'PROVINCIAL',
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "<real SHA>",
       "source_file_url": "<real URL>",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- 4. 1 个真实 policy_target (FK → 真实 policy_document)
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES (
    'c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
    '<real target_description>',
    <real target_value>, '<real unit>', <real target_year>, TRUE,
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "<real SHA>",
       "source_file_url": "<real URL>",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- 5. 1 个真实 policy_measure (FK → 真实 policy_document)
INSERT INTO policy_measure (...) VALUES (...);

-- 6. 1 个真实 government_commitment
--    (FK → 真实 policy_target + 真实 geo_entity (黑龙江) + source_document)
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
) VALUES (
    'c4eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
    'c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
    '<real commitment_text>', NULL,
    -- 黑龙江省 真实 geo_entity_id: 见 641-A.2 注释 (从 M2-a seed_m2_province_geo.py 黑龙江行获取)
    '<heilongjiang real geo_entity_id>',
    '<real commitment_date>',
    '<real due_date>', 'PROPOSED',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "<real SHA>",
       "source_file_url": "<real URL>",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- 7. 1 个真实 commitment_progress (FK → 真实 government_commitment)
INSERT INTO commitment_progress (...) VALUES (...);

-- 8. 1 个真实 project_event (FK → 真实 geo_entity 黑龙江)
INSERT INTO project_event (...) VALUES (...);
```

**黑龙江 geo_entity_id 获取策略**:
- M2-a `seed_m2_province_geo.py` 已 INSERT 30 省 geo_entity (黑龙江 row code "23" / canonical_name "黑龙江省")
- 但其 UUID 由 `uuid_generate_v4()` 生成,无法预测
- **方案 A**: 在 seed_m4_4_heilongjiang_real.sql 加 `SELECT id FROM geo_entity WHERE canonical_name = '黑龙江省' AND level = 'PROVINCIAL'` 子查询,获取真实 UUID 后 INSERT government_commitment / project_event
- **方案 B**: 复用 640 demo province 1-3 不合规 (640 demo 是 synthetic 不绑定真实省)
- **架构师裁**: **方案 A** (SELECT 子查询);保证真实化 spike 与 M2-a seed 兼容,不引入新 synthetic geo_entity

**lineage 隔离原则 (与 640 demo 共存)**:
- 6 政策表 × 1 真实 each 显式 `lineage->>'is_demo' = 'false'` (sentinel)
- 与 640 demo 共存 (640 demo `is_demo='true'`);应用层 SELECT 必须根据业务需求决定是否过滤 demo
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'` 或 NULL (production pattern)

**read-only 红线**:
- ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
- ❌ 不修改既有 registry 行 / mart_*.sql / 4 frontend fixture
- ❌ 不静默硬编码 GDP 值 (target_value 等从 641-A.1 抓取,如抓无则 NULL)
- ❌ demo ≤ 1 条 each 政策表 (1 真实 spike 边界,不重复 640 demo 3 行)
- ❌ 不宣称 Gate / O1 / M2 / M4 PASS
- ❌ 不爬网 (641-A.1 ≤4 次 HTTP)
- ❌ 不复现 639 6 REACHABLE 任免源 / 不复现 640 5 BLOCKED 政策源 (单省收口)
- ❌ 不新写 016 migration (沿用 009+010 lineage JSONB)
- ✓ 首次真实化 cegr.policy_document / policy_target / policy_measure /
    government_commitment / commitment_progress / project_event 真实行
- ✓ 真实 SHA ≠ 640 demo SHA `0…02`
- ✓ 真实 URL 来自黑龙江 /zwgk/zfwj/ (gov.cn 政府源; 非商业库)

### 641-A.3 docs/61 架构师级审查文档

6 段结构（类比 docs/58 / docs/59 / docs/60）：

```markdown
# 61 — M4.4 黑龙江政策真实化 spike（2026-09-01，knife 641）

> 类型: 架构师级审查文档
> 依据: docs/60 §5 (架构师推荐 641 = M4.4 黑龙江政策真实化 spike)
> 关键裁定: 沿用 docs/33 §3.2 sentinel (lineage JSONB is_demo='false');不新写 016 migration
> 不宣布 Gate / O1 / M2 / M4 PASS。
> 架构师裁定: <根据 641-A.1 真实抓取结果给出 642 推荐>

## 1. M4.4 落地终态
   5 sub-knife 状态表 + M4.4 收口结论 (首次真实化 spike)

## 2. 黑龙江真实抓取数据（基于 641-A.1）
   总抓取: ≤3 条真实政策样本
   REACHABLE 1: 黑龙江 /zwgk/zfwj/ (640 二次 probe 已证实)
   真实 SHA256 计算
   与 638/639/640 政策 demo 数据对比

## 3. 真实化 demo SQL 结构（基于 641-A.2）
   1 source_registry 真实 (黑龙江政府网) +
   1 source_document 真实 (real SHA, real URL) +
   6 政策表 × 1 真实样本 each
   lineage JSONB is_demo='false' 真实化 sentinel
   真实 SHA ≠ 640 demo SHA 0…02

## 4. lineage 真实化 sentinel（基于 009+010 lineage 复用）
   6 政策表 lineage JSONB 加列已完成 (009 + 010)
   R3-E provenance 真实生成 (chain_id='real_641_heilongjiang')
   不新写 016 migration 架构师裁定 (与 640 同)

## 5. 642 下一步
   642 = M5 WAF spike (推荐; 解决 5 BLOCKED 省根因)
   642 = M4.5 任免真实化 (调整; 复用 639 6 REACHABLE 任免源)
   642 = M5 + M4.5 并行 (架构师推荐; spike 不互斥)

## 6. 下一步 (642 = M5 WAF spike 推荐)
```

### 641-A.5 真实抓取报告

类比 639 `docs/reports/m4_2_renmian_v2_probe_20260901.md` 模板,但标记为"真实化 spike"(非 probe)。

### 641-A.6 EXEC-QUEUE rev67

`cc_head: a644e47 (640 receipt) + TBD (641)`；§NOW = 641 tasking；§CHAIN_TAIL 增 641 row。

---

## 3. 641-B 测试

**目标文件**：`tests/test_m4_4_heilongjiang_real.py` ≥ 6 用例：

1. `test_heilongjiang_real_fetch_report_exists_and_has_top_verdict` — 真实抓取报告存在 + 顶层裁定 (REAL_FETCHED)
2. `test_heilongjiang_real_evidence_json_parses` — evidence JSON parses + fetched_count ≥ 1 + 真实 SHA 64 hex chars
3. `test_seed_m4_4_sql_exists_and_has_real_data` — `scripts/seed_m4_4_heilongjiang_real.sql` 存在 + 6 表 × 1 真实 each
4. `test_seed_m4_4_sql_lineage_is_demo_false_isolation` — 6 政策表每行 lineage JSONB `is_demo='false'`;不含 `is_demo='true'`;与 640 demo 共存
5. `test_seed_m4_4_sql_real_sha_distinct_from_demo_sha` — 真实 SHA (64 char hex from 641-A.1) ≠ 640 demo SHA `0…02`
6. `test_doc_61_has_six_sections` + `test_doc_61_no_pass_announcement` — docs/61 段存在 + 不宣称 PASS

**全套 pytest**（M2 + 637 + 638 + 639 + 640 + 641）：71 + 6 = ≥ 77 用例 green (实际 count 由 pytest 报告为准)。

---

## 4. 红线（继承 + 641 增量）

| 红线 | 来源 | 状态 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | 继承 | ✓ 测试 + docs/61 disclaimer |
| 不让用户裁定 URL/年份 | 数据源治理铁律 | ✓ 抓取 URL 自取政府源 |
| 数据源唯一=政府/统计/研究机构 | 继承 | ✓ 抓取 URL = www.hlj.gov.cn |
| 不爬网 | 继承 | ✓ 641-A.1 ≤4 次 HTTP (硬性上限) |
| 不删表 / 不 DROP COLUMN | 继承 | ✓ seed SQL 仅 INSERT |
| 不静默硬编码 GDP 值 | 继承 | ✓ target_value 等从抓取;无则 NULL |
| 湖北必须 ≠ M1 半年表 c5cf5abe | 继承 | ✓ 641 不写湖北具体 observation |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | 640 架构裁定 | ✓ 641-A.2 不写 016 |
| 真实化 spike 边界 ≤1 each 政策表 | 641 新增 | ✓ test_seed_m4_4_sql_exists_and_has_real_data 验证 |
| lineage.is_demo='false' 真实化 sentinel | 641 新增 | ✓ test_seed_m4_4_sql_lineage_is_demo_false_isolation 验证 |
| 真实 SHA ≠ 640 demo SHA `0…02` | 641 新增 | ✓ test_seed_m4_4_sql_real_sha_distinct_from_demo_sha 验证 |
| 单省收口 (黑龙江唯一 REACHABLE) | 641 新增 | ✓ 抓取仅 www.hlj.gov.cn |
| 不复现 639 6 REACHABLE 任免源 | 641 新增 | ✓ 真实化范围限定 1 省 |
| 不复现 640 5 BLOCKED 政策源 | 641 新增 | ✓ 真实化范围限定 1 省 |
| 真实 URL 来自黑龙江 /zwgk/zfwj/ | 641 新增 | ✓ 抓取 source 字段 |
| R3-E provenance chain_id 非 demo_* | 641 新增 | ✓ chain_id='real_641_heilongjiang' |
| 双推 origin→github | 继承 | ✓ §5 commit + origin → github |

---

## 5. commit + 双推

### 641-A + 641-B commit 1 (delivery)

```bash
git add scripts/fetch_heilongjiang_policy_v1_2024.py \
        scripts/seed_m4_4_heilongjiang_real.sql \
        docs/61-m4-4-heilongjiang-real-20260901.md \
        docs/reports/m4_4_heilongjiang_real_20260901.md \
        evidence_pack/m4_4_heilongjiang_real_20260901.json \
        tests/test_m4_4_heilongjiang_real.py

git commit -m "feat(641): M4.4 黑龙江政策真实化 spike — 真实抓取 + 1 real each × 6 政策表 lineage.is_demo='false'"

git push origin HEAD
git push github HEAD
```

### 641-C commit 2 (cc_head backfill)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(641): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 641-C commit 3 (receipt)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/641-stage0-cc-m4-4-heilongjiang-real-receipt-20260901.md
git commit -m "docs(641): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 6. 完成后态

- EXEC-QUEUE rev68: 641 DELIVERED · 等用户接受 642 scope 推荐
- 测试：≥ 77 用例 green
- 双推：origin + github 三 commit 全部同步
- 641 内部审计 AUDITED
- 不宣布 Gate / O1 / M2 / M4 PASS
- 用户下一步：
  - 接受 641 推荐 → 642 = M5 WAF spike（解决 5 BLOCKED 省根因; WAF 网防G01 假设进一步验证）
  - 接受 641 推荐 → 642 = M4.5 任免真实化（复用 639 6 REACHABLE 任免源;1 spike 不互斥）
  - 接受 641 推荐 → 642 = M5 + M4.5 并行（架构师推荐; spike 不互斥）
  - 驳回 → 用户裁定 642 re-scope 或 643+

— End 641 tasking —