# 638 — M4.1 人物表 schema 收口 + 政府工作报告数据可得性 probe（架构师 tasking）

> **刀号**: 638
> **Milestone**: M4.1（人物政策子刀 1/4）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**: 
> - `docs/57-m3-launch-conditions-review-20260901.md` §6 下一步（637 路径 C 接受后启动）
> - `docs/54-milestone-replan-20260830.md` §M4.1 + §5 M4 优先序
> - 636 receipt §PHOTO-1..6（probe 方法学先例：REACHABLE / PARTIAL / BLOCKED / NOT_APPLICABLE / NOT_PROBED）
> **前置**: 637 DELIVERED (cc_head `5d957ef`, commit `27e4434`)；用户已接受路径 C
> **用户接收**：`接收，进入 638`（2026-09-01）
> **不宣布** Gate / O1 / M2 / M4 PASS。

---

## 0. 范围（一句话）

638 落地 3 件：**(A)** 政府工作报告可达性 probe（国务院 + 31 省） + 任免公告可达性 probe（中纪委 + 全国人大 + 国务院）；**(B)** `db/migrations/015-m4-1-people-schema.sql` 人物表 schema 收口（DDL add/alter 字段 + is_demo 隔离保留）；**(C)** `docs/58-m4-1-people-schema-gov-report-probe-20260901.md` 架构师级审查文档 + 全套 pytest ≥ 57/57 green + 回执 + 双推。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 638-A.1 | `scripts/probe_gov_report_2024.py` | DONE | 政府工作报告可达性 probe：1 国务院 + 31 省 = 32 URLs；同 636 方法学（REACHABLE/PARTIAL/BLOCKED/NOT_APPLICABLE/NOT_PROBED） |
| 638-A.2 | `scripts/probe_renmian_announcement_2024.py` | DONE | 任免公告可达性 probe：1 中纪委 + 1 全国人大 + 1 国务院 = 3 URLs；同方法学 |
| 638-A.3 | `db/migrations/015-m4-1-people-schema.sql` | DONE | 人物表 schema 收口：review migrations 001–014 现有 `person` 表；按需 ADD/ALTER 字段；is_demo 隔离保留；只 DDL 不 DML |
| 638-A.4 | `docs/58-m4-1-people-schema-gov-report-probe-20260901.md` | DONE | §1-§6：M4.1 落地终态 / probe 数据 / 任免 probe 数据 / schema 收口 / M4.2-M4.3 下一步 / 不宣称 PASS |
| 638-A.6 | `docs/reports/m4_1_gov_report_probe_20260901.md` + `evidence_pack/m4_1_gov_report_probe_20260901.json` | DONE | probe 报告 + 证据包（类比 636 输出） |
| 638-A.7 | `docs/reports/m4_1_renmian_probe_20260901.md` + `evidence_pack/m4_1_renmian_probe_20260901.json` | DONE | probe 报告 + 证据包 |
| 638-A.8 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev60 → rev61：637 DELIVERED → 638 tasking / in_progress |
| 638-B | `tests/test_m4_1_people_probe.py` | DONE | ≥ 8 用例：probe 报告存在 / evidence JSON parses / probe 不写 DB / probe 不静默硬编码 GDP / probe 脚本幂等 / migration 安全（无数据 drop）/ docs/58 六段 / docs/58 不宣称 PASS |
| 638-C | 回执 + commit + 双推 | DONE | `reviews/stage0-gate0-rework-2026-08-23/638-stage0-cc-m4-1-people-schema-gov-report-probe-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 638-A 详细

### 638-A.1 政府工作报告 probe

**Targets（自取，不问用户）：**

```python
GOV_REPORT_TARGETS = [
    # 国务院政府工作报告
    ("central", "https://www.gov.cn/zwgk/zfgbg.htm"),  # 国务院政府工作报告专栏
    ("central", "https://www.gov.cn/zwgk/zfgbg/2024-03-12/content_6940070.htm"),  # 2024 报告

    # 31 省人民政府政府工作报告（按 docs/54 §3 试点省优先）
    # 江苏
    ("jiangsu", "http://www.jiangsu.gov.cn"),
    # 广东
    ("guangdong", "http://www.gd.gov.cn"),
    # 浙江
    ("zhejiang", "http://www.zj.gov.cn"),
    # 山东
    ("shandong", "http://www.shandong.gov.cn"),
    # 四川
    ("sichuan", "http://www.sc.gov.cn"),
    # 上海
    ("shanghai", "http://www.shanghai.gov.cn"),
    # 北京
    ("beijing", "http://www.beijing.gov.cn"),
    # 其余 24 省（按 docs/00 Pinyin slug）
    # tianjin, hebei, shanxi, neimenggu, liaoning, jilin, heilongjiang,
    # anhui, fujian, jiangxi, henan, hubei, hunan, guangxi, hainan, chongqing,
    # guizhou, yunnan, xizang, shaanxi, gansu, qinghai, ningxia, xinjiang
]
```

**关键常数（继承 636）：**
- `WAF_IP = "125.93.9.191"` （634 + 636 已确认本机 IP）
- `USER_AGENTS`：5 profile（curl/python/headless chrome/firefox/safari）
- `TIMEOUT = 15s`、`MAX_REDIRECTS = 5`、`SAMPLE_YEARS = [2024]`
- verdict 分类同 636：`REACHABLE / PARTIAL / BLOCKED / NOT_APPLICABLE / NOT_PROBED`

**read-only 红线：** 不写 cegr.observation；不修改 source_registry/registry.csv；不修改 mart_*_*.sql；不动 4 frontend fixture bytes。

### 638-A.2 任免公告 probe

**Targets：**

```python
RENMIAN_TARGETS = [
    ("central-discipline", "https://www.ccdi.gov.cn"),  # 中央纪委国家监委
    ("npc", "http://www.npc.gov.cn"),  # 全国人大
    ("central", "https://www.gov.cn/zwgk/zfgbg.htm"),  # 国务院（兼任政府工作报告）
]
```

方法学同 638-A.1。

### 638-A.3 人物表 schema 收口

**当前 state 假设**（须 Read migrations 001–014 + schema/01-core.sql 确认）：

- `person` 表可能字段：id, name, name_pinyin, name_zh, birth_year, position, organization, tenure_start, tenure_end, is_demo, created_at, updated_at, source_url, source_id
- 缺什么字段由 probe 结果决定：若可达则保留 source 字段；不可达则置 NULL + 标记 demo_only

**migration 文件** `db/migrations/015-m4-1-people-schema.sql`：

```sql
-- 638 / M4.1: 人物表 schema 收口
-- 仅 DDL ADD/ALTER，不 DML；is_demo 隔离保留

