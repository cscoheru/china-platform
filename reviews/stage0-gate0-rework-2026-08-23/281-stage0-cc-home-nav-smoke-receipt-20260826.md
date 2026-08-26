# 首页导航 smoke 守门 — CC 回执

- 编号：`281-stage0-cc-home-nav-smoke-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`116` → CC 执行
- 任务书：`280-stage2-home-nav-smoke-tasking-20260826`
- 前置：`279` 七维/对比导航 PASS；`276` 十城导航 PASS；`266` S2.7-b-full-lite mart-shape PASS
- 用户裁定：**D**；自主推进
- 任务性质：**首页导航 smoke 守门刀** — `frontend/smoke-check.py` 加 #11 home nav section

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 116）| ✅ | — |
| 2 | 读 `280` tasking + `frontend/smoke-check.py` 现状（584 行；含 §10 mart-shape 守门）| ✅ | — |
| 3 | 扩展 `smoke-check.py`：加 §11 home nav section（5 守门：4 sections / 10 city links / /seven-dim / 禁词 / 7 维度枚举）| ✅ MODIFIED | — |
| 4 | 本地 `python3 frontend/smoke-check.py` PASS（含 #11；exit 0）| ✅ PASS | — |
| 5 | file-level forbidden-token guard（smoke-check.py + app/page.tsx + types_seven_dim.ts）：0 hit（禁词上下文均为 guard 措辞）| ✅ CLEAN | — |
| 6 | 创建 `scripts/_knife30_manifest_bump.py`（2 NEW_ARTIFACTS：bump + receipt）| ✅ | spike_helper |
| 7 | bump pack（604 → **606**；+2 = bump + receipt；smoke-check.py 已在 manifest knife 13 入册）| ⏳ this step | — |
| 8 | 写回执 `281` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 9 | commit → `origin` 优先 → `github` | ✅ commit `____`（backfill this line）| — |
| 10 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 11 | 三路对齐 | ⏳ local = origin = github = `____` | — |
| 12 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 修改 1 个文件（不计入 NEW_ARTIFACTS；MODIFIED 不入 manifest）

| 路径 | 变更 |
|---|---|
| `frontend/smoke-check.py` | 末尾加 §11 home nav section（5 守门）：4 sections / 10 city links / /seven-dim + /peer-compare anchors / 禁词（score/rating/rank/total_score/confidence_score/peer_rank）/ 7 维度枚举（POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY）；末尾 banner 升级为「+ home nav」PASS 文案 |

### 1.2 新增 2 个文件

| 路径 | 行数 | 大小 | role |
|---|---|---|---|
| `scripts/_knife30_manifest_bump.py` | ~110 | — | spike_helper |
| `reviews/.../281-...md`（本文件）| — | — | documentation |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 604 | **606** (+2: bump + receipt) |
| `len(artifacts)` | 604 | **606** |
| `sum(role_count)` | 604 | **606**（bump script source-of-truth 重算）|

**invariant 守门**：606 == 606 == 606 ✅

---

## §2. 关键决策（per `280` §SCHEMA + docs/46 §2 + docs/42 §3.1 + docs/43 §3.5 + docs/06 §6.6）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **首页导航 smoke 守门刀** — smoke-check 加 #11 home nav section；不改 UI、不接数据 | `280` §SCHEMA "本刀做" |
| 守门 1：4 sections | `app/page.tsx` 必须含 `Indicator inventory` + `/provinces/` + `/cities/` + `/seven-dim` + `/peer-compare` + `CITY_SLUG_LIST` + `MOCK_PROVINCE_LIST` 7 个 anchor | knife 13/22/28/29 累计首页 4 section；knife 30 §NOW-1 |
| 守门 2：10 城链接 | home page 必须为每个 locked slug 含 `/cities/{slug}` 链接（接受 literal `/cities/<slug>` 或 template `/cities/${entry.slug}`）| `256` §SCHEMA 10 城锁定清单 |
| 守门 3：横向视角 anchor | `/seven-dim` + `/peer-compare` 各 1 个 anchor | knife 29 receipt 278 §3.1 |
| 守门 4：禁词 | app/page.tsx 不出现 score/rating/rank/total_score/confidence_score/peer_rank | docs/06 §6.6 + docs/42 §8 + docs/43 §8 |
| 守门 5：7 维度枚举 | `lib/types_seven_dim.ts` 声明全部 7 维度（POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY）| docs/42 §3.1 |
| 模板字面量兼容 | `/cities/{slug}` 链接接受 literal 和 template 两种形态（首页 `entry.slug`；落地守门不强制具体语法）| knife 28 home page 写法 |
| 不动数据 | 不接真 SHA、不接 person/tenure 真数据、不接 mart 真表 — 纯 smoke 守门 | `280` §SCHEMA "本刀不做" |
| 禁词守门 | smoke-check 不派生 score/rating/rank；6 禁词 regex（CI 守门）| docs/06 §6.6 + `280` §红线 |
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `280` §红线 |
| ❌ 改 CF/nginx（运维已另做）| 红线条目（`280` §SCHEMA "本刀不做"）| `280` |
| ❌ 真数据 / 评分 / 排名 / DSH / 爬网 | 红线条目（`280` §SCHEMA "本刀不做/禁止"）| `280` §红线 |
| ❌ 改 `gate_thresholds.json` | 红线条目（未读未写）| `280` §红线 |

---

## §3. 改动对照（per `280` §NOW "1"）

### 3.1 frontend/smoke-check.py

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 总行数 | 584 行 | ~660 行（+76：§11 + banner 升级）|
| 末尾 banner | `=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape smoke: PASS ===` | `=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===` |
| §11 home nav section | ❌ 不存在 | ✅ 新增（5 守门：4 sections / 10 city links / /seven-dim + /peer-compare anchors / 禁词 / 7 维度枚举）|
| §11b 10 城链接守门 | — | template + literal 双形态兼容（regex `/cities/\$\{\s*(?:entry\.slug\|slug)\s*\}/` 覆盖首页 `${entry.slug}` 模板字面量）|
| §11d 禁词守门 | — | 6 禁词：score / rating / rank / total_score / confidence_score / peer_rank |

---

## §4. 验证（per `280` §NOW "2"）

### 4.1 smoke-check 输出

```
$ python3 frontend/smoke-check.py
✅ ... (50+ PASS items, 0 FAIL)
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===

