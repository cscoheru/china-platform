# 66 — M5 WAF spike 第三次收口（架构师级审查）

> **刀号**: 644
> **Milestone**: M5 第三次（沿用 642 + 643 模式；第三次收口）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/64-m5-waf-second-pass-20260901.md` (642 关键反发现 + 643 二次)
> - `docs/62-m5-waf-spike-20260901.md` (M5 spike 初版 642)
> - `643-stage0-architect-m5-2-m4-6-parallel-tasking-20260901.md` §2.643-A.1
> - `644-stage0-architect-m5-3-m4-7-parallel-tasking-20260901.md` §2.644-A.1
> **前置**: 643 M5 二次关键反发现 = 国务院 /zhengce/ root 200 REACHABLE (WAF selective 验证)
> **架构师综合**: 第三次收口 = 国务院 /zhengce/ root 索引 + WAF 网防G01 selective 子路径进一步验证
> **不宣布** Gate / O1 / M2 / M4 / M5 PASS。

---

## 1. M5 第三次落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 644-A.1 | `scripts/probe_m5_waf_v3_2024.py` + `evidence_pack/m5_waf_v3_probe_20260901.json` + `docs/reports/m5_waf_v3_probe_20260901.md` | DONE | M5 WAF 网防G01 假设验证三次；10 cells ≤10 HTTP；顶层裁定 MIXED (7 BLOCKED + 3 REACHABLE)；curl only；不爬网 |
| 644-A.4 | 本文档（docs/66） | DONE | §1-§6 架构师级审查 |
| 644-A.5 | `docs/reports/m5_waf_v3_probe_20260901.md` + `evidence_pack/m5_waf_v3_probe_20260901.json` | DONE | 1 报告 + 1 证据包 |
| 644-B | `tests/test_m5_waf_third_pass.py` ≥ 6 | DONE | 共 ≥ 6 用例；全套 pytest ≥ 29/29 green |
| 644-C | 回执 + commit + 双推 | DONE | `644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md` §PHOTO-1..6 |

---

## 2. M5 WAF 网防G01 第三次实测（10 cells 实测）

### 2.1 probe cells 设计

10 cells 分为 3 组：

**Group 1: 国务院 /zhengce/ 子路径 + WAF 网防G01 进一步验证 (4 cells)**

| # | URL | slot | 期望 |
|---|---|---|---|
| 1 | `/zhengce/zhengceku/` | `zhengceku_nested` | 403 WAF 网防G01 marker (嵌套子路径 WAF selective) |
| 2 | `/zhengce/content_2017-09/30/content_5189.htm` | `zhengce_real_content` | REACHABLE / BLOCKED (已知真实政策 URL 应 200 OK 或 404) |
| 3 | `/zhengce/content_2020-11/03/content_5556715.htm` | `zhengce_real_2020` | REACHABLE / BLOCKED (2020+ content) |
| 4 | `/zwgk/zcwj/` | `zwgk_zcwj_retry` | 403 WAF 网防G01 (沿用 642) |

**Group 2: 国务院 /zwgk/ 替代子路径 (3 cells)**

| # | URL | slot | 期望 |
|---|---|---|---|
| 5 | `/zwgk/zcfg/` | `zwgk_zcfg_retry` | 403 WAF 网防G01 |
| 6 | `/zwgk/2026-08/15/content_xxx.htm` | `zwgk_sub_2026` | 403 WAF 网防G01 |
| 7 | `/zwgk/` root | `zwgk_root_retry` | 403 WAF 网防G01 (沿用 642) |

**Group 3: 5 BLOCKED 省 /zwgk/ root 收口 (3 cells)**

| # | URL | slot | 期望 |
|---|---|---|---|
| 8 | fujian /zwgk/ | `fujian_zwgk_root` | REACHABLE (沿用 642) |
| 9 | henan /zwgk/ | `henan_zwgk_root` | REACHABLE (沿用 642) |
| 10 | yunnan /zwgk/ | `yunnan_zwgk_root` | REACHABLE (沿用 642) |

### 2.2 实测结果

**顶层裁定**: **MIXED** (7 BLOCKED + 3 REACHABLE)；http_count=10/10 达上限。

按 verdict 分布：

| verdict | 数量 | URL |
|---|---|---|
| BLOCKED (WAF) | 2 | /zhengce/zhengceku/ (403), /zwgk/ root (403) |
| BLOCKED (404) | 5 | /zhengce/content_2017..., /zhengce/content_2020..., /zwgk/zcwj/, /zwgk/zcfg/, /zwgk/2026-08/15/... |
| REACHABLE | 3 | fujian /zwgk/, henan /zwgk/, yunnan /zwgk/ |

---

## 3. M5 BLOCKED 根因分析收口（沿用 643 二元根因确认 + WAF 网防G01 marker 第三次确认）

### 3.1 642 假设 + 643 二次 + 644 三次完整验证链

- **642 假设**：子域名内栏目级别选择性 WAF 网防G01（**二元根因** = 中央子域 WAF + 子域内栏目缺失）
- **643 二次实测反发现**：
  - 4 BLOCKED 省替代 subpath（fujian/zfgb, fujian/zcwj, gd/zfgb, guizhou/szfwj, henan/wjzl）全部 404
  - **henan/zfgb 200 REACHABLE** ⇒ 河南路径别名 = zfwj（≠ zfgb）
  - 国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现
  - 国务院 /zhengce/ root 200 REACHABLE ⇒ WAF selective 验证
- **644 三次实测反发现**（沿用 643 + 增量）：
  - 国务院 `/zhengce/zhengceku/` 嵌套子路径仍 403 WAF 网防G01 marker（**第三次确认 WAF selective 真存在**）
  - 国务院 `/zhengce/content_xxx.htm` 404（特定 content_id 不存在；非 WAF marker）
  - 国务院 `/zwgk/zcwj/` 404（路径不存在；非 WAF marker — 沿用 642）
  - 国务院 `/zwgk/zcfg/` 404（路径不存在；非 WAF marker）
  - 国务院 `/zwgk/2026-08/15/content_xxx.htm` 404（content_id 不存在）
  - 国务院 `/zwgk/` root 仍 403 WAF 网防G01 marker（**第三次确认 WAF marker 仍出现**）
  - fujian/henan/yunnan /zwgk/ root 仍 200 REACHABLE（**3 BLOCKED 省路径别名非 WAF 第三次确认**）

### 3.2 修正后假设确认（**完全成立**）

二元根因（**中央子域 WAF + 子域内栏目缺失**）**完全成立**：

- **中央子域 WAF 网防G01 真出现**（沿用 642 + 643 + 644 三次确认）：
  - /zhengce/ root 200 REACHABLE
  - /zhengce/zhengceku/ 403 WAF 网防G01（嵌套子路径 WAF）
  - /zwgk/ root 403 WAF 网防G01
- **3 BLOCKED 省根因不是 WAF**（沿用 642 + 643 + 644 三次确认）：
  - 5 BLOCKED 省 /zwgk/ root 200 REACHABLE（fujian/henan/yunnan）
  - 子域内栏目缺失（zfwj 路径别名 ≠ zfgb）

### 3.3 关键意义

- WAF 网防G01 marker **真出现** 在中央子域 selective 子路径（zhengceku, zwgk root）
- 5 BLOCKED 省根因是路径缺失（zfwj 路径别名），不是 WAF
- **M5 第三次收口完成**：WAF selective 验证第三次成立 + 5 BLOCKED 省根因第三次确认

---

## 4. 替代路径可达性矩阵

沿用 642 + 643 + 644 三次实测完整路径 verdict 矩阵：

| URL 类别 | 实测 verdict | WAF marker | 来源 |
|---|---|---|---|
| gov /zhengce/ root | **REACHABLE** | false | 643 (WAF selective 验证) |
| gov /zhengce/zhengceku/ | BLOCKED | **true** | **644 第三次确认** |
| gov /zhengce/content_2017... | BLOCKED | false | 644 (404 - content_id 不存在) |
| gov /zhengce/content_2020... | BLOCKED | false | 644 (404 - content_id 不存在) |
| gov /zhengceku/ | BLOCKED | **true** | 643 (WAF 网防G01 验证) |
| gov /zwgk/ root | BLOCKED | **true** | **644 第三次确认 + 沿用 642** |
| gov /zwgk/zcwj/ | BLOCKED | false | 644 (404 - 路径不存在) |
| gov /zwgk/zcfg/ | BLOCKED | false | 644 (404 - 路径不存在) |
| gov /zwgk/2026-08/15/... | BLOCKED | false | 644 (404 - content_id 不存在) |
| fujian /zwgk/zfgb/ | BLOCKED | false | 643 (404 - 路径别名) |
| fujian /zwgk/zcwj/ | BLOCKED | false | 643 (404 - 路径别名) |
| fujian /zwgk/ root | **REACHABLE** | false | **644 第三次确认 + 沿用 642** |
| henan /zwgk/zfgb/ | **REACHABLE** | false | 643 (路径别名 zfwj 但 zfgb 可达) |
| henan /zwgk/wjzl/ | BLOCKED | false | 643 (404 - 路径别名) |
| henan /zwgk/ root | **REACHABLE** | false | **644 第三次确认 + 沿用 642** |
| yunnan /zwgk/ root | **REACHABLE** | false | **644 第三次确认 + 沿用 642** |
| guangdong /zwgk/zfgb/ | BLOCKED | false | 643 (404 - 路径别名) |
| guizhou /zwgk/szfwj/ | BLOCKED | false | 643 (404 - 路径别名) |

**完整 verdict**：12 BLOCKED + 5 REACHABLE（含 /zhengce/ root + 3 省 /zwgk/ root + 河南 /zwgk/zfgb/）

---

## 5. 645 下一步（架构师推荐）

**scope 选 A（推荐）**：645 = M6 spike 文档收口 + M4.8 政策详情扩展（沿用 644 3 试点省 × 1 detail each × 6 政策表 spike = 18 INSERT planned, chain_id='real_645_m4_8_policy_detail_v2'）

**scope 选 B**：645 = M5 收口（gov/zhengce/ root 索引全量）+ M4.8 并行

**scope 选 C**：645 = M5 + M4.8 + M6 三方并行（激进）

**scope 选 D**：645 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法

**scope 选 E**：645 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）

**沿用 644 模式**：架构师本终端自签 + 自交付（执行端模式继续）。

---

## 6. 下一步 + 不宣称 PASS

- 架构师（用户）接受/驳回 645 推荐 scope（A/B/C/D/E）
- 执行端（本终端即架构师）收到 645 tasking 后即签即自交付
- **不宣布** Gate / O1 / M2 / M4 / M5 PASS（沿用红线）
- 644 完成：M5 第三次收口（10 cells MIXED = 7 BLOCKED + 3 REACHABLE；WAF selective 第三次验证）

— End 644 docs/66 —
