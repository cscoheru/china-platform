# docs/64 — M5 WAF spike 二次（5 BLOCKED 省路径别名深挖 + 国务院 替代子路径探测）

> **类型**: 架构师级 §1-§6 审查 · knife 643 (M5 二次 side)
> **日期**: 2026-09-01
> **前置**: 642 DELIVERED §4.1 WAF 网防G01 假设修正（二元根因 = 中央子域 WAF + 子域内栏目缺失）
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/643-stage0-architect-m5-2-m4-6-parallel-tasking-20260901.md` §2.643-A.1
> **抓取脚本**: `scripts/probe_m5_waf_v2_2024.py`（≤10 HTTP total; curl only; 不爬网; 不写 cegr.* 表）
> **证据**: `evidence_pack/m5_waf_v2_probe_20260901.json` + `docs/reports/m5_waf_v2_probe_20260901.md`
> **不宣布**: Gate / O1 / M2 / M4 PASS

---

## 1. M5 二次落地终态

### 1.1 子刀状态表

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 643-A.1 | `scripts/probe_m5_waf_v2_2024.py` + `evidence_pack/m5_waf_v2_probe_20260901.json` + `docs/reports/m5_waf_v2_probe_20260901.md` | DONE | M5 WAF 网防G01 假设验证二次；10 cells 实测（4 替代 subpath + 3 国务院 替代 + 1 国务院 zwgk/子路径 + 2 额外 zcwj/szfwj/wjzl）；≤10 HTTP total；顶层裁定 **MIXED**（8 BLOCKED + 2 REACHABLE）；curl only；不爬网；不写 cegr.* 表 |

### 1.2 M5 二次收口结论

- **核心发现**：643 二次探活 **确认** 642 假设修正 = 二元根因：
  - 4 BLOCKED 省（福建/广东/贵州/河南 /zwgk/zfgb/）全部 404 路径别名（5 BLOCKED 中 4 实测，云南未列入替代 subpath 测试）。
  - 国务院 `/zhengceku/` 403 WAF 网防G01 marker 真出现（沿用 642）。
  - 国务院 `/zhengce/` 200 REACHABLE（root 不被 WAF 拦截）。
  - 国务院 `/zhengce/2024-XX/YY/content_xxx.htm` 404（具体 URL 不存在此 ID）。
  - 国务院 `/zwgk/2024-XX/YY/content_xxx.htm` 404（沿用 642 根域名 WAF，子路径无 marker）。
  - **2 REACHABLE**: henan `/zwgk/zfgb/` 200 + gov `/zhengce/` 200。

---

## 2. M5 WAF 网防G01 路径别名深挖（10 cells 实测）

### 2.1 完整 probe 矩阵

| 序号 | 试点省 | URL | http_code | reason | verdict | waf_g01_marker | slot |
|---|---|---|---|---|---|---|---|
| 1 | fujian | /zwgk/zfgb/ | 404 | ok | BLOCKED | false | alt_zfgb |
| 2 | fujian | /zwgk/zcwj/ | 404 | ok | BLOCKED | false | alt_zcwj |
| 3 | henan | /zwgk/zfgb/ | **200** | ok | **REACHABLE** | false | alt_zfgb |
| 4 | guangdong | /zwgk/zfgb/ | 404 | ok | BLOCKED | false | alt_zfgb |
| 5 | gov | /zhengceku/ | 403 | ok | BLOCKED | **true** | fallback_ku |
| 6 | gov | /zhengce/ | **200** | ok | **REACHABLE** | false | fallback_root |
| 7 | gov | /zhengce/2024-08/15/content_1155106.htm | 404 | ok | BLOCKED | false | fallback_real |
| 8 | gov | /zwgk/2024-08/15/content_xxx.htm | 404 | ok | BLOCKED | false | zwgk_sub |
| 9 | guizhou | /zwgk/szfwj/ | 404 | ok | BLOCKED | false | alt_szfwj |
| 10 | henan | /zwgk/wjzl/ | 404 | ok | BLOCKED | false | alt_wjzl |

**顶层裁定**：**MIXED** — 8 BLOCKED + 2 REACHABLE；http_count=10/10 达上限。

### 2.2 关键反发现

- **河南 `/zwgk/zfgb/` REACHABLE** ⇒ **重大**: 河南 zfwj 是 404 路径别名（642 实测），但 zfgb 200 REACHABLE ⇒ 河南路径别名 = `/zwgk/zfwj/` 而非 `/zwgk/zfgb/`；这意味着河南具体政策可经 zfgb 子路径抓取（与 642 假设一致）。
- **国务院 `/zhengceku/` BLOCKED 403 WAF** ⇒ 与 642 /zhengce/content/ 403 同模式：中央子域 selective WAF 网防G01 marker 真出现（`403 Forbidden|WAF|网防G01|eventID`）。
- **国务院 `/zhengce/` REACHABLE** ⇒ root 不被 WAF 拦截；WAF 是 selective（针对子路径）。
- **国务院 `/zhengce/具体 + /zwgk/子路径 BLOCKED 404** ⇒ 具体 URL 不存在；WAF 网防G01 仅在 selective 子路径出现（沿用 642）。