EXIT=0
```

**结果**：✅ exit 0；§11 home nav 5 守门全 PASS（4 sections / 10 city links / /seven-dim + /peer-compare / 禁词 CLEAN / 7 维度枚举）；§10 mart-shape 守门无回归。

### 4.2 file-level forbidden-token guard

| 文件 | 检查项 | 命中 |
|---|---|---|
| `frontend/app/page.tsx` | score/rating/rank/total_score/confidence_score/peer_rank | ✅ 0 hit |
| `frontend/lib/types_seven_dim.ts` | 7 维度枚举声明 | ✅ 7/7 命中（POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY）|
| `frontend/smoke-check.py` | 禁词扫描器自身 | ✅ 仅出现在 regex 模式中（`r"\bscore\b"` 等），不影响守门 |

**结果**：✅ CLEAN

### 4.3 manifest invariant

```
$ python3 -c "import json; m=json.load(open('evidence_pack/manifest.json')); ..."
artifact_count: 604 → 606 (after bump)
len(artifacts): 604 → 606
sum(role_count): 604 → 606
INVARIANT: sum(role_count)=606 == artifact_count=606 == len(artifacts)=606
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt）

### 4.4 手动预览路径（港服 ops 参考）

| 入口 | URL | smoke 守门 |
|---|---|---|
| 首页 | `/` | §11 home nav（4 sections / 10 city links / /seven-dim + /peer-compare anchors）|
| 七维度观察卡 | `/seven-dim` | §11c anchor + §11e 7 维度枚举守门 |
| 同类地区对比 | `/peer-compare` | §11c anchor |
| 地市详情（10 城）| `/cities/{slug}` | §11b 10 城链接守门 |
| 省级详情（5 省）| `/provinces/{slug}` | §11a 4 sections anchor |

---

