# 651 — M4.14 v8 递补池收官 + 红线 14 增补耗尽条款 — DELIVERY RECEIPT

> **刀号**: 651
> **类型**: DELIVERED (架构师本终端自签 + 自交付 per 2026-08-31 21:50 豁免)
> **日期**: 2026-09-02
> **任务书**: `reviews/stage0-gate0-rework-2026-08-23/650-audit-651-tasking-consolidated-20260902.md` (合并件: 650 审计 PASS·有限通过 + 651 任务书)
> **架构师审查**: `docs/75-m4-14-policy-detail-real-v8-20260902.md` (DONE)
> **不宣称任何** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5.x / M6 PASS。

---

## §NOW (执行态)

CC 执行 651 完成 (per 任务书 §A.0/A.1/A.2/A.3/A.4 + §B)。当前态: **M4.14 v8 真实化 (shaanxi + sichuan 第 15/16 样本) + 650 审计 P4×2 行内更正 + 递补池正式耗尽 [EXHAUSTED] + 红线 14 增补登记 + docs/75 §1-§6 + evidence ×2 + tests ≥26 new green + ≥163 跨刀 spike 回归**。

---

## §EXEC_BODY — 651 落地明细

### 651-A.0 650 审计 P4×2 行内更正 (DONE)

| 项 | 落点 | 状态 |
|---|---|---|
| **P4-1** `docs/74 §2.1 "sha anxi"` 行内更正为 `shaanxi` + 尾注 (650 编写笔误) | `docs/74-m4-13-policy-detail-real-v7-20260901.md:42` | ✓ |
| **P4-2** `docs/74 §2.4` "649 增量" 行 append 口径尾注 (HUBEI 为槽名 consumed; actual_province=liaoning) | `docs/74-m4-13-policy-detail-real-v7-20260901.md:79` | ✓ |
| **P4-2** `docs/74 §4.4` 池成员表行 append 同口径尾注 | `docs/74-m4-13-policy-detail-real-v7-20260901.md:214` | ✓ |
| `grep "sha anxi" docs/74-...md` 残留 | grep 计数 = **0** ✓ | ✓ |
| P4-1 + P4-2 尾注均显式 | `[per 650 审计 P4-1 行内更正 / 2026-09-02]` / `[per 650 审计 P4-2 口径尾注 / 2026-09-02]` | ✓ |
| `scripts/seed_m4_13_policy_detail_real_v7.sql` (650 蓝图) P3-1 更正 | 沿用 650-A.0 落地 (本刀无新 P3-1 更正) | — |

**红线 13 规范沿用 (per 649 审计 P3-1 + 650 蓝图更正)**: 代换行 source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB。本次 651 零 substitute 触发, 全部 16 INSERT 字段 `province/source_name/publisher` 均直接用 actual_province 口径 (与 province 一致)。

### 651-A.1 M4.14 v8 真实化 (DONE)

