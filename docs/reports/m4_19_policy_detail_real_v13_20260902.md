# 656-A.4 — M4.19 政策详情 v13 华南双省对 spike 附属报告 (knife 656, 2026-09-02)

> **刀号**: 656
> **Milestone**: M4.19（v13 华南双省对 spike；华南双省对 = GUANGXI / HAINAN；西部-华南接力）
> **角色**: 架构师 + 执行端（合并到本终端 per 2026-08-31 21:50 豁免）
> **日期**: 2026-09-02
> **前置**: 655 DELIVERED + 655 审计 **PASS（有限通过）**（rev97）+ 656 任务书签发（00a020b）+ 656-A.0 规范 v3.2 落地 + 656-A.2 O-1 根因修复（m2 报告只读化锁定测试）
> **配套文件**:
> - `scripts/fetch_m4_19_policy_detail_v13_2024.py`（fetch 脚本）
> - `scripts/seed_m4_19_policy_detail_real_v13.sql`（seed SQL，8 INSERT）
> - `evidence_pack/m4_19_policy_detail_real_v13_20260902.json`（主 evidence JSON）
> - `docs/80-m4-19-policy-detail-real-v13-20260902.md`（架构师级审查 §1-§6）
> - `tests/test_m4_19_policy_detail_real_v13.py`（测试守门 ≥10 cases）
> - `tests/test_m2_report_hygiene.py`（656-A.2 O-1 根因修复 ≥2 cases）

---

## §1. 实测结果总览（双样本）

| 样本 | URL 首选 | URL fallback | verdict | http_code | 字节 | 锚点 | WAF marker |
|---|---|---|---|---|---|---|---|
| **GUANGXI** | https://www.gxzf.gov.cn/zwgk/ | https://www.gxzf.gov.cn/ | **BLOCKED_NO_POOL** | **0 × 2** (SSL 失败) | **0 × 2** | **0 × 2** | **False × 2** |
| **HAINAN** | https://www.hainan.gov.cn/zwgk/ | https://www.hainan.gov.cn/ | **REACHABLE** | **200** | **30150** | **89** | **False** |

**双样本 verdict 总判**: **PARTIAL_BLOCKED**（1 REACHABLE + 1 BLOCKED_NO_POOL；混合态第二例落地，与 655 同构）

**HTTP 总用量**: 3/12（25% usage；GUANGXI 2 + HAINAN 1）

**NEW SHA**: `83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938`（HAINAN /zwgk/ 直命中）

**blocked_no_pool_count**: 1（GUANGXI 首试省首触发 BLOCKED_NO_POOL；SSL `error:1404B458:ST_CONNECT:tlsv1 unrecognized name` — 全链第四例首见失败形式）

**substitute_used_count**: 0（红线 14 增补沿用 655：递补池 [EXHAUSTED]，不可跨省代换）

---

## §2. 三态处置（按实报；任务书 §1.656-A.1 明文）

| 处置维度 | GUANGXI | HAINAN |
|---|---|---|
| **verdict** | BLOCKED_NO_POOL | REACHABLE |
| **INSERT 数** | 0（首试省首触发 BLOCKED 留痕） | 8（1 样本 × 8 表：source_registry + source_document + policy_document + policy_target + policy_measure + government_commitment + commitment_progress + project_event） |
| **actual_province** | NULL（不计入已用省） | HAINAN（计入已用省；华南双省对落定第 20 省） |
| **lineage retry_of** | retry_of=N/A（无前史首试） | retry_of=N/A（无前史首试） |
| **NEW SHA** | 无（BLOCKED 留痕无 SHA） | 83a13d18 |
| **留痕位置** | 4 处：fetch 分支 + 主 evidence cells[0] + docs/80 §2 + 本报告 §3 | 主 evidence cells[1] + seed SQL 8 INSERT |

**INSERT 总计** = **8 ROWS**（混合态按实报；任务书 §1.656-A.1 第三态）

---

## §3. GUANGXI BLOCKED_NO_POOL 失败形式详解（首见失败形式第四例）

### 3.1 两级 fallback 实测

```
URL: https://www.gxzf.gov.cn/zwgk/
HTTP: SSL 握手失败 (curl exit 35)
Body: (无; SSL 阶段即终止)
Error: LibreSSL/3.3.6: error:1404B458:SSL routines:ST_CONNECT:tlsv1 unrecognized name
Anchor Hits: 0 (SSL 失败未返回内容)
WAF Marker: False (SSL 失败未触发 WAF 检测)

URL: https://www.gxzf.gov.cn/
HTTP: SSL 握手失败 (curl exit 35)
Body: (无; SSL 阶段即终止)
Error: LibreSSL/3.3.6: error:1404B458:SSL routines:ST_CONNECT:tlsv1 unrecognized name (同上)
Anchor Hits: 0
WAF Marker: False

判定: BLOCKED_NO_POOL (两级 fallback 均触发 SSL 握手失败; tlsv1 unrecognized name = SNI/证书链不匹配)
```

### 3.2 SSL 失败类型识别

正则: `tlsv1 alert|SSL routines|error:1404`
- /zwgk/: **True** (含 `SSL routines:ST_CONNECT:tlsv1 unrecognized name`)
- /: **True** (同上)

