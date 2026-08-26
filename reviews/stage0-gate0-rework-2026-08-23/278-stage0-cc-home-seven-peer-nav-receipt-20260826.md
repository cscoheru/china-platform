# 首页七维/对比导航入口 — CC 回执

- 编号：`278-stage0-cc-home-seven-peer-nav-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`114` → CC 执行
- 任务书：`277-stage2-home-seven-peer-nav-tasking-20260826`
- 前置：`276` 首页十城导航 PASS（receipt 275）
- 用户裁定：**D**；自主推进
- 任务性质：**首页七维/对比导航入口刀** — 首页加 `/seven-dim` + `/peer-compare` 入口区

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 114）| ✅ | — |
| 2 | 读 `277` tasking + `frontend/app/page.tsx` 现状（已含 5 省 + 10 地市入口）| ✅ | — |
| 3 | 修改 `frontend/app/page.tsx`：header comment +1 行；新增"横向视角入口"section（2 行 × 4 列：入口/路由/演示范围/数据模式）；底部"不评分/不排名/不派生地区得分"提示 | ✅ MODIFIED | — |
| 4 | 验证 `cd frontend && NEXT_PUBLIC_USE_MOCK=true npm run build` 仍 PASS（21/21 static pages）| ✅ PASS | — |
| 5 | 验证 smoke-check 仍 PASS（含 §10 S2.7-b-full-lite mart-shape 守门）| ✅ | — |
| 6 | file-level forbidden-token guard（page.tsx）：0 hit（禁词上下文均为 negative/guard 措辞）| ✅ CLEAN | — |
| 7 | 创建 `scripts/_knife29_manifest_bump.py`（2 NEW_ARTIFACTS：bump + receipt）| ✅ | spike_helper |
| 8 | bump pack（602 → **604**；+2 = bump + receipt；page.tsx 已在 manifest knife 13/22/28 入册）| ⏳ this step | — |
| 9 | 写回执 `278` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 10 | commit → `origin` 优先 → `github` | ✅ commit `f17413b`（backfill this line）| — |
| 11 | commit SHA backfill（独立 commit；不 amend-after-push）| ✅ this commit | — |
| 12 | 三路对齐 | ✅ local = origin = github = `f17413b` | — |
| 13 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 修改 1 个文件（不计入 NEW_ARTIFACTS；MODIFIED 不入 manifest）

| 路径 | 变更 |
|---|---|
| `frontend/app/page.tsx` | Header comment 加 S2.8-lite / S2.9-lite 增量说明；新增"横向视角入口"section（2 行 × 4 列：入口/路由/演示范围/数据模式 — `/seven-dim` 7 维度 + `/peer-compare` 同类对比）；底部"仅展示计数；不评分/不排名/不派生地区得分"提示（per docs/06 §6.6 + docs/42 §8 + docs/43 §8）|

### 1.2 新增 2 个文件

| 路径 | 行数 | 大小 | role |
|---|---|---|---|
| `scripts/_knife29_manifest_bump.py` | ~110 | — | spike_helper |
| `reviews/.../278-...md`（本文件）| — | — | documentation |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 602 | **604** (+2: bump + receipt) |
| `len(artifacts)` | 602 | **604** |
| `sum(role_count)` | 602 | **604**（bump script source-of-truth 重算）|

**invariant 守门**：604 == 604 == 604 ✅

---

## §2. 关键决策（per `277` §SCHEMA + docs/42 §3.1 + docs/43 §3.5 + docs/06 §6.6）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **首页七维/对比导航入口刀** — 首页加 2 个横向视角入口；不改数据、不改评分/排名 | `277` §SCHEMA "本刀做" |
| 入口 1：七维度观察卡 | `/seven-dim`（已交付 S2.8-lite；mock；1 区域 × 7 cell）| docs/42 §3.1 + 7 维度枚举 (POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY) |
| 入口 2：同类地区对比 | `/peer-compare`（已交付 S2.9-lite；mock；1 group × 4 members；focal 江苏 + peer 浙江/广东/山东；4 维度匹配依据）| docs/43 §3.5 + 8 枚举 (POPULATION_TIER / LOCATION_TYPE / INDUSTRY_BASE / DEVELOPMENT_STAGE / ROLE_IN_GROUP / SELECTION_METHOD) |
| 列表结构 | 2 行 × 4 列：入口 / 路由 / 演示范围 / 数据模式 | 镜像 S2.7-a / S2.7-b 入口表结构 |
| 文案守门 | 底部"仅展示计数；不评分、不排名、不派生地区得分（per docs/06 §6.6 + docs/42 §8 + docs/43 §8）" | `277` §NOW "1"（mock / 不评分）|
| 不动数据 | 不接真 SHA、不接 person/tenure 真数据、不接 mart 真表 — 纯导航入口 | `277` §SCHEMA "本刀不做" |
| 禁词守门 | 不派生 score/rating/rank；底部"不评分/不排名/不派生地区得分"提示保留 | docs/06 §6.6 + `277` §红线 |
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `277` §红线 |
| ❌ 改 CF/nginx（运维已另做）| 红线条目（`277` §SCHEMA "本刀不做"）| `277` |
| ❌ 真数据 / 评分 / 排名 / DSH / 爬网 | 红线条目（`277` §SCHEMA "本刀不做/禁止"）| `277` §红线 |
| ❌ 改 `gate_thresholds.json` | 红线条目（未读未写）| `277` §红线 |

---

## §3. 改动对照（per `277` §NOW "1"）

### 3.1 frontend/app/page.tsx

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| Header comment | `// Stage 2 / S2.0.1 + S2.7-a + S2.7-b — Home page.` + 5 省 + 10 地市入口说明 | `// Stage 2 / S2.0.1 + S2.7-a + S2.7-b + S2.8-lite + S2.9-lite — Home page.` + 5 省 + 10 地市 + 七维 + 对比入口说明 |
| section "省级观察入口" | ✅ 5 行表（5 省）| ✅ 保留 |
| section "地市观察入口" | ✅ 10 行表（10 地市）| ✅ 保留 |
| section "横向视角入口" | ❌ 不存在 | ✅ 新增（2 行 × 4 列：七维度观察卡 + 同类地区对比）|
| 演示范围列文案 | — | 七维度：1 区域 × 7 cell（POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY）；同类对比：1 group × 4 members（focal 江苏 + peer 浙江/广东/山东；4 维度匹配依据）|
| 数据模式列文案 | — | mock（S2.8-lite）/ mock（S2.9-lite）|
| 底部"导航入口；不评分/不对比/不排名"提示 | ✅ 存在 | ✅ 保留 |
| 底部"仅展示计数；不评分/不排名/不派生地区得分"提示 | ❌ 不存在 | ✅ 新增（per docs/06 §6.6 + docs/42 §8 + docs/43 §8）|

