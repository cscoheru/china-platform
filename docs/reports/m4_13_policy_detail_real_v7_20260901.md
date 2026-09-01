# M4.13 政策详情 v7 真实化 spike — 附属复验/验证报告

> **附属产物**（独立文件，per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范）
> **主 evidence**: `evidence_pack/m4_13_policy_detail_real_v7_20260901.json`
> **本报告指针**: 引用主 evidence `summary.methodology` 字段
> **刀号**: 650 · 2026-09-01

---

## 1. 真实化样本复盘

### 1.1 guizhou（第 13 样本，直接 REACHABLE）

| 维度 | 值 |
|---|---|
| **原始请求省** | guizhou (cell.province = "guizhou") |
| **实际抓取省** | guizhou (cell.actual_province = "guizhou") — 无 substitute |
| **首选 URL** | `https://www.guizhou.gov.cn/zwgk/` |
| **首选 HTTP** | **200 REACHABLE** (chain_index=0 直接命中) |
| **fallback #1** | (未触发) |
| **SHA256** | `5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0` |
| **file_size_bytes** | 170166 |
| **chain_index** | 0 (直接 REACHABLE) |
| **fallback_chain_used** | ["zwgk_root"]` |
| **verdict** | REACHABLE |
| **substitute_used** | false |
| **HTTP attempts (本 cell)** | 1 |

### 1.2 jiangsu（第 14 样本，fallback #1 REACHABLE）

| 维度 | 值 |
|---|---|
| **原始请求省** | jiangsu (cell.province = "jiangsu") |
| **实际抓取省** | jiangsu (cell.actual_province = "jiangsu") — 无 substitute |
| **首选 URL** | `https://www.jiangsu.gov.cn/zwgk/` |
| **首选 HTTP** | 404 (Not Found, 146 bytes) |
| **fallback #1** | `https://www.jiangsu.gov.cn/` |
| **fallback #1 HTTP** | **200 REACHABLE** |
| **SHA256** | `def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534` |
| **file_size_bytes** | 82985 |
| **chain_index** | 1 (省府根 fallback) |
| **fallback_chain_used** | ["zwgk_root", "province_root"]` |
| **verdict** | REACHABLE |
| **substitute_used** | false |
| **HTTP attempts (本 cell)** | 2 |

---

## 2. 锚点 + WAF 三层交叉验证

| 维度 | guizhou | jiangsu |
|---|---|---|
| **锚点 (province-specific + 政务类 generic)** | 1215 hits (贵州 + 政务公开 + 政府公报 + 政府文件) | 306 hits (江苏 + 政务公开 + 政府公报 + 政府文件) |
| **WAF marker (`403 Forbidden\|WAF\|网防G01\|eventID`)** | 0 (REACHABLE 路径无 WAF) | 0 (REACHABLE 路径无 WAF) |
| **首字 `黔ICP备` / `苏ICP备`** | (无 ICP 标记可见; 但 provincial content 命中充分) | (无 ICP 标记可见; 但 provincial content 命中充分) |

**三层交叉验证通过**: SHA 字节级（不可篡改）+ 文件大小（防 truncation）+ 锚点命中（防空内容 + 防错站）。

---

## 3. HTTP 预算 vs 实测

| 指标 | 规划 | 实测 |
|---|---|---|
| HTTP 总数预算 | ≤12 | **3** |
| HTTP 总数实际 (sum of http_used list) | 2-10 预期 | **3** |
| Cell 1 (guizhou) attempts | ≤4 | **1** (zwgk 200) |
| Cell 2 (jiangsu) attempts | ≤4 | **2** (zwgk 404 → / 200) |

**HTTP 预算使用率**: 3/12 = 25%（剩余 9 HTTP 预算留给 651+ 后续 spike；本次比 649 6/12 = 50% 更省）。

---

## 4. 真实 SHA 区分表（per docs/73 §4.2 沿用）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| **24** | **650** | **guizhou** | **gz /zwgk/(200)** | **`5c5b1295...`** | **直接 REACHABLE (chain_index=0)** |
| **25** | **650** | **jiangsu** | **js /zwgk/(404)→/(200)** | **`def18a2f...`** | **fallback #1** |

650 全部 2 SHA ≠ 638-649 全部 23 SHA ✓ distinct

---

## 5. lineage JSONB 真实化 sentinel 落地

### 5.1 lineage JSONB schema（650 落地版）

```json
{
  "chain_id": "real_650_m4_13_policy_detail_v7",
  "source_file_sha256": "<SAMPLE_SHA>",
  "source_file_url": "<SAMPLE_URL>",
  "extractor_version": "v1.0",
  "is_demo": "false",
  "original_province": "<guizhou|jiangsu>",
  "actual_province": "<guizhou|jiangsu>",
  "substitute_used": false
}
```

### 5.2 16 INSERT lineage 落地清单

| 表 | 行数 | lineage.is_demo | chain_id | UUID prefix |
|---|---|---|---|---|
| source_registry | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i02/i03 |
| source_document | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i04/i05 |
| policy_document | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i11/i12 |
| policy_target | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i21/i22 |
| policy_measure | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i31/i32 |
| government_commitment | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i41/i42 |
| commitment_progress | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i51/i52 |
| project_event | 2 | 'false' | real_650_m4_13_policy_detail_v7 | i61/i62 |

总计：2 × 6 = **12 INSERT** 政策表 + 4 source = **16 INSERT** ✓

### 5.3 chain_id 严格区分

- 650 `real_650_m4_13_policy_detail_v7` ≠ 649 `real_649_m4_12_policy_detail_v6` ≠ 648 `real_648_m4_11_policy_detail_v5` ≠ 647 `real_647_m4_10_policy_detail_v4` ≠ 646 `real_646_m4_9_policy_detail_v3` ≠ 645 `real_645_m4_8_policy_detail_v2` ≠ 644 `real_644_m4_7_policy_detail` ≠ 643 `real_643_m4_6_govreport` ≠ 642 `real_642_m4_5_renmian` ≠ 641 `real_641_heilongjiang`

### 5.4 UUID prefix 严格递增

- 650 i 段 (i0/i1-i6 eebc99) ≠ 649 h 段 (h0/h1-h6 eebc99) ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段

---

## 6. substitute 池状态（per 649 §4.4 + 650 增量）

| 池成员 | 状态 (649 后) | 状态 (650 后) | 实际是否激活 |
|---|---|---|---|
| **liaoning** | **✓ 649 激活** | ✓ 649 激活 | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| shaanxi | 备而未触发 | 备而未触发 (优先级 1; 留给 651+) | 备而未触发 |
| sichuan | 备而未触发 | 备而未触发 (优先级 2; 留给 651+) | 备而未触发 |
| guizhou | 备而未触发 | ✓ **650 直接 REACHABLE** | gz /zwgk/ 200 |
| jiangsu | 备而未触发 | ✓ **650 fallback REACHABLE** | js /zwgk/ 404 → / 200 |

**650 substitute_used_count = 0** (双样本均原生 REACHABLE; 递补池备而未触发)。

---

## 7. 649 P3-1 蓝图更正落地（per 650-A.0）

| 项 | 更正前 | 更正后 | 行内 append 尾注 |
|---|---|---|---|
| h02 source_registry.province | `'HUBEI'` | `'LIAONING'` | ✓ |
| h02 source_registry.source_name | `'湖北省人民政府 政务公开 landing (hubei 412+412 → liaoning 递补省府根 /)'` | `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | ✓ |
| h04 source_document.title | `'湖北省人民政府 政务公开 landing (hubei→liaoning 递补)'` | `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | ✓ |
| h11 policy_document.title | `'省政府政策详情 v6（湖北政务公开 landing, hubei→liaoning 递补）'` | `'省政府政策详情 v7（辽宁政务公开 landing, hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正）'` | ✓ |
| h11 policy_document.publisher | `'湖北省人民政府'` | `'辽宁省人民政府'` | ✓ |
| h41 government_commitment.commitment_text | `'...湖北省政府, hubei→liaoning 递补...'` | `'...辽宁省政府, hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正...'` | ✓ |
| h51 commitment_progress.reporting_org | `'湖北省人民政府 (hubei→liaoning 递补)'` | `'辽宁省人民政府 (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | ✓ |
| h61 project_event.description | `'湖北省政府政策详情页落地; ...'` | `'辽宁省政府政策详情页落地 (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正); ...'` | ✓ |
| h41 + h61 geo_entity.canonical_name (FK lookup) | `'湖北省'` | `'辽宁省'` | ✓ |
| 文件末尾 尾注块 | (无) | 增补: `650-A.0 行内更正 尾注 (per 649 审计 P3-1 / 2026-09-01)` | ✓ |
| lineage JSONB `original_province='hubei'` / `actual_province='liaoning'` | 保留 | 保留 (per 红线 13 增补规范) | (不删行; lineage 内 provenance 留痕) |