### 3.3 失败形式分类（per 失败形式库 §5）

| 维度 | 值 |
|---|---|
| 失败形式 | **SSL error:1404B458 (ST_CONNECT:tlsv1 unrecognized name)** |
| 首见/复用 | **首见（第四例首见失败形式）** |
| 阻断域 | gxzf.gov.cn |
| 失败阶段 | SSL 握手阶段（curl exit 35）；无 HTTP 响应体 |
| 与 653 区分 | 653 = `error:1404B410:ssl3_read_bytes:tlsv1 alert internal error`（TLS alert internal error，服务器主动拒绝）vs 656 = `error:1404B458:ST_CONNECT:tlsv1 unrecognized name`（SNI/证书链不匹配）— SSL 层面的两种不同失败形式 |

---

## §4. 主 evidence JSON summary.methodology 援引链

```
v13 华南双省对 spike fetch: 2 cells (guangxi + hainan 第 25/26 样本;
双首试省 per 656 §0.14 沿用 655 §0.14).
GUANGXI 首选 https://www.gxzf.gov.cn/zwgk/ + fallback #1 https://www.gxzf.gov.cn/;
HAINAN 首选 https://www.hainan.gov.cn/zwgk/ + fallback #1 https://www.hainan.gov.cn/.
递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED] (per 656 §0.14 红线 14 增补沿用 655 §0.14);
两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换.
每 cell ≤2 attempts, 总预算 ≤12 HTTP.
lineage retry_of=N/A (双省无前史首试; per 656 §1.656-A.1).
三态均合法 (任务书明文): 双 REACHABLE → 16 INSERT ROWS 正常落 + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt).
Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针.
代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1).
Per 656 §0.14: 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 655 §0.14 模板, docs/79 §5.2 + 656 §0.14 复试).
递补池 [EXHAUSTED] 沿用 655.
华南双省对落定: GUANGXI + HAINAN (留 HEBEI/SHANXI 给 657 全国 31 省收官).
本次双样本结果: REACHABLE×1 / BLOCKED_NO_POOL×1.
```

---

## §5. 西部-华南接力叙事汇总（含 656 增量）

| 叙事段落 | 落定刀 | 已用省数 | NEW SHA | 触发 BLOCKED 形式 |
|---|---|---|---|---|
| 西部七省区首段 (SHAANXI/SICHUAN) | 651 | +2 (19→21) → 修正后 +1 (18→19) | 9d0ad78a / f58a3384 | 0 (双 REACHABLE) |
| 西部七省区续段 (XINJIANG/NEI MENGGU) | 652 | +2 (21→23) → 修正后 +2 (19→21) | 21c8211b / da1d4104 | 0 (双 REACHABLE) |
| 西部五省区三段 (GANSU/QINGHAI) | 654 | 0 (23) | 0 | 2 (SSL internal error + Connection reset) |
| 西部七省区尾章 (NINGXIA/XIZANG) | 655 | +1 (23→24) → 修正后 +1 (21→22) | 855af02f | 1 (405 + WAF) |
| **华南双省对 (GUANGXI/HAINAN)** | **656** | **+1 (24→25)** → **修正后 +1 (22→23)** | **83a13d18** | **1 (SSL error:1404B458)** |
| 全国 31 省收官 (HEBEI/SHANXI + 西部华南缺) | 657 (待) | TBD | TBD | TBD |

注：上表"已用省数"列采用 actual_province 口径（REACHABLE 样本计入；BLOCKED 留痕样本不计入）。656 增量 = 1（HAINAN REACHABLE）。

---

## §6. 656-A.0 规范 v3.2 落地验证

### 6.1 规范 v3.2 三要点 (per 655 审计 P4×2 教训沉淀; **v3.2 升级 v3.1**)

- ✓ **status 行零 SHA 绝对化**（v3.2 沿用 v3.1 终极条款; 杜绝 654 P4-1 字面违反; 迁移注记只入 §NOW/commit, status 仅写状态语义）
- ✓ **七字段原子同步**（v3.2 沿用 v3.1; header line 3 rev / §META 五字段 rev/status/last_delivery/last_receipt/tasking / §CHAIN_TAIL 当前行 同 commit 同步; 杜绝 654 P4-2 header 漏同步 + CHAIN_TAIL 漏更新）
- ✓ **中间态零残留首签**（v3.2 新增; status 行/§META tasking/§NOW 段零"进行中 X/7 / 待 commit / 待 user 授权"陈旧中间态文本; 杜绝 655 审计 P4×2 复发）
- ✓ 沿用 amend-first 规则

### 6.2 656-A.2 O-1 根因修复落地

- ✓ `tests/test_m2_report_hygiene.py` 落地（≥2 cases；m2 报告只读化锁定测试）
- ✓ 防线从人工还原升级为机制保障
- ✓ 杜绝 O-1 第三次复发再发生

---

## §7. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M4.18 / M4.19 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线 1，24 个里程碑不宣布）
- O1 仍 OPEN（B路 live-candidate 仅登记，不切换/启用）

---

— End 656-A.4 — M4.19 v13 华南双省对 spike 附属报告 20260902 —