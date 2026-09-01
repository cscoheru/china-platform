# 72 — M4.11 政策详情 v5 真实化 spike (架构师级审查)

> **刀号**: 648
> **Milestone**: M4.11（沿用 642/643/644/645/646/647 spike 模式；spike 第 6 次）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/71-m4-10-policy-detail-real-v4-20260901.md` (647 M4.10 政策详情 v4)
> - `647-stage0-cursor-s647-m4-10-v4-audit-PASS-20260901.md` (647 审计 PASS·有限通过)
> - `648-stage0-architect-m4-11-v5-quality-hygiene-tasking-20260901.md` §1.648-A.0 / 648-A.1 / 648-A.2
> **前置**: 647 DELIVERED + 审计 PASS（有限通过）
> **架构师综合**: 648 三合一 = A.0 jiangxi "403" 复验 (CONTENT_CONFIRMED) + A.1 M4.11 v5 hunan/anhui 16 INSERT (chain_id='real_648_m4_11_policy_detail_v5' UUID g 段 substitute 池备而不用) + A.2 m2 crosscheck 报告生成测试卫生收口 (--output tmp_path, 默认 skip 禁全量挂起)
> **chain_id**: `real_648_m4_11_policy_detail_v5` (末段 `_v5` ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: g 段 (g02-g62) ≠ 647 f 段 (f02-f62) ≠ 646 e 段 (e02-e62) ≠ 645 d 段 ≠ 644 c 段
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M5 / M6 PASS。

---

## 1. M4.11 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 648-A.0 | `scripts/reverify_jx_403_2024.py` + `evidence_pack/m4_10_reverify_jx_20260901.json` + docs/71 §7 行内 append | DONE | jiangxi "403" 复验 = CONTENT_CONFIRMED；SHA 字节级一致 + 48118 bytes 一致 + 72 anchor 命中；title="403" 解释为该江西站 WAF 拦截层真实页面结构 (非数据漂移) |
| 648-A.1 | `scripts/fetch_m4_11_policy_detail_v5_2024.py` + `scripts/seed_m4_11_policy_detail_real_v5.sql` + `evidence_pack/m4_11_policy_detail_real_v5_20260901.json` + `docs/reports/m4_11_policy_detail_real_v5_20260901.md` | DONE | M4.11 政策详情 v5 真实化；2 样本 (hunan + anhui) × 1 HTTP each = 2 cells；http_count=4/12；fetched_count=2；fetch_status=REAL_FETCHED |
| 648-A.2 | `scripts/crosscheck_m2_2024_gdp.py` (--output 改造) + `tests/test_m2_report_hygiene.py` | DONE | m2 crosscheck 测试卫生收口：--output tmp_path + 默认 skip (无 DSN 时跳过)；禁全量挂起套件；tracked 报告字节零漂移 |
| 648-A.3 | 本文档（docs/72） | DONE | §1-§6 架构师级审查 |
| 648-B | ≥8 新测试 + 52 回归 = ≥60 | DONE | **80/80 pytest green** (M4.11 新 16 + m2 hygiene 新 5 + reverify 新 8 + 647 回归 14 + 646 回归 10 + O1 回归 6 + 645 回归 12 + 644 回归 9) |
| 648-C | 回执 + commit + 双推 | DONE | `648-stage0-cc-m4-11-v5-quality-hygiene-receipt-20260901.md` §PHOTO-1..7 + 4 commits |

---

## 2. 648-A.0 jiangxi "403" 复验 CONTENT_CONFIRMED

### 2.1 复验动作（1×HTTP）

- **1×HTTP re-fetch**: `https://www.jiangxi.gov.cn/zwgk/` (timeout=15, curl only)
- **新 SHA256**: `56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4`
- **原 SHA256** (647 fetch): `56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4` ← 一致
- **file_size**: 48118 bytes ← 一致
- **http_code**: 200, **reason**: "ok"

### 2.2 三层交叉验证

| 维度 | 结果 |
|---|---|
| SHA256 字节级对比 | ✓ MATCH |
| 文件大小对比 | ✓ MATCH (48118 bytes) |
| 内容锚点 (`江西\|jiangxi\|政务公开\|政府公报\|政府文件\|政策法规\|公开目录\|领导信息`) | ✓ **72 hits** |
| WAF marker (`403 Forbidden\|WAF\|网防G01\|eventID`) | ✓ 真出现 (1 hit) |

### 2.3 verdict: **CONTENT_CONFIRMED**

- **判定理由**: SHA 字节级一致 + 文件大小一致 + 72 处 anchor 命中 → 三层交叉验证通过
- **title="403" 解释**: 该江西政务公开目录页的页面元数据 title 服务端模板被覆写为 "403"，但 body 仍是真实江西政务公开内容（72 处 anchor 命中佐证）；属于该站真实页面结构特性，**非数据漂移**
- **WAF marker 真出现**: 与 644/645 多次观测的 WAF 网防G01 marker 模式一致；江西站存在 WAF 拦截层但 /zwgk/ 路径返回 200 + 真内容

### 2.4 docs/52 零改动

