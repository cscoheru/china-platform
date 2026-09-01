# 640 — M4.3 政策项目 demo（架构师 tasking）

> **刀号**: 640
> **Milestone**: M4.3（政策项目子刀 3/4）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**:
> - `docs/59-m4-2-renmian-demo-20260901.md` §5 (M4.3 推荐 scope)
> - 639 receipt §8 (用户裁定: "接受 640 = M4.3 政策项目 demo")
> - `docs/33 §3.2 sentinel` (lineage JSONB 是 is_demo 唯一落点;非 015 模式)
> - 009 + 010 migration (policy_document / policy_target / policy_measure /
>   government_commitment / commitment_progress / project_event 已有 lineage JSONB)
> - 638 / 639 probe 方法学继承
> **前置**: 639 DELIVERED (cc_head `1fca08e` + receipt `11778db`)
> **用户接收**：`接受 640 = M4.3 政策项目 demo，签 640 tasking`（2026-09-01）
> **不宣布** Gate / O1 / M2 / M4 PASS。

---

## 0. 范围（一句话）

640 落地 5 件：**(A1)** 政策源二次探活（6 REACHABLE 试点省 `/zwgk/zfwj/` `/zwgk/zfgb/` `/zwgk/ghjh/` 政策承载路径 + ccdi/npc/国务院 政策栏目）；**(A2)** `scripts/seed_m4_3_policy_demo.sql` 政策项目 demo 最小实现（≤3 条 policy_document + ≤3 条 policy_target + ≤3 条 policy_measure + ≤3 条 government_commitment + ≤3 条 commitment_progress + ≤3 条 project_event，**全部用 lineage JSONB sentinel 隔离 `is_demo='true'`**——非 015 独立 BOOLEAN 列模式；demo SHA `0…02` 与 639 SHA `0…01` 区分）；**(A3)** `docs/60-m4-3-policy-demo-20260901.md` §1-§6 架构师级审查；**(B)** `tests/test_m4_3_policy_demo.py` ≥ 6 用例；**全套 pytest ≥ 70/70 green**；**(C)** 回执 + commit + 双推；**架构师推荐 641 = M4.4 任免 demo 真实化或 spike**。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 640-A.1 | `scripts/probe_policy_v1_2024.py` | DONE | 政策源二次探活：6 REACHABLE 试点省 `/zwgk/zfwj/` `/zwgk/zfgb/` `/zwgk/ghjh/` + ccdi `/specialn/` + 国务院 `/zhengce/` (政策); 不复用 639 任免数据 |
| 640-A.2 | `scripts/seed_m4_3_policy_demo.sql` | DONE | 政策 demo: 3 policy_document + 3 policy_target + 3 policy_measure + 3 government_commitment + 3 commitment_progress + 3 project_event; 全部 lineage JSONB `is_demo='true'` 隔离; demo SHA `0…02` 与 639 `0…01` 区分 |
| 640-A.3 | `docs/60-m4-3-policy-demo-20260901.md` | DONE | §1-§6：M4.3 落地终态 / 政策二次 probe 数据 / demo SQL 结构 / 009+010 lineage 复用 / 641 下一步 / 不宣称 PASS |
| 640-A.5 | `docs/reports/m4_3_policy_v1_probe_20260901.md` + `evidence_pack/m4_3_policy_v1_probe_20260901.json` | DONE | 政策 probe 报告 + 证据包 |
| 640-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev64 → rev65：639 DELIVERED → 640 tasking / in_progress |
| 640-B | `tests/test_m4_3_policy_demo.py` | DONE | ≥ 6 用例：政策 probe 报告 / JSON parses / seed SQL ≤3 demo each / seed lineage is_demo 隔离 / seed demo SHA `0…02` 区分 / docs/60 六段 / docs/60 不宣称 PASS |
| 640-C | 回执 + commit + 双推 | DONE | `reviews/stage0-gate0-rework-2026-08-23/640-stage0-cc-m4-3-policy-demo-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 640-A 详细

### 640-A.1 政策源二次探活

**639 发现 + 640 二次探新目标**（继承 638/639 路径选择性 WAF 假设修正）：

```python
POLICY_V1_TARGETS = [
    # 6 REACHABLE 试点省政策承载路径 (继承 639 任免 REACHABLE 6)
    ("heilongjiang-policy", "黑龙江政策文件", "https://www.hlj.gov.cn/zwgk/zfwj/"),
    ("heilongjiang-policy-gb", "黑龙江政府公报", "https://www.hlj.gov.cn/zwgk/zfgb/"),
    ("fujian-policy", "福建政策文件", "https://www.fujian.gov.cn/zwgk/zfwj/"),
    ("fujian-policy-gb", "福建政府公报", "https://www.fujian.gov.cn/zwgk/zfgb/"),
    ("henan-policy", "河南政策文件", "https://www.henan.gov.cn/zwgk/zfwj/"),
    ("henan-policy-ghjh", "河南规划计划", "https://www.henan.gov.cn/zwgk/ghjh/"),
    ("guangdong-policy", "广东政策文件", "https://www.gd.gov.cn/zwgk/zfwj/"),
    ("guangdong-policy-gb", "广东政府公报", "https://www.gd.gov.cn/zwgk/zfgb/"),
    ("guizhou-policy", "贵州政策文件", "https://www.guizhou.gov.cn/zwgk/zfwj/"),
    ("yunnan-policy", "云南政策文件", "https://www.yn.gov.cn/zwgk/zfwj/"),

    # ccdi 政策栏目 (639 PARTIAL;640 试 政策/法规 栏目)
    ("central-discipline-zhidu", "中央纪委制度", "https://www.ccdi.gov.cn/ldwd/"),

    # 国务院政策栏目 (639 PARTIAL zhengce;640 加试 内容/法规 子栏目)
    ("central-zhengce-zd", "国务院制度", "https://www.gov.cn/zhengce/zhengceku/"),
    ("central-zhengce-qt", "国务院其他", "https://www.gov.cn/zhengce/qt/"),
]
```

**关键约束**：
- 继承 `_probe_http_helpers.fetch() / classify_people_probe` (新建 POLICY_MARKER_RE: 政策文件|政府公报|规划计划|policy|regulation|五年规划 marker)
- 复用 probe result schema (slug / entity / year / source / url / verdict / http_code / reason / probed_at)
- 不爬网（仅探可达性，不抓内容入库）
- 不写 cegr.observation
- **不复用 639 任免数据** —— docs/59 §5.1 明确指出"6 REACHABLE 任免源 ≠ 政策源"

### 640-A.2 政策项目 demo SQL

**架构师裁定（关键）**：
- **沿用 docs/33 §3.2 sentinel**：lineage JSONB 是 is_demo 唯一落点，**不新写 016 migration 加独立 is_demo BOOLEAN 列**
- 009 + 010 已在 policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event 六表加 `lineage JSONB`
- demo 数据写 `lineage = {"chain_id": "demo_640", "source_file_sha256": "0…02", "source_file_url": "https://demo.placeholder/m4_3", "extractor_version": "demo_v1", "is_demo": "true"}`
- demo SHA `0…02` 与 639 SHA `0…01` 区分（避免 demo 污染）

**`scripts/seed_m4_3_policy_demo.sql` 结构**：

```sql
-- 640 / M4.3: 政策项目 demo seed
-- 全部 lineage->>'is_demo' = 'true' 隔离 (docs/33 §3.2 sentinel)
-- demo SHA 0…02 与 639 SHA 0…01 区分
-- ≤3 条 each table (6 表 × 3 = 18 demo 行, 较 639 20 行略少)

