# 650-stage0-architect-m4-13-v7-substitute-labeling-tasking — 任务书 (knife 650, 2026-09-01)

> **角色**: 架构师 → 执行端（沿用 645-649 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 649 DELIVERED + 审计 **PASS（有限通过）**（`649-stage0-cursor-s649-m4-12-v6-audit-PASS-20260901.md`）
> **scope**: scope A per docs/73 §5.1 = M4.13 v7（guizhou + jiangsu 第 13/14 样本）+ 649 审计 P3-1 蓝图更正与规范固化；**O1 零动作**
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线；**O1 仍 OPEN**）

---

## §0. 红线（13 条，12 沿用 + 1 增补）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-649）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（650 全刀预期 2-10）
4. 不改 docs/45/50/53/66/67/68/69/70/71/72/73 既有正文 —— **修正项一律行内 append 尾注，不删行不删 OPEN 行**（End 行就地扩展沿用前例须可溯；**scripts/ 蓝图 SQL 的 P3-1 更正不属 docs 正文，允许行内更正 + 尾注标记**）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项（2026-08-29 铁律）
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_650_m4_13_policy_detail_v7'`（末段 `_v7`，≠ 649 `_v6` ≠ 648 `_v5`）
10. UUID **i 段**（i0/i1-i6`eebc99`，后缀编号自报并全 distinct）≠ 649 h 段 / 648 g 段 / 647 f 段 / 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰；m2 crosscheck 报告零 diff
13. **增补**: O1 零动作 + 递补池按序（shaanxi → sichuan；每候选 ≤4 attempts）+ 附属产物指针条款（沿用）+ **代换行标注规范：source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB**（per 649 审计 P3-1，固化 647 先例）

## §1. 任务分解

### 650-A.0 649 审计 P3-1 蓝图更正 + 规范固化

- `scripts/seed_m4_12_policy_detail_real_v6.sql` h02 行行内更正（允许，非 docs 正文）：`'CN', 'HUBEI'` → `'CN', 'LIAONING'`；`source_name` → `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'`；行尾 append 尾注标记 `-- per 649 审计 P3-1 / 650-A.0 行内更正 2026-09-01`
- 同文件其余引用该样本名称的 policy 表行若有 "湖北省"（湖北）字样同步更正 + 尾注
- docs/73 §6 行内 append 尾注登记 649 审计结果（PASS·有限通过 + P3-1 + P4×3 已修/登记）

### 650-A.1 M4.13 政策详情 v7 真实化 spike（第 13/14 样本）

- 沿用 649 fetch/seed 模式：**2 新样本**（≤12 total）
  - guizhou 首选: `https://www.guizhou.gov.cn/zwgk/`；fallback #1 `https://www.guizhou.gov.cn/`（省府根）
  - jiangsu 首选: `https://www.jiangsu.gov.cn/zwgk/`；fallback #1 `https://www.jiangsu.gov.cn/`（省府根）
  - 两级均 BLOCKED → 递补池按序 shaanxi → sichuan
  - 已用省全集（不得重复，按 actual_province 口径）: HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/**LN**/JL
- 产物: `scripts/fetch_m4_13_policy_detail_v7_2024.py` + `scripts/seed_m4_13_policy_detail_real_v7.sql`（2 样本 × 8 表 = **16 INSERT 行**；语句数自报；代换若触发按红线 13 标注 actual_province）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID i 段；真实 SHA 2 个 distinct（≠ 638-649 全部 SHA；drift 按 docs/52 (a) 注记）

### 650-A.2 O1 零动作（沿用）

### 650-A.3 架构师级审查文档

- `docs/74-m4-13-policy-detail-real-v7-20260901.md` §1-§6 + 650-A.0 更正说明

### 650-A.4 证据 2 文件

- `docs/reports/m4_13_policy_detail_real_v7_20260901.md` + `evidence_pack/m4_13_policy_detail_real_v7_20260901.json`（沿用 649 cell 结构：actual_province/fallback_chain_used/逐 attempt 锚点）

### 650-B 测试（≥8 用例，全套 green）

- `tests/test_m4_13_policy_detail_real_v7.py` ≥8（守门: 2 SHA distinct ≠ 638-649 / i 段 ≠ h·g·f·e·d·c / chain_id `_v7` / 16 INSERT / is_demo='false' / 不宣称 PASS / docs/74 六节 / **P3-1 更正守门：seed_m4_12 无 'HUBEI' 残留于代换行 + 存在 LIAONING 更正尾注**）
- 回归: 649 全量 98 例保持 green（总 ≥106）

### 650-C 回执 + commit + 双推

- 回执 `650-stage0-cc-m4-13-v7-substitute-labeling-receipt-20260901.md` §PHOTO-1..N
- EXEC-QUEUE rev85 → rev86（§CURRENT DELIVERED + §CHAIN_TAIL 650 OPEN→DELIVERED + §ACK entry）；**backfill 三齐 + rev header 行同步**（per 649 审计 P4 教训：顶部 `> **rev N**` 行必须与 §META 同步）
- 每 commit 双推: `git push origin HEAD && git push github HEAD`

## §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
# 期望: 650 ≥8 + 649 侧 98 = ≥106 passed
git log --oneline -8 && git status -s   # 期望: 650 commits 双推, 无 pending diff
grep -n "LIAONING" scripts/seed_m4_12_policy_detail_real_v6.sql | head -2   # 期望: P3-1 更正命中 + 尾注标记
```

— End 650 tasking 20260901 —
