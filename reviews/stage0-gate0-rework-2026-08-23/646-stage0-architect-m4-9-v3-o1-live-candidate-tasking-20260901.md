# 646-stage0-architect-m4-9-v3-o1-live-candidate-tasking — 任务书 (knife 646, 2026-09-01)

> **角色**: 架构师 → 执行端（沿用 645 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 645 DELIVERED + 审计 **PASS**（`645-stage0-cursor-s645-m6-m4-8-audit-PASS-20260901.md`）
> **scope**: A（handoff §G 推荐，审计 §B.4 认可）= M4.9 政策详情 v3 扩展 + docs/52 B 路 live-candidate 探测（O1 主路径登记）+ 审计 P3 修正项
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线；**O1 仍 OPEN**）

---

## §0. 红线（13 条，12 沿用 + 1 新增）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-645）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total
4. 不改 docs/45/50/53/66/67/68/69 既有正文 —— **修正项一律行内 append 尾注，不删行不删 OPEN 行**
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项（2026-08-29 铁律）
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_646_m4_9_policy_detail_v3'`（末段 `_v3`，≠ 645 `_v2`）
10. UUID **e 段**（e0/e1-e6`eebc99`，e21-e94）≠ 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 11 行 registry SHA 零漂移；4 fixture 字节零触碰
13. **新增**: live-candidate 只登记不启用（O1 仍 OPEN；不换源、不动生产 connector；registry 零改动或仅追加 pending-candidate 登记行，等用户/架构师裁定）

## §1. 任务分解

### 646-A.0 审计 P3 修正项（行内 append 尾注，不删行）

- docs/68 §4 尾 + docs/50 §4.4 第48项行尾 + docs/53 §5 第48项行尾：更正 "7 个 distinct chain_id" → **8 个**（per 645 审计 F1/F2，附 638 probe 口径备注）
- docs/50/53 第48项行尾：`12/12 pytest green planned` → append `实际交付 22/22 green per 645 回执/审计`（F4）
- docs/69 或 docs/70 尾注登记 F7（henan-zwgk 日期元数据差异）；F3/F6 登记于本任务书即可
- COMPASS 已由 645 审计顺带刷新（F5），646 零动作

### 646-A.1 M4.9 政策详情 v3 真实化 spike（第 5/6 样本）

- 沿用 645 fetch/seed 模式：**2 新样本 × 1 HTTP each**（≤12 total）
  - fujian: `https://www.fujian.gov.cn/zwgk/`（644 已三连确认 REACHABLE）
  - guangdong 首选: `https://www.gd.gov.cn/zwgk/`；若 404/不可达 → fallback #1 `https://www.gd.gov.cn/zwgk/zcfg/` → fallback #2 `https://www.guizhou.gov.cn/zwgk/`（fall-through 政策 per 625，evidence 注明采用序号）
- 产物: `scripts/fetch_m4_9_policy_detail_v3_2024.py` + `scripts/seed_m4_9_policy_detail_real_v3.sql`（2 样本 × 8 表 = **16 INSERT 行**：12 政策表 + 2 registry + 2 document；语句数自报）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID e 段；真实 SHA 2 个 distinct（≠ 638-645 全部 SHA；若遇 drift 按 docs/52 (a) 更新并注记）

### 646-A.2 docs/52 B 路 live-candidate 探测登记（O1 主路径，只登记）

- 读 docs/52 B 路 spec + `source_registry/registry.csv` 现状，选 **≥1 个 live-candidate 政府/统计局源**做候选登记（markdown-only；不启用、不改生产 connector、不写 cegr.*）
- 产物并入 646-A.4 evidence/report；登记项含 URL / 归属 / 观测口径 / 启用前置条件；**O1 仍 OPEN**

### 646-A.3 架构师级审查文档

- `docs/70-m4-9-policy-detail-real-v3-20260901.md` §1-§6（终态 / spike 边界 / SQL 结构 / lineage sentinel / 下一步 / 不宣称 PASS）+ 646-A.0 修正项清单落地说明

### 646-A.4 证据 4 文件

- `docs/reports/m4_9_policy_detail_real_v3_20260901.md` + `evidence_pack/m4_9_policy_detail_real_v3_20260901.json`
- `docs/reports/o1_live_candidate_probe_20260901.md` + `evidence_pack/o1_live_candidate_probe_20260901.json`

### 646-B 测试（≥10 用例，全套 green）

- `tests/test_m4_9_policy_detail_real_v3.py` ≥6（守门 2 SHA distinct / e 段 ≠ d·c 段 / chain_id `_v3` / 16 INSERT / is_demo='false' / 不宣称 PASS）
- `tests/test_o1_live_candidate_probe.py` ≥4（守门 登记≥1 / O1 仍 OPEN / 不启用 / 零 registry 变更或仅 append）
- 回归: 645 22 例必须保持 green

### 646-C 回执 + commit + 双推

- 回执 `646-stage0-cc-m4-9-v3-o1-live-candidate-receipt-20260901.md` §PHOTO-1..N
- EXEC-QUEUE rev76 → rev77（§CURRENT DELIVERED + §CHAIN_TAIL 646 OPEN→DELIVERED + §ACK entry）
- 每 commit 双推: `git push origin HEAD && git push github HEAD`

## §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
# 期望: 646 ≥10 + 645 22 = ≥32 passed
git log --oneline -8 && git status -s   # 期望: 646 commits 双推, 无 pending diff
```

— End 646 tasking 20260901 —
