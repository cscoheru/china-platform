# 639 — M4.2 任免数据 demo（架构师 tasking）

> **刀号**: 639
> **Milestone**: M4.2（人物政策子刀2/4）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**:
> - `docs/58-m4-1-people-schema-gov-report-probe-20260901.md` §5 M4.2 推荐 scope
> - 638 receipt §8 (用户裁定: "接收639 scope")
> - 015 migration (`person.is_demo` / `appointment_event.is_demo` 加性)
> - 636 / 638 probe 方法学继承
> **前置**: 638 DELIVERED (cc_head `f1fdad5`, commit chain `f57712f → ee86977`)
> **用户接收**：`接收639 scope`（2026-09-01）
> **不宣布** Gate / O1 / M2 / M4 PASS。

---

## 0. 范围（一句话）

639 落地 4 件：**(A1)** 任免公告二次探活（ccdi 公告列表 + npc 新 URL + 国务院任免正确 URL + 23 试点省任免栏目）；**(A2)** `scripts/seed_m4_2_demo.sql` 人物政策 demo 最小实现（≤ 5 条 person + tenure + appointment_event，全部 is_demo=true 隔离，含 source_document 跳回 SHA）；**(A3)** `docs/59-m4-2-renmian-demo-20260901.md` §1-§6 架构师级审查；**(B)** 全套 pytest ≥ 63/63 green + 回执 + 双推。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 639-A.1 | `scripts/probe_renmian_v2_2024.py` | DONE | 任免公告二次探活：ccdi 公告列表 (1-2 URL) + npc 新 URL (HTTPS) + 国务院任免正确 URL + 23 试点省任免栏目 (`/zwgk/` 类) |
| 639-A.2 | `scripts/seed_m4_2_demo.sql` | DONE | 人物政策 demo ≤ 5 条 person + ≤ 5 条 tenure + ≤ 5 条 appointment_event + 1 条 source_document，全部 is_demo=true；可对 ops 测试 DB 一跳回 SHA |
| 639-A.3 | `docs/59-m4-2-renmian-demo-20260901.md` | DONE | §1-§6：M4.2 落地终态 / 任免二次 probe 数据 / demo SQL 结构 / 015 schema 落地 / M4.3 下一步 / 不宣称 PASS |
| 639-A.5 | `docs/reports/m4_2_renmian_v2_probe_20260901.md` + `evidence_pack/m4_2_renmian_v2_probe_20260901.json` | DONE | 二次 probe 报告 + 证据包 |
| 639-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev62 → rev63：638 DELIVERED → 639 tasking / in_progress |
| 639-B | `tests/test_m4_2_renmian_demo.py` | DONE | ≥ 6 用例：二次 probe 报告 / JSON parses / seed SQL ≤ 5 demo / seed is_demo=true 隔离 / demo 有 source_document_id / docs/59 六段 / docs/59 不宣称 PASS |
| 639-C | 回执 + commit + 双推 | DONE | `reviews/stage0-gate0-rework-2026-08-23/639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 639-A 详细

### 639-A.1 任免公告二次探活

**638 发现 + 639 二次探新目标：**

```python
RENMIAN_V2_TARGETS = [
    # ccdi 公告列表页（638 PARTIAL 是首页;639 探公告列表栏目）
    ("central-discipline-yaowen", "中央纪委要闻", "https://www.ccdi.gov.cn/yaowen/"),
    # ccdi 审查调查栏目（含部分任免）
    ("central-discipline-shenji", "中央纪委审查调查", "https://www.ccdi.gov.cn/specialn/scjcf/"),

    # 全国人大 npc 新 URL（HTTPS + 任免栏目）
    ("npc-renmian", "全国人大任免", "https://npc.gov.cn/npc/c2/"),
    ("npc-news", "全国人大要闻", "https://npc.gov.cn/npc/"),

    # 国务院任免正确 URL
    ("central-renmian", "国务院任免", "https://www.gov.cn/zhengce/"),
    ("central-yaowen", "国务院要闻", "https://www.gov.cn/yaowen/"),

    # 23 试点省任免栏目 (继承 638 REACHABLE 23 省)
    ("jiangsu-renmian", "江苏任免", "https://www.jiangsu.gov.cn/zwgk/"),
    ("guangdong-renmian", "广东任免", "https://www.gd.gov.cn/zwgk/"),
    ("zhejiang-renmian", "浙江任免", "https://www.zj.gov.cn/zwgk/"),
    ("shandong-renmian", "山东任免", "https://www.shandong.gov.cn/zwgk/"),
    ("sichuan-renmian", "四川任免", "https://www.sc.gov.cn/zwgk/"),
    ("shanghai-renmian", "上海任免", "https://www.shanghai.gov.cn/zwgk/"),
    ("beijing-renmian", "北京任免", "https://www.beijing.gov.cn/zwgk/"),
    # 24 省任免栏目（继承 638 REACHABLE 23 省中除湖北外的,湖北 BLOCKED 不探）
    # ... 试点 + 其余 16 省
]
```

**关键约束：**
- 继承 `_probe_http_helpers.fetch() / classify_people_probe` (RENMIAN_MARKER_RE)
- 复用 probe result schema (slug / entity / year / source / url / verdict / http_code / reason / probed_at)
- 不爬网（仅探可达性，不抓内容入库）
- 不写 cegr.observation

### 639-A.2 人物政策 demo SQL

**`scripts/seed_m4_2_demo.sql` 结构：**

```sql
-- 639 / M4.2: 人物政策 demo seed
-- 全部 is_demo=true 隔离;不写真实数据;≤5 条 person/tenure/appointment_event