BEGIN;

-- 1. 1 个 demo source_registry (synthetic;不修改既有 registry 行)
INSERT INTO source_registry (...) VALUES (
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'demo.placeholder',
    'M4.3 demo (synthetic)',
    'demo',
    'https://demo.placeholder/m4_3',
    ...
);

-- 2. 1 个 demo source_document (deterministic SHA 0…02)
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, ...
) VALUES (
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'S4',
    'UNVERIFIED',
    'M4.3 demo placeholder document',
    ...
    '0000000000000000000000000000000000000000000000000000000000000002',  -- demo SHA 0…02
    ...
);

-- 3. 3 个 demo policy_document (lineage.is_demo='true')
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, lineage
) VALUES
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'REGULATION',
     'demo-policy-document-1', 'M4.3 demo (synthetic)', '2024-01-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0…02",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'),
    -- ... 2 more demo policy_document
ON CONFLICT (id) DO NOTHING;

-- 4. 3 个 demo policy_target (FK → 上 3 条 demo policy_document)
INSERT INTO policy_target (
    id, policy_document_id, target_description, target_value,
    source_location_id
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
     'demo-policy-target-1', 1.0, NULL),
    -- ... 2 more
ON CONFLICT (id) DO NOTHING;

-- 5. 3 个 demo policy_measure (FK → 上 3 条 demo policy_document)
INSERT INTO policy_measure (...) VALUES ...;

