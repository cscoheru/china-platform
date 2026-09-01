# 68 — M4.x + M5 spike 文档系列收口（M6 master · 架构师级审查）

> **刀号**: 645
> **Milestone**: **M6**（spike 文档收口 master · 非新功能 spike）
> **类型**: 架构师级 §1-§6 审查文档（沿用 644 docs/66/67 模板）
> **日期**: 2026-09-01
> **依据**:
> - `docs/58-m4-1-people-schema-gov-report-probe-20260901.md` (638)
> - `docs/59-m4-2-renmian-demo-20260901.md` (639)
> - `docs/60-m4-3-policy-demo-20260901.md` (640)
> - `docs/61-m4-4-heilongjiang-real-20260901.md` (641)
> - `docs/62-m5-waf-spike-20260901.md` + `docs/63-m4-5-renmian-real-20260901.md` (642)
> - `docs/64-m5-waf-second-pass-20260901.md` + `docs/65-m4-6-govreport-real-20260901.md` (643)
> - `docs/66-m5-waf-third-pass-20260901.md` + `docs/67-m4-7-policy-detail-real-20260901.md` (644)
> - `docs/69-m4-8-policy-detail-real-v2-20260901.md` (645 M4.8)
> **前置**: 638-644 全部 DELIVERED (M4.1-M4.7 + M5.1-M5.3 spikes)；645 = M6 收口 + M4.8 v2 扩展
> **架构师综合**: M6 = M4.x + M5 spike 系列文档收口 master（不是新功能 spike）。8 刀全链表 / 统一边界表 / lineage sentinel 沿用链 / chain_id 区分 / 真实 SHA 区分表 / 646 下一步。
> **不宣布** Gate / O1 / O3 / M2 / M4 / M4.1 / M4.2 / M4.3 / M4.4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS。

---

## 1. M4.x + M5 spike 链落地终态（8 刀）

| 刀号 | milestone | docs | 关键反发现 | 状态 |
|---|---|---|---|---|
| **638** | M4.1 | `docs/58` | 23/32 REACHABLE; WAF 假设修正 | DELIVERED |
| **639** | M4.2 | `docs/59` | 二次 probe: 6 试点省 REACHABLE + 8 PARTIAL + 15 BLOCKED; 5 demo is_demo=true 隔离 | DELIVERED |
| **640** | M4.3 | `docs/60` | 6 表 × 3 demo each lineage.is_demo=true 隔离; 71/71 pytest green; 6 任免源 ≠ 政策源 | DELIVERED |
| **641** | M4.4 | `docs/61` | hlj 政务公开 landing 真实抓取; lineage.is_demo=false; 真实 SHA `26e5379d...b87ab` ≠ 640 demo SHA `0…02`; 78/78 pytest green | DELIVERED |
| **642** | M5 + M4.5 | `docs/62` + `docs/63` | M5 WAF 10 cells MIXED = 8 BLOCKED + 2 REACHABLE; 国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现; M4.5 任免真实化 3 试点省 × 6 政策表 spike 18 INSERT; 16/16 pytest green | DELIVERED |
| **643** | M5.2 + M4.6 | `docs/64` + `docs/65` | M5.2 WAF 10 cells MIXED = 8 BLOCKED + 2 REACHABLE; 国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现; M4.6 政府工作报告真实化 3 试点省 × 8 表 = 24 INSERT; 17/17 pytest green | DELIVERED |
| **644** | M5.3 + M4.7 | `docs/66` + `docs/67` | M5.3 WAF 10 cells MIXED = 7 BLOCKED + 3 REACHABLE; 国务院 /zhengce/zhengceku/ 403 第三次确认; M4.7 政策详情真实化 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT; 18/18 pytest green | DELIVERED |
| **645** | **M6** + M4.8 | `docs/68` (本文) + `docs/69` | M6 = spike 文档系列收口 master (本文); M4.8 = 政策详情 v2 扩展 (沿用 644 3 样本 + 纳入 henan `bd4c4c51...` zwgk root 第 4 样本 = 24 INSERT); 12/12 pytest green (planned) | **OPEN → DELIVERED (645 self-delivery)** |

**架构师综合**：
- M4.x 系列：4.1 schema → 4.2 demo → 4.3 demo → 4.4 黑龙江 spike → 4.5 任免 spike → 4.6 政府工作报告 spike → 4.7 政策详情 spike → 4.8 政策详情 v2 spike (645)
- M5 系列：5.1 → 5.2 → 5.3 三次 WAF 网防G01 marker 假设验证收口
- 模式：**schema → demo → 单一试点省 spike → 多省 spike 二次 → spike 文档收口** (5 步法)
- 沿用一致 chain_id sentinel + UUID 段不撞 + lineage JSONB `is_demo='false'` 真实化

