# 首页十城导航入口 — CC 回执

- 编号：`275-stage0-cc-home-cities-nav-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`112` → CC 执行
- 任务书：`274-stage2-home-cities-nav-tasking-20260826`
- 前置：`273` 前端 build 硬化 PASS（receipt 272）；预览 `china.3strategy.cc`
- 用户裁定：**D**；自主推进；O1 无材料保持 OPEN
- 任务性质：**首页十城导航入口刀** — 首页加 10 地市导航表（对齐 CITY_SLUG_LIST / docs/46）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 112）| ✅ | — |
| 2 | 读 `274` tasking + `frontend/app/page.tsx` 现状 + `frontend/lib/city_slug_map.ts` | ✅ | — |
| 3 | 修改 `frontend/app/page.tsx`：加 `CITY_SLUG_MAP / CITY_SLUG_LIST` 导入 + 新增"地市观察入口"section（10 行 × 4 列：地市/省份/路由/数据模式）| ✅ MODIFIED | — |
| 4 | 验证 `cd frontend && NEXT_PUBLIC_USE_MOCK=true npm run build` 仍 PASS（21/21 static pages）| ✅ PASS | — |
| 5 | 验证 smoke-check 仍 PASS（含 §10 S2.7-b-full-lite mart-shape 守门）| ✅ | — |
| 6 | file-level forbidden-token guard（page.tsx）：0 hit（仅"导航入口；不做评分"提示，无 score/rating/rank 任何禁词）| ✅ CLEAN | — |
| 7 | 创建 `scripts/_knife28_manifest_bump.py`（2 NEW_ARTIFACTS：bump + receipt）| ✅ | spike_helper |
| 8 | bump pack（600 → **602**；+2 = bump + receipt；page.tsx 已在 manifest knife 13 入册）| ⏳ this step | — |
| 9 | 写回执 `275` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 10 | commit → `origin` 优先 → `github` | ✅ commit `7751bb4`（backfill this line）| — |
| 11 | commit SHA backfill（独立 commit；不 amend-after-push）| ✅ this commit | — |
| 12 | 三路对齐 | ✅ local = origin = github = `7751bb4` | — |
| 13 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 修改 1 个文件（不计入 NEW_ARTIFACTS；MODIFIED 不入 manifest）

| 路径 | 变更 |
|---|---|
| `frontend/app/page.tsx` | Header comment 加 S2.7-b 增量说明；新增 `CITY_SLUG_MAP / CITY_SLUG_LIST` 导入；新增 `<h2>地市观察入口</h2>` section（10 行 × 4 列：地市/省份/路由/数据模式）；保留底部"导航入口；不评分/不对比/不排名"提示 |

### 1.2 新增 2 个文件

| 路径 | 行数 | 大小 | role |
|---|---|---|---|
| `scripts/_knife28_manifest_bump.py` | ~110 | — | spike_helper |
| `reviews/.../275-...md`（本文件）| — | — | documentation |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 600 | **602** (+2: bump + receipt) |
| `len(artifacts)` | 600 | **602** |
| `sum(role_count)` | 600 | **602**（bump script source-of-truth 重算）|

**invariant 守门**：602 == 602 == 602 ✅

---

## §2. 关键决策（per `274` §SCHEMA + docs/46 §2 + `256` §SCHEMA）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **首页十城导航入口刀** — 首页加 10 地市导航表；不改数据、不改评分/排名 | `274` §SCHEMA "本刀做" |
| 数据源 | `CITY_SLUG_MAP / CITY_SLUG_LIST` 从 `frontend/lib/city_slug_map.ts` 导入（10 城锁定清单 + 应用层 enum 守门）| docs/46 §2 + `256` §SCHEMA |
| 列表结构 | 10 行 × 4 列：地市 / 归属省份 / 路由（`/cities/{slug}`）/ 数据模式（mock；S2.7-b-lite / mart-shape opt-in）| 镜像 S2.7-a 省级入口表结构（tasking 168 §NOW-2 平行）|
| 不动数据 | 不接真 SHA、不接 person/tenure 真数据、不接 mart 真表 — 纯导航入口 | `274` §SCHEMA "本刀不做" |
| 禁词守门 | 不派生 score/rating/rank；底部"导航入口；不评分/不对比/不排名"提示保留（与 S2.7-a 表底一致）| docs/06 §6.6 + `274` §红线 |
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `274` §红线 |
| ❌ 改 Cursor 锁定的 10 城名单 | 红线条目（经 `CITY_SLUG_LIST` 迭代；不擅自换/加）| `256` §SCHEMA + docs/46 §2 |
| ❌ 真数据 / 评分 / 排名 / DSH / 爬网 / CF/nginx | 红线条目（`274` §SCHEMA "本刀不做/禁止"）| `274` §红线 |
| ❌ 改 `gate_thresholds.json` | 红线条目（未读未写）| `274` §红线 |

---

## §3. 改动对照（per `274` §NOW "1"）

### 3.1 frontend/app/page.tsx

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| Header comment | `// Stage 2 / S2.0.1 + S2.7-a — Home page.` + 5 省入口说明 | `// Stage 2 / S2.0.1 + S2.7-a + S2.7-b — Home page.` + 5 省 + 10 地市入口说明 |
| imports | `listIndicators, IS_MOCK_MODE` + `MOCK_PROVINCE_LIST` | + `CITY_SLUG_MAP, CITY_SLUG_LIST` 从 `../lib/city_slug_map` |
| section "省级观察入口" | ✅ 5 行表（5 省）| ✅ 保留 |
| section "地市观察入口" | ❌ 不存在 | ✅ 新增（10 行 × 4 列：地市/归属省份/路由/数据模式）|
| 数据模式列文案 | — | `mock（S2.7-b-lite / mart-shape opt-in）`（标明 S2.7-b-lite 已交 + S2.7-b-full-lite mart-shape opt-in）|
| 底部"导航入口；不评分/不对比/不排名"提示 | ✅ 存在 | ✅ 保留 |