BEGIN;

-- 1. 验证现有 person 表存在
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'person') THEN
        RAISE EXCEPTION 'person table missing - apply migrations 001-014 first';
    END IF;
END $$;

-- 2. 加字段（如缺）
ALTER TABLE person ADD COLUMN IF NOT EXISTS position_title VARCHAR(200);
ALTER TABLE person ADD COLUMN IF NOT EXISTS appointment_type VARCHAR(50);  -- 任命/免职/代理/确认
ALTER TABLE person ADD COLUMN IF NOT EXISTS announcement_url TEXT;
ALTER TABLE person ADD COLUMN IF NOT EXISTS announcement_date DATE;
ALTER TABLE person ADD COLUMN IF NOT EXISTS source_document_id INTEGER;
ALTER TABLE person ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ;

-- 3. 索引（按需）
CREATE INDEX IF NOT EXISTS idx_person_is_demo ON person(is_demo);
CREATE INDEX IF NOT EXISTS idx_person_announcement_date ON person(announcement_date);

-- 4. is_demo 隔离约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'person_demo_separation'
    ) THEN
        ALTER TABLE person ADD CONSTRAINT person_demo_separation
            CHECK (
                (is_demo = TRUE) OR
                (is_demo = FALSE AND source_document_id IS NOT NULL AND announcement_url IS NOT NULL)
            );
    END IF;
END $$;

COMMIT;
```

**is_demo 隔离原则**：所有 is_demo=false 行必须 `source_document_id` + `announcement_url` NOT NULL（= 可一跳回 SHA）。

**read-only 红线**：不删表 / 不 DROP COLUMN / 不 DELETE FROM；不修改现有 observation / 任免 demo 数据。

### 638-A.4 docs/58 架构师级审查文档

6 段结构（类比 docs/57）：

```markdown
# 58 — M4.1 人物表 schema 收口 + 政府工作报告数据可得性 probe（2026-09-01，knife 638）

> 类型: 架构师级审查文档
> 依据: docs/57 §6 下一步 + docs/54 §M4.1
> 不宣布 Gate / O1 / M2 / M4 PASS。
> 架构师裁定: <根据 probe 结果给出 1 个推荐>

## 1. M4.1 落地终态
   sub-knife 状态表 + M4.1 收口结论

## 2. 政府工作报告 probe 数据（基于 638-A.1）
   总分布: REACHABLE X / PARTIAL Y / BLOCKED Z
   试点省 (江苏/广东/浙江) 详细 verdict
   WAF 根因分析（继承 636 §2）

## 3. 任免公告 probe 数据（基于 638-A.2）
   总分布: REACHABLE X / PARTIAL Y / BLOCKED Z
   ccdi / npc / 国务院 verdict

## 4. 人物表 schema 收口（基于 638-A.3）
   加字段清单 + is_demo 隔离约束 + 索引

## 5. M4.2 / M4.3 下一步
   M4.2 任免数据 demo: 依 probe 可达性启动
   M4.3 政策项目 demo: 已 schema 存在, 等 M4.2

