# Knife 52 回执 — 公开提取 → 前端结构化呈现（tasking 349）

- 编号：`350-stage0-cc-public-extract-frontend-wire-receipt-20260826`（文件名须含 `-cc-` 供 gate_watch 识别）
- 前置：`348` PASS（receipt 347 ACK）；`7f04237` Cursor 修复 NBS extract 被 pytest 覆写；`60698d7` ACK + tasking 349;`f17fb56` knife 51 backfill
- 落地：build-time fixture 快照（`frontend/lib/public_extract_nbs.json`,63 行,registry SHA 锚定）+ 专用静态路由 `/public-extracts`（REGISTRY_SAMPLE · demo 显式标注,DemoBadge 复用,provenance 表,63 行全量展示）+ 首页导航入口 + smoke-check §12 gate + 7 case pytest + build 证据 + 回执 **`350`**

## §META

| 字段 | 值 |
|---|---|
| knife | 52 |
| tasking | 349 |
| phase | CC_ACTION_REQUIRED |
| queue_rev | 145 |
| cc_receipt | 350 |
| cc_head | `d321a65`（knife 52 feature commit;已推 origin + github,三向收敛） |
| user_ruling | D + 源工程 Cursor 代判;本地样本结构化已通 → 接前端呈现 |
| 测试 | **pytest 7/7 新 case PASS + 69 connector 无回归 = 76/76;smoke-check 全 PASS（含 §12 新 gate）;`next build` exit 0,`/public-extracts` 静态预渲染（22/22 pages）** |
| pack | 658 → 663（+5:fixture + page + pytest + bump + receipt） |

## §NOW — tasking 349 §SCHEMA 落点

| 决策点 | 落地 |
|---|---|
| (1) 前端可读 public_extracts（fixture 生成,构建期/运行期二选一,优先简单可测） | **构建期**:`frontend/lib/public_extract_nbs.json` 逐字节快照自 `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json`;`resolveJsonModule: true` 导入;静态预渲染零运行期 IO |
| (2) 首页或专用区块展示 NBS 提取表（≥若干行可见）;显式标注 REGISTRY_SAMPLE / demo,非 live O1 | **专用路由** `/public-extracts` 63 行全量展示 + **首页** 横向视角入口表加行链接;页面标题挂 `DemoBadge`（is_demo=true）+ 正文显式 `REGISTRY_SAMPLE / demo — 非 live O1` 字样 |
| (3) 保留现有 mart demo 旗标逻辑,不谎称真收口 | mart fixture / `NEXT_PUBLIC_USE_MART_FIXTURE` 零改动;本页不写 O1_AUTO_INTAKED;pytest `test_page_does_not_claim_live_o1` 守门 |
| (4) ≥1 测或 build 证据 | **三证齐给**:7/7 pytest + smoke-check PASS + `next build` exit 0 |
| (5) 回执 350 | 本文件 |

## §1 修改清单

| 文件 | 角色 | 状态 |
|---|---|---|
| `frontend/lib/public_extract_nbs.json` | data_contract_suite（NEW 计项 +1） | NEW（324 行快照;含 domain/category/source_sample_path/source_archive_path/source_sha256/row_count/rows[63]/extracted_at） |
| `frontend/app/public-extracts/page.tsx` | spike_helper（NEW 计项 +1） | NEW（~180 行;provenance 表 + 63 行提取表;列序 = 首行键序,不重排不 reinterpret） |
| `tests/test_public_extract_frontend_fixture.py` | schema_negative_test（NEW 计项 +1） | NEW（7 case;registry SHA / sample path 双锚定） |
| `scripts/_knife52_manifest_bump.py` | spike_helper（NEW 计项 +1） | NEW |
| `reviews/.../350-stage0-cc-public-extract-frontend-wire-receipt-20260826.md` | documentation（NEW 计项 +1） | NEW（本文件；gate 要求 `-cc-`） |
| `frontend/app/page.tsx` | —（未入 manifest） | MODIFIED（横向视角入口表 +1 行 `/public-extracts` + REGISTRY_SAMPLE·demo 标注;同 knife 280 homepage 先例不入 manifest） |
| `frontend/smoke-check.py` | spike_helper（已登记） | MODIFIED（+§12/§12b gate:bump SKIP） |

