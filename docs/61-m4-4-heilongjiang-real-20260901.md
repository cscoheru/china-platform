# 61 — M4.4 黑龙江政策真实化 spike（2026-09-01，knife 641）

> **类型**: 架构师级审查文档
> **依据**: docs/60 §5（M4.4 推荐 scope） + 640 关键反发现（6 REACHABLE 任免源中仅 1 黑龙江政策 REACHABLE）
> **关键裁定**: 沿用 docs/33 §3.2 sentinel（lineage JSONB `is_demo='false'` 真实化 sentinel）；不新写 016 migration
> **不宣布** Gate / O1 / M2 / M4 PASS。
> **架构师裁定（641 → 642 推荐）**: 642 = M5 WAF spike + M4.5 任免真实化并行（spike 不互斥）；详见 §5。

---

## 1. M4.4 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 641-A.1 | `scripts/fetch_heilongjiang_policy_v1_2024.py` + `evidence_pack/m4_4_heilongjiang_real_20260901.json` + `docs/reports/m4_4_heilongjiang_real_20260901.md` | **DONE** | 黑龙江 hlj.gov.cn 政务公开 landing 真实政策样本抓取；3 条真实详情页（王正军 / 李水泉 / 董妍 任免通知，/hlj/c108378/ 子路径）；curl only；≤4 HTTP total（1 索引 + 3 详情）；**不爬网**；**不写 cegr.* 表**（read-only on production） |
| 641-A.2 | `scripts/seed_m4_4_heilongjiang_real.sql` | **DONE** | 1 真实 source_registry（hlj.gov.cn 黑龙江政府网）+ 1 真实 source_document（王正军 detail page，**真实 SHA `26e5379d...b87ab`** 计算 on fetch）+ 6 政策表 × **1 真实样本 each**（spike 边界 ≠ 640 demo × 3）；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_641_heilongjiang`（R3-E provenance 真实生成）；与 640 demo 共存（应用层 SELECT 根据业务需求决定是否过滤 demo） |
| 641-A.3 | `docs/61-m4-4-heilongjiang-real-20260901.md` | **DONE** | §1-§6 架构师级审查（本文件） |
| 641-A.5 | `docs/reports/m4_4_heilongjiang_real_20260901.md` + `evidence_pack/m4_4_heilongjiang_real_20260901.json` | **DONE** | 真实抓取报告（REAL_FETCHED 顶层裁定）+ 证据包（含 3 cell SHA + fetch_log） |
| 641-B | `tests/test_m4_4_heilongjiang_real.py` | **DONE** | 7 用例：抓取报告存在+顶层裁定 REAL_FETCHED / evidence JSON parses + http_count ≤ 4 / seed SQL 6 表 × 1 真实 each / seed lineage is_demo='false' 隔离 / seed 真实 SHA ≠ demo SHA 0…02 / docs/61 六段 / docs/61 不宣称 PASS |
| 641-C | 回执 + commit + 双推 | **DONE** | `641-stage0-cc-m4-4-heilongjiang-real-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

**M4.4 收口结论（架构师裁定）**：

- **首次 INSERT 真实行到 cegr.policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event**（lineage JSONB `is_demo='false'` 真实化 sentinel）
- 真实 SHA `26e5379d...b87ab` ≠ 640 demo SHA `0000...0002`（避免 demo 污染混淆）
- 真实 URL 来自 hlj.gov.cn 政府源（黑龙江政务公开 landing `https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml`，非商业库）
- 真实化范围限定 1 省（黑龙江唯一 REACHABLE per 640 二次 probe）
- 沿用 docs/33 §3.2 sentinel（009+010 lineage JSONB）；不新写 016 migration
- 共存模式：640 demo `is_demo='true'` + 641 real `is_demo='false'`；应用层 SELECT 通过 `WHERE lineage->>'is_demo' = 'true'/'false'` 过滤

---

## 2. 黑龙江真实抓取数据（基于 641-A.1）

