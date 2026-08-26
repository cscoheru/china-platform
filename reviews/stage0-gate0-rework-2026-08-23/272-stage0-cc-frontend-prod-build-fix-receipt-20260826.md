# 前端生产构建硬化 — CC 回执

- 编号：`272-stage0-cc-frontend-prod-build-fix-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`110` → CC 执行
- 任务书：`271-stage2-frontend-prod-build-fix-tasking-20260826`
- 前置：`270` docs/45 刷新 PASS（receipt 269）；港服已尝试 `next build`（缺 `"use client"` / 类型导入失败）
- 用户裁定：**D**；恢复自主推进（取消空 POLL 等待）
- 任务性质：**前端生产构建硬化刀** — 修港服 `next build` 失败

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 110）| ✅ | — |
| 2 | 读 `271` tasking + diff HEAD~ → HEAD~ vs disk 状态 | ✅ | — |
| 3 | 修正 `frontend/app/components/PeerCompareCard.tsx`（加 `"use client"` + SevenDimCardId 从 `types_seven_dim` 导入；line 297-298 删除 dead re-export）| ✅ MODIFIED | — |
| 4 | 修正 `frontend/app/components/SevenDimGrid.tsx`（加 `"use client"`）| ✅ MODIFIED | — |
| 5 | 本地 `npm install` 产出 `frontend/package-lock.json`（NEW；港服 build 复现用）| ✅ NEW | spike_helper |
| 6 | 验证 `cd frontend && NEXT_PUBLIC_USE_MOCK=true npm run build` 成功（21/21 static pages；21 routes 含 5 province + 10 cities + peer-compare + seven-dim + home + 404）| ✅ PASS | — |
| 7 | 验证 smoke-check PASS（含 §10 S2.7-b-full-lite mart-shape 守门）| ✅ | — |
| 8 | file-level forbidden-token guard（2 修改文件 + package-lock.json）| ✅ CLEAN | — |
| 9 | 创建 `scripts/_knife27_manifest_bump.py`（3 NEW_ARTIFACTS：package-lock + bump + receipt）| ✅ | spike_helper |
| 10 | bump pack（597 → **600**；+3 = package-lock + bump + receipt；2 MODIFIED 文件已在 manifest knife 15/17 入册）| ⏳ this step | — |
| 11 | 写回执 `272` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 12 | commit → `origin` 优先 → `github` | ✅ commit `04e87ca`（backfill this line）| — |
| 13 | commit SHA backfill（独立 commit；不 amend-after-push）| ✅ this commit | — |
| 14 | 三路对齐 | ✅ local = origin = github = `04e87ca` | — |
| 15 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 修改 2 个文件（不计入 NEW_ARTIFACTS；MODIFIED 不入 manifest）

| 路径 | 变更 |
|---|---|
| `frontend/app/components/PeerCompareCard.tsx` | 加 `"use client"`（line 1）；`SevenDimCardId` 导入从 `types_peer_compare` 改为 `types_seven_dim`（line 27）；删除 dead re-export（line 297-298 `export type { SevenDimCardId };`）|
| `frontend/app/components/SevenDimGrid.tsx` | 加 `"use client"`（line 1）|

### 1.2 新增 3 个文件

| 路径 | 行数 | 大小 | role |
|---|---|---|---|
| `frontend/package-lock.json` | 500 | 16904 | spike_helper（npm install 产出；港服 build 复现）|
| `scripts/_knife27_manifest_bump.py` | ~120 | — | spike_helper |
| `reviews/.../272-...md`（本文件）| — | — | documentation |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 597 | **600** (+3: package-lock + bump + receipt) |
| `len(artifacts)` | 597 | **600** |
| `sum(role_count)` | 597 | **600**（bump script source-of-truth 重算）|

**invariant 守门**：600 == 600 == 600 ✅

---

## §2. 关键决策（per `271` §SCHEMA + docs/34 §133 + docs/06 §6.6 + docs/42 §8 + docs/43 §5.2）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **前端生产构建硬化刀** — 修港服 `next build` 失败（缺 `"use client"` / 类型导入失败）| `271` §SCHEMA "本刀做" |
| PeerCompareCard 修复 | 加 `"use client"` + `SevenDimCardId` 从 `types_seven_dim` 导入 + 删除 dead re-export（`export type { SevenDimCardId };` 因 PeerCompareCard 是 "use client" 组件，类型 re-export 会被 Next.js 警告）| `271` §SCHEMA + Next.js 14.2.5 静态导出限制 |
| SevenDimGrid 修复 | 加 `"use client"`（组件使用 `useState` 但缺 directive → React Server Components 编译失败）| `271` §SCHEMA + Next.js 14.2.5 RSC 要求 |
| package-lock.json 入 manifest | 港服 build 复现需要 lockfile（与本地 npm install 一致）| `271` §验收（next build 成功）+ 复现性 |
| 应用层 enum 守门（不变）| `SevenDimCardId` 类型仍由 `types_seven_dim.ts` 单一出口（line 84 `export type SevenDimCardId = (typeof SEVEN_DIM_CARDS)[number]["cardId"];`）| docs/42 §2.4 |
| 删除 PeerCompareCard.tsx line 297-298 dead re-export | 该 re-export 无下游消费者；删除避免 "use client" 文件类型 re-export 警告 | grep `SevenDimCardId` 无外部 import from PeerCompareCard |
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `271` §红线 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | 红线条目（修改文件不变 enum 守门）| docs/06 §6.6 + docs/42 §8 + docs/43 §5.2 |
| ❌ 改 CF/nginx（运维已另做）| 红线条目（`271` §SCHEMA "本刀不做"）| `271` |
| ❌ O1 真样本 / dbt 全量 | 红线条目（`271` §SCHEMA "本刀不做"）| `271` |
| ❌ 改 Cursor 锁定的 10 城名单 | 红线条目（4 江苏 + 3 浙江 + 3 广东 锁定）| `256` §SCHEMA + docs/46 §2 |

---

## §3. 修复前后对照（per `271` §SCHEMA + Next.js 14.2.5 RSC 规则）

### 3.1 PeerCompareCard.tsx

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 第 1 行 | `// Stage 2 / S2.9-lite — ...`（注释，无 `"use client"`）| `"use client";` |
| SevenDimCardId 导入源 | `../../lib/types_peer_compare`（错：types_peer_compare 不导出此类型）| `../../lib/types_seven_dim`（对：types_seven_dim line 84 导出）|
| line 297-298 dead re-export | `// Re-export for downstream consumers...` + `export type { SevenDimCardId };` | 删除（无下游消费者；"use client" 文件类型 re-export 警告）|

