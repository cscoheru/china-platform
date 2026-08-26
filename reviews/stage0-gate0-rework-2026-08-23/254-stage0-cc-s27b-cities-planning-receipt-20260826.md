# S2.7-b 10 地市观察页 规划 — CC 回执

- 编号：`254-stage0-cc-s27b-cities-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`99` → CC 执行
- 任务书：`253-stage2-s27b-cities-plan-tasking-20260826`
- 前置：`252` S2.10-lite PASS；`docs/45` §2 #1 OPEN；`docs/44` §5.1.2-§5.1.3；`docs/34` §4 序 5
- 用户裁定：Stage 2 **C**；缩刀 **D**；**自主推进**（仅功能测试 / §BLOCKED 再找用户）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 99）| ✅ | — | — |
| 2 | 读 `252` PASS + `253` tasking + `docs/45 §2 #1` + `docs/44 §5.1.2-§5.1.3` + `docs/34 §4/§10.4` | ✅ | — | — |
| 3 | 起草 **`docs/46-stage2-s27b-cities-evidence-plan-20260826.md`**（11 节）| ✅ | `2a572c64` | documentation |
| 4 | smoke-check 仍 PASS（无 frontend 改动）| ✅ | — | — |
| 5 | 文件级 forbidden-token guard（docs/46 CLEAN；唯一命中"官员能力总分"在 §1.2 红线自检表内，**否定语境**）| ✅ | — | — |
| 6 | 跨 lite 回归（s21lite..s26lite = **42/42** + s210 = **12 PASS** = **54 PASS**）| ✅ | — | — |
| 7 | 补 pack（577 → **579**；含 docs/46 + receipt 254）| ✅ | — | documentation |
| 8 | 写回执 `254` 入 `reviews/` | ✅（本文件）| （backfill）| documentation |
| 9 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 10 | 三路对齐 | ⏳ | — | — |
| 11 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 节数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `docs/46-stage2-s27b-cities-evidence-plan-20260826.md` | **11 节** | **17984** | `2a572c64` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/254-stage0-cc-s27b-cities-planning-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 docs/46 章节结构（11 节）

| § | 主题 | 来源 |
|---|---|---|
| §1 | 目标 + S2.7-b 与前置刀关系 + 红线 | per `253` §SCHEMA + docs/34 §1 + §8 + §10.4 + `253` §红线 |
| §2 | **10 地市锁定清单**（Cursor 裁定，4 江苏 + 3 浙江 + 3 广东）| per `253` §SCHEMA "10 地市锁定" + docs/05 §8.1 + docs/43 §4.1 |
| §3 | Slug 约定 + 路由（**A `/cities/{slug}` 顶层**）| per `253` §SCHEMA "路由建议" + AGENTS.md Static-segment 守门 |
| §4 | UI 复用 S2.7-a 5 省模板（EvidenceChain + SevenDimGrid + PeerCompareCard）| per docs/44 §5.1.1 + `253` §SCHEMA "缩刀落地预期" |
| §5 | EvidenceChain 接入边界（6 段 city 段级适配 + 数据契约 OPEN）| per docs/44 §5.2 + docs/40 §2 + docs/41 §3 |
| §6 | **切刀边界：S2.7-b-lite（mock 壳）vs S2.7-b-full（接 mart）**| per `253` §SCHEMA + §OPEN |
| §7 | 验收清单（lite 10 项 + full 5 项；OPEN）| per docs/08 §3.2 #1 + docs/44 §5.1.2 + `253` §SCHEMA |
| §8 | 红线自检表 | `253` §红线 + docs/34 §1/§8/§133/§10.4 + AGENTS.md Static-segment 守门 |
| §9 | 不做什么（15 项）| per `253` §SCHEMA + docs/34 §4.3 |
| §10 | 与现有文档的关系（25 引用）| per docs/42 §10 + docs/44 §10 + docs/45 §8 平行 |
| §11 | CC 建议（5 选项）| per docs/42 §11 + docs/43 §11 平行 |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 577 | **579** (+2: docs/46 + receipt 254) |
| `len(artifacts)` | 577 | **579** |
| `sum(role_count)` | 577 | **579**（bump script 重新从 artifacts 计算 source-of-truth）|

**invariant 守门**：579 == 579 == 579 ✅

**注**：knife 16 bug 修复后，本刀沿用 source-of-truth 模式。

---