---

## §4. 验证（per `277` §NOW "2"）

### 4.1 本地 `next build` 输出

```
Route (app)                              Size     First Load JS
┌ ƒ /                                    158 B          87.2 kB   ← 158B（与 knife 27/28 一致；增量 < 1kB）
├ ○ /_not-found                          871 B          87.9 kB
├ ● /cities/[slug]                       2.46 kB        91.6 kB
├   ├ /cities/nanjing
├   ├ /cities/suzhou
├   ├ /cities/wuxi
├   └ [+7 more paths]
├ ○ /peer-compare                        173 B          89.3 kB   ← 入口路径
├ ○ /provinces/guangdong                 158 B          87.2 kB
├ ƒ /provinces/jiangsu                   158 B          87.2 kB
├ ○ /provinces/shandong                  158 B          87.2 kB
├ ○ /provinces/sichuan                   158 B          87.2 kB
├ ○ /provinces/zhejiang                  158 B          87.2 kB
└ ○ /seven-dim                           2.45 kB        89.5 kB   ← 入口路径
```

**结果**：✅ Compiled successfully；✅ 21/21 static pages（与 knife 27/28 一致 — 首页增量 < 1kB）

### 4.2 smoke-check 输出

```
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape smoke: PASS ===
```

**结果**：✅ §10 S2.7-b-full-lite mart-shape 守门 PASS；无回归

### 4.3 file-level forbidden-token guard

```
$ grep -n -E "(?i)\b(score|rating|rank|total_score|confidence_score|credibility_score|peer_rank)\b" \
    frontend/app/page.tsx

（无输出）
```

**结果**：✅ CLEAN — 0 hit（底部"不评分/不排名/不派生地区得分"是无禁词的 negative/guard 措辞）

### 4.4 手动预览路径（港服 ops 参考）

| 入口 | URL | 渲染 |
|---|---|---|
| 首页 | `/` | 5 省列表 + 10 地市列表 + 横向视角入口（/seven-dim + /peer-compare）|
| 七维度观察卡 | `/seven-dim` | `SevenDimGrid` 演示（1 区域 × 7 cell；mock；S2.8-lite；receipt 239）|
| 同类地区对比 | `/peer-compare` | `PeerCompareGrid` 演示（1 group × 4 members；mock；S2.9-lite；receipt 245）|

---