-- 6. 3 个 demo government_commitment (FK → policy_target + geo_entity)
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    source_id, lineage  -- demo lineage JSONB
) VALUES ...;

-- 7. 3 个 demo commitment_progress (FK → government_commitment)
INSERT INTO commitment_progress (
    id, commitment_id, progress_date, progress_value,
    source_id
) VALUES ...;

-- 8. 3 个 demo project_event (FK → geo_entity)
INSERT INTO project_event (
    id, project_name, geo_entity_id, status, event_date,
    source_id, lineage  -- demo lineage JSONB
) VALUES ...;

COMMIT;
```

**lineage 隔离原则**：
- 全部 demo `policy_document` / `government_commitment` / `project_event` 行显式 `lineage->>'is_demo' = 'true'` (sentinel)
- demo 数据**只能** SELECT 通过 `WHERE lineage->>'is_demo' = 'true'` 过滤 (应用层 + 测试层)
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'` 或 NULL (009+010 已存在索引 `idx_*_lineage_gin`)
- demo SHA `0…02` 与 639 SHA `0…01` 区分（一跳回 SHA 时不混淆）

**read-only 红线**：
- ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
- ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
- ❌ 不写 cegr.observation 真实行
- ❌ 不静默硬编码 GDP 值（demo 表无 GDP 字段；target_value 等纯 demo 数值）
- ❌ demo ≤ 3 条 each table
- ❌ 不宣称 Gate / O1 / M2 / M4 PASS
- ✓ 沿用 009+010 lineage JSONB (不新写 016 migration)

### 640-A.3 docs/60 架构师级审查文档

6 段结构（类比 docs/58 / docs/59）：

```markdown
# 60 — M4.3 政策项目 demo（2026-09-01，knife 640）

> 类型: 架构师级审查文档
> 依据: docs/59 §5 + 639 receipt §8 (用户接收 640 scope)
> 关键裁定: 沿用 docs/33 §3.2 sentinel (lineage JSONB is_demo);不新写 016 migration
> 不宣布 Gate / O1 / M2 / M4 PASS。
> 架构师裁定: <根据 640-A.1 二次 probe 结果给出 641 推荐>

## 1. M4.3 落地终态
   5 sub-knife 状态表 + M4.3 收口结论

## 2. 政策源 二次 probe 数据（基于 640-A.1）
   总分布: REACHABLE X / PARTIAL Y / BLOCKED Z
   6 REACHABLE 试点省政策承载路径 verdict
   与 639 任免二次 probe 对比

## 3. demo SQL 结构（基于 640-A.2）
   1 source_registry + 1 source_document (demo SHA 0…02) +
   3 policy_document + 3 policy_target + 3 policy_measure +
   3 government_commitment + 3 commitment_progress +
   3 project_event
   lineage JSONB is_demo='true' 隔离原则 (docs/33 §3.2 sentinel)

## 4. 009+010 schema 落地（基于 638-A.3 lineage 复用）
   6 政策表 lineage JSONB 加列已完成 (009 + 010)
   demo SHA 0…02 与任免 SHA 0…01 区分

## 5. 641 下一步
   641 = M4.4 任免 demo 真实化 (从 6 REACHABLE 试点省选 1-2 省试抓)
   或 641 = M5 spike (e.g. WAF 进一步探活 / 政策 demo 真实化)

## 6. 下一步 (641 = M4.4 或 M5 spike)
```

### 640-A.5 二次 probe 报告

类比 639 `docs/reports/m4_2_renmian_v2_probe_20260901.md` 模板。

### 640-A.6 EXEC-QUEUE rev65

`cc_head: 11778db (639) + TBD (640)`；§NOW = 640 tasking；§CHAIN_TAIL 增 640 row。

---

## 3. 640-B 测试

**目标文件**：`tests/test_m4_3_policy_demo.py` ≥ 6 用例：