---

## §4. 验证（per `274` §NOW "2"）

### 4.1 本地 `next build` 输出

```
Route (app)                              Size     First Load JS
┌ ƒ /                                    158 B          87.2 kB   ← 158B (158B；首屏仅 87.2kB；与 knife 27 一致)
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
```

**结果**：✅ Compiled successfully；✅ 21/21 static pages（与 knife 27 一致 — 首页增量 < 1kB，Home / 路由仍 158B）

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

**结果**：✅ CLEAN — 0 hit（底部提示"不评分/不对比/不排名"是无禁词的 negative/guard 措辞）

### 4.4 手动预览路径（港服 ops 参考）

| 入口 | URL | 渲染 |
|---|---|---|
| 首页 | `/` | 5 省列表 + 10 地市列表（江苏 4 + 浙江 3 + 广东 3，按 `CITY_SLUG_LIST` 顺序） |
| 地市详情（默认 mock）| `/cities/{slug}` | `CityPage`（mock；S2.7-b-lite；receipt 257） |
| 地市详情（mart-shape opt-in）| `/cities/{slug}` + `NEXT_PUBLIC_USE_MART_FIXTURE=1` | `CityPageMart`（S2.7-b-full-lite；receipt 266） |

---

## §5. 红线自检（per `274` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/46 §1.2）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ 经 `CITY_SLUG_LIST` 迭代（4 江苏 + 3 浙江 + 3 广东）；smoke-check §10b 守门 |
| ❌ 不接真 SHA 样本 | ✅ 仅导航入口；不动 dbt / 不动 schema |
| ❌ 不接 O1 收口 | ✅ 本刀与 O1 无关 |
| ❌ 不全量 dbt seed | ✅ 本刀仅前端导航入口 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | ✅ file-level guard CLEAN（0 hit）；底部"不评分/不对比/不排名"提示保留 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 CF/nginx（运维已另做）| ✅ `274` §SCHEMA "本刀不做"；本刀不动 infra |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `274` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 600 → 602；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ next build 仍 PASS | ✅ 21/21 static pages（首页仍 158B / 87.2kB First Load JS）|
| ✅ smoke-check PASS | ✅ §10 S2.7-b-full-lite 仍 PASS |
| ✅ 兼容 S2.7-a / S2.7-b-lite / S2.7-b-full-lite 已交 | ✅ 不动 mock 数据；不动 mart-shape 接驳 |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ `CITY_SLUG_MAP / CITY_SLUG_LIST` 应用层 enum-style 守门（isValidCitySlug）|
| ✅ Static-segment 守门（dynamic segment route）| ✅ docs/46 §3.2 平行；不动 [slug]/page.tsx |

