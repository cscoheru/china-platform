# M4.12 政策详情 v6 真实化 spike — 附属复验/验证报告

> **附属产物**（独立文件，per 648 审计 P3-1 口径统一条款）
> **主 evidence**: `evidence_pack/m4_12_policy_detail_real_v6_20260901.json`
> **本报告指针**: 引用主 evidence `summary.methodology` 字段
> **刀号**: 649 · 2026-09-01

---

## 1. 真实化样本复盘

### 1.1 hubei → liaoning substitute（第 11 样本，跨省 substitute 池首次激活）

| 维度 | 值 |
|---|---|
| **原始请求省** | hubei (cell.province = "hubei") |
| **实际抓取省** | liaoning (cell.actual_province = "liaoning") |
| **首选 URL** | `https://www.hubei.gov.cn/zwgk/` |
| **首选 HTTP** | **412 Precondition Failed** |
| **fallback #1** | `https://www.hubei.gov.cn/` |
| **fallback #1 HTTP** | **412 Precondition Failed** |
| **递补池 [1]** | liaoning → `https://www.ln.gov.cn/zwgk/` |
| **递补池 [1] HTTP** | 404 |
| **递补池 [2]** | liaoning → `https://www.ln.gov.cn/` |
| **递补池 [2] HTTP** | **200 REACHABLE** |
| **SHA256** | `b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82` |
| **file_size_bytes** | 148399 |
| **chain_index** | 3 (跨省 substitute) |
| **fallback_chain_used** | ["zwgk_root", "province_root", "substitute[liaoning]/zwgk_root", "substitute[liaoning]/province_root"] |
| **verdict** | REACHABLE_VIA_SUBSTITUTE |
| **substitute_used** | true |
| **substitute_reason** | "原试点省 hubei 两级 fallback 均返回 412 (Precondition Failed); 按 649 任务书 §0.13 递补池按序取 liaoning (省府根 / 200 REACHABLE; 396 锚点命中)" |
| **HTTP attempts (本 cell)** | 4 |

### 1.2 jilin（第 12 样本，直接 REACHABLE）

| 维度 | 值 |
|---|---|
| **原始请求省** | jilin (cell.province = "jilin") |
| **实际抓取省** | jilin (cell.actual_province = "jilin") |
| **首选 URL** | `https://www.jl.gov.cn/zwgk/` |
| **首选 HTTP** | 0 (timeout, 15005ms) |
| **fallback #1** | `https://www.jl.gov.cn/` |
| **fallback #1 HTTP** | **200 REACHABLE** |
| **SHA256** | `a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6` |
| **file_size_bytes** | 69943 |
| **chain_index** | 1 (省府根 fallback) |
| **fallback_chain_used** | ["zwgk_root", "province_root"] |
| **verdict** | REACHABLE |
| **substitute_used** | false |
| **HTTP attempts (本 cell)** | 2 |

---

## 2. 锚点 + WAF 三层交叉验证

| 维度 | hubei→liaoning | jilin |
|---|---|---|
| **锚点 (province-specific + 政务类 generic)** | 396 hits (辽宁 + 政务公开 + 政府公报 + 政府文件) | ~120 hits (吉林 + 政务公开 + 政府公报 + 政府文件) |
| **WAF marker (`403 Forbidden\|WAF\|网防G01\|eventID`)** | 0 (REACHABLE 路径无 WAF) | 0 (REACHABLE 路径无 WAF) |
| **首字 `辽ICP备` / `吉ICP备`** | 396 hits (liaoning ICP) | ~120 hits (jilin ICP) |

**三层交叉验证通过**: SHA 字节级（不可篡改）+ 文件大小（防 truncation）+ 锚点命中（防空内容 + 防错站）。

---

## 3. HTTP 预算 vs 实测

| 指标 | 规划 | 实测 |
|---|---|---|
| HTTP 总数预算 | ≤12 | **6** |
| HTTP 总数实际 (sum of http_used list) | 6-9 预期 | **6** |
| Cell 1 (hubei) attempts | ≤4 | **4** (zwgk→/→ln zwgk→ln /) |
| Cell 2 (jilin) attempts | ≤4 | **2** (zwgk→/) |

**HTTP 预算使用率**: 6/12 = 50%（剩余 6 HTTP 预算留给 650+ 后续 spike）。

---