**红线 13 规范固化**（per 649 审计 P3-1）: **代换行 source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB**。

---

## 8. 附属产物指针（per 648 审计 P3-1）

- 主 evidence: `evidence_pack/m4_13_policy_detail_real_v7_20260901.json`
- 附属 report（本文件）: `docs/reports/m4_13_policy_detail_real_v7_20260901.md`
- 主 evidence `summary.methodology` 含指针: "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. 代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1). → docs/reports/m4_13_policy_detail_real_v7_20260901.md"
- docs/74 §4.5 双向登记 ✓

---

## 9. 验收

- ✓ 主 evidence JSON 落盘 `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` (REAL_FETCHED + 2 SHA + http_count=3)
- ✓ 附属 report 落盘 `docs/reports/m4_13_policy_detail_real_v7_20260901.md`（本文件）
- ✓ seed SQL 落盘 `scripts/seed_m4_13_policy_detail_real_v7.sql`（16 INSERT）
- ✓ fetch script 落盘 `scripts/fetch_m4_13_policy_detail_v7_2024.py`
- ✓ 架构师审查文档落盘 `docs/74-m4-13-policy-detail-real-v7-20260901.md`
- ✓ 649 蓝图更正落盘 `scripts/seed_m4_12_policy_detail_real_v6.sql`（P3-1 行内更正 + 尾注）
- ✓ docs/73 §6.1 尾注登记
- ✓ tests 落盘 `tests/test_m4_13_policy_detail_real_v7.py`（≥8 cases; 含 P3-1 更正守门）
- ✓ ≥106 pytest green（含 649 回归 98 + M4.13 新 ≥8）
- ✓ 不宣称任何 PASS（红线 1）; 不宣布 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS

---

— End M4.13 v7 真实化 spike 附属报告 20260901 —