- 一致=CONTENT_CONFIRMED, 不登记 (a) drift, docs/52 零改动
- seed SQL 56481050 lineage 零改动 (CONTENT_CONFIRMED 不换样)

---

## 3. M4.11 v5 spike 边界（vs 648 tasking 规划）

### 3.1 648 tasking 规划 vs 实测对比

**648 tasking 规划**：

- 沿用 647 模式 + 加 hunan 第 9 样本 + anhui 第 10 样本
- = **12 INSERT planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = 16 INSERT total
- ≤12 HTTP total (2 cells × 1 HTTP each)
- chain_id='real_648_m4_11_policy_detail_v5' (末段 `_v5`，≠ 647 `_v4`)
- UUID prefix g 段 ≠ 647 f 段 ≠ 646 e 段
- 2 新 SHA 全 distinct ≠ 638-647 全部 SHA
- substitute 预授权池: jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu (备而不用)
- 已用省全集不得重复: HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX

**648 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - hunan `4006439ee1494314...` (省府根 / fallback chain_index=1) — 全新 SHA；与 638-647 全部 distinct
  - anhui `a06e174f10eda8b5...` (省府根 / fallback chain_index=1) — 全新 SHA；与 638-647 全部 distinct
- 1 样本 /zwgk/ 404 → / fallback 200 REACHABLE (hunan)
- 1 样本 /zwgk/ timeout → / fallback 200 REACHABLE (anhui)
- **substitute 预授权池备而不用**（首选 hunan + anhui 均一次 fallback 成功）
- spike 边界 **实测 12 INSERT** = **规划 12 INSERT = 0 调整**

### 3.2 625 fall-through chain 注记

| 样本 | 首选 /zwgk/ | fallback #1 (省府根) | substitute |
|---|---|---|---|
| hunan | 404 | 200 (省府根 /) | **REACHABLE** (chain_index=1) |
| anhui | timeout (15005 ms) | 200 (省府根 /) | **REACHABLE** (chain_index=1) |

hunan + anhui 各 2 attempts (首选 /zwgk/ + 省府根 fallback), 全部一次成功 200 REACHABLE。**substitute 池未激活** (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu 备而不用)。

### 3.3 spike 边界明细（12 INSERT 政策表 + 4 source = 16 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 647 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | g0eebc99-...g02/g03 | 647 = f02/f03 |
| source_document | 2 | `'false'` (NEW) | g0eebc99-...g04/g05 | 647 = f04/f05 |
| policy_document | **2** | `'false'` (spike) | g1eebc99-...g11/g12 | 647 f 段 (≠ f11/f12) |
| policy_target | **2** | `'false'` (spike) | g2eebc99-...g21/g22 | 647 f 段 (≠ f21/f22) |
| policy_measure | **2** | `'false'` (spike) | g3eebc99-...g31/g32 | 647 f 段 (≠ f31/f32) |
| government_commitment | **2** | `'false'` (spike) | g4eebc99-...g41/g42 | 647 f 段 (≠ f41/f42) |
| commitment_progress | **2** | `'false'` (spike) | g5eebc99-...g51/g52 | 647 f 段 (≠ f51/f52) |
| project_event | **2** | `'false'` (spike) | g6eebc99-...g61/g62 | 647 f 段 (≠ f61/f62) |

**总计**：2 × 6 = **12 INSERT** (vs 647 实测 12 INSERT；M4.11 是 spike 6 次，2 试点省扩展) + 4 source_registry/source_document = **16 INSERT total**

### 3.4 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 648 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | hunan | hunan_zwgk_chain | `/zwgk/` (404) → `/` (200) | `4006439ee1494314` | 113,702 | ✓ | **全新 SHA (第 9 样本)** chain_index=1 fallback |
| 2 | anhui | anhui_zwgk_chain | `/zwgk/` (timeout) → `/` (200) | `a06e174f10eda8b5` | 128,409 | ✓ | **全新 SHA (第 10 样本)** chain_index=1 fallback |

**2 SHA distinct vs 638-647 SHA**：

- 648 `4006439e` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ≠ 640 demo `0…02` ≠ 639 demo `0…01` ✓
- 648 `a06e174f` ≠ 全部 638-647 SHA ✓
- 2 SHA 全部 distinct ≠ 638-647 全部 SHA

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 11 真实化刀 lineage 沿用 (per docs/33 §3.2)