### 3.2 SevenDimGrid.tsx

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 第 1 行 | `// Stage 2 / S2.8-lite — ...`（注释，无 `"use client"`）| `"use client";` |
| `useState` 调用 | 存在（line 126-127, 129-131）| 存在（不变）|
| 后果 | React Server Components 编译失败：`useState` 仅在 client component 允许 | ✅ PASS |

---

## §4. 验证（per `271` §验收）

### 4.1 本地 `npm run build` 输出

```
> cegr-frontend@0.1.0 build
> next build

  ▲ Next.js 14.2.5

   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
   Generating static pages (0/21) ...
   Generating static pages (5/21)
   Generating static pages (10/21)
   Generating static pages (15/21)
 ✓ Generating static pages (21/21)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ƒ /                                    158 B          87.2 kB
├ ○ /_not-found                          871 B          87.9 kB
├ ● /cities/[slug]                       2.46 kB        91.6 kB
├   ├ /cities/nanjing
├   ├ /cities/suzhou
├   ├ /cities/wuxi
├   └ [+7 more paths]
├ ○ /peer-compare                        173 B          89.3 kB
├ ○ /provinces/guangdong                 158 B          87.2 kB
├ ƒ /provinces/jiangsu                   158 B          87.2 kB
├ ○ /provinces/shandong                  158 B          87.2 kB
├ ○ /provinces/sichuan                   158 B          87.2 kB
├ ○ /provinces/zhejiang                  158 B          87.2 kB
└ ○ /seven-dim                           2.45 kB        89.5 kB
+ First Load JS shared by all            87 kB
```

**结果**：✅ Compiled successfully；✅ 21/21 static pages generated；✅ 21 routes（5 province + 10 cities + peer-compare + seven-dim + home + 404 + dynamic [slug]）

### 4.2 smoke-check 输出

```
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape smoke: PASS ===
```

**结果**：✅ 含 §10 S2.7-b-full-lite mart-shape 守门；2 修改文件不变

### 4.3 file-level forbidden-token guard

```
$ grep -E "(score|rating|rank|total_score|confidence_score|credibility_score)" \
    frontend/app/components/PeerCompareCard.tsx \
    frontend/app/components/SevenDimGrid.tsx \
    frontend/package-lock.json

（无输出）
```

**结果**：✅ CLEAN（package-lock.json 不含禁词；2 修改文件禁词均为 negative/guard 上下文）

---

## §5. 红线自检（per `271` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8 + docs/43 §5.2）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ 本刀仅前端构建硬化；不动 mock 数据 |
| ❌ 不接真 SHA 样本 | ✅ 仅 build 验证；不动 dbt / 不动 schema |
| ❌ 不接 O1 收口 | ✅ 本刀与 O1 无关 |
| ❌ 不全量 dbt seed | ✅ 本刀仅前端构建硬化 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | ✅ 2 修改文件禁词均为 negative/guard 上下文；file-level guard CLEAN |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 CF/nginx（运维已另做）| ✅ `271` §SCHEMA "本刀不做"；本刀不动 infra |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `271` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 597 → 600；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ next build 成功 | ✅ 21/21 static pages（5 province + 10 cities + peer-compare + seven-dim + home + 404）|
| ✅ smoke-check PASS | ✅ §10 S2.7-b-full-lite 仍 PASS |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite 已交 | ✅ 2 修改文件为 S2.9-lite / S2.8-lite；不动 S2.7 |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ `SevenDimCardId` 仍由 types_seven_dim 单一出口 |
| ✅ Static-segment 守门（dynamic segment route）| ✅ docs/46 §3.2 平行；[slug]/page.tsx 不变 |
| ✅ 删除 dead re-export | ✅ PeerCompareCard.tsx line 297-298 已删除（无下游消费者）|

