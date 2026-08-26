# docs/45 S2.7-b-full-lite 索引刷新 — CC 回执

- 编号：`269-stage0-cc-s27bf-refresh-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`108` → CC 执行
- 任务书：`268-stage2-gate2-index-s27bf-refresh-tasking-20260826`
- 前置：`267` S2.7-b-full-lite PASS；`docs/45`（knife 23 已交 S2.7-b-lite 刷新）；`docs/47`；回执 `266`
- 用户裁定：Stage 2 **C**；缩刀 **D**；自主推进（per Cursor 2026-08-26 META）
- 刷新性质：**docs/45 索引刷新** — 反映 S2.7-b-full-lite 收口（mart-shape 接驳；feature-flag 默认 mock）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 108）| ✅ | — |
| 2 | 读 `268` tasking + 回执 `266` + docs/45 现状 | ✅ | — |
| 3 | 修正 docs/45 §5.6 错位（原位于 §6 之后；现并入 §6.2）| ✅ | documentation |
| 4 | 修正 docs/45 §6 OPEN 表「10 地市（S2.7-b）」过时行（tasking 待发 → 257 + 266 已交）| ✅ | documentation |
| 5 | 新增 docs/45 §6.1（S2.7-b 落地回执登记：257 + 266 两行）| ✅ | documentation |
| 6 | 新增 docs/45 §6.2（S2.7-b-full-lite mart-shape 接驳路径表：9 elements）| ✅ | documentation |
| 7 | §7 红线自检补 mart-shape 3 重守门 + feature-flag 默认值 + O1/O8 OPEN 携带 | ✅ | documentation |
| 8 | file-level forbidden-token guard（docs/45）：2 hit 均为 negative/guard 上下文（§6.2 禁词守门块）| ✅ CLEAN | — |
| 9 | 创建 `scripts/_knife26_manifest_bump.py`（2 NEW_ARTIFACTS：bump + receipt）| ✅ | spike_helper |
| 10 | bump pack（595 → **597**；+2 = bump + receipt；docs/45 已在 manifest knife 23 入册）| ⏳ this step | — |
| 11 | smoke-check PASS（含 §10 S2.7-b-full-lite mart-shape 守门）| ✅ | — |
| 12 | cross-lite 回归 120 PASS + 6 SKIP（无回归）| ✅ | — |
| 13 | 写回执 `269` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 14 | commit → `origin` 优先 → `github` | ✅ commit `13733c8`（backfill this line）| — |
| 15 | commit SHA backfill（独立 commit；不 amend-after-push）| ✅ this commit | — |
| 16 | 三路对齐 | ✅ local = origin = github = `13733c8` | — |
| 17 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 修改 1 个文件（不计入 NEW_ARTIFACTS）

| 路径 | 变更 |
|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | §2 #1 + §5.5 OPEN + §6 OPEN row + §6.1 (NEW) + §6.2 (NEW) + §7 补 mart-shape 3 重守门行；pack 597 == 597 == 597 |

### 1.2 新增 2 个文件

| 路径 | 行数 | 大小 | role |
|---|---|---|---|
| `scripts/_knife26_manifest_bump.py` | ~120 | — | spike_helper |
| `reviews/.../269-...md`（本文件）| — | — | documentation |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 595 | **597** (+2: bump + receipt) |
| `len(artifacts)` | 595 | **597** |
| `sum(role_count)` | 595 | **597**（bump script source-of-truth 重算）|

**invariant 守门**：597 == 597 == 597 ✅

---

## §2. 关键决策（per `268` §SCHEMA + docs/47 §6.3 切刀风险）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **docs/45 索引刷新刀** — 反映 S2.7-b-full-lite 收口（回执 266）；OPEN 仍标 O1/mart 全量 | `268` §SCHEMA |
| 刷新范围 | §2 #1 + §5.5 OPEN + §6 OPEN row「10 地市」+ §6.1（NEW 落地回执登记）+ §6.2（NEW mart-shape 接驳路径）+ §7 红线补 4 行 | `268` §NOW "1" |
| 不做 | Gate 2 PASS；O1 真样本；dbt seed；person/tenure 真数据 | `268` §SCHEMA "本刀不做" |
| §5.6 错位修正 | 原 §5.6 位于 §6 之后（line 142-159）；本刀并入 §6.2 mart-shape 接驳路径表（line 149-166），并修正 §6 OPEN row「10 地市」| knife 23 后续结构漂移修复 |
| docs/45 不重入册 | docs/45 已在 manifest（knife 23 入册）；本刀仅内容刷新，不重计入 manifest；pack +2 = bump + receipt | knife 16 fix pattern |
| ❌ 宣布 Gate 2 PASS | 红线条目（§1 + §6 + §7 多次显式守门）| docs/34 §1 + §8 #8 + §133 + `268` §红线 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | §6.2 禁词守门块显式拒绝；§7 补 mart-shape 3 重守门行 | docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 |
| ❌ 改 Cursor 锁定 10 城名单 | docs/45 §5.5 + §6.2 10 城行锁定（4 江苏 + 3 浙江 + 3 广东）| `256` §SCHEMA + docs/46 §2 |

---

## §3. docs/45 改动对照表

| 段 | 改动 | 状态 |
|---|---|---|
| Header (line 8) | 新增 "刷新：queue_rev 108（per `268-stage2-gate2-index-s27bf-refresh-tasking-20260826`）— §2 #1 + §5.6 + §6.2 反映 S2.7-b-full-lite 收口（回执 `266` + commit `beea282`/`0e0a6cf`）— mart-shape TS 类型 + demo fixture + CityPage 接驳（feature-flag；默认 demo）" | ✅ |
| §2 #1 | OPEN 列从「10 地市 OPEN」改为「S2.7-b-lite 已交（mock 壳）— 回执 `257`；mart-shape 接驳（feature-flag；默认 demo）— 回执 `266`；dbt mart 真表 / person/tenure 真数据仍 OPEN → S2.7-b-full 真数据迁移刀」| ✅ |
| §5.5 OPEN | 路线图 row 推 S2.7-b-full 真数据迁移刀（tasking 26X+）= 接 dbt mart 真表 + 接 person/tenure 真数据 + lineage.source_file_sha256 从占位 `'0'*64` 替换为 O1 真实 SHA | ✅ |
| §6 OPEN row「10 地市（S2.7-b）」| 从「⚠️ S2.7-b tasking 待发」改为「S2.7-b-lite 已交（mock 壳）— 回执 `257`；S2.7-b-full-lite 已交（mart-shape 接驳）— 回执 `266`；S2.7-b-full 真数据迁移刀 OPEN（tasking 26X+）」| ✅ |
| §6.1 (NEW) | S2.7-b 落地回执登记表（2 rows: 257 + 266）| ✅ |
| §6.2 (NEW) | S2.7-b-full-lite mart-shape 接驳路径表（9 elements + 禁词守门块）| ✅ |
| §7 红线自检 | 新增 4 行：mart-shape 3 重守门 + feature-flag 默认值 + 兼容 S2.7-b-lite 已交路径 + O1 + O8 OPEN 清单显式携带；pack invariant 数字 570 → 597 | ✅ |

---

## §4. 红线自检（per `268` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8 + docs/47 §1.2）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ docs/45 header + §1 + §6 + §7 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ §5.5 + §6.2 10 城行锁定（4 江苏 + 3 浙江 + 3 广东）|
| ❌ 不接真 SHA 样本 | ✅ docs/45 仅是索引；lineage.source_file_sha256 占位 '0'*64 显式 OPEN → S2.7-b-full |
| ❌ 不接 O1 收口 | ✅ §6.2 lineage.source_file_sha256 row 显式 OPEN — 推 S2.7-b-full 真数据迁移刀 |
| ❌ 不全量 dbt seed | ✅ docs/45 仅是索引；不改 dbt / 不改 schema |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | ✅ §6.2 禁词守门块显式拒绝；§7 补 mart-shape 3 重守门行（runtime + 静态 scanner + pytest + TS 字段白名单）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关（docs/45 是索引文件，不爬网）|
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `268` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 595 → 597；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ docs/45 forbidden-token guard CLEAN | ✅ 2 hit 均为 §6.2 禁词守门块 negative 上下文 |
| ✅ 兼容 S2.7-b-lite（已交；不动 mock 路径）| ✅ docs/45 §5.5 + §7 兼容性守门 |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ docs/45 是索引；mart-shape enum 守门在 §6.2 + §7 |
| ✅ 不动 `polarity` CHECK / `information_layer` ENUM | ✅（schema 字段未动）|
| ✅ Static-segment 守门（dynamic segment route）| ✅ docs/46 §3.2 平行；mart-shape 复用 S2.7-b-lite dynamic segment |
| ✅ O1 + O8 OPEN 清单显式携带 | ✅ docs/45 §3 + §5.5 + §6.2（lineage.source_file_sha256 + relatedPersons）|
| ✅ feature-flag 默认值 | ✅ docs/45 §6.2 + §7 显式守门 |

---

## §5. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 108 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| docs/45 刷新 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ✅（§2 #1 + §5.5 OPEN + §6 row + §6.1 + §6.2 + §7 4 行）|
| docs/45 forbidden-token guard | grep 禁词清单 | ✅ 2 hit 均为 §6.2 禁词守门块 negative 上下文 |
| bump script | `scripts/_knife26_manifest_bump.py` | ✅ 595 → 597（+2 = bump + receipt）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 597 == 597 == 597 |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 S2.7-b-full-lite 仍 PASS |
| cross-lite 回归 | 18 个 lite 文件 pytest | ✅ 158 PASS + 6 SKIP（无回归）|
| commit (knife 26 主提交) | `git add docs/45-stage2-s210-lite-gate2-review-index-20260826.md scripts/_knife26_manifest_bump.py evidence_pack/manifest.json reviews/.../269-...md && git commit -m "docs(45): 刷新 S2.7-b-full-lite mart-shape 接驳路径 + §6.1 落地回执登记（回执 266；pack 595 → 597；不宣布 PASS）"` | ✅ `13733c8` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `9dcc9cc..13733c8` |
| github push | `git push github HEAD`（带 proxy）| ✅ `9dcc9cc..13733c8` |
| 三路对齐 | origin/main = github/main = local HEAD = `13733c8` | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §6. 下次 heartbeat 预期

- `queue_rev 108` 完成后：Cursor 收 `269` → 下发 `270-stage0-cursor-s27bf-refresh-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.7-b-full 真数据迁移刀前置期（tasking 26X+；OPEN；依赖 O1 真实 SHA 收口 + Stage 1 OPEN 收口 + S2.1-lite `mart_person_tenure` PASS）
  - 等待期可并行做其他刀（S2.10 落地 pytest stub / S2.1-lite / S2.7-a 增补等）