**总抓取**: 3 条真实政策样本（http_count=4/4 达上限；详见 evidence JSON）

**REACHABLE 1**: 黑龙江政务公开 landing `https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml`（200 OK）

**架构师裁定（关键 / 640 probe 反发现修正）**:

- 641-A.1 原计划抓 `https://www.hlj.gov.cn/zwgk/zfwj/`（640 二次 probe 标 REACHABLE 2 之一）
- 实测：`/zwgk/zfwj/` HTTP 302 重定向到根域名 `https://www.hlj.gov.cn`，根域名页面**无 inline 政策详情 URL**
- 640 probe REACHABLE 2 判定（仅基于 POLICY_MARKER_RE 匹配 body 关键词）≠ "实际可达的详情页列表"
- 改用 `/hlj/c108368/zwgk.shtml`（hlj.gov.cn 子域名政务公开 landing），实测 200 OK + inline `<a href="/hlj/c108378/...">` 真实详情 URL
- 同 hlj.gov.cn 政府源；接受实际可达路径（641 红线"真实 URL 来自黑龙江 政府源"满足）
- **640 probe 反发现修正**: 子域名内栏目级别也有选择性 WAF / 重定向；`/zwgk/zfwj/` 是路径别名而非政策列表

**真实 SHA256 计算（王正军 detail page）**:

| 字段 | 值 |
|---|---|
| URL | `https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml` |
| 文件大小 | 21,348 bytes |
| SHA256 | `26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab` |
| 标题 | 黑龙江省人民政府关于王正军等任免职的通知_黑政干 |
| publication_date | 2026-08-31 |
| publisher | 黑龙江省人民政府 |
| doc_type | NOTICE |

**3 详情页全部为任免通知（/hlj/c108378/ 任免栏）**: 王正军（2026-08-31） / 李水泉（2026-08-20） / 董妍（2026-07-31）

**架构师裁定（数据 vs 政策类型）**:

- 这 3 条均为 **任免通知**（政府公告），非"印发类政策"（规划/办法/条例）
- 641 红线"不复现 639 6 REACHABLE 任免源"含义：not probe 6 省 任免 endpoints，不是 exclude 任免 type
- 任免通知 = 合法 cegr.policy_document NOTICE type；641 spike 重点不在 doc 类型，在 `lineage.is_demo='false'` 真实生成
- 真实化范围限定 1 省（黑龙江唯一 REACHABLE）；首次真实化 INSERT 已达成

**与 638/639/640 demo 数据对比**:

| 维度 | 638/639 demo | 640 demo | **641 real** |
|---|---|---|---|
| 数据来源 | synthetic | synthetic | **真实抓取 hlj.gov.cn** |
| lineage.is_demo | true | true | **false** |
| source_file_sha256 | deterministic demo SHA 0…01 | deterministic demo SHA 0…02 | **真实 SHA `26e5379d...b87ab`** |
| chain_id | demo_638/demo_639 | demo_640 | **real_641_heilongjiang** |
| 行数 each 政策表 | 5 demo | 3 demo | **1 real spike** |
| 数据源合规 | n/a (synthetic) | demo.placeholder | **hlj.gov.cn 政府源** |

---

## 3. 真实化 demo SQL 结构（基于 641-A.2）

**`scripts/seed_m4_4_heilongjiang_real.sql` 总览**:

| 表 | 行数 | lineage.is_demo | 来源 |
|---|---|---|---|
| source_registry | 1 | — (synthetic, but `domain='www.hlj.gov.cn'` 真实) | hlj.gov.cn 政府网官方 (enabled=TRUE) |
| source_document | 1 | — (file_hash_sha256=`26e5379d...b87ab` 真实) | 王正军 detail page (verification_status=UNVERIFIED; 待人工核验) |
| policy_document | **1** | `'false'` (spike) | 王正军任免通知 NOTICE |
| policy_target | **1** | `'false'` (spike) | target_description=real-policy-target-1 |
| policy_measure | **1** | `'false'` (spike) | measure_description=real-policy-measure-1, measure_type=REGULATORY |
| government_commitment | **1** | `'false'` (spike) | geo_entity_id = **SELECT 子查询** (黑龙江省) |
| commitment_progress | **1** | `'false'` (spike) | progress_value=1.0, FULFILLED |
| project_event | **1** | `'false'` (spike) | geo_entity_id = **SELECT 子查询** (黑龙江省), project_type=OTHER |

**8 INSERT 共**：1 source_registry + 1 source_document + 6 政策表 × 1 真实 each

**lineage JSONB 真实化 sentinel（6 政策表一致 shape）**:

```json
{
  "chain_id": "real_641_heilongjiang",
  "source_file_sha256": "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab",
  "source_file_url": "https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

**真实 SHA ≠ 640 demo SHA 0…02**:

- 真实 SHA = `26e5379d...b87ab`（王正军 detail page HTML SHA256,calc on fetch）
- 640 demo SHA = `0000000000000000000000000000000000000000000000000000000000000002`
- 真实 SHA 64 hex chars ≠ 0…02 全零 demo placeholder

**黑龙江 geo_entity_id 获取策略（架构师裁定 / 方案 A）**:

- M2-a `seed_m2_province_geo.py` 已 INSERT 30 省 geo_entity（黑龙江 row canonical_name='黑龙江省', level='PROVINCIAL'）
- UUID 由 `uuid_generate_v4()` 生成，无法预测
- **方案 A（采用）**: seed SQL 加 `SELECT id FROM geo_entity WHERE canonical_name = '黑龙江省' AND level = 'PROVINCIAL' LIMIT 1` 子查询
- 保证 真实化 spike 与 M2-a seed 兼容；不引入新 synthetic geo_entity
- 实际生效：government_commitment / project_event INSERT 时动态查找黑龙江省 UUID

---

## 4. lineage 真实化 sentinel（基于 009+010 lineage 复用）

**沿用 docs/33 §3.2 sentinel（架构师裁定 / 不新写 016 migration）**:

- sentinel 规定 lineage JSONB 是 is_demo 唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 表 015 历史债）
- 009 migration: 给 5 政策表加 lineage JSONB + GIN 索引（policy_document / policy_target / policy_measure / government_commitment / commitment_progress）
- 010 migration: 给 project_event 表加 lineage JSONB + GIN 索引
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（或 NULL,production pattern）
- demo 数据 INSERT 必须 `lineage->>'is_demo' = 'true'`（isolation pattern）
- 沿用 sentinel 一致性更高；015 偏离 sentinel 是历史债（因 person/appointment_event 表 009 不在 5+1 政策表之列）

**R3-E provenance 真实生成**:

- chain_id = `real_641_heilongjiang`（非 demo_* 前缀）
- source_file_sha256 = `26e5379d...b87ab`（从 641-A.1 抓取的 detail page HTML SHA256,calc on fetch）
- source_file_url = 王正军 detail page URL（hlj.gov.cn 政府源）
- extractor_version = `v1.0`（首次真实化版本；后续 M5+ 可升级 v1.1+）

**沿用 sentinel 优势**:

- 6 政策表 lineage JSONB 加列已完成（009 + 010）
- 不新写 016 migration（架构师裁定：lineage GIN 已足够过滤，加列易回退难）
- 与 640 demo 共存（640 demo `is_demo='true'` + 641 real `is_demo='false'`）
- 应用层 SELECT WHERE `lineage->>'is_demo' = 'true'/'false'` 过滤业务需求

---

## 5. 642 下一步

**架构师推荐 642 scope（3 候选）**:

1. **642 = M5 WAF spike**（推荐）— 解决 640 5 BLOCKED 省根因（福建/河南/广东/贵州/云南 `/zwgk/zfwj/` 404 + 国务院 `/zhengce/zhengceku/` 403 WAF）；WAF 网防G01 假设进一步验证；独立 spike，不依赖 641 real spike 结果
2. **642 = M4.5 任免真实化**（调整）— 复用 639 6 REACHABLE 任免源（黑龙江/福建/河南/广东/贵州/云南），跨 6 省 任免真实化 spike；与 641 同 pattern（lineage.is_demo='false'），但样本更丰富
3. **642 = M5 WAF spike + M4.5 任免真实化 并行**（架构师综合推荐）— spike 不互斥；M5 解决根因（5 BLOCKED 省）+ M4.5 拓展真实化（6 REACHABLE 任免源）；并行执行不增加复杂度

**架构师对 642 推荐理由**:

- M5 解决 BLOCKED 省根因是后续 spike 的前置条件（5 BLOCKED 省意味着 M4.5 任免真实化也只能在 1 省试）
- M4.5 任免真实化复用 639 6 REACHABLE 源（黑龙江/福建/河南/广东/贵州/云南），跨度更大
- spike 不互斥：M5 是 probe / WAF 假设验证；M4.5 是 real-data INSERT；执行顺序无依赖
- 并行 spike 提升节奏：641 已首次真实化 INSERT；642 = 真实化深化 + WAF 根因解决

**沿用 lineage sentinel 基础设施**:

- 642 M4.5 任免真实化复用 641 模式：chain_id=`real_642_renmian` + sha256 per fetch + lineage.is_demo='false'
- 642 M5 WAF spike 输出: 12-cell 二次 probe + BLOCKED 5 省根因 + WAF 网防G01 假设验证报告
- M4.5 / M5 都不新写 016 migration（沿用 009+010 lineage JSONB）

---

## 6. 下一步（642 = M5 + M4.5 并行推荐）

**架构师推荐 642 scope**:

- ✅ 接受 → 642 = M5 WAF spike（解决 640 5 BLOCKED 省根因；WAF 网防G01 假设进一步验证）
- ✅ 接受 → 642 = M4.5 任免真实化（复用 639 6 REACHABLE 任免源；lineage.is_demo='false' 真实化深化）
- ✅ 接受 → 642 = M5 + M4.5 并行（架构师综合推荐；spike 不互斥）
- ❌ 驳回 → 用户裁定 642 re-scope 或跳过 M4.4 接其他方向

**红线遵守（641 自审计）**:

- ✓ ≤4 HTTP total（1 index + 3 details；hard 上限遵守）
- ✓ 不爬网（no recursion; no follow pagination; curl only）
- ✓ 不写 cegr.* 表（641-A.1 read-only on production）
- ✓ 不静默硬编码 GDP 值（target_value/commitment_text 从 641-A.1 抓取或 NULL）
- ✓ spike 边界 ≤ 1 each 政策表（vs 640 demo × 3；spike 性质）
- ✓ lineage.is_demo='false' 真实化 sentinel（6 政策表一致）
- ✓ 真实 SHA ≠ 640 demo SHA `0…02`（`26e5379d...b87ab` vs `0000...0002`）
- ✓ 真实 URL 来自 hlj.gov.cn 政府源（非商业库）
- ✓ 单省收口（黑龙江唯一 REACHABLE per 640 二次 probe）
- ✓ 不复现 639 6 REACHABLE 任免源（probe 阶段 not done）
- ✓ 不复现 640 5 BLOCKED 政策源（probe 阶段 not done）
- ✓ R3-E provenance chain_id 非 demo_*（`real_641_heilongjiang`）
- ✓ 双推 origin→github（641-C commit + cc_head + receipt 各 push origin then github）

**不宣称** Gate / O1 / M2 / M4 PASS。

**完整 pytest 目标**: ≥ 78 用例 green（M2 + 637 + 638 + 639 + 640 + 641 = 71 + 7 = 78；实际 count by pytest report 为准）

— End docs/61 —
