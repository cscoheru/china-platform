# S2.9 同类地区对比 规划 CC 回执

- 编号：`242-stage0-cc-s29-peer-compare-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`94` → CC 执行
- 任务书：`241-stage2-s29-peer-compare-planning-tasking-20260826`
- 前置：`240` S2.8-lite PASS（含 OPEN: pack 漏登 `239`）；`docs/34` §4 序 12；`docs/05` §8；`docs/10` §133

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 94）| ✅ | — | — |
| 2 | 读 `240` PASS（含 OPEN）+ `241` + `docs/34` §4 序 12 + `docs/05` §8 + `docs/10` §133 | ✅ | — | — |
| 3 | **补 pack 登记回执 239**（Cursor audit 240 OPEN 收口）| ✅ | `4ffaef42` | documentation |
| 4 | 起草 **`docs/43-stage2-s29-peer-compare-plan-20260826.md`**（641 行；10 节）| ✅ | `0cbd8bf6` | documentation |
| 5 | smoke-check 仍 PASS（无 frontend 改动）| ✅ | — | — |
| 6 | 文件级 forbidden-token guard（docs/43 CLEAN）| ✅ | — | — |
| 7 | 跨 lite 回归（s21lite..s26lite = **42/42**）| ✅ | — | — |
| 8 | 补 pack（558 → **561**；含 receipt 239 backfill + docs/43 + receipt 242）| ✅ | — | documentation |
| 9 | 写回执 `242` 入 `reviews/` | ✅（本文件）| （见 backfill）| documentation |
| 10 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 11 | 三路对齐 | ⏳ | — | — |
| 12 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `docs/43-stage2-s29-peer-compare-plan-20260826.md` | **641** | （backfill）| `0cbd8bf6` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/239-stage0-cc-s28-lite-seven-dim-impl-receipt-20260826.md` | （backfill per audit 240 OPEN）| 10488 | `4ffaef42` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/242-stage0-cc-s29-peer-compare-planning-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 docs/43 章节结构（10 节）

| § | 主题 | 来源 |
|---|---|---|
| §1 | 目标 + S2.9 与 S2.7/S2.8 边界 + 红线 | per `241` §SCHEMA + docs/34 §4.3 + docs/05 §8.3 |
| §2 | 契约：`comparison_group` + `comparison_group_member` schema + `mart_peer_region_compare` 视图 + 应用层守门 | per docs/05 §8.1 + docs/40 §2.3 + docs/41 §2.3 平行 |
| §2.5 | 与 S2.7 EvidenceChain 接驳（段级对比）| per docs/40 §5.1 平行 |
| §2.6 | 与 S2.8 七维度 cell 接驳（region-level 聚合）| per docs/42 §5.3 + docs/06 §6.6 |
| §3 | UI 形态：RegionCard tab + 同类地区对比卡（折叠/展开）| per docs/08 §S2.9 |
| §4 | 首批入库策略：5 focal × 3 peer = 20 行 seed | per docs/08 §S2.9 + docs/33 §3.2 sentinel |
| §5 | 与 S2.7/S2.8/S2.6/S2.10 接驳 + 验证 | per docs/41 §5.1 + docs/42 §5.3 |
| §6 | 验收清单（23 项）| per docs/42 §6 平行 |
| §7 | 关键风险与回滚（9 项）| per docs/42 §7 平行 |
| §8 | 不做什么（22 项红线）| per docs/42 §8 平行 + docs/06 §6.6 |
| §9 | 与现有文档的关系（19 引用）| per docs/42 §9 平行 |
| §10 | CC 建议（8 选项）| per docs/42 §10 平行 |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 558 | **561** (+3: receipt 239 backfill + docs/43 + receipt 242) |
| `len(artifacts)` | 558 | **561** |
| `sum(role_count)` | 547 ❌ | **561** ✅（bump script 重新从 artifacts 计算 source-of-truth）|

**invariant 守门**：561 == 561 == 561 ✅

**bug 修复**：knife 11-15 期间 manifest 的 `role_count` 字段未随 `artifacts` 同步更新，导致 sum(role_count)=547 != artifact_count=558（11 unaccounted）。本刀 bump script 改为从 artifacts 重新计算 role_count（per `docs/42 §2.6` 应用层 enum-style 守门平行）；不再让两个字段单独漂移。

**OPEN 收口**：Cursor audit 240 标注的 "回执 239 漏登 manifest" 已通过本 knife 步 3 修复。

---