## §2. 关键决策（per `253` §SCHEMA 钉死 + docs/08 §3.2 + docs/34 §4/§10.4）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **规划刀** — 仅 docs/46；无 migration / 无 dbt / 无 pytest / 无 frontend 改动 | `253` §SCHEMA + 用户裁定 D + 自主推进 |
| 10 地市名单 | **锁定**（南京/苏州/无锡/南通 + 杭州/宁波/温州 + 广州/深圳/东莞）| `253` §SCHEMA "10 地市锁定（Cursor 裁定，勿另挑）" |
| 路由方案 | **A `/cities/{slug}` 顶层**（dynamic segment route）| docs/45 §5.1 + AGENTS.md Static-segment 守门 |
| slug 字符集 | `[a-z0-9-]+` | docs/45 §5.1 + §3.1 |
| 切刀策略 | **S2.7-b-lite 优先（mock 壳）→ S2.7-b-full 接 mart（OPEN）** | `253` §SCHEMA "缩刀落地预期" |
| 不可降级验收项 | 仅六段证据链 UI（验收项 #2 — S2.7-b-lite 必带）| docs/45 §2 #2 |
| 演示级可过 | 10 城路由（验收项 #1 配套）/ 七维度观察卡（验收项 #3 复用 S2.8）| docs/45 §2 |
| 已守门 | 官员能力总分（验收项 #4）| docs/45 §2 + docs/46 §1.2 |
| 已交 | INFERENCE/JUDGMENT 角标（验收项 #5）| migration 012 + types |
| 已交 | 反例登记 trigger（验收项 #6）| migration 013 + docs/41 |
| 部分已交 | docs/10 §3.1-3.5（验收项 #7）| knife 20 + s210 pytest 12 PASS |
| ❌ Gate 2 PASS 守门 | receipt 254 严禁 "Gate 2 PASS" 字样 + Cursor 审验 | docs/34 §8 #8 + §133 + `253` §红线 |
| ❌ 改 10 城名单 | 红线（per `253` §SCHEMA）| 不得擅自换/加 |
| 10 城 vs docs/44 §5.1.3 候选 | Cursor 缩减版（每省 3-4 候选 → 3-4 锁定；总 12 候选 → 10 锁定）| docs/44 §5.1.3 + `253` §SCHEMA |
| Gate 2 评审日期 | 暂定 W8（不擅自提前）| docs/34 §10.4 |
| Gate 2 演示数据策略 | 仅 mock（per docs/34 §141）| docs/34 §8 + §11.2 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ §1.2 + §2 + §8 + §11 多次显式守门；receipt 254 严禁 "Gate 2 PASS" 字样 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ §2 锁定清单；落地刀不得擅自换/加 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 仅规划 |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""维度严重度"）| ✅ docs/46 §1.2 + §8 红线条款内显式守门 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §11 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 577 → 579；bump script source-of-truth |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（per `253` §SCHEMA "不接真 mart"）|
| ✅ 不写 migration | ✅（per `253` §SCHEMA）|
| ✅ 不写 pytest case | ✅（per `253` §SCHEMA；落地刀写）|
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3）|
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ 必带 O1 + O3 OPEN 清单 | ✅ §8 显式守门（沿用 docs/45）|
| ✅ 不引入 score / rating / rank 字段 | ✅ §9 红线条目 |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门 |
| ✅ 不动 `polarity` CHECK | ✅ 无关 |
| ✅ 不动 `information_layer` ENUM | ✅ 无关 |
| ✅ 不引入跨行 CHECK 约束 | ✅ trigger + 应用层守门 |
| ✅ 跨 lite 回归 s21lite..s26lite = 42/42 | ✅ |
| ✅ s210 pytest = 12 PASS | ✅ |
| ✅ smoke-check 仍 PASS | ✅ |
| ✅ docs/46 文件级 forbidden-token guard CLEAN | ✅（唯一命中为红线条款否定语境）|
| ✅ Static-segment 守门（dynamic segment route）| ✅ §3.2 显式守门 |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 99 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| docs/46 起草 | 11 节 / sha `2a572c64` | ✅ |
| docs/46 file-level guard | 扫描 forbidden tokens | ✅ CLEAN（红线否定语境）|
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 579 == 579 == 579 |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ PASS（无 frontend 改动）|
| pytest 跨 lite | `python3 -m pytest tests/test_*_s*lite.py -q` | ✅ 42/42 |
| pytest s210 | `python3 -m pytest tests/test_*_s210.py -q` | ✅ 12 PASS + 6 skipped |
| commit | `git add docs/46-...md evidence_pack/manifest.json scripts/_knife21_manifest_bump.py reviews/.../254-...md && git commit -m "feat(docs): S2.7-b 10 地市观察页 规划 (10 城锁定 + 路由 + 切刀边界; 不宣布 PASS)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 99` 完成后：Cursor 收 `254` → 下发 `255-stage0-cursor-s27b-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.7-b-lite 落地刀（tasking 256+）— 10 城 mock 壳 + 路由 + 复用 S2.7-a 模板
- 若 FAIL：`254-correction` 回合（修 docs/46 + re-commit）

---

## §6. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b 最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **10 城名单已锁定** — Cursor 锁定清单 4 江苏 + 3 浙江 + 3 广东（per `253` §SCHEMA）；落地刀不得擅自换/加城市；如需调整须经 Cursor 重发 tasking + 改 `253` §SCHEMA 表。
- **路由采用 dynamic segment** — `/cities/[slug]` 顶层（per §3.2 选项 A）；不与省 slug 冲突（province 已用 `jiangsu/zhejiang/guangdong`）；AGENTS.md "Static-segment Next.js routes must NOT branch on params.*" 守门。
- **切刀：lite → full** — S2.7-b-lite（10 城 mock 壳）首落，tasking 256+；S2.7-b-full（接 mart）次落，tasking 25X+，依赖 O1 真实 SHA + Stage 1 OPEN 收口。
- **person/tenure 真数据接入契约（OPEN）** — 段级 evidence 6 段 city 适配；mart JOIN 通过 docs/44 §7.3 + docs/43 §4.1 守门。

— End of `254` —