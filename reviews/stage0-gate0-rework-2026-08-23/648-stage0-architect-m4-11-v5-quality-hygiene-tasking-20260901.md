# 648-stage0-architect-m4-11-v5-quality-hygiene-tasking — 任务书 (knife 648, 2026-09-01)

> **角色**: 架构师 → 执行端（沿用 645-647 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 647 DELIVERED + 审计 **PASS（有限通过）**（`647-stage0-cursor-s647-m4-10-v4-audit-PASS-20260901.md`）
> **scope**: 三合一 = A.0 jiangxi 样本质量复验（审计 P3-1）+ A.1 M4.11 v5 省扩展（scope A per docs/71 §5.1）+ A.2 m2 报告污染卫生收口（审计 P3-3）；**O1 零动作**
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线；**O1 仍 OPEN**）

---

## §0. 红线（13 条，12 沿用 + 1 显式化）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-647）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（648 全刀实际预期 3-7）
4. 不改 docs/45/50/53/66/67/68/69/70/71 既有正文 —— **修正项一律行内 append 尾注，不删行不删 OPEN 行**（648-A.2 改测试代码文件不属于 docs 正文红线）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项（2026-08-29 铁律）
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_648_m4_11_policy_detail_v5'`（末段 `_v5`，≠ 647 `_v4` ≠ 646 `_v3`）
10. UUID **g 段**（g0/g1-g6`eebc99`，后缀编号自报并全 distinct）≠ 647 f 段 / 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰；**m2 crosscheck 报告只允许通过还原保持干净，不允许 648 交付 diff 包含它**
13. **显式化（原 O1 零动作 + substitute 条款）**: O1 零动作（不新增 probe、不启用、不动 registry/connector）；**跨省 substitute 仅限本任务书 §1 A.1 预授权代换池**（jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu），触发即须在 evidence `substitute_reason` + docs/72 §2 登记，且不得取自已用省全集

## §1. 任务分解

### 648-A.0 jiangxi "403" 样本质量复验（审计 P3-1）

- 1×HTTP re-fetch `https://www.jiangxi.gov.cn/zwgk/`（计入 ≤12 预算）：
  - SHA 与 `56481050…` 一致 → evidence 注记 `reverify: CONTENT_CONFIRMED`（title="403" 判定为页面真实标题/模板异常，样本有效）
  - SHA 不一致 → 按 docs/52 (a) drift 登记（旧/新 SHA + 时间戳），并做 1 次内容锚点检查（页面含"政务公开"字样）；若内容为 WAF 挑战页（无锚点）→ 登记 `SAMPLE_DEGRADED` 并在 docs/72 §2 评估换样（换样只可从 §0-13 代换池取，1×HTTP）
- 产物并入 648-A.4 evidence（fetch_log `phase=jiangxi_reverify`）

### 648-A.1 M4.11 政策详情 v5 真实化 spike（第 9/10 样本）

- 沿用 647 fetch/seed 模式：**2 新样本**（≤12 total 含 A.0 复验）
  - hunan 首选: `https://www.hunan.gov.cn/zwgk/`；fallback #1 `https://www.hunan.gov.cn/`（省府根）
  - anhui 首选: `https://www.ah.gov.cn/zwgk/`；fallback #1 `https://www.ah.gov.cn/`（省府根）
  - 两级均 BLOCKED → 启用 §0-13 预授权代换池（按序 jilin → liaoning → hubei…，每候选 ≤4 attempts，总预算 ≤12）
  - 已用省全集（不得重复）: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX
- 产物: `scripts/fetch_m4_11_policy_detail_v5_2024.py` + `scripts/seed_m4_11_policy_detail_real_v5.sql`（2 样本 × 8 表 = **16 INSERT 行**：12 政策表 + 2 registry + 2 document；语句数自报）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID g 段；真实 SHA 2 个 distinct（≠ 638-647 全部 SHA；drift 按 docs/52 (a) 更新并注记）

### 648-A.2 m2 crosscheck 报告污染卫生收口（审计 P3-3，复发 2 次）

- 定位重写 tracked `docs/reports/m2_2024_gdp_crosscheck_20260831.md` 的生成型测试（嫌疑 `tests/test_sure.py` 或同族）
- 最小改动二选一： 生成路径改 `tmp_path`/`/tmp`（推荐，保运行时校验）； 默认 `pytest.mark.skip` + 显式 flag 启用
- 约束: 不删测试逻辑、不碰 4 fixture、不动 `docs/54 §08b` 协议文本；改后该测试单独跑 green；**禁止运行全量挂起套件**（网络/DB 依赖测试，645 教训）验证方式 = 目标文件 + 该测试文件
- 交付前 `git status` 必须干净（tracked 报告零 diff）

### 648-A.3 架构师级审查文档

- `docs/72-m4-11-policy-detail-real-v5-quality-hygiene-20260901.md` §1-§6（终态 / spike 边界 + substitute 登记 / SQL 结构 / lineage sentinel + SHA 区分表 / 下一步 / 不宣称 PASS）+ A.0 复验结论 + A.2 卫生收口说明

### 648-A.4 证据 2 文件

- `docs/reports/m4_11_policy_detail_real_v5_20260901.md` + `evidence_pack/m4_11_policy_detail_real_v5_20260901.json`（含 A.0 reverify fetch_log 条目）

### 648-B 测试（≥8 用例，全套 green）

- `tests/test_m4_11_policy_detail_real_v5.py` ≥8（守门: 2 SHA distinct ≠ 638-647 / g 段 ≠ f·e·d·c / chain_id `_v5` / 16 INSERT / is_demo='false' / 不宣称 PASS / jiangxi reverify 注记存在 / 代换登记守门〔若触发〕）
- 回归: 647 52 例保持 green（总 ≥60）
- 卫生: 改造后的生成型测试单独跑 green 且 tracked 报告零 diff

### 648-C 回执 + commit + 双推

- 回执 `648-stage0-cc-m4-11-v5-quality-hygiene-receipt-20260901.md` §PHOTO-1..N
- EXEC-QUEUE rev80 → rev81（§CURRENT DELIVERED + §CHAIN_TAIL 648 OPEN→DELIVERED + §ACK entry）
- 每 commit 双推: `git push origin HEAD && git push github HEAD`（SSH fallback，HTTPS 443 阻塞沿用）

## §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_policy_detail_real_v4.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
# 期望: 648 ≥8 + 647 侧 42 = ≥60 passed（M4.10 14 + M4.9 10 + O1 6 + M6 10 + M4.8 12 = 52 回归）
git log --oneline -8 && git status -s   # 期望: 648 commits 双推, 无 pending diff（含 m2 报告干净）
grep -c 'reverify' evidence_pack/m4_11_policy_detail_real_v5_20260901.json   # 期望: ≥1（A.0 复验留痕）
```

— End 648 tasking 20260901 —