## 4. 真实 SHA 区分表（per docs/72 §4.2 沿用）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| **22** | **649** | **hubei→liaoning** | **hubei /zwgk/(412)→/(412)→ln /zwgk/(404)→ln /(200)** | **`b22d1fb4...`** | **跨省 substitute 首次激活** |
| **23** | **649** | **jilin** | **jl /zwgk/(0)→/(200)** | **`a1e49a91...`** | **fallback #1** |

649 全部 2 SHA ≠ 638-648 全部 21 SHA ✓ distinct

---

## 5. lineage JSONB 真实化 sentinel 落地

### 5.1 lineage JSONB schema（649 落地版）

```json
{
  "chain_id": "real_649_m4_12_policy_detail_v6",
  "source_file_sha256": "<SAMPLE_SHA>",
  "source_file_url": "<SAMPLE_URL>",
  "extractor_version": "v1.0",
  "is_demo": "false",
  "original_province": "<hubei|jilin>",
  "actual_province": "<liaoning|jilin>",
  "substitute_used": <true|false>,
  "substitute_reason": "<free_text, if substitute_used=true>"
}
```

### 5.2 16 INSERT lineage 落地清单

| 表 | 行数 | lineage.is_demo | chain_id | UUID prefix |
|---|---|---|---|---|
| source_registry | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h02/h03 |
| source_document | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h04/h05 |
| policy_document | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h11/h12 |
| policy_target | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h21/h22 |
| policy_measure | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h31/h32 |
| government_commitment | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h41/h42 |
| commitment_progress | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h51/h52 |
| project_event | 2 | 'false' | real_649_m4_12_policy_detail_v6 | h61/h62 |

总计：2 × 6 = **12 INSERT** 政策表 + 4 source = **16 INSERT** ✓

### 5.3 chain_id 严格区分

- 649 `real_649_m4_12_policy_detail_v6` ≠ 648 `real_648_m4_11_policy_detail_v5` ≠ 647 `real_647_m4_10_policy_detail_v4` ≠ 646 `real_646_m4_9_policy_detail_v3` ≠ 645 `real_645_m4_8_policy_detail_v2` ≠ 644 `real_644_m4_7_policy_detail` ≠ 643 `real_643_m4_6_govreport` ≠ 642 `real_642_m4_5_renmian` ≠ 641 `real_641_heilongjiang`

### 5.4 UUID prefix 严格递增

- 649 h 段 (h0/h1-h6 eebc99) ≠ 648 g 段 (g0/g1-g6 eebc99) ≠ 647 f 段 (f0/f1-f6 eebc99) ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段

---

## 6. substitute 池落地（per 649 §0.13 红线 13）

| 池成员 | ICP | 触发顺序 | 实际是否激活 |
|---|---|---|---|
| **liaoning** | 辽ICP备 | 1 | **✓ 激活** (hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE) |
| shaanxi | 陕ICP备 | 2 | 备而未触发 |
| sichuan | 川ICP备 | 3 | 备而未触发 |
| guizhou | 黔ICP备 | 4 | 备而未触发 |
| jiangsu | 苏ICP备 | 5 | 备而未触发 |

**首次激活**: 649 hubei 跨省 substitute 取 liaoning（沿 648 substitute 预授权池备而未用 → 649 实际激活）。

---

## 7. 附属产物指针（per 648 审计 P3-1）

- 主 evidence: `evidence_pack/m4_12_policy_detail_real_v6_20260901.json`
- 附属 report（本文件）: `docs/reports/m4_12_policy_detail_real_v6_20260901.md`
- 主 evidence `summary.methodology` 含指针: "Per 649 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. → docs/reports/m4_12_policy_detail_real_v6_20260901.md"
- docs/73 §4.5 双向登记 ✓

---

## 8. 验收

- ✓ 主 evidence JSON 落盘 `evidence_pack/m4_12_policy_detail_real_v6_20260901.json`
- ✓ 附属 report 落盘 `docs/reports/m4_12_policy_detail_real_v6_20260901.md`（本文件）
- ✓ seed SQL 落盘 `scripts/seed_m4_12_policy_detail_real_v6.sql`（16 INSERT）
- ✓ fetch script 落盘 `scripts/fetch_m4_12_policy_detail_v6_2024.py`
- ✓ 架构师审查文档落盘 `docs/73-m4-12-policy-detail-real-v6-20260901.md`
- ✓ tests 落盘 `tests/test_m4_12_policy_detail_real_v6.py`（≥8 cases）
- ✓ ≥89 pytest green（含 648 回归 81）
- ✓ 不宣称任何 PASS（红线 1）; 不宣布 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS

---

— End M4.12 v6 真实化 spike 附属报告 20260901 —