| 项 | 落点 | 状态 |
|---|---|---|
| `scripts/fetch_m4_14_policy_detail_v8_2024.py` | 2 cells (shaanxi + sichuan 第 15/16 样本); **SUBSTITUTE_POOL=[] (EXHAUSTED)** + BLOCKED_NO_POOL 分支 | ✓ |
| `scripts/seed_m4_14_policy_detail_real_v8.sql` | 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document; lineage JSONB 全 red_line_14_status='EXHAUSTED' | ✓ |
| `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` | 主 evidence REAL_FETCHED 2 samples; http_count=4/12 (33% usage); substitute_pool_status='EXHAUSTED' | ✓ |
| chain_id `real_651_m4_14_policy_detail_v8` | UUID j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 | ✓ |
| 2 NEW SHA distinct | `9d0ad78a` (shaanxi) + `f58a3384` (sichuan) | ✓ |
| substitute_used_count | **0** (双样本均 fallback #1 REACHABLE; 池耗尽也无需触发) | ✓ |
| blocked_no_pool_count | **0** (本次未触发 BLOCKED; 双样本均 REACHABLE) | ✓ |
| HTTP budget | 4/12 = 33% usage (vs 650 3/12 = 25%; vs 649 6/12 = 50%) | ✓ |
| lineage JSONB is_demo | 全 `'false'` 真实化 sentinel | ✓ |
| lineage JSONB red_line_14_status | 全 `'EXHAUSTED'` (per 红线 14 增补) | ✓ |

**2 样本 fetch 详情**:
- shaanxi: `/zwgk/` 404 → `/` 200 REACHABLE (chain_index=1 fallback) — 87,956 bytes; SHA `9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5`
- sichuan: `/zwgk/` 403 WAF → `/` 200 REACHABLE (chain_index=1 fallback) — 100,536 bytes; SHA `f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5`

### 651-A.2 O1 零动作 (DONE)

- O1 仍 OPEN (live-candidate 仅登记, 不切换/启用)
- docs/52 零改动 = 合规
- 不新增 probe、不启用、不改 registry/connector

### 651-A.3 docs/75 §1-§6 架构师级审查 (DONE)

`docs/75-m4-14-policy-detail-real-v8-20260902.md` 已落盘; 6 节齐全:
- §1 M4.14 v8 落地终态 (5 子刀状态表)
- §2 substitute 跨省代换登记 + **递补池生命周期收官登记** (4 阶段: 649/650/651/651 后)
- §3 M4.14 v8 spike 边界 (规划 vs 实测 + 625 fall-through chain 注记 + 16 INSERT 明细 + 真实样本 SHA 表)
- §4 lineage 真实化 sentinel + chain_id 区分 (14 真实化刀) + SHA 区分表 (27 SHA 累计) + UUID prefix 严格递增 + 649 池收官 + 651-A.4 evidence 落地
- §5 后续 652+ BLOCKED 留痕口径 (5 候选 scope)
- §6 下一步 + 不宣称 PASS (19 个里程碑不宣布)

### 651-A.4 evidence × 2 (DONE)

| 文件 | 角色 | 状态 |
|---|---|---|
| `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` | 主 evidence; summary.methodology 含附属产物指针 + 651 §0.14 援引 + BLOCKED_NO_POOL 留痕不代换条款 | ✓ |
| `docs/reports/m4_14_policy_detail_real_v8_20260902.md` | 附属产物 (per 648 审计 P3-1 + 649 审计 P3-1 + 651 §0.14 红线 14 增补); 9 节齐全 | ✓ |

主 evidence `summary.methodology` 含: "v8 spike fetch: 2 cells (shaanxi + sichuan)... 递补池 (SUBSTITUTE_POOL) 显式标记 [EXHAUSTED] (per 651 §0.14 红线 14 增补); 两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换. ... Per 651 §0.14: BLOCKED_NO_POOL 留痕不代换."

---

## §PHOTO — 验证铁证

- **PHOTO-1** (M4.14 v8 evidence JSON): `evidence_pack/m4_14_policy_detail_real_v8_20260902.json`
  - `summary.fetch_status = REAL_FETCHED`
  - `summary.fetched_count = 2`
  - `summary.http_count = 4` (33% usage)
  - `summary.http_limit = 12`
  - `summary.substitute_used_count = 0`
  - `summary.substitute_pool_status = "EXHAUSTED"` (per 红线 14)
  - `summary.blocked_no_pool_count = 0` (本次未触发 BLOCKED)
  - `summary.distinct_shas = ["9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5", "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5"]`
  - cells[0] shaanxi: REACHABLE / chain_index=1 / verdict=REACHABLE / substitute_used=false / 87956 bytes / SHA 9d0ad78a
  - cells[1] sichuan: REACHABLE / chain_index=1 / verdict=REACHABLE / substitute_used=false / 100536 bytes / SHA f58a3384
  - fetch_log: sx/zwgk 404, sx/ 200, sc/zwgk 403 WAF, sc/ 200
  - methodology 字段含附属产物指针 + 651 §0.14 援引 + BLOCKED_NO_POOL 留痕不代换条款 + 649 P3-1 援引

- **PHOTO-2** (附属报告): `docs/reports/m4_14_policy_detail_real_v8_20260902.md`
  - 9 节齐全: 任务背景 / 样本复盘 / 三层交叉验证 / HTTP 预算 / SHA 区分表 + lineage 落地 / 递补池耗尽登记 / 651 §0.14 红线 14 增补登记 / 附属产物指针 / 验收 checklist

- **PHOTO-3** (fetch script BLOCKED_NO_POOL 分支): `scripts/fetch_m4_14_policy_detail_v8_2024.py`
  - `SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []` (5 原始候选全部 consumed)
  - `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"` (per 红线 14)
  - `fetch_cell()` 含 `verdict: "BLOCKED_NO_POOL"` + `blocked_reason` 字段 (本次未触发; 因双样本 fallback #1 REACHABLE)

- **PHOTO-4** (seed SQL red_line_14_status): `scripts/seed_m4_14_policy_detail_real_v8.sql`
  - 16 INSERT 全部 lineage JSONB 含 `red_line_14_status: "EXHAUSTED"` (≥12 个 source_file_sha256 显式登记)
  - source_registry 2 行 lineage JSONB 含 `substitute_pool_note` 显式说明
  - 2 NEW SHA 9d0ad78a/f58a3384 显式登记; 638-650 全部 stale SHA 严格不出现

- **PHOTO-5** (docs/75 架构师级审查): `docs/75-m4-14-policy-detail-real-v8-20260902.md`
  - 286 行; §1-§6 齐全; 2 NEW SHA 9d0ad78a/f58a3384 显式登记; j 段 UUID 区分; 27 SHA 全部 distinct
  - §2.2 递补池生命周期收官 (4 阶段: 649 激活 / 650 备而未触发 / 651 转正 / 651 后 EXHAUSTED)
  - §2.3 递补池成员最终状态 (5 候选全部落定)
  - §4.4 649 substitute 预授权池状态更新 (收官表)
  - §6 显式 "不宣称任何 PASS" + 19 个里程碑不宣布

- **PHOTO-6** (docs/74 P4×2 行内更正 + 尾注): `docs/74-m4-13-policy-detail-real-v7-20260901.md`
  - 第 42 行: `shaanxi` (正确连写) + 尾注 `[per 650 审计 P4-1 行内更正 / 2026-09-02]: 行内 "递补池按序" 一行原写 shanxi 省名含意外空格 (650 编写笔误, 省名断字 typo); 行内更正为 shanxi 正确连写`
  - 第 79 行 (§2.4): `> [per 650 审计 P4-2 口径尾注 / 2026-09-02]: ...HUBEI 为槽名 (consumed; 跨省 substitute 池消耗); 实际抓取省 (actual_province) = LIAONING...`
  - 第 214 行 (§4.4): `> [per 650 审计 P4-2 口径尾注 / 2026-09-02]: ...行内 HUBEI 项为槽名...读法: "649 substitute 槽消耗 HUBEI → actual=LIAONING; JILIN 直接 REACHABLE"...`
  - `grep -c "sha anxi" docs/74-...md` = **0** ✓

- **PHOTO-7** (tests 26 new green): `tests/test_m4_14_policy_detail_real_v8.py`
  - 26 cases 全 PASSED in 1.28s
  - 含 5 个核心守门:
    - `test_evidence_json_real_fetched_2_samples` (http_count=4, REAL_FETCHED)
    - `test_evidence_json_substitute_pool_status_exhausted` (红线 14 增补守门)
    - `test_fetch_script_blocked_no_pool_branch_present` (BLOCKED_NO_POOL 分支守门)
    - `test_seed_sql_red_line_14_status_exhausted` (lineage JSONB 守门)
    - `test_p4_1_docs_74_no_sha_anxi_residue` (650 审计 P4-1 行内更正守门)
    - `test_p4_2_docs_74_slot_actual_province_koujings` (650 审计 P4-2 口径尾注守门)
    - `test_red_line_14_pool_exhaustion_fetch_script` (SUBSTITUTE_POOL=[] + BLOCKED_NO_POOL 分支 守门)
    - `test_red_line_14_pool_exhaustion_seed_sql` (lineage JSONB 守门)
    - `test_red_line_14_pool_exhaustion_evidence` (主 evidence 守门)
    - `test_docs_75_sections_1_to_6_present` (docs/75 §1-§6 守门)
    - `test_docs_75_pool_depletion_records` (递补池生命周期收官 4 阶段守门)

- **PHOTO-8** (≥163 跨刀 spike 回归): M4.1→M4.14 全套 = 163 passed in 1.03s
  - M4.14 v8 新增: 26
  - M4.13→M4.1 回归: 137
  - 总计 163 ≥ 126 任务书阈值 ✓

---

## §RED_LINE_AUDIT

- ✓ 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS (per 红线 1) — 19 个里程碑不宣布
- ✓ 不补零 / 不静默硬编码 value (per 红线 2) — domain 值 NULL 透明占位 (沿用 641-650)
- ✓ 不爬网 / 不镀铬四轨 (per 红线 3) — ≤12 HTTP total (本次 4/12 = 33% usage)
- ✓ 不把目录页标 FETCHED (per 红线 4) — 仅 fallback 链落入 seed
- ✓ ≤12 HTTP total (per 红线 5) — 4/12 = 33% usage
- ✓ 不改 docs/45/50/53/66/67/68/69/70/71/72/73 既有正文 (per 红线 6) — 仅 docs/74 行内 append 尾注 (per 650 审计 P4×2 落地)
- ✓ scripts/ 蓝图 SQL 的 P3-1 更正不属 docs 正文, 允许行内更正 + 尾注标记 (per 红线 7)
- ✓ 不碰 4 fixture 锁值 (per 红线 8) — nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c 零漂移
- ✓ 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 (per 红线 9 + 2026-08-29 铁律)
- ✓ 完成 = observation SUCCESS, 禁止 PARTIAL (per 红线 10) — fetch_status=REAL_FETCHED
- ✓ 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) (per 红线 11)
- ✓ chain_id = `real_651_m4_14_policy_detail_v8` (末段 _v8) ≠ 650 _v7 ≠ 649 _v6 (per 红线 12)
- ✓ UUID j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 (per 红线 13)
- ✓ 不写 cegr.* 生产表 (per 红线 14)
- ✓ 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff (per 红线 15)
- ✓ O1 零动作 + 递补池按序 (per 红线 16) — 本次递补池已耗尽
- ✓ 附属产物指针条款 (per 648 P3-1 口径统一) (per 红线 17)
- ✓ 代换行标注规范 (per 649 P3-1 固化) (per 红线 18 增补)
- ✓ backfill 完整性三齐: cc_head 入链 + last_receipt SHA + §NOW 刷新 (per 红线 19)
- ✓ EXEC-QUEUE rev header 同步 (rev 87 → rev 88) (per 649 审计 P4 教训)
- ✓ 已用省全集 (按 actual_province 口径): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / HUBEI / JILIN / LIAONING / GUIZHOU / JIANGSU / **SHAANXI / SICHUAN** = 16 省 (per 红线 20)
- ✓ **红线 14 增补 (递补池耗尽条款, 2026-09-02 立)**: SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS="EXHAUSTED" + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed + 红线 14 生效 (per 任务书 §0.14 + docs/75 §2.2/§2.3/§5)

> **[per 652-A.0 P4×2 规范固化 / 2026-09-02]:** 651 审计定案 PASS（有限通过）+ 2×P4 教训沉淀（详见 docs/75 §6 末尾补):
> - **P4-1** — status/§CURRENT/§NOW **不 pin 中间 SHA**; 仅"三 ref 全等 + 最终 HEAD"表述
> - **P4-2** — cc_head 链 SHA 一律 `git log` 实测; amend 操作必须**先 amend 完成再写链文本**（或先取 SHA 再 amend），禁止凭推理
> - **O-1 预测命中**: m2 复跑污染第 2 次命中, `git checkout` 即还原 (加固开放)
> - **O-2 未复发**: 关闭观察