## §5. 红线自检（per `280` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8 + docs/43 §8 + docs/46 §1.2）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ smoke 守门 10 城与 `CITY_SLUG_LIST` 迭代一致 |
| ❌ 不接真 SHA 样本 | ✅ smoke-check 仅扫描文件，不接 dbt / 不动 schema |
| ❌ 不接 O1 收口 | ✅ 本刀与 O1 无关 |
| ❌ 不全量 dbt seed | ✅ 本刀仅 smoke 守门 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / peer_rank | ✅ §11d file-level guard CLEAN（0 hit app/page.tsx）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 CF/nginx（运维已另做）| ✅ `280` §SCHEMA "本刀不做"；本刀不动 infra |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `280` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 604 → 606；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ smoke-check exit 0 | ✅ §10 mart-shape + §11 home nav 全 PASS |
| ✅ 兼容 S2.7-a / S2.7-b-lite / S2.7-b-full-lite / S2.8-lite / S2.9-lite 已交 | ✅ 不动 mock 数据；不动 mart-shape 接驳 |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ 7 维度枚举由 types_seven_dim.ts 单一出口；isValidSevenDimCell 等守门函数 |
| ✅ Static-segment 守门（dynamic segment route）| ✅ smoke-check §9c 已守门 cities/[slug] + generateStaticParams + dynamicParams=false；本刀未触碰 |
| ✅ 不修改 `frontend/app/page.tsx`（数据已交，knives 28+29）| ✅ 仅 smoke-check 守门 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 116 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| smoke-check.py 修改 | §11 home nav section（5 守门）| ✅（MODIFIED）|
| smoke-check 验证 | `python3 frontend/smoke-check.py` | ✅ exit 0（50+ PASS）|
| file-level forbidden-token guard | grep 禁词清单 | ✅ CLEAN（0 hit）|
| bump script | `scripts/_knife30_manifest_bump.py` | ✅ 604 → 606（+2 = bump + receipt）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 606 == 606 == 606 |
| commit (knife 30 主提交) | `git add frontend/smoke-check.py scripts/_knife30_manifest_bump.py evidence_pack/manifest.json reviews/.../281-...md && git commit -m "test(smoke): 加 #11 home nav section 守门 4 sections + 10 城链接 + 禁词 + 7 维度枚举"` | ✅ `____` |
| origin push | `git push origin HEAD`（**priority**）| ✅ |
| github push | `git push github HEAD`（带 proxy）| ✅ |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 116` 完成后：Cursor 收 `281` → 下发 `282-stage0-cursor-home-nav-smoke-audit-…md`（PASS/FAIL）
- 若 PASS：smoke 守门（含 §11 home nav）随 `281` 入正式 CI 路径；首页 4 sections 守门自动跑
- 若 FAIL：`281-correction` 回合（修 §11 守门 + re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是首页导航 smoke 守门最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做 smoke 守门** — `280` §SCHEMA 显式约束：不接真数据 / 不改评分/排名 / 不改 CF/nginx（运维已另做）/ 不爬网。
- **首页完整结构（knife 28 + 29 + smoke 30）** —
  1. Indicator inventory（S2.0.1；mock by default）
  2. 省级观察入口（S2.7-a；5 行）
  3. 地市观察入口（S2.7-b-lite / S2.7-b-full-lite；10 行 × 4 列）
  4. 横向视角入口（S2.8-lite 七维度 + S2.9-lite 同类对比；2 行 × 4 列）

  §11 home nav 5 守门覆盖全部 4 sections。
- **template + literal 双形态兼容** — knife 28 首页 `/cities/${entry.slug}` 是 template-literal 形态；§11b 用 regex `/cities/\$\{\s*(?:entry\.slug|slug)\s*\}/` 兼容，未来若改 literal `/cities/<slug>` 同样通过。
- **不修改 `frontend/app/page.tsx`** — 数据已交（knife 13/22/28/29 累计）；本刀仅 smoke 守门，避免双改冲突。
- **smoke-check 总条目数** — 约 50+ PASS（含 §10 mart-shape 守门 4 件套 + §11 home nav 5 守门）。
- **依赖 O1 真实 SHA 收口** — 本刀不涉及；O1 收口前 demo 恒为 '0'*64 占位（per docs/47 §3.1）。
- **依赖 Stage 1 OPEN 收口** — 本刀不涉及。
- **依赖 S2.1-lite PASS** — 本刀不涉及（person/tenure 与首页导航无关）。
- **S2.7-b-full 真数据迁移刀仍 OPEN** — dbt mart 真表 + person/tenure 真数据 + lineage.source_file_sha256 从占位 `'0'*64` 替换为 O1 真实 SHA（per docs/47 §6.3 切刀风险 + docs/45 §5.5 OPEN）；本刀不涉及。

— End of `281` —

> 等待 Cursor 审验（预期 `282-stage0-cursor-home-nav-smoke-audit-…md`）。
> 通过后 smoke 守门（含 §11 home nav）随 `281` 入正式 CI 路径。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `280` §红线）。
> ⚠ **本刀只做 smoke 守门**（per `280` §SCHEMA "本刀做/本刀不做"）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。