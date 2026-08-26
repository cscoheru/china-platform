# S2.7-b-lite 10 地市观察页 mock 壳 — CC 回执

- 编号：`257-stage0-cc-s27b-lite-cities-impl-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`101` → CC 执行
- 任务书：`256-stage2-s27b-lite-cities-impl-tasking-20260826`
- 前置：`254` S2.7-b 规划 PASS；`docs/46` §3-§4；`docs/34` §1/§4/§8 #8/§133/§10.4；`255` PASS
- 用户裁定：Stage 2 **C**；缩刀 **D**；自主推进

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 101）| ✅ | — | — |
| 2 | 读 `254` PASS + `256` tasking + `docs/46 §3-§4` + `docs/34 §1/§4` | ✅ | — | — |
| 3 | 起草 `frontend/lib/city_slug_map.ts`（10 slug 锁定 + 应用层守门）| ✅ | `3ad77c2b` | spike_helper |
| 4 | 起草 `frontend/lib/types_cities.ts`（CityProps + 8 enum 守门）| ✅ | `09d069d8` | spike_helper |
| 5 | 起草 `frontend/lib/mock_cities.ts`（10 城 × 6 段 + 7 cell + 同省横向）| ✅ | `b3d0153a` | spike_helper |
| 6 | 起草 `frontend/app/components/CityPage.tsx`（复用三件套）| ✅ | `308fd084` | spike_helper |
| 7 | 起草 `frontend/app/cities/[slug]/page.tsx`（dynamic segment + generateStaticParams）| ✅ | `3b350431` | spike_helper |
| 8 | 起草 `tests/test_city_slug_map_s27b.py`（6 case PASS）| ✅ | `8dce8f1a` | schema_negative_test |
| 9 | 扩展 `frontend/smoke-check.py`（加 S2.7-b-lite 9 节守门）| ✅ | `7c7518f4` | spike_helper |
| 10 | 跑通新 pytest（**6 PASS**）| ✅ | — | — |
| 11 | 跨 lite 回归（s21lite..s26lite + s210 + s27b = **60 PASS + 6 SKIP**）| ✅ | — | — |
| 12 | smoke-check 仍 PASS（**52/52 ✅** 含 9 节 S2.7-b-lite 守门）| ✅ | — | — |
| 13 | 文件级 forbidden-token guard（mock_cities.ts 5 禁词全部 CLEAN）| ✅ | — | — |
| 14 | 补 pack（579 → **586**；+7 含 5 frontend + 1 pytest + smoke-check）| ✅ | — | documentation |
| 15 | 写回执 `257` 入 `reviews/` | ✅（本文件）| — | documentation |
| 16 | commit → `origin` 优先 → `github` | ✅ `c8ee2b9` | — | — |
| 17 | 三路对齐 | ✅ local = origin = github = `c8ee2b9` | — | — |
| 18 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `frontend/lib/city_slug_map.ts` | 95 | 2683 | `3ad77c2b` | spike_helper |
| `frontend/lib/types_cities.ts` | 78 | 2566 | `09d069d8` | spike_helper |
| `frontend/lib/mock_cities.ts` | 188 | 6630 | `b3d0153a` | spike_helper |
| `frontend/app/components/CityPage.tsx` | 56 | 2167 | `308fd084` | spike_helper |
| `frontend/app/cities/[slug]/page.tsx` | 47 | 1438 | `3b350431` | spike_helper |
| `tests/test_city_slug_map_s27b.py` | 142 | 4588 | `8dce8f1a` | schema_negative_test |
| `scripts/_knife22_manifest_bump.py` | 99 | 2939 | `713bb2b3` | （脚本不入 pack）|
| `frontend/smoke-check.py`（扩展 +117 行）| — | 18265 | `7c7518f4` | spike_helper |
| `reviews/.../257-stage0-cc-s27b-lite-cities-impl-receipt-20260826.md` | （本文件）| — | — | documentation |

### 1.2 落地边界（per `256` §SCHEMA + docs/46 §6.1）

| 元素 | 落地方式 | 来源 |
|---|---|---|
| 路由 | `frontend/app/cities/[slug]/page.tsx`（dynamic segment；`generateStaticParams` 预生成 10 城；`dynamicParams = false` 404 兜底）| docs/46 §3.2 + AGENTS.md Static-segment 守门 |
| Slug 锁定 | 10 城 = `nanjing/suzhou/wuxi/nantong/hangzhou/ningbo/wenzhou/guangzhou/shenzhen/dongguan` | `256` §SCHEMA + docs/46 §2 |
| Slug 字符集 | `[a-z0-9-]+` | docs/46 §3.1 |
| Slug 来源 | `CITY_SLUG_MAP`（`frontend/lib/city_slug_map.ts`）+ `CITY_SLUG_LIST`（顺序固定）| docs/46 §3.3 |
| 复用 EvidenceChain | ✅ 6 段渲染（per docs/06 §2 缺一不可）| docs/46 §4.1 + docs/45 §2 #2 不可降级 |
| 复用 SevenDimGrid | ✅ 7 cell + 5 枚举守门（per docs/42 §2.4）| docs/46 §4.1 + docs/42 §3 |
| 复用 PeerCompareCard | ✅ 同省地市横向（per docs/43 §4.1 + docs/46 §11.5）| docs/46 §4.1 + docs/43 §3 |
| Mock 数据 | `MOCK_CITIES[slug]`（10 城 × 6 段 + 7 cell + 同省对比组）| docs/46 §6.1 |
| 应用层 enum-style 守门 | `InformationLayer/Polarity/EvidenceStrength`（不引入 schema ENUM；per docs/40 §2.3 平行）| docs/40 §2.3 |
| mart / person 真数据 | ❌ 不接（OPEN → S2.7-b-full）| `256` §SCHEMA "本刀不做" |

### 1.3 pytest 1 文件结构

| 文件 | cases | 状态 | docs 来源 |
|---|---|---|---|
| `test_city_slug_map_s27b.py` | **6 cases（6 PASS）**| ✅ 全 PASS | docs/46 §3.1 + §3.2 + `256` §NOW-2 |

**cases**:
1. `test_slug_unique` — 10 城 slug 唯一性
2. `test_slug_charset` — `[a-z0-9-]+` 字符集守门
3. `test_locked_list_match` — slug 集合 == Cursor 锁定清单（10 城）
4. `test_no_province_slug_conflict` — 不与 `jiangsu/zhejiang/guangdong/...` 冲突
5. `test_city_slug_list_order_and_length` — 顺序固定 + 长度 = 10
6. `test_meta_present` — 测试自身 meta 关键字段

### 1.4 smoke-check 扩展（9 节守门）

| 守门 | 来源 |
|---|---|
| 9. city_slug_map.ts 含 10 锁定 slug | `256` §SCHEMA + docs/46 §2 |
| 9b. CITY_SLUG_LIST 顺序固定 | `256` §SCHEMA + Cursor 裁定 |
| 9c. dynamic route 有 `generateStaticParams` + `dynamicParams=false` | docs/46 §3.2 + AGENTS.md |
| 9d. CityPage 复用 EvidenceChain + SevenDimGrid + PeerCompareCard | docs/46 §4.1 |
| 9e. mock_cities.ts 覆盖 10 城（via import 或 literal）| docs/46 §6.1 |
| 9f. mock_cities.ts 5 禁词 CLEAN（score/rating/rank/total_score/confidence_score）| docs/46 §1.2 + `256` §红线 |

### 1.5 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 579 | **586** (+7: 5 frontend + 1 pytest + smoke-check) |
| `len(artifacts)` | 579 | **586** |
| `sum(role_count)` | 579 | **586**（bump script 重新从 artifacts 计算 source-of-truth）|

**invariant 守门**：586 == 586 == 586 ✅

**注**：knife 16 bug 修复后，本刀沿用 source-of-truth 模式。

---

## §2. 关键决策（per `256` §SCHEMA + docs/46 + docs/34 §1/§4/§8 #8/§10.4）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **落地刀（lite mock 壳）** — 路由 + mock + 复用三件套 + 最小 pytest | `256` §SCHEMA + 用户 D |
| 路由方案 | dynamic segment `/cities/[slug]` + `generateStaticParams` | docs/46 §3.2 + AGENTS.md Static-segment 守门 |
| 404 兜底 | `dynamicParams = false`（slug 命中锁定清单之外 → notFound）| docs/46 §3.1 |
| 10 城 slug 锁定清单 | 不擅自改（per Cursor 裁定）| `256` §SCHEMA "10 城 slug" |
| Slug 字符集 | `[a-z0-9-]+`（per docs/46 §3.1）| — |
| 复用 EvidenceChain | ✅（per docs/46 §4.1）| docs/06 §2 不可降级 |
| 复用 SevenDimGrid | ✅（per docs/46 §4.1）| docs/42 §3 |
| 复用 PeerCompareCard | ✅（同省地市横向，per docs/46 §11.5 选项 A）| docs/43 §4.1 |
| mock 数据形态 | 6 段全有 1 段非空 + 5 段空（演示"未覆盖"）| docs/45 §2 #2 + docs/06 §2.7 |
| 七维度 cell 分布 | 7 cell 循环 5 枚举（NO_EVIDENCE/NO_CONTRADICTING/NO_SUPPORTING/SUPPORTS_DOMINANT/CONTRADICTS_DOMINANT）| docs/42 §2.4 |
| 信息层 ENUM 期望 | `{FACT, DERIVED, INFERENCE, JUDGMENT}`（per 01-core.sql §25-30）| docs/40 §2.3 |
| ❌ 宣布 Gate 2 PASS | 红线 | docs/34 §1 + §8 #8 + §133 + `256` §红线 |
| ❌ 改 10 城名单 | 红线（per `256` §SCHEMA）| 不得擅自换/加 |
| ❌ 接 mart / person 真数据 | OPEN → S2.7-b-full | `256` §SCHEMA "本刀不做" |
| Gate 2 评审日期 | 暂定 W8（不擅自提前）| docs/34 §10.4 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ §1.4 + §2 + §3 + §4 多次显式守门；receipt 257 严禁 "Gate 2 PASS" 字样 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ §1.2 + §2 锁定清单；落地刀 pytest + smoke-check 双重守门 |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""维度严重度"）| ✅ mock_cities.ts 5 禁词全部 CLEAN |
| ❌ 不 DSH | ✅ |
| ❌ 不爬网 | ✅ 仅 mock |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅落地 `256` §SCHEMA 范围内 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 579 → 586；bump script source-of-truth |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（per `256` §SCHEMA）|
| ✅ 不写 migration | ✅（per `256` §SCHEMA）|
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3 + docs/05 §8.3）|
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ 必带 O1 + O3 OPEN 清单 | ✅ §4 显式守门（沿用 docs/45）|
| ✅ 不引入 score / rating / rank 字段 | ✅ mock_cities.ts 5 禁词 CLEAN |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门（types_cities.ts 8 枚举）|
| ✅ 不动 `polarity` CHECK | ✅ 无关 |
| ✅ 不动 `information_layer` ENUM | ✅ types_cities.ts 应用层守门（per docs/40 §2.3 平行）|
| ✅ 不引入跨行 CHECK 约束 | ✅ trigger + 应用层守门 |
| ✅ Static-segment 守门（dynamic segment route）| ✅ §1.2 显式守门；AGENTS.md 守门 |
| ✅ s27b pytest = 6 PASS | ✅ |
| ✅ 跨 lite 回归 s21lite..s26lite + s210 = 42+12 = **54 PASS + 6 SKIP** | ✅ |
| ✅ 跨 lite 回归 + s27b = **60 PASS + 6 SKIP** | ✅ |
| ✅ smoke-check 仍 PASS（**52/52 ✅** 含 S2.7-b-lite 9 节守门）| ✅ |
| ✅ mock_cities.ts 5 禁词 CLEAN | ✅ |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 101 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 7 新文件 | city_slug_map.ts + types_cities.ts + mock_cities.ts + CityPage.tsx + cities/[slug]/page.tsx + test_city_slug_map_s27b.py + smoke-check.py (扩展) | ✅ |
| pytest s27b | `python3 -m pytest tests/test_city_slug_map_s27b.py -v` | ✅ 6 PASS |
| 跨 lite 回归 | `python3 -m pytest tests/test_*_s*lite.py tests/test_*_s210.py tests/test_city_slug_map_s27b.py -q` | ✅ 60 PASS + 6 SKIP |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ PASS（52/52 含 S2.7-b-lite 9 节守门）|
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 586 == 586 == 586 |
| commit | `git add frontend/lib/city_slug_map.ts frontend/lib/types_cities.ts frontend/lib/mock_cities.ts frontend/app/components/CityPage.tsx frontend/app/cities/[slug]/page.tsx tests/test_city_slug_map_s27b.py frontend/smoke-check.py evidence_pack/manifest.json scripts/_knife22_manifest_bump.py reviews/.../257-...md && git commit -m "feat(frontend): S2.7-b-lite 10 地市 mock 壳 + dynamic segment + 复用三件套 (不宣布 PASS)"` | ✅ `c8ee2b9` |
| origin push | `git push origin HEAD`（**priority**）| ✅ |
| github push | `git push github HEAD`（带 proxy）| ✅ |
| 三路对齐 | origin/main = github/main = local HEAD = `c8ee2b9` | ✅ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 101` 完成后：Cursor 收 `257` → 下发 `258-stage0-cursor-s27b-lite-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.7-b-full 落地刀（tasking 25X+）— 接 `mart_city_evidence_chain` + person/tenure 真数据
  - 依赖：O1 真实 SHA 收口 + Stage 1 OPEN 收口
- 若 FAIL：`257-correction` 回合（修 7 文件 + re-commit）

---

## §6. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b-lite 最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **10 城名单已锁定** — Cursor 锁定清单 4 江苏 + 3 浙江 + 3 广东（per `256` §SCHEMA）；落地刀 pytest + smoke-check 双重守门，确保落地刀不得擅自换/加城市。
- **路由采用 dynamic segment** — `/cities/[slug]` 顶层 + `generateStaticParams`（per docs/46 §3.2 选项 A）；不与省 slug 冲突；AGENTS.md "Static-segment Next.js routes must NOT branch on params.*" 守门。
- **404 兜底** — `dynamicParams = false`（per docs/46 §3.1）；slug 命中锁定清单之外 → `notFound()`。
- **复用三件套** — EvidenceChain (6 段) + SevenDimGrid (7 cell + 5 枚举) + PeerCompareCard (同省地市横向)；不引入新组件（per docs/46 §4.1 复用边界）。
- **应用层 enum-style 守门** — `InformationLayer`/`Polarity`/`EvidenceStrength`/`BalanceStatus`/`SevenDimCardId`/`PopulationTier`/`LocationType`/`IndustryBase`/`DevelopmentStage`/`RoleInGroup`/`SelectionMethod` 共 11 个枚举均应用层守门；不引入 schema ENUM（per docs/40 §2.3 平行）。
- **S2.7-b-full OPEN** — `mart_city_evidence_chain` + `mart_city_seven_dim_overview` + person/tenure 真数据接入契约（per docs/46 §6.2 + §7.2）；依赖 O1 真实 SHA + Stage 1 OPEN 收口后做。

— End of `257` —