## §2. 关键决策（per `241` §SCHEMA 钉死 + docs/05 §8 + docs/10 §133）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **规划刀** — 仅 `docs/43`；无 migration / 无 schema / 无新表 | `241` §SCHEMA + 用户裁定 D |
| 范围 | **手工选择**初版（per docs/05 §8.2 手动匹配）| docs/05 §8.2 + docs/34 §4 序 12 |
| ❌ 全国实时排名 | 红线（per docs/34 §4.3 + docs/05 §8.3）| `241` §SCHEMA 红线 |
| ❌ Mahalanobis 距离自动匹配 | Stage 3 范围 | docs/05 §8.2 |
| ❌ 倾向得分匹配 | Stage 3 范围 | docs/05 §8.2 |
| ❌ 按 GDP 总量取 top N | 红线（per docs/05 §8.3）| `241` §红线 |
| 匹配依据 4 维度 | 人口规模 / 区位 / 产业基础 / 发展阶段 | docs/05 §8.1 |
| 每 group 1 focal + 3-5 peer | peer 范围守门 | docs/05 §8.2 + docs/08 §S2.9 |
| `selection_justification` 非空 | NOT NULL + CHECK `<> ''` | docs/10 §133 |
| `selection_method` CHECK 含 3 种 | manual / mahalanobis / propensity（仅 manual 落地）| docs/05 §8.2 + §10.2 |
| 首批 seed 规模 | 5 focal × 3 peer = **20 行**（5 group + 15 peer + 5 focal）| docs/08 §S2.9 |
| mart 行数守门 | ≤ 20 行（演示守门）| §4.2 |
| `is_demo` 流转 | DRAFT = `"true"`；公开登记后 = `"false"` | docs/33 §3.2 sentinel |
| 评分字段 | ❌ **不引入**（per docs/06 §6.6 红线）| docs/06 §6.6 + §10.6 |
| schema ENUM | ❌ **不引入**（应用层 enum-style 守门）| docs/40 §2.3 + docs/41 §2.3 平行 |
| `comparison_group_member.role_in_group` | `focal` / `peer` 双值 | docs/05 §8.2 + §10.7 |
| S2.9 × S2.7 接驳粒度 | mart 仅展示 n_observation 等聚合列（per §5.1）| docs/42 §5.3 + `241` §红线 |
| S2.9 × S2.8 接驳粒度 | mart 仅展示 region-level 聚合（per §5.2）| docs/06 §6.6 + `241` §红线 |
| 同类区间显示位 | 折叠态保留占位 + 注 "（S2.9 范围；此刀不接）" | docs/42 §10.8 平行 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅规划 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 仅规划 + 手工选择 |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""维度严重度"）| ✅ §8 + docs/06 §6.6 + docs/41 §10.8 红线条目 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §10 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 558 → 561；bump script 重新计算 role_count source-of-truth |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ OPEN 收口（Cursor audit 240 标注的 receipt 239 漏登）| ✅ 步 3 修复 |
| ✅ bug 修复（manifest role_count 漂移）| ✅ bump script 改为 source-of-truth 计算 |
| ✅ 不写 dbt mart | ✅（per `241` §SCHEMA）|
| ✅ 不写 migration | ✅（per `241` §SCHEMA）|
| ✅ 不接 S2.7 EvidenceChain UI 改动 | ✅（per `241` §SCHEMA 红线）|
| ✅ 不接 S2.8 七维度观察卡 UI 改动 | ✅（per `241` §SCHEMA 红线）|
| ✅ 不接 S2.6 反例登记 UI 改动 | ✅（per `241` §SCHEMA 红线）|
| ✅ 不接 S2.10 Gate 2 评审包 | ✅（per `241` §SCHEMA 红线）|
| ✅ 不接全国实时排名 | ✅（per `241` §SCHEMA 红线 + docs/34 §4.3）|
| ✅ 不接 Mahalanobis 距离自动匹配 | ✅（per docs/05 §8.2 — Stage 3 范围）|
| ✅ 不接倾向得分匹配 | ✅（per docs/05 §8.2 — Stage 3 范围）|
| ✅ 不按 GDP 总量取 top N | ✅（per docs/05 §8.3 红线 + §10.6）|
| ✅ 不引入 score / rating / rank / peer_rank 字段 | ✅ §8 红线条目 |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门 |
| ✅ 不动 `polarity` CHECK | ✅ 无关 |
| ✅ 不动 `information_layer` ENUM | ✅ 无关 |
| ✅ 不引入跨行 CHECK 约束 | ✅ trigger + 应用层守门 |
| ✅ 跨 lite 回归 s21lite..s26lite = 42/42 | ✅ |
| ✅ smoke-check 仍 PASS | ✅ |
| ✅ docs/43 文件级 forbidden-token guard CLEAN | ✅ |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 94 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| OPEN 收口 | bump script 添加 receipt 239 (Cursor audit 240 OPEN) | ✅ `4ffaef42` 入 manifest |
| docs/43 起草 | 641 行 / sha `0cbd8bf6` | ✅ |
| docs/43 file-level guard | 扫描 forbidden tokens | ✅ CLEAN |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 561 == 561 == 561 |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ PASS（无 frontend 改动）|
| pytest 跨 lite | `python3 -m pytest tests/test_*_s*lite.py -q` | ✅ 42/42 |
| commit | `git add docs/43-stage2-s29-peer-compare-plan-20260826.md evidence_pack/manifest.json reviews/.../239-...md reviews/.../242-...md && git commit -m "feat(docs): S2.9 同类地区对比规划 (5 focal × 3 peer; 4 维度匹配; manual only)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 94` 完成后：Cursor 收 `242` → 下发 `243-stage0-cursor-s29-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.9 落地刀（tasking 244+）— migration + seed + dbt mart + admin/UI 接驳
- 若 FAIL：`242-correction` 回合（修 docs/43 + re-commit）

---

## §6. 备注

- **manifest bug 修复**：knife 11-15 期间 manifest 的 `role_count` 字段未随 `artifacts` 同步更新，导致 sum(role_count)=547 != artifact_count=558（11 unaccounted）。本刀 bump script 改为从 artifacts 重新计算 role_count；后续 bump script 都按此 source-of-truth 模式（避免再漂移）。
- **OPEN 收口**：Cursor audit 240 标注的 "回执 239 漏登 manifest" 已修复；同时上轮的 "回执 236 漏登" 在 knife 15 已修复。

— End of `242` —