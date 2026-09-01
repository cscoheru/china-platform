# 642 — M5 WAF spike + M4.5 任免真实化 spike 并行（架构师 tasking）

> **刀号**: 642
> **Milestone**: M5 + M4.5（并行 spike；spike 不互斥）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**:
> - `docs/61 §5 / 641 receipt §4 / 641 §5.642 推荐` （架构师综合推荐 = M5 + M4.5 并行）
> - `docs/60 §2.1`（640 关键反发现：5 BLOCKED 省 + 1 REACHABLE 省；6 REACHABLE 任免源）
> - `docs/33 §3.2 sentinel`（lineage JSONB 是 is_demo 唯一落点；不新写 016 migration）
> - 638 / 639 / 640 / 641 demo + real spike 累积
> - 641 是首次真实化 spike；642 = 真实化深化（M4.5 跨 6 省）+ WAF 根因解决（M5）
> **用户接收**：`接受 642 scope`（2026-09-01）
> **不宣布** Gate / O1 / M2 / M4 PASS。

---

## 0. 范围（一句话）

642 落地 **5 件并行 spike**（spike 不互斥）：**(A1)** M5 WAF 网防G01 假设验证 — 5 BLOCKED 省（福建/河南/广东/贵州/云南）+ 国务院 /zhengce/zhengceku/ 反发现深挖；多路径探测 + WAF 网防G01 网防验证；≤10 HTTP（≤5 cell × 2 HTTP）；**(A2)** M4.5 任免真实化 — 复用 639 6 REACHABLE 任免源（黑龙江/福建/河南/广东/贵州/云南）× 1 detail each + 6 政策表 × 1 real each × 6 source = 36 INSERT；lineage `is_demo='false'` 真实化 sentinel；≤12 HTTP（6 indices + 6 details）；**(A3)** `docs/62-m5-waf-spike-20260901.md` §1-§6 + `docs/63-m4-5-renmian-real-20260901.md` §1-§6 架构师级审查；**(B)** `tests/test_m5_waf_spike.py` ≥ 6 + `tests/test_m4_5_renmian_real.py` ≥ 6 = **全套 pytest ≥ 90/90 green**；**(C)** 回执 + commit + 双推；**架构师推荐 643 = M5 WAF spike 二次 + M4.6 政府工作报告真实化（复用 638 政府报告 PARTIAL 1/2 路径） 或 643 = M6 + M4.6 并行**。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 642-A.1 | `scripts/probe_m5_waf_v1_2024.py` + `evidence_pack/m5_waf_v1_probe_20260901.json` | DONE | M5 WAF 网防G01 假设验证 probe；5 BLOCKED 省（福建/河南/广东/贵州/云南）+ 国务院 /zhengce/zhengceku/ + 替代路径探测；≤10 HTTP |
| 642-A.2 | `scripts/seed_m4_5_renmian_real.sql` | DONE | 6 REACHABLE 任免源 × 1 detail each + 6 政策表 × 1 real each × 6 source = 36 INSERT；lineage `is_demo='false'` 真实化 sentinel；chain_id=`real_642_m4_5_renmian`；≤12 HTTP total |
| 642-A.3 | `docs/62-m5-waf-spike-20260901.md` + `docs/63-m4-5-renmian-real-20260901.md` | DONE | §1-§6 双文档架构师级审查 |
| 642-A.5 | `docs/reports/m5_waf_v1_probe_20260901.md` + `evidence_pack/m5_waf_v1_probe_20260901.json` + `docs/reports/m4_5_renmian_real_20260901.md` + `evidence_pack/m4_5_renmian_real_20260901.json` | DONE | 双 spike probe + real 报告 + 证据包 |
| 642-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev69 → 642 tasking OPEN · 等 CC 落地（即签即自交付；rev69 同时落地） |
| 642-B | `tests/test_m5_waf_spike.py` ≥ 6 + `tests/test_m4_5_renmian_real.py` ≥ 6 | DONE | 共 ≥ 12 用例；全套 pytest ≥ 90/90 green |
| 642-C | 回执 + commit + 双推 | DONE | `642-stage0-cc-m5-m4-5-parallel-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 642-A 详细

### 642-A.1 M5 WAF 网防G01 假设验证 probe

**目标 URL（5 BLOCKED 省 + 1 国务院 + 替代路径）**:

| 类别 | URL 模板 | 期望 verdict |
|---|---|---|
| BLOCKED 省 zfwj | `https://www.{省}.gov.cn/zwgk/zfwj/` | 640 实测 BLOCKED (404) |
| BLOCKED 省 zfgb | `https://www.{省}.gov.cn/zwgk/zfgb/` | 640 实测 BLOCKED (404) |
| BLOCKED 省 ghjh | `https://www.{省}.gov.cn/zwgk/ghjh/` | 640 实测 BLOCKED (404) |
| 国务院 zhengceku | `https://www.gov.cn/zhengce/zhengceku/` | 640 实测 BLOCKED (403 WAF) |
| 替代路径: 福建 子路径 `https://www.fujian.gov.cn/zwgk/` | 国务院 总门户 | 试探 |
| 替代路径: 河南 `https://www.henan.gov.cn/zwgk/` | 试探 | |
| 替代路径: 国务院 `https://www.gov.cn/zwgk/` | 试探 | |
| 替代路径: 国务院 `https://www.gov.cn/zhengce/` | 试探 | |
| 替代路径: 国务院 `https://www.gov.cn/zhengce/content/` | 试探 | |
| 替代路径: 国务院 `https://www.gov.cn/zhengce/2024-01/15/content_xxx.htm` | 试探（已知真实政策 URL） |