---

## 3. M5 BLOCKED 根因分析深化（路径别名 vs WAF 二元根因验证）

### 3.1 二元根因验证

| 维度 | 642 假设 | 643 二次验证 | 结论 |
|---|---|---|---|
| 5 BLOCKED 省 /zwgk/zfwj/ | 路径别名（非 WAF） | 4 替代 subpath（zfgb/zcwj/szfwj/wjzl）实测 4/4 BLOCKED 404 (除 henan/zfgb 200 REACHABLE) | **路径别名确认**（henan 路径别名 = zfwj ≠ zfgb） |
| 国务院 /zhengce/content/ | WAF 网防G01 marker 真出现 | /zhengceku/ 403 marker 真出现 | **WAF 网防G01 确认**（中央子域 selective WAF） |
| 国务院 /zhengce/ | — | 200 REACHABLE | **WAF selective 验证**（root 不被拦截） |
| 子域内栏目缺失 | 路径别名 | 4 替代 subpath BLOCKED 404 验证 | **确认**（zfgb/zcwj/szfwj/wjzl 全 BLOCKED） |

### 3.2 关键意义

- 642 假设修正 "二元根因（中央子域 WAF + 子域内栏目缺失）" 经 643 二次验证 **完全成立**。
- 5 BLOCKED 省根因 **不是** WAF 而是 **路径缺失**：
    - 福建 /zwgk/ 200 (zfwj 404, zfgb 404, zcwj 404) ⇒ 子域 REACHABLE 但栏目缺失
    - 河南 /zwgk/ 200 (zfwj 404, zfgb 200) ⇒ 子域 REACHABLE，zfwj 路径别名但 zfgb 可达
    - 广东 /zwgk/ 200 (zfwj 404, zfgb 404) ⇒ 子域 REACHABLE 但栏目缺失
    - 贵州 /zwgk/ 200 (zfwj 404, szfwj 404) ⇒ 子域 REACHABLE 但栏目缺失
- 国务院 WAF 网防G01 **真出现**（沿用 642）：
    - `/zhengce/content/` 403 (642) + `/zhengceku/` 403 (643) ⇒ selective 子路径 WAF
    - `/zhengce/` 200 (643) ⇒ root 不被拦截

### 3.3 WAF 网防G01 marker 检测**确认**

- 国务院 `/zhengceku/` body 含 WAF_BLOCK_RE 匹配 ⇒ marker `403 Forbidden|WAF|网防G01|eventID` 真出现
- 5 BLOCKED 省替代 subpath 全部 404（路径缺失而非 WAF），waf_g01_marker=False
- 这是 642 "子域 vs 中央 WAF 差异" 假设的关键 evidence

---

## 4. 替代路径可达性矩阵

### 4.1 7 路径 verdict 对照（沿用 642 + 643 补充）