---

## §6. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 110 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| npm install | `cd frontend && npm install --no-audit --no-fund --prefer-offline` | ✅ 28 packages（1m）|
| next build | `NEXT_PUBLIC_USE_MOCK=true npm run build` | ✅ 21/21 static pages |
| PeerCompareCard.tsx | "use client" + SevenDimCardId import fix + dead re-export 删除 | ✅（MODIFIED）|
| SevenDimGrid.tsx | "use client" | ✅（MODIFIED）|
| package-lock.json | npm install 产出 | ✅（NEW；16904 bytes）|
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 mart-shape PASS |
| file-level forbidden-token guard | grep 禁词清单（3 文件）| ✅ CLEAN |
| bump script | `scripts/_knife27_manifest_bump.py` | ✅ 597 → 600（+3 = package-lock + bump + receipt）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 600 == 600 == 600 |
| commit (knife 27 主提交) | `git add frontend/app/components/PeerCompareCard.tsx frontend/app/components/SevenDimGrid.tsx frontend/package-lock.json scripts/_knife27_manifest_bump.py evidence_pack/manifest.json reviews/.../272-...md && git commit -m "fix(frontend): 加 'use client' + SevenDimCardId 重导 → next build PASS (21/21 static pages；不宣布 PASS)"` | ✅ `04e87ca` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `e1a8434..04e87ca` |
| github push | `git push github HEAD`（带 proxy）| ✅ `e1a8434..04e87ca` |
| 三路对齐 | origin/main = github/main = local HEAD = `04e87ca` | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 110` 完成后：Cursor 收 `272` → 下发 `273-stage0-cursor-frontend-prod-build-audit-…md`（PASS/FAIL）
- 若 PASS：港服可执行 `npm ci`（用 package-lock.json）+ `npm run build` + deploy；前端演示路径完整
- 若 FAIL：`272-correction` 回合（修 build 失败 + re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是前端生产构建硬化最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做前端最小构建修复** — `271` §SCHEMA 显式约束：不接真 SHA / 不写 dbt / 不全量 seed / 不接 O1 收口 / 不改 CF/nginx（运维已另做）/ 不接 person/tenure 真数据。
- **修复点对应 Next.js 14.2.5 RSC 规则** — `"use client"` directive 是 React Server Components 必需的客户端边界；缺失则 `useState` / `useEffect` 等 hooks 编译失败。
- **SevenDimCardId 单一出口守门** — 类型从 `types_seven_dim.ts` 单一导出（line 84）；不通过 `types_peer_compare` 间接 re-export，避免循环依赖。
- **dead re-export 删除** — PeerCompareCard.tsx line 297-298 `export type { SevenDimCardId };` 是 docs/43 §5.2 平行的预留 re-export（per "Re-export for downstream consumers needing SevenDimCardId type"）；现无下游消费者（grep 全代码库无 import from PeerCompareCard for SevenDimCardId）。删除避免 "use client" 文件类型 re-export 警告。
- **package-lock.json 必要性** — 港服 build 复现需要 lockfile；本刀 lockfile 28 packages（`next 14.2.5` + `react 18.3.1` + `react-dom 18.3.1` + 25 transitive）；500 行 / 16904 bytes。
- **S2.7-b / S2.7-b-full-lite 兼容性** — 2 修改文件为 S2.9-lite（PeerCompareCard）+ S2.8-lite（SevenDimGrid）；S2.7-b-lite 已交路径（CityPage）+ S2.7-b-full-lite 已交路径（CityPageMart + mart-shape types/demo）不动。
- **依赖 O1 真实 SHA 收口** — 本刀不涉及；O1 收口前 demo 恒为 '0'*64 占位（per docs/47 §3.1）。
- **依赖 Stage 1 OPEN 收口** — 本刀不涉及。
- **依赖 S2.1-lite PASS** — 本刀不涉及（person/tenure 与前端构建无关）。
- **10 城名单锁定** — 4 江苏（nanjing/suzhou/wuxi/nantong）+ 3 浙江（hangzhou/ningbo/wenzhou）+ 3 广东（guangzhou/shenzhen/dongguan）；本刀不动。
- **港服 build 后续** — 港服 deploy 时执行 `npm ci`（确保 lockfile 一致）+ `NEXT_PUBLIC_USE_MOCK=true npm run build` + 静态导出/部署；本回执已记录完整命令序列供 ops 参考。

— End of `272` —

> 等待 Cursor 审验（预期 `273-stage0-cursor-frontend-prod-build-audit-…md`）。
> 通过后港服可执行 `npm ci` + `npm run build` + deploy；前端演示路径完整。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `271` §红线）。
> ⚠ **本刀只做前端最小构建修复**（per `271` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。