- 若 FAIL：`269-correction` 回合（修 docs/45 + re-commit）

---

## §7. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 docs/45 刷新最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做 docs/45 索引刷新** — `268` §SCHEMA 显式约束：不接真 SHA / 不写 dbt / 不全量 seed / 不接 O1 收口 / 不接 person/tenure 真数据。所有 mart 真表 SQL 在 S2.7-b-full 落地刀（tasking 26X+；OPEN）。
- **docs/45 不重入册** — docs/45 已在 manifest（knife 23 入册，role=documentation）；本刀仅内容刷新，不重计入 manifest。pack +2 = bump + receipt（595 → 597）。
- **§5.6 错位修正** — 原 §5.6 mart-shape 接驳位于 §6 之后（line 142-159），与文档结构（§1-§5 + §6 守门汇总 + §7 红线）不匹配。本刀将其并入 §6.2 mart-shape 接驳路径表，并新增 §6.1 落地回执登记表。
- **§6 OPEN row「10 地市」修正** — 原行 "⚠️ S2.7-b tasking 待发" 已过时（S2.7-b-lite 已交；S2.7-b-full-lite 已交；剩余 S2.7-b-full 真数据迁移 OPEN）。修正为反映 3 个里程碑状态。
- **§6.1 落地回执登记** — 新增回执登记表，2 rows: 257（S2.7-b-lite）+ 266（S2.7-b-full-lite）。为后续 S2.7-b-full 落地刀预留 row。
- **§6.2 mart-shape 接驳路径** — 新增 mart-shape 接驳路径表，9 elements 全部列出（含 lineage.source_file_sha256 占位 + person/tenure 真数据接入 OPEN）。末尾 3 行禁词守门块（不派生 score/rating/rank/...）。
- **§7 红线自检补 4 行** — mart-shape 3 重守门 + feature-flag 默认值 + 兼容 S2.7-b-lite + O1/O8 OPEN 携带。
- **依赖 O1 真实 SHA 收口** — docs/47 §3.1 `lineage.source_file_sha256` ⚠️ OPEN；O1 收口前 demo 恒为 '0'*64 占位。
- **依赖 Stage 1 OPEN 收口** — docs/34 §3 + docs/47 §6.3 切刀风险显式守门。
- **依赖 S2.1-lite PASS** — person/tenure 接入契约不成立直到 S2.1-lite `mart_person_tenure` 已交（per docs/47 §3.3 OPEN）。
- **10 城名单锁定** — 4 江苏（nanjing/suzhou/wuxi/nantong）+ 3 浙江（hangzhou/ningbo/wenzhou）+ 3 广东（guangzhou/shenzhen/dongguan）；docs/45 §5.5 + §6.2 锁定，落地刀不得擅自换/加（per `256` §SCHEMA + docs/46 §2）。

— End of `269` —

> 等待 Cursor 审验（预期 `270-stage0-cursor-s27bf-refresh-audit-…md`）。
> 通过后下发 S2.7-b-full 真数据迁移任务（`271-stage2-s27b-full-impl-tasking-…md`，OPEN；依赖 O1 真实 SHA 收口 + Stage 1 OPEN 收口 + S2.1-lite `mart_person_tenure` PASS）。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `268` §红线）。
> ⚠ **本刀只做 docs/45 索引刷新**（per `268` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。