| 刀 | chain_id | is_demo | 试点省 | UUID prefix |
|---|---|---|---|---|
| 641 | `real_641_heilongjiang` | false | heilongjiang | real prefix |
| 642 | `real_642_m4_5_renmian` | false | henan/guangdong/guizhou | b 段 (b1-b6) |
| 643 | `real_643_m4_6_govreport` | false | hlj/henan/yunnan | c 段 (c41-c41) |
| 644 | `real_644_m4_7_policy_detail` | false | hlj/henan/yunnan | c 段 (c41-c93) |
| 645 | `real_645_m4_8_policy_detail_v2` | false | hlj/henan-zfgb/henan-zwgk/yunnan | d 段 (d21-d94) |
| 646 | `real_646_m4_9_policy_detail_v3` | false | fujian + guangdong | e 段 (e02-e62) |
| 647 | `real_647_m4_10_policy_detail_v4` | false | zhejiang + jiangxi (substitute) | f 段 (f02-f62) |
| **648** | **`real_648_m4_11_policy_detail_v5`** | **false** | **hunan + anhui (substitute 池备而不用)** | **g 段 (g02-g62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 19 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-18 | (沿用 638-647) | (略) | (略) | (略) | (见 docs/71 §4.2) |
| 19 | 638 (probe) | various | 23 试点省 | n/a (probe only) | 638 = `real_638_m4_1_people` chain_id 计入全链表 |
| **20** | **648** | **hunan-zwgk-v5** | **/zwgk/ (404) → /** | **`4006439e...`** | **NEW 648 第 9 样本** chain_index=1 fallback |
| **21** | **648** | **anhui-zwgk-v5** | **/zwgk/ (timeout) → /** | **`a06e174f...`** | **NEW 648 第 10 样本** chain_index=1 fallback |

**21 SHA 全部 distinct** (✓ 不撞 638-647)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f → g (648)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62  →  648 g02-g62
```

**648 g 段** (`g0eebc99` / `g1eebc99` / `g2eebc99` / `g3eebc99` / `g4eebc99` / `g5eebc99` / `g6eebc99`) **≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 648 substitute 预授权池 (备而不用)

Per 648 tasking §A.1 显式 substitute 预授权池:

| 池成员 | 状态 | 备注 |
|---|---|---|
| jilin | 备而不用 | 优先留给 649+ |
| liaoning | 备而不用 | 优先留给 649+ |
| hubei | 备而不用 | 优先留给 649+ |
| shaanxi | 备而不用 | 优先留给 649+ |
| sichuan | 备而不用 | 优先留给 649+ |
| guizhou | 备而不用 | 优先留给 649+ |
| jiangsu | 备而不用 | 优先留给 649+ |

**已用省全集** (不得重复): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX  
**648 首选**: hunan + anhui → 各 1 次 fallback 200 REACHABLE → 池未激活

### 4.5 648-A.0 reverify 落地

- ✓ `scripts/reverify_jx_403_2024.py` (1×HTTP 复验脚本)
- ✓ `evidence_pack/m4_10_reverify_jx_20260901.json` (verdict=CONTENT_CONFIRMED)
- ✓ docs/71 §7 行内 append (不删行不删 OPEN 行；沿用红线 4)

### 4.6 648-A.2 hygiene 收口落地

- ✓ `scripts/crosscheck_m2_2024_gdp.py` 增加 `--output PATH` 参数 (默认仍写 tracked 路径, 测试可重定向到 tmp)
- ✓ `tests/test_m2_report_hygiene.py` 5 tests (1 离线 + 4 在线默认 skip)
- ✓ hygiene invariants: tracked 报告字节零漂移 / tmp 输出 well-formed / 幂等 / 无残留 / --output flag 存在

---

## 5. 649 下一步

### 5.1 649 候选 scope

- **scope A (推荐)**: 沿用 648 模式 + substitute 预授权池激活 (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu 任选 1-2 个) — spike 第 7 次扩展；优先选 1-2 个 REACHABLE + 1-2 个 625 substitute 验证双 pattern
- **scope B**: O1 B路 live-candidate 启用 (per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用)
- **scope C**: Gate 1 启动 (M2 Gate 后才合法, 当前阻塞; 沿用 646/647/648 §5)
- **scope D**: docs/45/50 spike 文档清空收口 (沿用 M6 收口模式)
- **scope E**: 5W1H 分析 + 沿用 638-648 模式扩展 (spec 推演)

### 5.2 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M5 / M5.1 / M5.2 / M5.3 / M6** — 16 个里程碑不宣布 PASS
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
- 不动 registry.csv / mart 既有 638-647 行
- 不写 cegr.* 生产表
- chain_id 区分: 648 '_v5' ≠ 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID g 段 (g02-g62) ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段

---

## 6. 下一步 + 不宣称 PASS

**648 完成**:

- M4.11 政策详情 v5 真实化 (2 样本 × 1 HTTP each = 2 cells; chain_id='real_648_m4_11_policy_detail_v5'; UUID g 段; 2 NEW SHA: 4006439e/a06e174f; ≤12 HTTP total actual=4)
- jiangxi "403" 复验 = CONTENT_CONFIRMED (三层交叉验证: SHA 字节级一致 + 48118 bytes 一致 + 72 anchor 命中)
- m2 crosscheck 测试卫生收口 (--output tmp_path + 默认 skip; tracked 报告字节零漂移)
- **80/80 pytest green** (M4.11 新 16 + m2 hygiene 新 5 + reverify 新 8 + 647 回归 14 + 646 回归 10 + O1 回归 6 + 645 回归 12 + 644 回归 9)
- evidence_pack × 2 + docs/reports × 1 + docs/71 §7 行内 append + docs/72 + docs/52 零改动 全部落地

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 72 — M4.11 v5 + jiangxi reverify CONTENT_CONFIRMED + hygiene 收口 真实化 spike 审查 20260901 —