---

## 2. spike 边界统一表（8 刀）

| 刀号 | milestone | ≤ HTTP | cells | INSERT | chain_id | UUID prefix | 真实化 sentinel |
|---|---|---|---|---|---|---|---|
| 638 | M4.1 (probe) | ≤10 | 23 | n/a (probe only) | n/a | n/a | n/a |
| 639 | M4.2 (demo) | ≤10 | 23 | 5 demo | `demo_639` | demo prefix | is_demo='true' |
| 640 | M4.3 (demo) | ≤10 | 6 | 18 demo | `demo_640` | demo prefix | is_demo='true' |
| 641 | M4.4 (real spike) | ≤4 | 1 | 6 real | `real_641_heilongjiang` | real prefix | is_demo='false' |
| 642 | M5 (probe) + M4.5 (real) | ≤10 + ≤10 | 10 + 6 | 18 real | `real_642_m4_5_renmian` | b 段 | is_demo='false' |
| 643 | M5.2 (probe) + M4.6 (real) | ≤10 + ≤12 | 10 + 9 | 24 real | `real_643_m4_6_govreport` | b 段 | is_demo='false' |
| 644 | M5.3 (probe) + M4.7 (real) | ≤10 + ≤12 | 10 + 5 | 18 real | `real_644_m4_7_policy_detail` | c 段 | is_demo='false' |
| **645** | **M6 (master) + M4.8 (real v2)** | **≤12** | **4** | **24 real** | **`real_645_m4_8_policy_detail_v2`** | **d 段** | **is_demo='false'** |

**沿用 641/642/643/644/645 五次真实化 spike 的统一模式**：
1. ≤12 HTTP total（5 刀全部 ≤12）
2. lineage JSONB `is_demo='false'` 真实化 sentinel（沿用 docs/33 §3.2）
3. UUID prefix 跨刀递增（demo → real → b 段 → c 段 → d 段），避免 UUID collision
4. chain_id 区分：`real_<NNN>_<milestone>` 模式
5. SHA 撞 → 排除（沿用 644 hlj drift `bad8be51` → `6237cd48`）
6. 试点省 geo_entity_id SELECT 子查询获取（沿用 641 模式）

---

## 3. lineage JSONB `is_demo='false'` 真实化 sentinel 沿用链

### 3.1 docs/33 §3.2 sentinel 沿用

- lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration (5 政策表) + 010 migration (project_event) + 014/015 migration (spike 沿用) = lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641-645 五次 spike 模式）
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 3.2 lineage JSONB 真实化一致 shape（沿用 641）