## §5. 红线自检（per `277` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8 + docs/43 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ 经 `CITY_SLUG_LIST` 迭代；本刀不动 10 城入口 |
| ❌ 不接真 SHA 样本 | ✅ 仅导航入口；不动 dbt / 不动 schema |
| ❌ 不接 O1 收口 | ✅ 本刀与 O1 无关 |
| ❌ 不全量 dbt seed | ✅ 本刀仅前端导航入口 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | ✅ file-level guard CLEAN（0 hit）；底部"不评分/不排名/不派生地区得分"提示保留 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 CF/nginx（运维已另做）| ✅ `277` §SCHEMA "本刀不做"；本刀不动 infra |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `277` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 602 → 604；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ next build 仍 PASS | ✅ 21/21 static pages（首页仍 158B / 87.2kB First Load JS）|
| ✅ smoke-check PASS | ✅ §10 S2.7-b-full-lite 仍 PASS |
| ✅ 兼容 S2.7-a / S2.7-b / S2.8-lite / S2.9-lite 已交 | ✅ 不动 mock 数据；不动接驳 |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ 7 维度 + 8 enum 由 types_seven_dim / types_peer_compare 单一出口 |
| ✅ Static-segment 守门（dynamic segment route）| ✅ docs/46 §3.2 平行；不动 [slug]/page.tsx |

---

## §6. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 114 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| page.tsx 修改 | "横向视角入口" section（2 行 × 4 列）| ✅（MODIFIED）|
| next build | `cd frontend && NEXT_PUBLIC_USE_MOCK=true npm run build` | ✅ 21/21 static pages（与 knife 27/28 一致）|
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 mart-shape PASS |
| file-level forbidden-token guard | grep 禁词清单 | ✅ CLEAN（0 hit）|
| bump script | `scripts/_knife29_manifest_bump.py` | ✅ 602 → 604（+2 = bump + receipt）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 604 == 604 == 604 |
| commit (knife 29 主提交) | `git add frontend/app/page.tsx scripts/_knife29_manifest_bump.py evidence_pack/manifest.json reviews/.../278-...md && git commit -m "feat(home): 加 /seven-dim + /peer-compare 横向视角入口（mock；不评分/不排名/不派生地区得分）"` | ✅ `f17413b` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `61044e7..f17413b` |
| github push | `git push github HEAD`（带 proxy）| ✅ `61044e7..f17413b` |
| 三路对齐 | origin/main = github/main = local HEAD = `f17413b` | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 114` 完成后：Cursor 收 `278` → 下发 `279-stage0-cursor-home-seven-peer-nav-audit-…md`（PASS/FAIL）
- 若 PASS：港服可执行 `npm ci` + `npm run build` + deploy；首页含完整 5 省 + 10 地市 + 七维 + 对比入口
- 若 FAIL：`278-correction` 回合（修导航入口 + re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是首页七维/对比导航入口最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做首页最小导航入口** — `277` §SCHEMA 显式约束：不接真数据 / 不改评分/排名 / 不改 CF/nginx（运维已另做）/ 不爬网。
- **首页完整结构（knife 28 + 29 合并）** —
  1. Indicator inventory（S2.0.1；mock by default）
  2. 省级观察入口（S2.7-a；5 行）
  3. 地市观察入口（S2.7-b-lite / S2.7-b-full-lite；10 行 × 4 列）
  4. 横向视角入口（S2.8-lite 七维度 + S2.9-lite 同类对比；2 行 × 4 列）
- **文案守门一致性** — 4 个 section 各自底部都有"导航入口；不评分/不对比/不排名"或"仅展示计数；不评分/不排名/不派生地区得分"提示（per docs/06 §6.6 + docs/42 §8 + docs/43 §8）。
- **应用层 enum 守门** — 7 维度（`SevenDimCardId`）+ 8 枚举（`POPULATION_TIER / LOCATION_TYPE / INDUSTRY_BASE / DEVELOPMENT_STAGE / ROLE_IN_GROUP / SELECTION_METHOD`）由 `types_seven_dim.ts` / `types_peer_compare.ts` 单一出口 + `isValid*` 守门函数；本刀不引入新 schema ENUM。
- **依赖 O1 真实 SHA 收口** — 本刀不涉及；O1 收口前 demo 恒为 '0'*64 占位（per docs/47 §3.1）。
- **依赖 Stage 1 OPEN 收口** — 本刀不涉及。
- **依赖 S2.1-lite PASS** — 本刀不涉及（person/tenure 与首页导航无关）。
- **5 省 + 10 地市 + 横向入口完整** — 现首页 4 个 section 完整覆盖 Gate 2 评审演示入口（per docs/44 §5 + docs/45 §5.5 验证清单：5 省 + 10 地市 + 七维度 + 同类对比）。
- **S2.7-b-full 真数据迁移刀仍 OPEN** — dbt mart 真表 + person/tenure 真数据 + lineage.source_file_sha256 从占位 `'0'*64` 替换为 O1 真实 SHA（per docs/47 §6.3 切刀风险 + docs/45 §5.5 OPEN）；本刀不涉及。

— End of `278` —

> 等待 Cursor 审验（预期 `279-stage0-cursor-home-seven-peer-nav-audit-…md`）。
> 通过后港服可执行 `npm ci` + `npm run build` + deploy；首页含完整 5 省 + 10 地市 + 七维 + 对比入口。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `277` §红线）。
> ⚠ **本刀只做首页最小导航入口**（per `277` §SCHEMA "本刀做/本刀不做"）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。