## §2 验证证据

### 2.1 pytest（7 新 case + 69 connector 回归）

```
tests/test_public_extract_frontend_fixture.py::test_fixture_row_count_is_63 PASSED
tests/test_public_extract_frontend_fixture.py::test_fixture_provenance_sha_matches_registry PASSED
tests/test_public_extract_frontend_fixture.py::test_fixture_source_sample_path_matches_registry PASSED
tests/test_public_extract_frontend_fixture.py::test_fixture_first_row_key_shape PASSED
tests/test_public_extract_frontend_fixture.py::test_page_imports_fixture_and_labels_registry_sample PASSED
tests/test_public_extract_frontend_fixture.py::test_page_does_not_claim_live_o1 PASSED
tests/test_public_extract_frontend_fixture.py::test_home_page_links_public_extracts PASSED

tests/test_auto_ingest_public_source_s52.py 69 case + fixture 7 case = 76 passed in 1.67s
```

### 2.2 smoke-check（含 §12 新 gate）

```
✅ public_extract_nbs.json: 63 行 NBS 提取 fixture 在位
✅ public-extracts/page.tsx: fixture import + REGISTRY_SAMPLE 标注 + provenance
✅ app/page.tsx links /public-extracts nav anchor
=== ... smoke: PASS ===
```

### 2.3 build 证据

```
✓ Generating static pages (22/22)
├ ○ /public-extracts   160 B   87.2 kB
○  (Static)   prerendered as static content
```

`/public-extracts` 以 `○ (Static)` 预渲染 — 构建期 fixture 生效,零运行期文件 IO。

### 2.4 pytest 副作用处理（诚实记录）

connector 回归跑完后 `data/public_extracts/{stats.gov.cn,sz.gov.cn}/*.json` 被
main-returning case 重写（extracted_at 时间戳变化）— 与 `7f04237` Cursor 修复的
是同一现象。已 `git checkout --` 恢复,恢复后 fixture pytest 复跑 7/7 PASS
（fixture 溯源锚 registry SHA,不依赖与 live extract 的字节对比,天然免疫此覆写）。

## §3 设计决策:构建期 fixture（非运行期读盘）

| 方案 | 取/舍 |
|---|---|
| **构建期快照**（本刀采用） | `cp` 逐字节快照 + `resolveJsonModule` 导入;静态预渲染;无运行期 fs 依赖;溯源靠 fixture 内 `source_sha256` 字段 == registry `file_hash_sha256`（pytest 锚定） |
| 运行期读盘（舍） | RSC 内 `fs.readFile` 读 repo 相对路径;dev 可行但 standalone build 产物不 trace 该文件;且读到的是会被 connector 测试覆写的 live 文件 — 溯源不稳 |

溯源锚定用 registry SHA 而非「fixture ↔ live extract 字节对比」:后者会被
connector pytest 的覆写打破（7f04237 教训）,前者是稳定契约。

## §4 页面契约

| 要素 | 值 |
|---|---|
| 路由 | `/public-extracts`（静态段;无 `params.*` 分支 — per tasking 150 既有红线） |
| 标注 | 标题挂 `<DemoBadge lineage={{is_demo: "true", demo_reason: "REGISTRY_SAMPLE — ... 非 live O1; sample ≠ live closure"}}/>` + 正文 `REGISTRY_SAMPLE / demo` 加粗声明 |
| provenance | 8 字段表:domain / category / intake_status=REGISTRY_SAMPLE_INTAKED / source_sample_path / source_archive_path(WORM) / source_sha256 / row_count / extracted_at |
| 表格 | 列序 = 首行键序（`指 标` / `7月` / `1—7月`）;63 行原样渲染;空白与「…」保留不补造;注明原表两层表头被展平 |
| 免责 | 「非 live O1;live 探测仍 JS 壳 tech-blocked (rc=7)」 |