BEGIN;

-- 1. 单一 source_document (synthetic, 用于 demo 一跳回 SHA)
INSERT INTO source_document (
    id, file_hash_sha256, source_url, title,
    publisher, doc_kind, language, uploader_id,
    file_format, is_demo
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    '0000000000000000000000000000000000000000000000000000000000000001',  -- demo SHA
    'https://www.gov.cn/zhengce/',  -- 639-A.1 国务院任免 URL
    'M4.2 demo placeholder',
    'demo',
    'NORMAL',
    'zh',
    'm4_2_demo',
    'sql',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- 2. 5 个 demo position (synthetic)
INSERT INTO position (id, title, level, is_key, is_demo)
VALUES
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'demo-position-1', 'central', 'f', TRUE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'demo-position-2', 'central', 'f', TRUE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'demo-position-3', 'central', 'f', TRUE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'demo-position-4', 'central', 'f', TRUE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'demo-position-5', 'central', 'f', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 3. 5 个 demo person (全部 is_demo=true)
INSERT INTO person (id, canonical_name, is_demo, last_verified_at)
VALUES
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'demo-person-1', TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'demo-person-2', TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'demo-person-3', TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'demo-person-4', TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'demo-person-5', TRUE, NOW())
ON CONFLICT (id) DO NOTHING;

-- 4. 5 个 demo tenure (全部 is_demo=true;FK 关联 person + position + source_document)
INSERT INTO tenure (id, person_id, position_id, start_date, end_date, source_id, is_demo)
VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
     '2024-01-01', NULL,
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    -- ... 4 more
ON CONFLICT (id) DO NOTHING;

-- 5. 5 个 demo appointment_event (全部 is_demo=true;含 document_url)
INSERT INTO appointment_event (id, tenure_id, event_type, event_date, document_url, source_id, is_demo)
VALUES
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'appointment', '2024-01-01',
     'https://www.gov.cn/zhengce/',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    -- ... 4 more
ON CONFLICT (id) DO NOTHING;

COMMIT;
```

**is_demo 隔离原则**：
- 全部 5 person + 5 tenure + 5 appointment_event + 5 position + 1 source_document 显式 `is_demo=true`
- demo 数据**只能** SELECT 通过 `WHERE is_demo=true` 过滤（应用层 + 测试层）
- 真实数据 INSERT 必须 `is_demo=false` + `source_id NOT NULL`（016+ 引入 CHECK 约束）

**read-only 红线：**
- 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
- 不修改 source_registry / mart / 4 fixture
- 不写 cegr.observation 真实行
- 不静默硬编码 GDP 值（demo 表无 GDP）
- demo 数据 ≤ 5 条（避免镀铬）
- 不宣称 Gate / O1 / M2 / M4 PASS

### 639-A.3 docs/59 架构师级审查文档

6 段结构（类比 docs/58）：

```markdown
# 59 — M4.2 任免数据 demo（2026-09-01，knife 639）

> 类型: 架构师级审查文档
> 依据: docs/58 §5 + 638 receipt §8 (用户接收 639 scope)
> 不宣布 Gate / O1 / M2 / M4 PASS。
> 架构师裁定: <根据 639-A.1 二次 probe 结果给出 M4.3 推荐>

## 1. M4.2 落地终态
   639-A.1/A.2/A.3 三 sub-knife 状态表 + M4.2 收口结论

## 2. 任免公告二次 probe 数据（基于 639-A.1）
   总分布: REACHABLE X / PARTIAL Y / BLOCKED Z
   试点省 + ccdi/npc/国务院 verdict
   与 638 PARTIAL 1 / BLOCKED 2 对比

## 3. demo 表 SQL 结构（基于 639-A.2）
   source_document (1 条 demo) + position (5 条 demo) + person (5 条 demo) +
   tenure (5 条 demo) + appointment_event (5 条 demo)
   is_demo=true 隔离原则