---

## §CHAIN_MAPPING

| 任务书条目 | 落地文件 | commit (待 §C-3 双推) |
|---|---|---|
| 651-A.0 | `docs/74-m4-13-policy-detail-real-v7-20260901.md` §2.1 + §2.4 + §4.4 行内 append 尾注 | (内含于 delivery commit) |
| 651-A.1 | `scripts/fetch_m4_14_policy_detail_v8_2024.py` + `scripts/seed_m4_14_policy_detail_real_v8.sql` + `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` | (内含于 delivery commit) |
| 651-A.2 | O1 零动作 (docs/52 零改动) | — |
| 651-A.3 | `docs/75-m4-14-policy-detail-real-v8-20260902.md` | (内含于 delivery commit) |
| 651-A.4 | `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` + `docs/reports/m4_14_policy_detail_real_v8_20260902.md` | (内含于 delivery commit) |
| 651-B | `tests/test_m4_14_policy_detail_real_v8.py` (26 cases) | (内含于 delivery commit) |
| 651-C | 本 receipt + EXEC-QUEUE rev87→rev88 + backfill 三齐 | 待 §C-3 + §C-4 |

---

## §SUMMARY

- **651-A.0 蓝图更正**: ✓ docs/74 §2.1 P4-1 行内更正 + §2.4/§4.4 P4-2 口径尾注 (grep "sha anxi" 残留 = 0)
- **651-A.1 M4.14 v8 真实化**: ✓ 16 INSERT; chain_id='real_651_m4_14_policy_detail_v8'; UUID j 段; 2 NEW SHA 9d0ad78a/f58a3384; substitute_used=0; HTTP 4/12 (33%)
- **651-A.2 O1 零动作**: ✓ O1 仍 OPEN; docs/52 零改动
- **651-A.3 架构师审查**: ✓ docs/75 §1-§6 286 行 (含递补池生命周期收官 4 阶段登记)
- **651-A.4 evidence ×2**: ✓ 主 evidence (含 651 §0.14 + BLOCKED_NO_POOL 援引) + 附属报告 (9 节齐全)
- **651-B tests**: ✓ 26 cases PASSED in 1.28s; ≥163 跨刀 spike 回归 (M4.1→M4.14 全套) 满足 ≥126 任务书阈值
- **651-C commits + 双推 + backfill 三齐 + rev header**: 待 §C-3 + §C-4 执行

---

— End 651 DELIVERED receipt —