## §5 invariant 守恒

| 步骤 | artifact_count | sum(role_count) | len(artifacts) | 一致 |
|---|---|---|---|---|
| knife 51 后基线 | 658 | 658 | 658 | ✅ |
| + fixture | 659 | 659 | 659 | ✅ |
| + page | 660 | 660 | 660 | ✅ |
| + pytest | 661 | 661 | 661 | ✅ |
| + bump | 662 | 662 | 662 | ✅ |
| + receipt | 663 | 663 | 663 | ✅ |

`NEW_ARTIFACTS = +5` ⇒ pack `658 → 663`。

## §6 红线审计

| 红线 | 守 |
|---|---|
| ❌ 不宣布 Gate/O1 PASS | 页面/回执零 PASS 字样;`REGISTRY_SAMPLE_INTAKED` ≠ O1 |
| ❌ sample ≠ live / 把 sample 标成 live 真数据 | DemoBadge + 显式「非 live O1」;pytest `test_page_does_not_claim_live_o1` 断言无 O1_AUTO_INTAKED |
| ❌ 不伪造 | 空白/「…」原样;两层表头展平如实注明;63 行未增删 |
| ❌ 不评分/不排名（禁词） | smoke-check §12 对 page.tsx 扫 score/rating/rank/total_score — PASS |
| ❌ 静态段不分支 params.* | `/public-extracts` 无 params;无 PageProps |
| ❌ 不绕 AUTH / 不 HTTP pin / 不 headless | 本刀纯前端,零网络 |
| ❌ 不改 gate_thresholds.json / 不碰 00-CC-CURRENT.md | untouched |
| ❌ 不擅自 --force | 常规 ff-only + push |
| ✅ pack invariant | §5 三冗余守恒 |
| ✅ receipt location | `reviews/stage0-gate0-rework-2026-08-23/350-...md` |
| ✅ mart demo 旗标逻辑保留 | `NEXT_PUBLIC_USE_MART_FIXTURE` / mart_city_* 零改动 |

## §7 与 docs/52 §3 试点对账（前端呈现维度）

| 试点 | 状态 |
|---|---|
| NBS HTML | 后端:46/47/51（local 63 行）;**前端:本刀 `/public-extracts` 已呈现**;live 仍 JS 壳 |
| Hubei EXCEL | 后端:48/49/50/51（opt-in pytest 覆盖）;前端:未呈现（0 行 EXCEL 抽取未跑实跑,待 Cursor 启动） |
| Shenzhen HTML | 后端:50/51（local 0 行,需 v2 抽取）;前端:不呈现（0 行无内容可显;不伪造） |

## §8 推 / 落地

- commit: **`d321a65`** `feat(frontend): 349 public-extract wire — /public-extracts REGISTRY_SAMPLE page`
- push origin: ✅ `95a8569..d321a65 HEAD -> main`
- push github: ✅ `95a8569..d321a65 HEAD -> main`
- three-way convergence: ✅ `HEAD = origin/main = github/main = d321a65`
- 期间 Cursor 提交 `95a8569`（再次恢复 NBS extract 被 subprocess 测试覆写）— 与本刀 `git checkout` 恢复等价,fast-forward 无冲突
- backfill SHA: 本 commit（另起,per knife 17:不 amend-after-push）

## §9 下次心跳预期

`./scripts/cc_gate_watch.sh --pull` → re-arm → 84 POLL;`cursor_ack` bump 前只 POLL;`queue_rev` 变化 → 读 §NOW。

— End of Knife 52 receipt 350 —
