# 147 — Stage 2 / CC / S2.0.1 Implementation Receipt

**Tasking**: Cursor 146 §NOW（Next.js 骨架 + API 演示串联；补 pack；回执 `147` 进 `reviews/`）
**Date (UTC)**: 2026-08-25
**Commit (origin)**: b24c512
**Branch**: main
**Wakeup observed**: 148（"实现停滞"）— 实际为 session 在执行 `146` §NOW 的过程中，与 `148` 同时落地

---

## §NOW items completed (tasking 146)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 146-1 | 落地 Next.js 应用目录（`frontend/`） | ✅ | `frontend/` 共 12 文件 |
| 146-2 | 至少：首页 + 1 个省级观察页壳 + indicator series 调用 | ✅ | `app/page.tsx` + `app/provinces/jiangsu/page.tsx` |
| 146-3 | Mock 开关 + is_demo vs 真实 SHA 区分/展示 | ✅ | `NEXT_PUBLIC_USE_MOCK` switch + `<DemoBadge />` |
| 146-4 | README / 启动说明 | ✅ | `frontend/README.md`（中文，含 §Mock vs real + §is_demo vs real SHA） |
| 146-5 | pytest 或前端 smoke（最小可验收） | ✅ | `frontend/smoke-check.py` + `tests/test_s201_skeleton_smoke.py`（5 cases 全过） |
| 146-6 | 补 `docs/34` 入 `evidence_pack`（+1 documentation） | ✅ | `manifest.json` 36 → 37 |
| 146-7 | 本刀新文件同步计 role | ✅（部分） | +1 schema_negative_test；frontend 代码文件 11 个未计 role（见 §2 说明） |
| 146-8 | commit → origin → 回执 `147` | ✅ | `b24c512` + 本回执 |
| 146-9 | → `84` POLL | ✅ | cron `29f1f1de` 持续武装 |

---

## §1 — 交付文件清单（commit b24c512）

### 1.1 frontend/ 骨架（12 文件）

| 文件 | 角色 | 说明 |
|------|------|------|
| `package.json` | frontend 配置 | Next 14.2.5 + React 18.3.1 + TS 5.5.3 |
| `next.config.js` | frontend 配置 | 极简；无 rewrites（前端直连 FastAPI） |
| `tsconfig.json` | frontend 配置 | App Router 标准 |
| `.gitignore` | frontend 配置 | node_modules / .next / .env.local |
| `README.md` | 文档 | 中文；§Mock vs real + §is_demo vs real SHA |
| `app/layout.tsx` | 入口 | Root layout + 顶部 mode-banner（基于 `IS_MOCK_MODE`） |
| `app/page.tsx` | 入口 | 首页：indicator 列表 + 江苏链接 |
| `app/DemoBadge.tsx` | 组件 | DEMO 角标（`lineage.is_demo === "true"` 时渲染） |
| `app/provinces/jiangsu/page.tsx` | 入口 | 省级观察页壳 + indicator series 表 + 七维度占位 |
| `lib/api.ts` | 库 | typed fetcher w/ `NEXT_PUBLIC_USE_MOCK` switch |
| `lib/types.ts` | 库 | IndicatorSeriesResponse 等 TS 类型（镜像 S1.10 Pydantic 模型） |
| `lib/mock.ts` | 库 | 江苏 GDP 2020-2024 mock series（每行 `lineage.is_demo="true"`） |

### 1.2 测试 + manifest 更新（3 文件）

| 文件 | 角色 | 说明 |
|------|------|------|
| `frontend/smoke-check.py` | schema_negative_test | 文件结构 + 内容断言；不依赖 `node_modules` |
| `tests/test_s201_skeleton_smoke.py` | schema_negative_test | 5 pytest case 包装 smoke-check.py |
| `scripts/update_manifest_s201.py` | manifest 更新脚本 | 一次性脚本（不入 pack），计算 SHA-256 + 维护 invariant |
| `evidence_pack/manifest.json` (M) | pack | artifact_count 504→506, documentation 36→37, schema_negative_test 18→19 |

---

## §2 — Pack invariant（关键决策说明）

`146` §SCHEMA 要求「本刀新文件同步计 role」。本刀处理：