**probe 边界（硬性红线）**:

- ≤10 次 HTTP total（每 cell ≤2 HTTP: 1 main + 1 fallback alternative）
- 不爬网（no recursion; no follow pagination）
- 仅探可达性（不抓内容入库）
- curl only（no JS / no headless browser）

**`scripts/probe_m5_waf_v1_2024.py`**:

```python
# M5 WAF 网防G01 假设验证;5 BLOCKED 省 + 替代路径
PROBE_CELLS = [
    # 5 BLOCKED 省 + 替代路径
    ("fujian",  "https://www.fujian.gov.cn/zwgk/",          "main"),
    ("fujian",  "https://www.fujian.gov.cn/",                "fallback_root"),
    ("henan",   "https://www.henan.gov.cn/zwgk/",           "main"),
    ("henan",   "https://www.henan.gov.cn/",                "fallback_root"),
    ("guangdong","https://www.gd.gov.cn/zwgk/",             "main"),
    ("guizhou", "https://www.guizhou.gov.cn/zwgk/",         "main"),
    ("yunnan",  "https://www.yn.gov.cn/zwgk/",              "main"),
    # 国务院 替代路径 (640 BLOCKED zhengceku)
    ("gov",     "https://www.gov.cn/zhengce/content/",      "main"),
    ("gov",     "https://www.gov.cn/zwgk/",                 "fallback"),
    ("gov",     "https://www.gov.cn/",                      "fallback_root"),
]
```

**verdict 映射（沿用 638/639/640）**:

- REACHABLE: HTTP 200 + body 含 POLICY_MARKER_RE
- PARTIAL: HTTP 200 + body 不含 POLICY_MARKER_RE（栏目是别的不是政策）
- BLOCKED: HTTP 404 / 403 WAF / TLS reset / connection error
- 顶层裁定: **MIXED** if verdict 混合 / **BLOCKED** if 全 BLOCKED / **PARTIAL** if 全 PARTIAL / **REACHABLE** if 全 REACHABLE

### 642-A.2 M4.5 任免真实化 spike

**目标 URL（639 6 REACHABLE 任免源）**:

| 试点省 | URL 模板 | 639 verdict |
|---|---|---|
| 黑龙江 | `https://www.hlj.gov.cn/zwgk/rmtzb/` (or 任免 公告 栏) | REACHABLE |
| 福建 | `https://www.fujian.gov.cn/zwgk/rmtzb/` (or 任免 公告 栏) | REACHABLE |
| 河南 | `https://www.henan.gov.cn/zwgk/rmtzb/` (or 任免 公告 栏) | REACHABLE |
| 广东 | `https://www.gd.gov.cn/zwgk/rmtzb/` (or 任免 公告 栏) | REACHABLE |
| 贵州 | `https://www.guizhou.gov.cn/zwgk/rmtzb/` (or 任免 公告 栏) | REACHABLE |
| 云南 | `https://www.yn.gov.cn/zwgk/rmtzb/` (or 任免 公告 栏) | REACHABLE |

**fetch 边界（硬性红线）**:

- ≤12 HTTP total（6 indices + 6 details）
- 不爬网
- 真实 SHA256 计算（每 detail page HTML sha256）
- 真实化 INSERT: chain_id=`real_642_m4_5_renmian` + lineage.is_demo='false'

**`scripts/seed_m4_5_renmian_real.sql` 结构**:

```sql
-- 642 / M4.5: 6 省任免真实化 spike (knife 642)
-- 沿用 docs/33 §3.2 sentinel (lineage JSONB is_demo='false' 真实化)
-- 真实 SHA = 642-A.2 fetch 详情页 SHA256
-- 6 政策表 × 1 real each × 6 source = 36 INSERT

BEGIN;

-- 6 source_registry (6 试点省 各 1)
INSERT INTO source_registry (...) VALUES
    ('d1eebc99-...', 'hlj', ...),
    ('d1eebc99-...', 'fujian', ...),
    ... ;

-- 6 source_document (6 试点省 detail page SHA)
INSERT INTO source_document (...) VALUES
    ('d1eebc99-...', 'hlj_detail_sha', ...),
    ('d1eebc99-...', 'fujian_detail_sha', ...),
    ... ;

-- 6 policy_document (NOTICE 任免, 每试点省 1)
-- 6 policy_target + 6 policy_measure
-- 6 government_commitment (geo_entity_id via SELECT 子查询 from M2-a seed)
-- 6 commitment_progress + 6 project_event

COMMIT;
```

**架构师裁定**（与 641 同）:

- 沿用 docs/33 §3.2 sentinel（lineage JSONB is_demo='false'）
- 不新写 016 migration
- 真实 SHA ≠ 640/641 demo SHA（与所有 demo SHA 区分）
- chain_id = `real_642_m4_5_renmian`（非 demo_* 前缀；非 641 real_* 前缀）
- 6 试点省 geo_entity_id 通过 SELECT 子查询获取（兼容 M2-a seed）

### 642-A.3 docs/62 + docs/63 架构师级审查文档

**docs/62 §1-§6** (M5 WAF spike):
- §1. M5 落地终态 + 5 BLOCKED 省根因 / 国务院 WAF 替代路径 verdict
- §2. WAF 网防G01 假设验证（基于 642-A.1 真实 probe）
- §3. M5 BLOCKED 根因分析（5 省路径 404 + 国务院 WAF 403）
- §4. 替代路径可达性矩阵
- §5. 643 下一步（M5 WAF 二次 + M4.6 政府工作报告真实化）
- §6. 不宣称 PASS

**docs/63 §1-§6** (M4.5 任免真实化):
- §1. M4.5 落地终态 + 6 REACHABLE 试点省任免真实化
- §2. 6 试点省任免抓取数据（基于 642-A.2）
- §3. 真实化 demo SQL 结构（36 INSERT = 6 × 6）
- §4. lineage 真实化 sentinel 沿用（chain_id=`real_642_m4_5_renmian`）
- §5. 643 下一步
- §6. 不宣称 PASS

### 642-A.5 双 spike 报告 + 证据包

- `docs/reports/m5_waf_v1_probe_20260901.md` + `evidence_pack/m5_waf_v1_probe_20260901.json`
- `docs/reports/m4_5_renmian_real_20260901.md` + `evidence_pack/m4_5_renmian_real_20260901.json`

### 642-A.6 EXEC-QUEUE rev69

`cc_head: da0e77a (641 receipt) + TBD (642)`；§NOW = 642 tasking；§CHAIN_TAIL 增 642 row。

---

## 3. 642-B 测试

**目标文件**:

- `tests/test_m5_waf_spike.py` ≥ 6 用例:
  1. probe 报告存在 + 顶层裁定 (MIXED/BLOCKED/PARTIAL/REACHABLE)
  2. evidence JSON parses + probed_count = 10 + http_count ≤ 10
  3. WAF 网防G01 假设验证 (5 BLOCKED 省路径 404; 国务院 zhengceku 403)
  4. 替代路径 verdict (国务院 /zwgk/ 等 fallback REACHABLE)
  5. docs/62 六段 + 不宣称 PASS
  6. probe 脚本幂等 (no time.sleep / no random)

- `tests/test_m4_5_renmian_real.py` ≥ 6 用例:
  1. fetch 报告存在 + 顶层裁定 REAL_FETCHED
  2. evidence JSON parses + 6 source SHAs + http_count ≤ 12
  3. seed SQL 6 表 × 1 real each × 6 source = 36 INSERT
  4. seed lineage is_demo='false' 隔离 (vs 640/641 demo is_demo='true')
  5. seed 真实 SHA ≠ 640 demo SHA 0…02 ≠ 641 真实 SHA 0…26e5 ≠ 639 demo SHA 0…01
  6. docs/63 六段 + 不宣称 PASS

**全套 pytest 目标**: M2 + 637 + 638 + 639 + 640 + 641 + 642 = 78 + 12 = **≥ 90 用例 green** (实际 count by pytest report 为准)。

---

## 4. 红线（继承 + 642 增量）