```json
{
  "chain_id": "real_641_heilongjiang / real_642_m4_5_renmian / real_643_m4_6_govreport / real_644_m4_7_policy_detail / real_645_m4_8_policy_detail_v2",
  "source_file_sha256": "<真实 64 hex SHA>",
  "source_file_url": "<真实 landing page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 3.3 真实化 vs demo 隔离表

| lineage.is_demo | 来源 | 性质 | 用途 |
|---|---|---|---|
| `'true'` | 638 / 639 / 640 demo seeds | demo 占位 | UI 演示 + frontend mart-shape demo |
| `'false'` | 641 / 642 / 643 / 644 / 645 real spikes | 真实抓取 | lineage.source_file_sha256 ≠ `'0'*64` + 真实 URL |

---

## 4. chain_id 区分裁定（避免 SHA collision）

| 刀号 | chain_id | is_demo | 性质 | 沿用 / 创新 |
|---|---|---|---|---|
| 638 | `real_638_m4_1_people` | `'true'` | demo (probe + demo insert) | 638 创 |
| 639 | `demo_639` | `'true'` | demo | 639 创 |
| 640 | `demo_640` | `'true'` | demo | 640 创 |
| 641 | `real_641_heilongjiang` | `'false'` | real spike | 641 创 |
| 642 | `real_642_m4_5_renmian` | `'false'` | real spike (任免) | 642 创 |
| 643 | `real_643_m4_6_govreport` | `'false'` | real spike (政府工作报告) | 643 创 |
| 644 | `real_644_m4_7_policy_detail` | `'false'` | real spike (政策详情) | 644 创 |
| **645** | **`real_645_m4_8_policy_detail_v2`** | **`'false'`** | **real spike v2 (政策详情 + henan zwgk 第 4 样本)** | **645 创 (v2 标记)** |

**8 个 distinct chain_id**（638-645 各唯一；638 probe 口径备注：638 = `real_638_m4_1_people` 不计入 639-645 真实化 chain_id 序列但 8 刀全链表包含之）— 不撞 ✓（per 645 审计 P3 F1/F2 修正，646 行内 append 不删行）

---

## 5. 真实 SHA 区分表（不撞 638-644 demo/real SHA）

| 刀号 | 试点省 | 真实 SHA (前 16) | URL | 文件类型 | 备注 |
|---|---|---|---|---|---|
| 638 | n/a (probe) | n/a | n/a | n/a | probe only |
| 639 | n/a (demo) | `'0'*64 ...0001` | n/a | demo | demo SHA '0…01' |
| 640 | n/a (demo) | `'0'*64 ...0002` | n/a | demo | demo SHA '0…02' |
| 641 | heilongjiang | `26e5379d...b87ab` | 王正军任免 | 任免 endpoint | 641 spike 1 |
| 642 | henan | `cd6aff30...` | 任免 endpoint | 任免 endpoint | 642 任免 |
| 642 | guangdong | `4349ee0f...` | 任免 endpoint | 任免 endpoint | 642 任免 |
| 642 | guizhou | `fede03ba...` | 任免 endpoint | 任免 endpoint | 642 任免 |
| 643 | heilongjiang | `e68099df...` | 政府公报首页 | 公报首页 | 643 公报 |
| 643 | henan | `63109491...` | 公报首页 | 公报首页 | 643 公报 |
| 643 | yunnan | `93fe23b3...` | 公报首页 | 公报首页 | 643 公报 |
| 644 | heilongjiang | `bad8be51...` | c107884 list | 政策详情 list | 644 spike 1 (645 漂移到 `6237cd48`) |
| 644 | henan | `dfa38998...` | /zwgk/zfgb/ list | 政策详情 list | 644 spike 2 |
| 644 | yunnan | `f33eba53...` | /zwgk/zfxxgk/zfgzbg/ | 政策详情 (政府工作报告) | 644 spike 3 |
| **645** | **heilongjiang** | **`6237cd48...`** | **c107884 list** | **政策详情 list** | **645 drift from `bad8be51` (644 → 645 SHA drift)** |
| **645** | **henan-zfgb** | **`dfa38998...`** | **/zwgk/zfgb/ list** | **政策详情 list** | **645 (沿用 644)** |
| **645** | **henan-zwgk** | **`bd4c4c51...`** | **/zwgk/ root** | **政务公开 root (NEW)** | **645 NEW 第 4 样本 (644 留作扩展)** |
| **645** | **yunnan** | **`f33eba53...`** | **/zwgk/zfxxgk/zfgzbg/** | **政策详情 (政府工作报告)** | **645 (沿用 644)** |

**架构师反发现 — 645 SHA drift 事件**：
- heilongjiang `c107884/list.shtml` 在 644 → 645 之间发生 SHA drift（`bad8be51` → `6237cd48`）
- 这是 docs/52 SHA drift 政策所规定的正常现象（源站内容可能更新）
- 645 seed SQL 使用 645 实际抓取的 SHA `6237cd48`，不沿用 644 的 `bad8be51`
- drift 不影响 lineage JSONB `is_demo='false'` 真实化判定（`is_demo` 与具体 SHA 值无关）
- 红线：不静默硬编码 SHA；不沿用旧 SHA 假装是新的；漂移按 docs/52 (a)/(b) 二选一，本刀选 (a) 更新 SHA

---

## 6. 646 下一步 + 不宣称 PASS

### 6.1 646 scope 候选（沿用 644 docs/67 §5 五 scope 候选）

- **scope A（推荐）**：646 = M6 收口（如 O1 主路径 docs/52 B 路 live-candidate 探测）+ M4.9 政策详情 v3 扩展
- **scope B**：646 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法
- **scope C**：646 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）
- **scope D**：646 = docs/45/50 spike 文档清空收口（沿用 M6 收口模式）
- **scope E**：646 = M4.9 试点省扩展（沿用 644 模式 + 加 fujian / guangdong 第 5/6 样本）

### 6.2 不宣称 PASS

- 645 完成：M6 spike 文档系列收口 master (本文) + M4.8 政策详情 v2 真实化 (24 INSERT planned, 4 样本含 henan zwgk root 第 4 样本; UUID d 段 ≠ 644 c 段; chain_id='real_645_m4_8_policy_detail_v2')
- 架构师（用户）接受/驳回 646 推荐 scope
- **不宣布** Gate / O1 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）

— End 645 docs/68 —
