# 654 — M4.17 政策详情 v11 西北双省 spike (附属报告)

> **刀号**: 654
> **Milestone**: M4.17 政策详情 v11 西北双省 spike (第 13 次扩展; 西北五省区收官)
> **日期**: 2026-09-02
> **主 evidence**: `evidence_pack/m4_17_policy_detail_real_v11_20260902.json`
> **架构师级审查**: `docs/78-m4-17-policy-detail-real-v11-20260902.md` (六节)
> **任务书**: `reviews/stage0-gate0-rework-2026-08-23/653-audit-654-tasking-consolidated-20260902.md` PART 2
> **回执**: `reviews/stage0-gate0-rework-2026-08-23/654-stage0-cc-m4-17-v11-northwest-receipt-20260902.md`

---

## 1. 任务背景

654 = M4.17 v11 西北双省 spike (gansu + qinghai 第 21/22 样本) — 与 652 XINJIANG/NEIMENGGU 构成西北五省区叙事收官。两省均无前史 → retry_of 不适用（首试省）；若 BLOCKED → 纯 BLOCKED_NO_POOL 留痕；三态合法。

## 2. 实测结果

| 样本 | 首选 /zwgk/ | fallback #1 / | verdict | http | retry_of |
|---|---|---|---|---|---|
| **gansu** | 412 | 412 | **BLOCKED_NO_POOL** | 2 | N/A (无前史) |
| **qinghai** | 0 (Connection reset by peer) | 0 (Connection reset by peer) | **BLOCKED_NO_POOL** | 2 | N/A (无前史) |

**汇总**: REACHABLE×0 / BLOCKED_NO_POOL×2; HTTP 4/12 = 33%; 0 NEW SHA; substitute_used=0; fetch_status=`ALL_BLOCKED_NO_POOL`。

## 3. 三态合法判定 (per 654 §1.654-A.1)

本次为**双 BLOCKED** 第三态 — 双首试省均两级 fallback 全失败 → BLOCKED_NO_POOL 留痕 (合法)。

INSERT 数按实报: **0 INSERT ROWS** (per 654 §0.14 红线 14 + BLOCKED 口径沿用 653)。

## 4. 西北五省区叙事收官 (per docs/78 §3.2)

| 西北省 | 落定刀 | verdict | retry_of |
|---|---|---|---|
| XINJIANG | 652 | REACHABLE | — |
| NEI MENGGU | 652 | REACHABLE | — |
| SHAANXI (邻接) | 651 | REACHABLE | — |
| **GANSU** | **654** | **BLOCKED_NO_POOL** | **N/A** |
| **QINGHAI** | **654** | **BLOCKED_NO_POOL** | **N/A** |

**西北五省区 = 651 + 652 + 654 三刀收官** (3 REACHABLE + 2 BLOCKED 双首试省首触发)。

## 5. 失败形式库登记 (per docs/78 §5.3)

新增 1 例首见失败形式:

- **654 qinghai "Connection reset by peer"** (curl recv failure, 0/0) — **全链第二例首见失败形式**, 继 653 shandong SSL handshake failure 后

复用 1 例旧形式:

- **654 gansu 412×2** (同 649 hubei 412×2 史, 但 retry_of=N/A 首试省不引用)

**全链首见失败形式累计 = 2 例** (653 + 654)。

## 6. 主 evidence methodology 指针

主 evidence `summary.methodology` 含:
- 648 审计 P3-1 口径统一条款 (附属产物指针)
- 649 审计 P3-1 代换行标注规范固化入红线 13 (代换行 source_registry province/source_name 一律用 actual_province)
- 652 §0.14 红线 14 增补登记 (沿用)
- 653 §0.14 红线 14 复试 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用)
- **654 §0.14 沿用 653 §0.14** + 三态合法 + 双首试省首触发双例
- 递补池 [EXHAUSTED] 沿用 653
- 双样本结果: REACHABLE×0 / BLOCKED_NO_POOL×2

## 7. 654-A.0 规范 v3 落地

per 653 审计 P4×2 处置:
- §META 五字段原子更新 (rev/status/last_delivery/last_receipt/tasking 状态行与 cc_head 同 commit)
- status 行禁含任何具体 SHA (终极条款, 杜绝第四型 pin 陈旧)
- 沿用 amend-first 规则

commit 9b54dbd (rev93) 落地。

## 8. 654 红线自检

14 条红线 (沿用 653) — 全 ✓:
- 红线 1: 不宣称 PASS (本报告 + docs/78 + evidence + seed 全标"不宣称")
- 红线 2: 不补零 (0 INSERT ROWS + retry_of=N/A 透明)
- 红线 3: 不爬网 (HTTP 4/12 = 33% usage; ≤12 红线)
- 红线 4: 不改 docs/45/50/53/66-77 既有正文 (docs/77 零改动; docs/78 是新文档)
- 红线 5: 不碰 4 fixture
- 红线 6: 数据源唯一 = 政府自取 (gansu/qinghai gov.cn); 用户零裁定
- 红线 7: 完成 = observation SUCCESS, 禁止 PARTIAL (特例: BLOCKED_NO_POOL 留痕合法)
- 红线 8: 不新写 016 migration
- 红线 9: chain_id = 'real_654_m4_17_policy_detail_v11' (末段 _v11)
- 红线 10: UUID m 段 (m0eebc99-m6eebc99) ≠ 653 l 段 ≠ 652 k 段
- 红线 11: 不写 cegr.* 生产表
- 红线 12: 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff
- 红线 13: O1 零动作 + 附属产物指针 + 代换行 actual_province (本报告即附属产物)
- 红线 14: 递补池 [EXHAUSTED] + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed (沿用 653)

## 9. 不宣称 PASS + O1 OPEN

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.7-17 / M5 / M5.x / M6 PASS (沿用红线 1)
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)

---

— End 654 — M4.17 v11 西北双省 spike 附属报告 20260902 —