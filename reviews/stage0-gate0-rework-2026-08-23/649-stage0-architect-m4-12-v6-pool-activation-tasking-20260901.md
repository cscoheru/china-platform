# 649-stage0-architect-m4-12-v6-pool-activation-tasking — 任务书 (knife 649, 2026-09-01)

> **角色**: 架构师 → 执行端（沿用 645-648 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 648 DELIVERED + 审计 **PASS（有限通过）**（`648-stage0-cursor-s648-m4-11-v5-audit-PASS-20260901.md`）
> **scope**: scope A per docs/72 §5.1 = M4.12 v6 预授权池激活（hubei + jilin）+ 648 审计 P3-1 口径统一落地 + P4 登记；**O1 零动作**
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线；**O1 仍 OPEN**）

---

## §0. 红线（13 条，12 沿用 + 1 沿用改述）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-648）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（649 全刀预期 2-9）
4. 不改 docs/45/50/53/66/67/68/69/70/71/72 既有正文 —— **修正项一律行内 append 尾注，不删行不删 OPEN 行**（End 行就地扩展沿用前例须可溯）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项（2026-08-29 铁律）
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_649_m4_12_policy_detail_v6'`（末段 `_v6`，≠ 648 `_v5` ≠ 647 `_v4`）
10. UUID **h 段**（h0/h1-h6`eebc99`，后缀编号自报并全 distinct）≠ 648 g 段 / 647 f 段 / 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰；m2 crosscheck 报告零 diff
13. **沿用改述**: O1 零动作 + **跨省 substitute 仅限递补池**（liaoning/shaanxi/sichuan/guizhou/jiangsu），触发即 evidence `substitute_reason` + docs/73 §2 登记；**附属复验/验证产物允许独立文件，但主 evidence `summary.methodology` 必须含指针**（文件名 + verdict，per 648 审计 P3-1）

## §1. 任务分解

### 649-A.0 648 审计修正/登记项

- docs/72 §6 行内 append 尾注登记 648 审计结果（PASS·有限通过 + P3-1 口径统一 + P3-2 回填缺失 + P4-1/3/4 清单）；rev81 三处回填缺口已由审验端 rev82 全面修复（登记即可）
- 648 审计 P3-1 口径统一条款 → 红线 13（本任务书已固化，docs/72 尾注援引即可）

### 649-A.1 M4.12 政策详情 v6 真实化 spike（第 11/12 样本，预授权池激活）

- 沿用 648 fetch/seed 模式：**2 新样本**（≤12 total）
  - hubei 首选: `https://www.hubei.gov.cn/zwgk/`；fallback #1 `https://www.hubei.gov.cn/`（省府根）
  - jilin 首选: `https://www.jl.gov.cn/zwgk/`；fallback #1 `https://www.jl.gov.cn/`（省府根）
  - 两级均 BLOCKED → 递补池按序 liaoning → shaanxi → sichuan → guizhou → jiangsu（每候选 ≤4 attempts，总预算 ≤12）
  - 已用省全集（不得重复）: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH
- 产物: `scripts/fetch_m4_12_policy_detail_v6_2024.py` + `scripts/seed_m4_12_policy_detail_real_v6.sql`（2 样本 × 8 表 = **16 INSERT 行**：12 政策表 + 2 registry + 2 document；语句数自报）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID h 段；真实 SHA 2 个 distinct（≠ 638-648 全部 SHA；drift 按 docs/52 (a) 更新并注记）

### 649-A.2 O1 零动作

- 不新增 probe、不启用、不改 registry/connector；回执 O1 = OPEN（沿用 646 登记）

### 649-A.3 架构师级审查文档

- `docs/73-m4-12-policy-detail-real-v6-20260901.md` §1-§6（终态 / spike 边界 + 代换登记〔若触发〕/ SQL 结构 / lineage sentinel + SHA 区分表 / 下一步 / 不宣称 PASS）+ 649-A.0 登记说明

### 649-A.4 证据 2 文件

- `docs/reports/m4_12_policy_detail_real_v6_20260901.md` + `evidence_pack/m4_12_policy_detail_real_v6_20260901.json`（若有附属复验产物按红线 13 加指针）

### 649-B 测试（≥8 用例，全套 green）

- `tests/test_m4_12_policy_detail_real_v6.py` ≥8（守门: 2 SHA distinct ≠ 638-648 / h 段 ≠ g·f·e·d·c / chain_id `_v6` / 16 INSERT / is_demo='false' / 不宣称 PASS / docs/73 六节 / evidence methodology 指针守门〔若适用〕）
- 回归: 648 全量 81 例保持 green（总 ≥89）

### 649-C 回执 + commit + 双推

- 回执 `649-stage0-cc-m4-12-v6-pool-activation-receipt-20260901.md` §PHOTO-1..N
- EXEC-QUEUE rev83 → rev84（§CURRENT DELIVERED + §CHAIN_TAIL 649 OPEN→DELIVERED + §ACK entry）；**backfill 完整性三齐**：cc_head 入链 + last_receipt SHA + §NOW 刷新（per 648 审计 P3-2）
- 每 commit 双推: `git push origin HEAD && git push github HEAD`

## §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
# 期望: 649 ≥8 + 648 侧 81 = ≥89 passed
git log --oneline -8 && git status -s   # 期望: 649 commits 双推, 无 pending diff（含 m2 报告干净）
grep -n 'real_649_m4_12_policy_detail_v6' scripts/seed_m4_12_policy_detail_real_v6.sql | head -1   # 期望: chain_id 命中
```

— End 649 tasking 20260901 —