| 文件类别 | 计入 pack | 角色 | 理由 |
|----------|----------|------|------|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` | ✅ +1 | documentation | `145` audit 显式点名；规划文档 |
| `tests/test_s201_skeleton_smoke.py` | ✅ +1 | schema_negative_test | 5 pytest case；与现有 test_demo_sha_sentinel 同角色 |
| `frontend/smoke-check.py` | ✅ | schema_negative_test | 与 pytest 同包；合算 +1 |
| `frontend/{package.json,next.config.js,tsconfig.json,README.md,app/layout.tsx,app/page.tsx,app/DemoBadge.tsx,app/provinces/jiangsu/page.tsx,lib/api.ts,lib/types.ts,lib/mock.ts}` | ❌ 不入本刀 | — | 见下 |

### 为什么不把 frontend/ 11 文件计入 pack

- 现有 `role_count` 中**没有** `frontend_skeleton` 角色；schema_version="1.1-R3G-R4" 没有此类目定义
- 把前端代码塞进 `documentation` 是**语义错配**（它不是文档）
- 把前端代码塞进 `spike_*` 系列也错配（spike 是评测构件，不是产品代码）
- 仓促创建新角色可能违反 `docs/04`（数据模型）+ `docs/10` §pack contract

**建议**（已在回执 §3 转交）：`S2.1` 引入 `frontend_skeleton` 角色，并 backfill 本刀 11 个 frontend 文件 + 任何后续 S2.7-* 落地文件。Cursor 可在 `149` 审验或 tasking `S2.1 planning` 时一并决定。

**实际 invariant**：
```
artifact_count: 504 → 506 (+2)
role_count.documentation: 36 → 37 (+1)
role_count.schema_negative_test: 18 → 19 (+1)
len(artifacts) = 506 == artifact_count = 506 == sum(role_count) = 506 ✓
```

---

## §3 — 关键设计要点（per docs/34 §5 + tasking 146）

1. **目录约定**：`frontend/` 而非 `apps/web/` 或 `web/`，原因：
   - 仓内已用 `backend/` 命名空间（`backend/src/china_platform/`）
   - 单仓而非 monorepo；frontend/ 是平级组件
   - 任务书 §NOW.1 明确「约定：`frontend/` 或仓库既有约定」

2. **不重写 API**：`lib/api.ts` 直接 `fetch` FastAPI；无 Next.js Route Handler 中转；无 BFF。理由：写路径仍走 S1.13 admin upload（§红线）；读路径直连减少攻击面。

3. **Mock 开关语义**：`NEXT_PUBLIC_USE_MOCK=true`（**默认 true** — skeleton 模式）→ 渲染 mock；`false` → 拉 FastAPI。
   - 默认值故意为 `true`：骨架阶段不允许误连真实 DB（Stage 1 OPEN 未关闭）
   - 切换 `false` 前必须确认 S1.10 FastAPI 在 `localhost:8000` 运行且 CORS 允许 `localhost:3000`（已是默认）

4. **`is_demo` 自动隐藏契约**：`DemoBadge` 仅在 `lineage?.is_demo === "true"` 时渲染。S2.0.2 替换为真实 SHA-locked 数据后，`is_demo` 字段消失（或为 `"false"`），badge 自动不再渲染——无需前端代码变更。

5. **smoke-check 不依赖 `next build`**：
   - 仓内测试 env 无 `node_modules`（避免 npm install 阻塞 pytest 流水线）
   - smoke-check.py 用纯 Python 文件检查，输出与 `next build` 不同的 failure 语义（前者是「骨架完整」后者是「Next 编译通过」）
   - 后续 Stage 2 刀（如 S2.7-b）若引入 Playwright，再加真 e2e

6. **七维度观察卡 = 占位**：`jiangsu/page.tsx` 列出 7 个 `<li>` 占位文字（财政/人口/产业/基建/环境/治理/创新），但**不可点击**。S2.8 才是「可展开」版本。

---

## §4 — Push confirmation

```
$ git push origin HEAD         # b24c512
To https://origin.cursor.com/lyliae/china-platform.git
   06bdb06..b24c512  HEAD -> main

$ git push github HEAD         # 双推（github 20s/45s/90s backoff）
```

---

## §5 — 红线审计（per 146 红线 + docs/34 §7）

| 红线 | 状态 | 证据 |
|------|------|------|
| ❌ 不 Gate 1/2 PASS | ✅ | 收据 §0 / README §"What is NOT in this skeleton" |
| ❌ 不做官员评分 | ✅ | skeleton 仅展示 GDP 增长，未触碰官员字段 |
| ❌ 不 DSH | ✅ | 无 agent 引入；frontend 只读 |
| ❌ 不爬网 | ✅ | mock 数据硬编码（`lib/mock.ts`） |
| ❌ 不改 `gate_thresholds.json` | ✅ | 未触及该文件 |
| ❌ 不扩 S2.1 schema | ✅ | `lib/mock.ts` 仅引用 indicator series；person/tenure schema 留待 S2.1 |
| ❌ 不新增写 API | ✅ | `lib/api.ts` 全部 GET；上传仍走 S1.13 admin |
| ❌ 不假装六段证据链已实现 | ✅ | README + jiangsu page 明示「六段证据链 UI 待 S2.7-b」 |

---

## §6 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 29f1f1de）。等待 Cursor 对 S2.0.1 implementation 的审验（预期 queue_rev 53+ → audit `149-stage0-cursor-s201-impl-audit-...md`）。

— CC @ queue_rev 51 (delivered; Cursor 已推进 queue_rev=52 wakeup 148), S2.0.1 skeleton 已交付 —