## 6. 下一步 (639 = M4.2?)
```

### 638-A.6/A.7 probe 报告

类比 636 `docs/reports/m2_2001_backfill_feasibility_20260901.md` 模板：top verdict / 各 verdict 计数 / 分 source 类 / 试点省细分 / 样本 cells。

### 638-A.8 EXEC-QUEUE rev61

`cc_head: 5d957ef (637) + TBD (638)`；§NOW = 638 tasking；§CHAIN_TAIL 增 638 row。

---

## 3. 638-B 测试

**目标文件**：`tests/test_m4_1_people_probe.py` ≥ 8 用例：

1. `test_gov_report_probe_report_exists` — `docs/reports/m4_1_gov_report_probe_20260901.md` 存在且含 top verdict
2. `test_gov_report_probe_evidence_json_parses` — `evidence_pack/m4_1_gov_report_probe_20260901.json` parses；含 summary / cells / probed_count
3. `test_gov_report_probe_does_not_modify_database` — probe 脚本不调用 INSERT/UPDATE/DELETE/psycopg.connect
4. `test_gov_report_probe_no_hardcoded_gdp_values` — probe 报告不含 31 省 2024 期望 GDP 真值
5. `test_renmian_probe_evidence_json_parses` — 同 1 但 renmian
6. `test_migration_015_no_dml` — `db/migrations/015-m4-1-people-schema.sql` 不含 INSERT/UPDATE/DELETE/TRUNCATE/DROP TABLE/DROP COLUMN；只 ADD COLUMN / CREATE INDEX / ADD CONSTRAINT
7. `test_doc_58_has_six_sections` — docs/58 含 ## 1.-## 6. + 58/2026-09-01/638 标头
8. `test_doc_58_no_pass_announcement` — docs/58 不含 "M2 PASS" / "M4 PASS" / "Gate PASS"（智能排除 disclaimer 否定句）

**全套 pytest**（M2 + 637 + 638）：≥ 49 + 9 + 8 = ≥ 66 用例；实测目标 ≥ 60（绿）。

---

## 4. 红线（继承 + 638 增量）

| 红线 | 来源 | 状态 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | 继承 | ✓ 测试 + docs/58 disclaimer |
| 不让用户裁定 URL/年份 | 数据源治理铁律 | ✓ probe targets 自取政府源 |
| 数据源唯一=政府/统计/研究机构 | 继承 | ✓ probe targets 全部 gov.cn |
| 不爬网 | 继承 | ✓ probe 只探可达性, 不抓内容入库 |
| 不写 cegr.observation | 继承 | ✓ probe read-only; test 验证 |
| 不静默硬编码 GDP 值 | 继承 | ✓ test 验证 |
| 不删 person 表 / 不 DROP COLUMN | 638 新增 | ✓ migration 仅 ADD/CREATE/ADD CONSTRAINT |
| 不改 source_registry / mart / 4 fixture | 继承 | ✓ 638 不动这些 |
| is_demo 隔离 | 638 新增 | ✓ migration 加 CHECK 约束 |
| 湖北必须 ≠ M1 半年表 c5cf5abe | 继承 | ✓ 638 不写湖北具体 observation |
| probe 脚本幂等 | 638 新增 | ✓ no time.sleep / no random in classify |
| 双推 origin→github | 继承 | ✓ §5 commit + origin → github |

---

## 5. commit + 双推

### 638-A + 638-B commit 1 (delivery)

```bash
git add scripts/probe_gov_report_2024.py \
        scripts/probe_renmian_announcement_2024.py \
        db/migrations/015-m4-1-people-schema.sql \
        docs/58-m4-1-people-schema-gov-report-probe-20260901.md \
        docs/reports/m4_1_gov_report_probe_20260901.md \
        evidence_pack/m4_1_gov_report_probe_20260901.json \
        docs/reports/m4_1_renmian_probe_20260901.md \
        evidence_pack/m4_1_renmian_probe_20260901.json \
        tests/test_m4_1_people_probe.py \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md

git commit -m "feat(638): M4.1 人物表 schema 收口 + 政府工作报告/任免公告可达性 probe"

git push origin HEAD
git push github HEAD
```

### 638-C commit 2 (cc_head backfill)

```bash
# After §8 commit, update EXEC-QUEUE cc_head TBD → <commit hash>
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(638): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 638-C commit 3 (receipt, separate)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/638-stage0-cc-m4-1-people-schema-gov-report-probe-receipt-20260901.md
git commit -m "docs(638): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 6. 完成后态

- EXEC-QUEUE rev62: 638 DELIVERED · 等用户接受/驳回 638 推荐
- 测试：≥ 60 用例 green
- 双推：origin + github 三 commit 全部同步
- 638 内部审计 AUDITED
- 不宣布 Gate / O1 / M2 / M4 PASS
- 用户下一步：
  - 接受 638 推荐 → 639 = M4.2 任免数据 demo（依 probe 可达性）
  - 驳回 → 用户裁定 639 re-scope 或 640 (M3.3 重启)

— End 638 tasking —