---

## §6. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 112 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| page.tsx 修改 | "地市观察入口" section（10 行 × 4 列）| ✅（MODIFIED）|
| next build | `cd frontend && NEXT_PUBLIC_USE_MOCK=true npm run build` | ✅ 21/21 static pages（与 knife 27 一致）|
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 mart-shape PASS |
| file-level forbidden-token guard | grep 禁词清单 | ✅ CLEAN（0 hit）|
| bump script | `scripts/_knife28_manifest_bump.py` | ✅ 600 → 602（+2 = bump + receipt）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 602 == 602 == 602 |
| commit (knife 28 主提交) | `git add frontend/app/page.tsx scripts/_knife28_manifest_bump.py evidence_pack/manifest.json reviews/.../275-...md && git commit -m "feat(home): 加 10 地市导航入口（对齐 CITY_SLUG_LIST / docs/46；不评分/不对比/不排名）"` | ✅ `7751bb4` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `eb10972..7751bb4` |
| github push | `git push github HEAD`（带 proxy）| ✅ `eb10972..7751bb4` |
| 三路对齐 | origin/main = github/main = local HEAD = `7751bb4` | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 112` 完成后：Cursor 收 `275` → 下发 `276-stage0-cursor-home-cities-nav-audit-…md`（PASS/FAIL）
- 若 PASS：港服可执行 `npm ci` + `npm run build` + deploy；首页含完整 5 省 + 10 地市入口
- 若 FAIL：`275-correction` 回合（修导航入口 + re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是首页十城导航入口最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做首页最小导航入口** — `274` §SCHEMA 显式约束：不接真数据 / 不改评分/排名 / 不改 CF/nginx（运维已另做）/ 不爬网。
- **10 城名单锁定** — 4 江苏（nanjing/suzhou/wuxi/nantong）+ 3 浙江（hangzhou/ningbo/wenzhou）+ 3 广东（guangzhou/shenzhen/dongguan）；本刀经 `CITY_SLUG_LIST` 迭代，落地刀不得擅自换/加（per `256` §SCHEMA + docs/46 §2）。
- **应用层 enum 守门** — `CITY_SLUG_MAP / CITY_SLUG_LIST / isValidCitySlug` 是 `frontend/lib/city_slug_map.ts` 已交的应用层 enum-style 守门（per docs/46 §3.1）；本刀不引入新 schema ENUM。
- **首页体积** — 增量 < 1kB（仅新表格 10 行 × 4 列）；首页 / 路由仍 158B / 87.2kB First Load JS（与 knife 27 一致）；build 时间无明显变化。
- **港服 preview 链接** — `china.3strategy.cc`（per `273` 验收）；本刀部署后首页"地市观察入口"section 可点击直达 10 个 `/cities/{slug}` 路由（默认 mock；mart-shape opt-in via `NEXT_PUBLIC_USE_MART_FIXTURE=1`）。
- **依赖 O1 真实 SHA 收口** — 本刀不涉及；O1 收口前 demo 恒为 '0'*64 占位（per docs/47 §3.1）。
- **依赖 Stage 1 OPEN 收口** — 本刀不涉及。
- **依赖 S2.1-lite PASS** — 本刀不涉及（person/tenure 与首页导航无关）。
- **5 省 + 10 地市入口对称** — S2.7-a 省级入口（5 行）+ S2.7-b 地市入口（10 行）现已在同一首页；为 Gate 2 评审包入口演示完整（per docs/44 §5 + docs/45 §5.5）。
- **S2.7-b-full 真数据迁移刀仍 OPEN** — dbt mart 真表 + person/tenure 真数据 + lineage.source_file_sha256 从占位 `'0'*64` 替换为 O1 真实 SHA（per docs/47 §6.3 切刀风险 + docs/45 §5.5 OPEN）；本刀不涉及。

— End of `275` —

> 等待 Cursor 审验（预期 `276-stage0-cursor-home-cities-nav-audit-…md`）。
> 通过后港服可执行 `npm ci` + `npm run build` + deploy；首页含完整 5 省 + 10 地市入口。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `274` §红线）。
> ⚠ **本刀只做首页最小导航入口**（per `274` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。