| 红线 | 来源 | 状态 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | 继承 | ✓ 测试 + docs/62+docs/63 disclaimer |
| 不让用户裁定 URL/年份 | 数据源治理铁律 | ✓ probe + fetch URL 自取政府源 |
| 数据源唯一=政府/统计/研究机构 | 继承 | ✓ 5 试点省 + 国务院 gov.cn 政府源 |
| 不爬网 (M5) | 继承 | ✓ M5 ≤10 HTTP (5 cell × 2); M4.5 ≤12 HTTP (6 ind + 6 det) |
| 不爬网 (M4.5) | 继承 | ✓ 复用 639 6 REACHABLE 路径, 不蔓延 |
| 不删表 / 不 DROP COLUMN | 继承 | ✓ seed SQL 仅 INSERT ON CONFLICT |
| 不静默硬编码 GDP 值 | 继承 | ✓ target_value 等从抓取; 无则 NULL |
| 湖北必须 ≠ M1 半年表 c5cf5abe | 继承 | ✓ 642 不写湖北具体 observation; 湖北不在 6 REACHABLE 任免源之列 (640 BLOCKED) |
| 不新写 016 migration (沿用 009+010) | 继承 | ✓ 642 不写 016 |
| M5 BLOCKED 根因深入 | 642 新增 | ✓ docs/62 §3 BLOCKED 根因分析 |
| M4.5 spike 边界 ≤1 each × 6 source | 642 新增 | ✓ 6 表 × 1 each × 6 试点省 = 36 INSERT (spike) |
| lineage.is_demo='false' 真实化 sentinel | 642 新增 | ✓ chain_id='real_642_m4_5_renmian' |
| 真实 SHA ≠ 640/641 demo/real SHA | 642 新增 | ✓ 6 试点省 真实 SHA 全 distinct |
| 不复现 640 5 BLOCKED 政策源 (probe) | 642 新增 | ✓ M5 probe 5 BLOCKED + 替代路径 (verdict 矩阵) |
| 不复现 639 6 REACHABLE 任免源 (probe) | 642 新增 | ✓ M4.5 真实化 复用 639 6 REACHABLE, 不重新 probe |
| R3-E provenance chain_id 非 demo_* | 642 新增 | ✓ chain_id='real_642_m4_5_renmian' |
| 6 试点省 geo_entity_id via SELECT 子查询 | 642 新增 | ✓ government_commitment + project_event INSERT + SELECT |
| 双推 origin→github | 继承 | ✓ §5 commit + origin → github |

---

## 5. commit + 双推

### 642-A + 642-B commit 1 (delivery)

```bash
git add scripts/probe_m5_waf_v1_2024.py \
        scripts/seed_m4_5_renmian_real.sql \
        scripts/fetch_m4_5_renmian_v1_2024.py \
        docs/62-m5-waf-spike-20260901.md \
        docs/63-m4-5-renmian-real-20260901.md \
        docs/reports/m5_waf_v1_probe_20260901.md \
        docs/reports/m4_5_renmian_real_20260901.md \
        evidence_pack/m5_waf_v1_probe_20260901.json \
        evidence_pack/m4_5_renmian_real_20260901.json \
        tests/test_m5_waf_spike.py \
        tests/test_m4_5_renmian_real.py

git commit -m "feat(642): M5 WAF spike + M4.5 任免真实化 并行 — 5 BLOCKED 根因 probe + 6 REACHABLE × 6 政策表 lineage.is_demo='false'"

git push origin HEAD
git push github HEAD
```

### 642-C commit 2 (cc_head backfill)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(642): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 642-C commit 3 (receipt)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/642-stage0-cc-m5-m4-5-parallel-receipt-20260901.md
git commit -m "docs(642): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 6. 完成后态

- EXEC-QUEUE rev70: 642 DELIVERED · 等用户接受 643 scope 推荐
- 测试：≥ 90 用例 green
- 双推：origin + github 三 commit 全部同步
- 642 内部审计 AUDITED
- 不宣布 Gate / O1 / M2 / M4 PASS
- 用户下一步：
  - 接受 642 推荐 → 643 = M5 WAF spike 二次（解决 5 BLOCKED 省根因; WAF 网防G01 假设进一步验证）
  - 接受 642 推荐 → 643 = M4.6 政府工作报告真实化（复用 638 政府报告 PARTIAL 1/2 路径）
  - 接受 642 推荐 → 643 = M6 + M4.6 并行（架构师推荐; spike 不互斥）
  - 驳回 → 用户裁定 643 re-scope 或 644+

— End 642 tasking —
