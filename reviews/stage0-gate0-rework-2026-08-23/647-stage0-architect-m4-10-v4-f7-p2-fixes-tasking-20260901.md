# 647-stage0-architect-m4-10-v4-f7-p2-fixes-tasking — 任务书 (knife 647, 2026-09-01)

> **角色**: 架构师 → 执行端（沿用 645/646 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 646 DELIVERED + 审计 **PASS（有限通过）**（`646-stage0-cursor-s646-m4-9-o1-audit-PASS-20260901.md`）
> **scope**: A（docs/70 §5.1 推荐，审计 §F 认可）= M4.10 政策详情 v4 省扩展（zhejiang + shandong 第 7/8 样本）+ 646 审计 P2/P3 修正项；**O1 零动作**
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线；**O1 仍 OPEN**）

---

## §0. 红线（13 条，12 沿用 + 1 改述）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-646）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（M4.10 side 实际 2）
4. 不改 docs/45/50/53/66/67/68/69/70 既有正文 —— **修正项一律行内 append 尾注，不删行不删 OPEN 行**
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项（2026-08-29 铁律）
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_647_m4_10_policy_detail_v4'`（末段 `_v4`，≠ 646 `_v3` ≠ 645 `_v2`）
10. UUID **f 段**（f0/f1-f6`eebc99`，后缀编号自报并全 distinct）≠ 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰
13. **改述**: O1 零动作（不新增 live-candidate probe、不启用 646 登记的 data.stats.gov.cn、不动 registry/connector；live-candidate 沿用 646 evidence/report 登记，等用户/架构师裁定）

## §1. 任务分解

### 647-A.0 646 审计 P2/P3 修正项（行内 append 尾注，不删行）

- **P2-1 F7 补登记**: docs/70 §4 表尾（或 §6 行尾）append 尾注：`per 645 审计 F7 / 646 审计 P2-1 补登记：henan-zwgk 样本 evidence publication_date=2026-08-20 vs seed SQL policy_document 2026-08-30（SHA/字节数一致，纯元数据日期差异，非数据漂移）`
- **P3-2 措辞更正**: docs/70 §6 行内 append 尾注：`per 646 审计 P3-2 更正：646 链 docs/52 本体零改动（合规，任务书 A.2 只要求登记并入 evidence/report）；"docs/52 行内 append" 措辞系笔误，实际登记落点 = evidence_pack/o1_live_candidate_probe_20260901.json + docs/reports/o1_live_candidate_probe_20260901.md`
- P4-1/2/3 登记于本任务书即可（免修）

### 647-A.1 M4.10 政策详情 v4 真实化 spike（第 7/8 样本）

- 沿用 646 fetch/seed 模式：**2 新样本 × 1 HTTP each**（≤12 total）
  - zhejiang 首选: `https://www.zj.gov.cn/zwgk/`；若 404/不可达 → fallback #1 `https://www.zj.gov.cn/`（省府根）
  - shandong 首选: `https://www.shandong.gov.cn/zwgk/`；若 404/不可达 → fallback #1 `https://www.shandong.gov.cn/`（省府根）
  - fall-through 政策 per 625，evidence 注明采用序号（首选命中则注明 fallback 未触发）
  - 已用省全集（不得重复）: HLJ / HENAN / YUNNAN / FUJIAN / GD
- 产物: `scripts/fetch_m4_10_policy_detail_v4_2024.py` + `scripts/seed_m4_10_policy_detail_real_v4.sql`（2 样本 × 8 表 = **16 INSERT 行**：12 政策表 + 2 registry + 2 document；语句数自报）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID f 段；真实 SHA 2 个 distinct（≠ 638-646 全部 SHA；若遇 drift 按 docs/52 (a) 更新并注记）

### 647-A.2 O1 零动作

- 不新增 probe、不启用、不改 registry/connector；回执中 O1 状态 = OPEN（沿用 646 登记）即可

### 647-A.3 架构师级审查文档

- `docs/71-m4-10-policy-detail-real-v4-20260901.md` §1-§6（终态 / spike 边界 / SQL 结构 / lineage sentinel + SHA 区分表 / 下一步 / 不宣称 PASS）+ 647-A.0 修正项落地说明

### 647-A.4 证据 2 文件

- `docs/reports/m4_10_policy_detail_real_v4_20260901.md` + `evidence_pack/m4_10_policy_detail_real_v4_20260901.json`

### 647-B 测试（≥10 用例，全套 green）

- `tests/test_m4_10_policy_detail_real_v4.py` ≥10（守门: 2 SHA distinct ≠ 638-646 / f 段 ≠ e·d·c 段 / chain_id `_v4` / 16 INSERT / is_demo='false' / 不宣称 PASS / docs/70 F7 尾注存在 / docs/70 P3-2 尾注存在）
- 回归: 646+645 共 38 例必须保持 green（总 ≥48）

### 647-C 回执 + commit + 双推

- 回执 `647-stage0-cc-m4-10-v4-f7-fixes-receipt-20260901.md` §PHOTO-1..N
- EXEC-QUEUE rev78 → rev79（§CURRENT DELIVERED + §CHAIN_TAIL 647 OPEN→DELIVERED + §ACK entry）
- 每 commit 双推: `git push origin HEAD && git push github HEAD`（SSH fallback，HTTPS 443 阻塞沿用）

## §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
# 期望: 647 ≥10 + 646+645 38 = ≥48 passed
git log --oneline -8 && git status -s   # 期望: 647 commits 双推, 无 pending diff
grep -c 'P2-1\|P3-2' docs/71-m4-10-policy-detail-real-v4-20260901.md   # 期望: ≥2（修正落地说明）
```

— End 647 tasking 20260901 —