## 4. 015 schema 落地（基于 638-A.3）
   person.is_demo / appointment_event.is_demo 加性验证
   016+ backfill 既有 NULL 行

## 5. M4.3 下一步
   M4.3 政策项目 demo: 依 639 demo 验证启动
   is_demo=true 模式复用

## 6. 下一步 (640 = M4.3)
```

### 639-A.5 二次 probe 报告

类比 638 `docs/reports/m4_1_renmian_probe_20260901.md` 模板。

### 639-A.6 EXEC-QUEUE rev63

`cc_head: ee86977 (638) + TBD (639)`；§NOW = 639 tasking；§CHAIN_TAIL 增 639 row。

---

## 3. 639-B 测试

**目标文件**：`tests/test_m4_2_renmian_demo.py` ≥ 6 用例：

1. `test_renmian_v2_probe_report_exists_and_has_top_verdict` — 二次 probe 报告存在 + 顶层裁定
2. `test_renmian_v2_evidence_json_parses` — evidence JSON parses + probed_count ≥ 1
3. `test_seed_m4_2_sql_exists_and_has_demo_data` — `scripts/seed_m4_2_demo.sql` 存在 + 5 demo person rows
4. `test_seed_m4_2_sql_is_demo_isolation` — 所有 demo INSERT 必须 `is_demo=true`
5. `test_seed_m4_2_sql_has_source_document_back_link` — demo 至少 1 条 source_document + 跳回 SHA
6. `test_doc_59_has_six_sections` + `test_doc_59_no_pass_announcement` — docs/59 段存在 + 不宣称 PASS

**全套 pytest**（M2 + 637 + 638 + 639）：49 + 8 + 6 = ≥ 63 用例 green。

---

## 4. 红线（继承 + 639 增量）

| 红线 | 来源 | 状态 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | 继承 | ✓ 测试 + docs/59 disclaimer |
| 不让用户裁定 URL/年份 | 数据源治理铁律 | ✓ probe targets 自取政府源 |
| 数据源唯一=政府/统计/研究机构 | 继承 | ✓ probe targets 全部 gov.cn |
| 不爬网 | 继承 | ✓ 二次 probe 只探可达性 |
| 不写 cegr.observation 真实行 | 639 | ✓ demo is_demo=true 隔离 |
| demo 数据 is_demo=true 显式隔离 | 639 新增 | ✓ test_seed_m4_2_sql_is_demo_isolation 验证 |
| demo ≤ 5 条 person/tenure/appointment_event | 639 新增 | ✓ test_seed_m4_2_sql_exists_and_has_demo_data 验证 |
| 不删表 / 不 DROP COLUMN | 继承 | ✓ seed SQL 仅 INSERT |
| demo 有 source_document_id 跳回 SHA | 639 新增 | ✓ test_seed_m4_2_sql_has_source_document_back_link 验证 |
| 不静默硬编码 GDP 值 | 继承 | ✓ test 验证 |
| 湖北必须 ≠ M1 半年表 c5cf5abe | 继承 | ✓ 639 不写湖北具体 observation |
| probe 脚本幂等 | 继承 | ✓ no time.sleep / no random in classify |
| 双推 origin→github | 继承 | ✓ §5 commit + origin → github |

---

## 5. commit + 双推

### 639-A + 639-B commit 1 (delivery)

```bash
git add scripts/probe_renmian_v2_2024.py \
        scripts/seed_m4_2_demo.sql \
        docs/59-m4-2-renmian-demo-20260901.md \
        docs/reports/m4_2_renmian_v2_probe_20260901.md \
        evidence_pack/m4_2_renmian_v2_probe_20260901.json \
        tests/test_m4_2_renmian_demo.py \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md

git commit -m "feat(639): M4.2 任免数据 demo — 二次 probe + 5 demo person/tenure/appointment_event is_demo=true 隔离"

git push origin HEAD
git push github HEAD
```

### 639-C commit 2 (cc_head backfill)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(639): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 639-C commit 3 (receipt)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md
git commit -m "docs(639): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 6. 完成后态

- EXEC-QUEUE rev64: 639 DELIVERED · 等用户接受 M4.3 scope 推荐
- 测试：≥ 63 用例 green
- 双推：origin + github 三 commit 全部同步
- 639 内部审计 AUDITED
- 不宣布 Gate / O1 / M2 / M4 PASS
- 用户下一步：
  - 接受 639 推荐 → 640 = M4.3 政策项目 demo（依 639 demo 验证）
  - 驳回 → 用户裁定 640 re-scope 或 641 (M5.1 spike)

— End 639 tasking —