1. `test_policy_v1_probe_report_exists_and_has_top_verdict` — 政策 probe 报告存在 + 顶层裁定
2. `test_policy_v1_evidence_json_parses` — evidence JSON parses + probed_count ≥ 1 + 试点省 REACHABLE ≥ 1
3. `test_seed_m4_3_sql_exists_and_has_demo_data` — `scripts/seed_m4_3_policy_demo.sql` 存在 + 3 demo each table (policy_document × 3 + policy_target × 3 + policy_measure × 3 + government_commitment × 3 + commitment_progress × 3 + project_event × 3)
4. `test_seed_m4_3_sql_lineage_is_demo_isolation` — 所有 demo policy_document / government_commitment / project_event 行 lineage JSONB `is_demo='true'` 隔离;不含 `is_demo='false'`
5. `test_seed_m4_3_sql_demo_sha_distinct_from_renmian` — demo SHA `0…02` 不等于 639 demo SHA `0…01`
6. `test_doc_60_has_six_sections` + `test_doc_60_no_pass_announcement` — docs/60 段存在 + 不宣称 PASS

**全套 pytest**（M2 + 637 + 638 + 639 + 640）：49 + 8 + 8 + 7 + 6 = ≥ 78 用例 green (实际 count 由 pytest 报告为准;估计 70-72 因部分文件案例数差异)。

---

## 4. 红线（继承 + 640 增量）

| 红线 | 来源 | 状态 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | 继承 | ✓ 测试 + docs/60 disclaimer |
| 不让用户裁定 URL/年份 | 数据源治理铁律 | ✓ probe targets 自取政府源 |
| 数据源唯一=政府/统计/研究机构 | 继承 | ✓ probe targets 全部 gov.cn |
| 不爬网 | 继承 | ✓ 二次 probe 只探可达性 |
| 不写 cegr.observation 真实行 | 继承 | ✓ demo lineage.is_demo='true' 隔离 |
| demo 数据 lineage.is_demo='true' 显式隔离 (sentinel) | 640 新增 | ✓ test_seed_m4_3_sql_lineage_is_demo_isolation 验证 |
| demo ≤ 3 条 each table | 640 新增 | ✓ test_seed_m4_3_sql_exists_and_has_demo_data 验证 |
| 不删表 / 不 DROP COLUMN | 继承 | ✓ seed SQL 仅 INSERT |
| demo 有 source_document_id 跳回 SHA 0…02 | 640 新增 | ✓ test_seed_m4_3_sql_demo_sha_distinct_from_renmian 验证 |
| 不静默硬编码 GDP 值 | 继承 | ✓ test 验证 |
| 湖北必须 ≠ M1 半年表 c5cf5abe | 继承 | ✓ 640 不写湖北具体 observation |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | 640 架构裁定 | ✓ 640-A.2 不写 016 |
| demo SHA 0…02 与 639 SHA 0…01 区分 | 640 新增 | ✓ test_seed_m4_3_sql_demo_sha_distinct_from_renmian 验证 |
| probe 脚本幂等 | 继承 | ✓ no time.sleep / no random in classify |
| 双推 origin→github | 继承 | ✓ §5 commit + origin → github |

---

## 5. commit + 双推

### 640-A + 640-B commit 1 (delivery)

```bash
git add scripts/probe_policy_v1_2024.py \
        scripts/seed_m4_3_policy_demo.sql \
        docs/60-m4-3-policy-demo-20260901.md \
        docs/reports/m4_3_policy_v1_probe_20260901.md \
        evidence_pack/m4_3_policy_v1_probe_20260901.json \
        tests/test_m4_3_policy_demo.py \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md

git commit -m "feat(640): M4.3 政策项目 demo — 二次 probe + 3 demo each × 6 tables lineage.is_demo='true' 隔离"

git push origin HEAD
git push github HEAD
```

### 640-C commit 2 (cc_head backfill)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(640): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 640-C commit 3 (receipt)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/640-stage0-cc-m4-3-policy-demo-receipt-20260901.md
git commit -m "docs(640): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 6. 完成后态

- EXEC-QUEUE rev65: 640 DELIVERED · 等用户接受 641 scope 推荐
- 测试：≥ 70 用例 green
- 双推：origin + github 三 commit 全部同步
- 640 内部审计 AUDITED
- 不宣布 Gate / O1 / M2 / M4 PASS
- 用户下一步：
  - 接受 640 推荐 → 641 = M4.4 任免 demo 真实化（6 REACHABLE 试点省选 1-2 省试抓）
  - 接受 640 推荐 → 641 = M5 spike（WAF 进一步探活 / 政策 demo 真实化）
  - 驳回 → 用户裁定 641 re-scope 或 642+

— End 640 tasking —