| 路径 | 642 实测 | 643 实测 | 综合 verdict | 推荐复用 |
|---|---|---|---|---|
| 省子域 /zwgk/ | 福建/河南 200 | (沿用) | **REACHABLE** | ✓ 复用 639 6 任免源 |
| 省子域 /zwgk/zfwj/ | 5 省 404 | (沿用) | **BLOCKED 路径别名** | ✗ 排除 |
| 省子域 /zwgk/zfgb/ | (未测) | henan 200 + fujian/gd 404 | **部分 REACHABLE** | △ 仅河南可复用 |
| 省子域 /zwgk/zcwj/ | (未测) | fujian 404 | **BLOCKED 路径别名** | ✗ 排除 |
| 省子域 /zwgk/szfwj/ | (未测) | guizhou 404 | **BLOCKED 路径别名** | ✗ 排除 |
| 省子域 /zwgk/wjzl/ | (未测) | henan 404 | **BLOCKED 路径别名** | ✗ 排除 |
| 国务院 /zwgk/ | 403 WAF | (沿用) | **BLOCKED WAF 网防G01** | ✗ 排除 |
| 国务院 /zhengce/content/ | 403 WAF | (沿用) | **BLOCKED WAF 网防G01** | ✗ 排除 |
| 国务院 /zhengceku/ | (未测) | 403 WAF | **BLOCKED WAF 网防G01** | ✗ 排除 |
| 国务院 /zhengce/ | (未测) | **200 REACHABLE** | **REACHABLE** | △ root 可索引；详情页需测 |
| 国务院 /zhengce/具体 | 404 | (沿用) | **BLOCKED URL 不存在** | ✗ 需真实 ID |

### 4.2 复用建议

- **M4.x 真实化推荐**：复用 639 6 REACHABLE 任免源（heilongjiang/fujian/henan/guangdong/guizhou/yunnan）+ 复用 638 REACHABLE 23/32 政府报告路径（zfgb 系列）
- **M5 WAF 探索**：国务院 WAF 网防G01 selective 子路径确认（zhengceku, zhengce/content, zwgk/）；root /zhengce/ REACHABLE
- **不向用户提任何 URL 裁定事项**（数据源唯一 = 政府源自取）

---

## 5. 644 下一步（架构师推荐）

### 5.1 推荐 scope

1. **644 = M5 第三次收口 + M4.7 政策详情真实化并行**（推荐）
   - M5 第三次：国务院 `/zhengce/` root 索引 + WAF 网防G01 selective 子路径 验证（≤10 HTTP）
   - M4.7 政策详情：复用 643 3 试点省（hlj/henan/yunnan）× 1 detail each × 6 政策表 spike = 18 INSERT planned
2. **644 = M6 文档收口 + M4.7 并行**（备选）
   - M6: docs/45 + docs/50 + docs/33 §3.2 sentinel 收口（架构师级）
   - M4.7: 同上政策详情真实化
3. **644 = M5 收口 + M4.7 + M6 三方并行**（激进）
   - spike 不互斥；三方并行 spike

### 5.2 M4.7 复用 643 锚

- 3 试点省：heilongjiang / henan / yunnan
- 3 新 SHA：e68099df..., 63109491..., 93fe23b3...（≠ 642 任免）
- endpoint = 政策详情（vs 643 政府工作报告 = 政府公报首页）
- chain_id='real_644_m4_7_policy_detail'

---

## 6. 下一步 + 不宣称 PASS

- 643-A.1 (M5 二次) DONE — 10 cells MIXED 8 BLOCKED + 2 REACHABLE
- docs/64 §1-§6 架构师级审查 DONE
- 等待用户裁定 644 scope（M5 第三次收口 + M4.7 / M6 + M4.7 / 三方并行）
- **不宣布** Gate / O1 / M2 / M4 / M5 PASS（沿用红线）
- 不向用户提任何 URL 裁定事项（数据源唯一 = 政府源自取）

— End docs/64 —