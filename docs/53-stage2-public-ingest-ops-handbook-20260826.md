# 53 · Stage 2 — 公开源自动获取 · Ops 手册

> ⚠ 本手册描述**现状行为**，不宣布任何 Gate / O1 PASS。
> ⚠ sample 轨与 LIVE_CANDIDATE 轨是**分轨**：候选轨永远不覆盖 sample 轨；候选轨是 drift 候选，**等用户裁定**，不是 O1 收口数据。
> ⚠ 手册诚实标注 demo / candidate 语义（per tasking 364 §红线）。

- 起草：CC · 2026-08-26 · queue_rev 150（tasking 364）
- 位置：Stage 2 · 公开源（stats.gov.cn 试点）
- 上游规划：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`
- 索引登记：`docs/45-stage2-s210-lite-gate2-review-index-20260826.md`
- 覆盖的刀：344/347（connector + local-sample 提取）→ 350（前端 sample 区块）→ 353（pytest 提取保护）→ 356（JS 壳启发式 + NBS live 过壳）→ 359（live WORM 提取 + LIVE_CANDIDATE 前端区块）→ 362（`--refresh-live-candidate` 一键刷新）

---

## 1. 工具与入口

- 脚本：`scripts/auto_ingest_public_source.py`（single-file connector）
- 试点：`--pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN`（均为默认值）
- registry：`source_registry/registry.csv`（`file_hash_sha256` 是 sample 轨锚；live drift **不**自动改写 registry，per knife 333 drift 契约 + Cursor `341`）
- 根目录覆盖（先于任何写路径解析）：
  - CLI：`--archive-root=DIR` / `--extract-root=DIR`
  - 环境变量：`CEGR_ARCHIVE_ROOT` / `CEGR_EXTRACT_ROOT` / `CEGR_FRONTEND_LIB_ROOT`（pytest 用它们把三个写根全部指到 tmp 目录，per tasking 352）

## 2. 四种运行模式（命令例）

### 2.1 dry-run（默认，无网络）

```bash
python3 scripts/auto_ingest_public_source.py
```

只校验 registry 过滤器能否命中 pilot 行；不下载、不写任何文件。预期 `rc=0`。

### 2.2 local-sample 入库（无网络）

```bash
python3 scripts/auto_ingest_public_source.py --from-local-sample \
    --confirm-live=reviews/stage0-gate0-rework-2026-08-23/<lineage-output>.jsonl
```

- 读 registry 行的 `local_sample_path`，SHA 必须等于 `file_hash_sha256`
- 写 lineage；`intake_status=REGISTRY_SAMPLE_INTAKED`，`is_demo=true`（sample 即 demo 语义）
- 湖北（registry `enabled=FALSE`）需另加 `--allow-disabled-local-sample`

### 2.3 live 探测（网络 + WORM 归档）

```bash
python3 scripts/auto_ingest_public_source.py --live \
    --confirm-live=reviews/stage0-gate0-rework-2026-08-23/<lineage-output>.jsonl
```

流水线：壳门（JS 壳启发式）→ 同域 deeplink 解析 → 重下载 → SHA → WORM 归档（`data/public_archives/YYYY-MM/<domain>/…`，只增不改）。SHA 与 registry 锚不一致 → `rc=4`（drift，出报告等裁定，**不**自动收口）。

### 2.4 一键刷新 LIVE_CANDIDATE（live + 候选双写）

```bash
python3 scripts/auto_ingest_public_source.py --live \
    --confirm-live=reviews/stage0-gate0-rework-2026-08-23/<lineage-output>.jsonl \
    --refresh-live-candidate
```

- 在 2.3 的完整 live 流水线之后，把提取结果写入候选双轨：
  - data 侧：`data/public_extracts/{domain}/{category}_LIVE_CANDIDATE.json`
  - 前端：`frontend/lib/public_extract_nbs_live_candidate.json`（byte-verbatim 同步，stats.gov.cn/NATIONAL_BULLETIN 专用）
- drift（rc=4）与 match（rc=0）两分支都会写候选轨；AUTH/transport/tech-blocked 早退路径不写
- **绝不触碰 sample 轨**（sample JSON / sample fixture / registry 哈希；pytest 字节级前后对比锁定，per 362）
- 忘带 `--live` → 直接 `rc=6` 拒绝（refresh 即 live，同授权纪律）

## 3. 出口码速查

| rc | 含义 | 处置 |
|---|---|---|
| 0 | 成功（dry-run 过 / local-sample 入库 / live SHA 匹配） | 正常 |
| 1 | pilot 行未命中（过滤器无匹配；或 `enabled=FALSE` 行未加 `--allow-disabled-local-sample`） | 检查 `--pilot-domain/--pilot-category` |
| 2 | registry CSV 缺失或为空 | 检查 `source_registry/public_sources.csv` |
| 3 | AUTH（live 授权链失败） | 检查 `--confirm-live` |
| 4 | SHA drift（live 下载 ≠ registry 锚） | **等用户裁定**；drift 报告 + WORM 已留档；不自动改 registry |
| 5 | transport（网络传输失败） | 重试或排查网络 |
| 6 | live 无 confirm（`--live` / `--from-local-sample` / `--refresh-live-candidate` 缺 `--confirm-live`；refresh 缺 `--live`） | 补授权参数 |
| 7 | tech-blocked（JS 壳页 / 大页面无 `<table>` 空内容） | 记 tech-block 报告；不硬闯 |
| 8 | local-sample SHA 与 registry `file_hash_sha256` 不符 | 停手；先对账 |
| 9 | `local_sample_path` 文件缺失 | 检查 sample 文件在位 |

## 4. sample 轨 vs LIVE_CANDIDATE 轨（分轨契约）

| | REGISTRY_SAMPLE（sample 轨） | LIVE_CANDIDATE（候选轨） |
|---|---|---|
| 文件（data 侧） | `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` | `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN_LIVE_CANDIDATE.json` |
| 前端 fixture | `frontend/lib/public_extract_nbs.json` | `frontend/lib/public_extract_nbs_live_candidate.json` |
| 行数 / SHA | 63 行 · `dea13b8a…`（registry 锚定） | 60 行 · `0b85212f…`（WORM `zxfb` 归档锚定，2026-08-21 NBS 文章） |
| `intake_status` | `REGISTRY_SAMPLE_INTAKED`（`--from-local-sample` 入库） | `LIVE_CANDIDATE`（`--refresh-live-candidate` 刷新） |
| `is_demo` | true（sample 即 demo） | true（候选沿 knife 333 CANDIDATE_AUTO 惯例） |
| 语义 | 契约演示轨，registry 哈希锁定 | drift 候选，**非 O1 收口**，等用户裁定 |

- 两条轨道互不覆盖：候选轨文件名带 `_LIVE_CANDIDATE` 后缀；刷新永不写 sample 文件名。
- drift 裁定后若用户确认升级 sample，须走显式任务书（改 registry 锚 + 换 sample 文件），不由本手册流程自动完成。

## 5. 预览

> 🌐 **公网预览**：`https://china.3strategy.cc/public-extracts`（HTTP 200 per 回执 `446` 公网验收基线：四轨 + 一览条 + 行筛选 + JSON/CSV + 全站顶栏 site-nav 常驻入口）+ 首页 4 deeplink 提示（`https://china.3strategy.cc/` → `/public-extracts#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb`）；命令链见本节第 16 项 🔧 条目，URL 块互链登记见第 18 项 + `docs/50` §4.4 公网预览段（per 回执 `454`）。`docs/45` 侧互链登记见第 19 项（per 回执 `464`）+ `docs/45` §1。**公网 URL 是运维演示入口，与本地预览同构（demo/candidate build），非 O1/Gate PASS**。本地预览说明保留于下：

```bash
cd frontend && npm run dev   # 或 npm run build && npm start
```

打开 **`/public-extracts`**（静态预渲染路由，无 `params.*` 分支）：

1. 上半区 = sample 轨区块（REGISTRY_SAMPLE，63 行 + provenance）
2. 下半区 = live 候选区块（LIVE_CANDIDATE，60 行 + deeplink/WORM/SHA provenance + DemoBadge 注明 drift 候选、非 O1 收口、与上方 sample 分轨互不覆盖）
3. 尾部 = 深圳区块（REGISTRY_SAMPLE 散文轨，sz.gov.cn MUNICIPAL_BULLETIN，71 行 `{section, paragraph}` + provenance + DemoBadge 注明 demo、SSL 暂缓未做过 live 探测、与 NBS 两轨分轨互不覆盖；per 回执 `368`/`371`）
4. 尾尾 = 湖北区块（REGISTRY_SAMPLE xlsx 轨，tjj.hubei.gov.cn PROVINCIAL_BULLETIN，21 行 `{指标, 单位, 增速}` + provenance + DemoBadge 注明 demo、live `enabled=FALSE` 暂缓未做过 live 探测、与 NBS+深圳三轨分轨互不覆盖；per 回执 `377`）
5. **页首 = 四轨一览条 overview strip**（7 列 × 4 行 = NBS sample / NBS live 候选 / 深圳 / 湖北；domain / category / 行数 / SHA 前 8 / demo|candidate 标注 / 锚链到 4 分节；数据只读自既有 4 fixture，不重算；per 回执 `383`；smoke §12f 门）
6. **各数据表 = 每轨独立行筛选**（四个数据表各一受控 input（`data-testid="track-filter-{nbs-sample,nbs-live,sz,hb}"`）；单元格文本包含匹配、大小写不敏感、空查询=全量；纯客户端 `"use client"` + useState（路由仍 ○ 静态）；匹配 X / Y 计数行 + 「非权威库检索 / 视图过滤 / 不改数据 / SHA」守门 + 空匹配占位行；不改 fixture 字节；per 回执 `398`；smoke §12h 门）
7. **全站顶栏 `site-nav` = `/public-extracts` 常驻入口**（`frontend/app/layout.tsx` 在 `<header data-testid="mode-banner">` 之后插入 `<nav data-testid="site-nav">`：首页 + `<a href="/public-extracts" data-testid="site-nav-public-extracts">公开提取样本（四轨 demo）</a>`；旁注「全站顶栏常驻链；四轨 demo / 非 O1 / 不宣布 Gate PASS（per tasking 409）」；纯 `<a href>` 锚链未引入 `next/link`，build 仍 ○ Static 22/22；不分支 `params.*`；per 回执 `410`；smoke §13c 门 6 针 + 5 pytest `test_layout_site_nav_public_extracts.py`）；**site-nav 是顶栏入口演示，非 O1/Gate PASS；不引入 next/link 保留 build ○ Static 特征**

> 📍 **Gate 2 评审包端到端交付清单节点** = `docs/50-stage2-gate2-review-packet-draft-20260826.md` **§4.4「公开提取演示里程碑」**（per `416` cc 回执；queue_rev 176 落地）：四轨 + 一览条 + 行筛选 + JSON/CSV 下载 + 全站顶栏 site-nav + 预览 URL 的 9 行里程碑表 + 5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」守门清单；链到 `docs/45` §1 + §6.2 + §7。docs/50 §4.4 是 Gate 2 评审包草稿新增节点，不宣布 Gate 2 PASS。

> 🔗 **首页 NBS sample 轨显式 deeplink**（per `420` cc 回执；queue_rev 179 落地；commit `a70a557` + cc_head backfill `bee7950`）：`frontend/app/page.tsx` 公开提取表内「公开提取样本（四轨 demo）」行 → 「公开提取 NBS sample 轨（demo）」行；href `/public-extracts` → `/public-extracts#track-nbs-sample` + `data-testid="home-public-extracts-nbs-sample"`；结构镜像本表第 4 项湖北轨 `#track-hb`（per knife 67 tasking 394）；smoke §12b' 4 针 + `tests/test_nbs_home_deeplink_public_extract.py` 3 cases；不动 4 fixture byte SHA（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）。**首页 NBS deeplink 是顶栏入口之外的首页表内显式锚链演示，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link；不分支 `params.*`**。

> 🔗 **首页 NBS live 候选轨显式 deeplink**（per `424` cc 回执；queue_rev 181 落地；commit `1ced2bd` + cc_head backfill `29467c4`）：`frontend/app/page.tsx` 公开提取表内 NBS sample 行后新增「公开提取 NBS live 候选轨（candidate demo）」行；href `/public-extracts#track-nbs-live` + `data-testid="home-public-extracts-nbs-live"`；描述列「stats.gov.cn / NATIONAL_BULLETIN 60 行（WORM `zxfb` LIVE_CANDIDATE 提取；drift 候选；per 回执 `359` / `362`）」；数据模式标 `LIVE_CANDIDATE · drift 候选 · 非 O1 收口`；与 NBS sample 行同表内并列（镜像本表第 1 项 NBS sample `#track-nbs-sample` 行 + 第 4 项湖北轨 `#track-hb` 行）；smoke §12b'' 4 针 + `tests/test_nbs_live_home_deeplink_public_extract.py` 3 cases；不动 4 fixture byte SHA（与 knife 76 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）。**首页 NBS live deeplink 是顶栏入口之外的首页表内显式锚链演示，drift 候选非 O1 收口；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`**。

> 🔗 **`docs/45` ↔ `docs/50` §4.4 首页 deeplink 互链**（per `430` cc 回执；queue_rev 184 落地；commit `10f26cf` + cc_head backfill `4e385ed` → docs/45/docs/53/docs/50 互链）：`docs/50-stage2-gate2-review-packet-draft-20260826.md` §4.4 里程碑表末尾（docs/45+53 同步登记行后）补登 2 行：(a) **首页 NBS sample 轨显式 deeplink** `#track-nbs-sample`（per 回执 `420` + cc_head backfill `bee7950`）+ (b) **首页 NBS live 候选轨显式 deeplink** `#track-nbs-live`（per 回执 `424` + cc_head backfill `29467c4`）；2 行均显式 demo/candidate 演示、非 O1/Gate PASS；docs/45 文首 queue_rev 184 刷新行 + §1 互链段 + §6.2 +1 行 + §7 pack invariant 链 741 → 743；docs/53 §5 第 11 项（此条）同步登记；链 `docs/45` §1 + §6.2 + §7 + `docs/53` §5（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 2 行）；不引入 `next/link` 保留 build ○ Static；不分支 `params.*`（AGENTS.md 静态路由红线）；4 fixture byte SHA 前 8 锁不漂（双刀锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）。**docs/50 §4.4 新增 2 行 是 Gate 2 评审包草稿里程碑表首页表内显式锚链演示节点，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`；仍不宣布 Gate 2 PASS**。

> 🔗 **首页四轨一览 overview 显式 deeplink**（per `432` cc 回执；queue_rev 185 落地；commit `624f02a` + cc_head backfill `a23e5c8`）：`frontend/app/page.tsx` 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview` + `data-testid="home-public-extracts-overview"`；描述列「stats.gov.cn / sz.gov.cn / tjj.hubei.gov.cn 7 列 × 4 行 overview（轨 / domain / category / 行数 / SHA 前 8 / demo\|candidate 标注 / 分节锚点；数据只读自既有 4 fixture，不重算；per 回执 `383`；smoke §12f 门）」；数据模式标 `OVERVIEW · 四轨 demo · 非 O1`；结构镜像本表第 1 项 NBS sample `#track-nbs-sample` 行 + 第 2 项 NBS live `#track-nbs-live` 行 + 第 4 项湖北轨 `#track-hb` 行；smoke §12b''' 4 针 + `tests/test_overview_home_deeplink_public_extract.py` 3 cases；不动 4 fixture byte SHA（与 knife 76/78/81 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；`pytest` `9 passed in 0.68s`（3 新 + 6 prior home deeplink regression）。**首页四轨一览 overview deeplink 是顶栏入口之外的首页表内显式锚链演示，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`**。

> 🔗 **`docs/45` ↔ `docs/50` §4.4 overview 首页 deeplink 互链**（per `436` cc 回执；queue_rev 187 落地；commit `d4fb7d4` + cc_head backfill `440c7c9` → docs/45/docs/53/docs/50 三向互链）：`docs/50-stage2-gate2-review-packet-draft-20260826.md` §4.4 里程碑表末尾（docs/45+53 同步登记行 + knife 80 NBS deeplink 2 行后）补登 1 行：**首页四轨一览 overview 显式 deeplink** `#overview`（per 回执 `432` + cc_head backfill `a23e5c8`；smoke §12b''' 4 针 + pytest 3 cases `test_overview_home_deeplink_public_extract.py` + 4 fixture byte SHA 前 8 锁不漂，与 knife 76/78/81 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；docs/45 文首 queue_rev 188 刷新行 + §1 互链段 + §6.2 +1 行 + §7 pack invariant 链 750 → 752；docs/53 §5 第 13 项（此条）同步登记；链 docs/45 §1 + §6.2 + §7 + docs/53 §5（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 1 行）；不引入 `next/link` 保留 build ○ Static；不分支 `params.*`（AGENTS.md 静态路由红线）。**docs/50 §4.4 新增 1 行 是 Gate 2 评审包草稿里程碑表首页表内显式锚链演示节点，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`；仍不宣布 Gate 2 PASS**。

> 📍 **首页公开提取入口一览**（per 回执 `410` + `420` + `424` + `432` + `377` cc；queue_rev 188 落地）：
>
> | 入口 | 锚链 | 数据模式 / 用途 | 来源回执 |
> | --- | --- | --- | --- |
> | **全站顶栏 site-nav**（`<nav data-testid="site-nav">`）| `/public-extracts` | 全站任意页 top 常驻链；四轨 demo · 不分支 `params.*` · build ○ Static 22/22 | `410`（smoke §13c 门 6 针 + 5 pytest `test_layout_site_nav_public_extracts.py`） |
> | **首页表内 NBS sample 轨**（`data-testid="home-public-extracts-nbs-sample"`）| `/public-extracts#track-nbs-sample` | `REGISTRY_SAMPLE · demo · 非 live O1`（63 行 / `dea13b8a…`）| `420`（commit `a70a557` + cc_head backfill `bee7950`；smoke §12b' 4 针 + pytest 3 cases `test_nbs_home_deeplink_public_extract.py`）|
> | **首页表内 NBS live 候选轨**（`data-testid="home-public-extracts-nbs-live"`）| `/public-extracts#track-nbs-live` | `LIVE_CANDIDATE · drift 候选 · 非 O1 收口`（60 行 / `0b85212f…`）| `424`（commit `1ced2bd` + cc_head backfill `29467c4`；smoke §12b'' 4 针 + pytest 3 cases `test_nbs_live_home_deeplink_public_extract.py`）|
> | **首页表内四轨一览 overview strip**（`data-testid="home-public-extracts-overview"`）| `/public-extracts#overview` | `OVERVIEW · 四轨 demo · 非 O1`（7 列 × 4 行；数据只读自既有 4 fixture）| `432`（commit `624f02a` + cc_head backfill `a23e5c8`；smoke §12b''' 4 针 + pytest 3 cases `test_overview_home_deeplink_public_extract.py`）|
> | **首页表内湖北轨**（per knife 67 tasking 394）| `/public-extracts#track-hb` | `REGISTRY_SAMPLE · xlsx · live enabled=FALSE 暂缓`（21 行 / `c5cf5abeb4fdf97a…`）| `377`（smoke §12e 门 + pytest 4 轨交叉检查）|
>
> **首页公开提取入口一览是顶栏 site-nav + 首页表内 4 行显式 deeplink 的端到端入口演示汇总，非 O1/Gate PASS；不动 4 fixture 字节；不引入 `next/link` 保留 build ○ Static；不分支 `params.*`；4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`（与 knife 76/78/81/82/84/85 完全一致）**。

> 🔗 **`docs/45` ↔ `docs/50` §4.4 首页公开提取入口一览行 互链**（per `442` cc 回执；queue_rev 190 落地；commit `0021930` + cc_head backfill `6de6c5a` → docs/45/docs/53/docs/50 三向互链）：`docs/50-stage2-gate2-review-packet-draft-20260826.md` §4.4 里程碑表末尾（首页四轨一览 overview 显式 deeplink 行 + knife 87 自身行后）补登 1 行：**首页公开提取入口一览**（顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示汇总；per 回执 `440` + cc_head backfill `6d54d63`；docs/53 §5 5 行 markdown 表（site-nav + 4 首页 deeplink）；smoke §13c + §12b' + §12b'' + §12b''' 合计 18 针 + pytest 3+5+3+3 = 14 cases + 4 fixture byte SHA 前 8 锁不漂，与 knife 76/78/81/82/84/85/86 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；docs/45 文首 queue_rev 191 刷新行 + §1 互链段 + §6.2 +1 行 + §7 pack invariant 链 756 → 758；docs/53 §5 第 15 项（此条）同步登记；链 docs/45 §1 + §6.2 + §7 + docs/53 §5（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 1 行）；不引入 `next/link` 保留 build ○ Static 22/22；不分支 `params.*`（AGENTS.md 静态路由红线）。**docs/50 §4.4 行 199 是 Gate 2 评审包草稿里程碑表顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示节点，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`；仍不宣布 Gate 2 PASS**。

> 📍 **公网预览部署 `https://china.3strategy.cc` 运维登记**（per `446` cc 回执；queue_rev 195 落地）：源站 = SSH **`newvps`**（`207.57.133.177:52134`），路径 **`/opt/china-platform/frontend`**，**宿主机 systemd** `china-platform-frontend` → `127.0.0.1:3000`（非容器），nginx `/etc/nginx/sites-enabled/china.3strategy.cc.conf`（`proxy_pass http://127.0.0.1:3000`），CF 橙云 A → `207.57.133.177`；**勿用 `hk` / `103.59.103.85`**（其上无本站路径；回执 `446` §分工与约束有误查记录）。

> 🔧 **redeploy 命令链**（per 回执 `446` §分工：ops 侧在 newvps 执行，CC 只做公网 HTTP 验收）：`ssh newvps` → `cd /opt/china-platform/frontend`（先 rsync 或 git pull 同步 repo 至宿主路径）→ `npm ci` → `NEXT_PUBLIC_USE_MOCK=true npm run build` → `systemctl restart china-platform-frontend`（SSH 易超时用 `nohup` 包裹长命令）。公网验收基线（per 回执 `446`，2026-08-27 实测）：首页 4/4 deeplink（`#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb`，含 3 个 `home-public-extracts-*` testId）+ `/public-extracts` HTTP 200（105,893 bytes；5 锚点 id + `site-nav-public-extracts` testId + 4 `track-filter-*` testId）。**预览部署登记是运维信息补登，非 O1/Gate PASS；preview 容器化择机另刀（本刀不做 Docker）；不换服务器；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76/78/81/82/84/85/86/87 锁值完全一致）；不改代码**。

> 🔗 **`docs/45` ↔ `docs/50` §4.4 公网预览 redeploy 运维行 互链**（per `450` cc 回执；queue_rev 197 落地；commit `c7a4c5d` + cc_head backfill `eaebe43`；**docs/53 §5 第 17 项（此条）**，标签补登 per 回执 `462`）：docs/50 §4.4 里程碑表行 200 补登「公网预览 redeploy 运维」里程碑（本节第 16 项 📍 运维登记 + 🔧 redeploy 命令链为其交付列登记源，per 回执 `448` + `69090e7`；公网验收基线 per 回执 `446`）；docs/45 文首 queue_rev 199 刷新行 + §1 + §6.2 + §7 互链；链 docs/45 §1 + §6.2 + §7 + docs/53 §5 **第 17 项**（此条；第 16 项保留给 📍 + 🔧 redeploy 登记；双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 行 200）。本第 17 项互链已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 17 项公网预览 redeploy 运维行互链」行补登（per 回执 `468`）。**非 O1/Gate PASS；不换服务器；不动 4 fixture 字节**。

> 🔗 **`docs/45` ↔ `docs/50` §4.4 公网预览 URL 块 互链**（per `456` cc 回执；queue_rev 203 落地）：docs/50 §4.4 预览 URL 块补登「**公网预览**」段——`https://china.3strategy.cc/public-extracts`（HTTP 200：四轨 + 一览条 + 行筛选 + JSON/CSV + site-nav）+ 首页 `https://china.3strategy.cc/` 4 deeplink（`#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb`；per 回执 `454` + cc_head backfill `1e9b159`；段头链本节第 16 项 + docs/50 §4.4 行 200 + 回执 `446`）；「本地预览」localhost 段逐字保留；⚠ 守门清单 +1 条（公网与本地同构 demo/candidate build，非 O1/Gate PASS）；docs/45 文首 queue_rev 202 刷新行 + §1 + §6.2 + §7 互链；链 docs/45 §1 + §6.2 + §7 + docs/53 §5 第 18 项（此条，双向）。本第 18 项互链已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 18 项公网预览 URL 块互链」行补登（per 回执 `466`）。**非 O1/Gate PASS；不改代码；不换服务器；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）**。

> 🔗 **docs/53 §5 第 19 项（此条）· `docs/45` ↔ §5 🌐 公网预览首行 互链登记**（per `460` cc 回执；queue_rev 211 落地）：🌐 公网预览首行（回执 `458` 交付）与 `docs/45` 文首 queue_rev 刷新行 + §1 + §6.2 + §7 的双向对账登记；🌐 正文仅补互链指向句「`docs/45` 侧互链登记见第 19 项（per 回执 `464`）+ `docs/45` §1」，URL/deeplink 正文原样未动；链本节第 16 项（📍+🔧 redeploy 登记）/ 第 17 项（per-450 运维行互链，标签补登 per `462`）/ 第 18 项（URL 块互链）+ 回执 `446`（公网验收基线）/ `454`（docs/50 §4.4 公网预览段）；docs/50 §4.4 公网预览段头可选一句同步。本第 19 项互链已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 19 项 🌐 公网预览首行互链」行补登（per 回执 `470`）。**非 O1/Gate PASS；不改代码；不换服务器；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）**。

> 🔗 **docs/53 §5 第 20 项（此条）· `docs/50` §4.4 第 16–19 项公网预览互链里程碑弧收口**（per `472` cc 回执；queue_rev 219 落地）：登记 `docs/50` §4.4 公网预览互链里程碑四节点弧——第 16 项 = 📍 运维登记 + 🔧 redeploy 命令链（per 回执 `448` + `69090e7`）；第 17 项 = redeploy 运维行互链（互链 per `452`；标签补登 per `462`；docs/50 里程碑行补登 per `468`）；第 18 项 = URL 块互链（per `454` 落地 / `456` 互链；docs/50 里程碑行补登 per `466`）；第 19 项 = 🌐 公网预览首行互链（per `458` 首行 / `460`+`464` 互链；docs/50 里程碑行补登 per `470`）；链行 200 + 回执 `446`（公网验收基线）/ `454`（公网段）；第 16–19 项既有正文原样未动，本条仅并列弧收口。本第 20 项弧收口已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 20 项 16–19 公网预览互链弧收口」行补登（per 回执 `474`）；`docs/50` §4.4 intro ⚠ 收据链尾已续接至 `→ 474`（per 回执 `476`）。**非 O1/Gate PASS；不改代码；不换服务器；不动 16–19 既有正文；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）**。

> 🔗 **docs/53 §5 第 21 项（此条）· O1 公开源 B 路下一试点轴 = `stats.gov.cn` / `NATIONAL_BULLETIN`（HTML）**（per `480` cc 回执；queue_rev 227 落地）：登记 O1 自动获取 B 路下一试点轴 = **`stats.gov.cn` / `NATIONAL_BULLETIN` HTML 月度发布**（per docs/52 §3 #1：URL 格式稳定、HTML 可直接 `curl`、无需 OCR；per `478` docs/45 主路径指针 = docs/52 官方公开源自动获取 B 路；per docs/52 §5 A/B 两路并存、用户投递仍可用但非唯一）；工具与入口见本手册 §1（`scripts/auto_ingest_public_source.py` single-file connector），connector 四种运行模式见本手册 §2（§2.1 dry-run 无网络 / §2.2 local-sample 入库无网络 / §2.3 live 探测 网络+WORM / §2.4 一键刷新 LIVE_CANDIDATE 候选双写）；B 路流水线六步 discover→download→sha256→archive→extract→observation 守门 per docs/52 §4；遇登录/验证码/付费墙/技术限制 → 停止并报告用户、不绕过、不静默失败 per docs/52 §6 AUTH 升级协议；live drift 不自动改 registry、候选轨等用户裁定；链回执 `446`（公网验收基线）/ `454`（公网段）；第 16–20 项既有正文原样未动，本条为并列登记节点。本第 21 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 21 项 O1 B 路试点轴登记」行补登（per 回执 `482`）。docs/52 文首 O1/WAITING_FILE 语义已对齐（per 回执 `486`，校准 per `484`）：`WAITING_FILE` 仅保留为 intake 出口码 / mart 真 SHA 未入仓的技术状态语义，非「等用户投喂才可继续」，主路径 = 本 B 路（**O1 仍 OPEN**）。**O1 仍 OPEN——试点轴登记只登记路径选择：不实装新爬取代码、不启用 Hubei live、不等用户投喂文件、不宣布任何 O1/Gate 收口**。**非 O1/Gate PASS；不改代码；不换服务器；不动 16–20 既有正文；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）**。

> 🔗 **docs/53 §5 第 22 项（此条）· O1 B 路 NATIONAL_BULLETIN connector dry-run 证据登记**（per `492` cc 回执；queue_rev 239 落地）：`scripts/auto_ingest_public_source.py --dry-run --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN` 已实跑——exit code **0**，stdout 关键句「OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN · primary_url: https://www.stats.gov.cn/sj/zxfb/ · auth_note: 公开；无需授权 · expected SHA: dea13b8a4ff116ca…」+「OK dry-run; no network, no archive, no lineage writes.」（dry-run 默认模式：无网络、无 DB 写、不 --live、不改 registry）。本项只登记 dry-run 运行证据，验证 connector 入口与 registry 过滤可执行，**非 O1 收口**：不 `--live`/`--confirm-live`、不动 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）、不等用户投喂文件；**O1 仍 OPEN——dry-run 证据不构成任何 O1/Gate 收口；非 O1/Gate PASS；不改代码；不换服务器；不动第 21 项既有正文**。本第 22 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 22 项 O1 B 路 dry-run 证据登记」行补登（per 回执 `496`）。

> 🔗 **第 23 项（此条）· O1 B 路 NATIONAL_BULLETIN `--from-local-sample` 证据登记（显式 demo/sample）**（per `494` cc 回执；queue_rev 241 落地）：`scripts/auto_ingest_public_source.py --from-local-sample --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-local-sample-lineage.jsonl` 已实跑——exit code **0**，**无网络**（读 registry `local_sample_path` 本地样本 `spikes/01-national-yearbook/sample.html`，SHA 与 registry 记录一致 `dea13b8a4ff116ca…`），stdout 关键句「OK local-sample pilot matched: stats.gov.cn / NATIONAL_BULLETIN (enabled=TRUE)」+「OK archived / OK extract JSON / OK lineage / OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure)」；lineage 落盘路径 = 回执 `494` 粘贴的 `--confirm-live` 值，`intake_status=REGISTRY_SAMPLE_INTAKED`、**`is_demo=true`、sample ≠ live closure**。运行副作用如实披露：本次运行重写了 tracked `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` 的 `extracted_at` 时间戳字段（唯一 diff，内容数据零变化；该文件非 4 fixture 锁对象），本刀已恢复其 HEAD 字节以避免易变时间戳字节抖动；lineage JSONL 与归档副本留作未跟踪运行产物（drift-report 房规先例）。本项只登记 local-sample 摄取链路可执行证据，**非真 SHA 收口、非 O1 收口**：不 `--live`、不改 registry `enabled`、不动 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）、不等用户投喂文件；**O1 仍 OPEN——local-sample 显式 demo 运行不构成任何 O1/Gate 收口；非 O1/Gate PASS；不改代码；不换服务器；不动第 21/22 项既有正文**。本第 23 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 23 项 O1 B 路 local-sample 证据登记」行补登（per 回执 `498`）。

> 🔗 **第 24 项（此条）· O1 B 路 NATIONAL_BULLETIN 证据弧收口（第 21–23 项）**（per `500` cc 回执；queue_rev 247 落地）：并列登记本手册 §5 O1 公开源 B 路三节点证据弧——第 21 项 = 🧭 试点轴登记（`stats.gov.cn` / `NATIONAL_BULLETIN` HTML 月度发布；per 回执 `480` 落地 + docs/50 §4.4 第 21 项里程碑行补登 per `482`）；第 22 项 = dry-run 证据登记（connector 入口可执行性，exit code **0** + 无网络 + 无 DB 写；per `492` + 行补登 per `496`）；第 23 项 = local-sample 证据登记（registry 样本摄取链路可执行性，exit code **0** + 无网络 + `intake_status=REGISTRY_SAMPLE_INTAKED`、**`is_demo=true`、sample ≠ live closure 非真 SHA 收口**；per `494` + 行补登 per `498`）；链 docs/52 §3 #1（试点轴判定：URL 格式稳定、HTML 可直接 curl、无需 OCR）+ `478`（docs/45 O1 主路径指针登记）；docs/50 §4.4 intro ⚠ 收据链尾已续接至 `→ 498`（per 回执 `500` 本刀可选句）。第 21/22/23 项既有正文原样未动，本条仅并列弧收口。本弧收口只做文档节点汇总，不新增任何运行或证据实体，**非真 SHA 收口、非 O1 收口**：不 `--live`、不改 registry、不改代码、不等用户投喂文件、不动第 21–23 项既有正文、不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；**O1 仍 OPEN——弧收口不构成任何 O1/Gate 收口；非 O1/Gate PASS；不换服务器**。本第 24 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 24 项 O1 B 路 21–23 弧收口」行补登（per 回执 `502`）。docs/50 §4.4 intro ⚠ 收据链尾已同步续接至 `→ 502`（per 回执 `504`）。

> 🔗 **第 25 项（此条）· O1 B 路 NATIONAL_BULLETIN 下一探测轴 = live-candidate 探测登记（本条只登记、不运行）**（per `506` cc 回执；queue_rev 253 落地）：登记 O1 B 路下一探测轴 = connector 模式 **`--live --confirm-live`** live-candidate 探测——按 docs/52 §4 六步流水线（discover→download→sha256→archive→extract→observation 守门）+ docs/52 §6 AUTH 升级协议（遇 AUTH 阻停报告不绕过，不静默失败）；探测产物若产生则走 LIVE_CANDIDATE 候选轨（候选轨等用户裁定，live drift 不自动改 registry `enabled`，per docs/53 §2 四种运行模式语义一致）；**本刀只登记不运行**：未实跑 `--live`、未改 registry `enabled`、无网络副作用；链 21–24 弧收口与互链 per `500`（docs/53 §5 第 24 项）/`502`（docs/50 §4.4 第 24 项行）/`504`（docs/50 §4.4 intro 链尾 `→ 502`）。本项只做下一轴路径文档登记，不新增任何运行或证据实体，**非真 SHA 收口、非 O1 收口**：不实跑任何 connector、不改代码、不等用户投喂文件、不动第 21–24 项既有正文、不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；**O1 仍 OPEN——live-candidate 探测登记不构成任何 O1/Gate 收口；非 O1/Gate PASS；不换服务器**。本第 25 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 25 项 O1 B 路 live-candidate 下一探测轴登记」行补登（per 回执 `508`）。

> 🔗 **第 26 项（此条）· O1 B 路 NATIONAL_BULLETIN live-candidate 探测证据登记（per `510` cc 回执；queue_rev 257 落地）**：`scripts/auto_ingest_public_source.py --live --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl` 已实跑（**有网络**，per `510` 任务书显式授权 `--live`+`--confirm-live`）——exit code **0**：OK pilot matched（stats.gov.cn / NATIONAL_BULLETIN · primary_url `https://www.stats.gov.cn/sj/zxfb/` · auth_note 公开；无需授权）→ OK deeplink discovered `https://www.stats.gov.cn/sj/zxfb/202608/t20260827_1965129.html` → OK downloaded **180165 bytes**，sha256=`a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` ≠ registry expected `dea13b8a4ff116ca…` → SHA drift 非静默处理：drift 报告落盘 `reviews/.../20260827T122022Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md` + lineage JSONL 落盘 `reviews/.../20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl`（`intake_status=CANDIDATE_AUTO`、**`is_demo=true` 绝不伪装真数据**、`source_agency=国家统计局`、`intake_ts` ISO-8601）。⚠ 如实披露两点：(1) **WORM 幂等未覆盖**——archive() 目标路径 `data/public_archives/2026-08/stats.gov.cn/zxfb` 已存在（tracked clean，sha256 前 8 位 `0b85212f`，mtime 早于本刀），本刀实测下载字节未持久化至磁盘，输出消息中的归档路径指向既有文件；(2) 自动生成的 drift 报告含「WORM 归档实测字节：已写入」模板句，与本条磁盘实测不符，本项登记以磁盘为准、模板措辞修正留后续用户裁定。registry `enabled` 与 `file_hash_sha256` 均未改（connector 不自动改 registry）；无 headless、未绕任何 AUTH/验证码（公开直连成功）；候选轨处置等用户裁定二选一（(a) 更新 registry 哈希认定源站换版 / (b) 改用稳定归档 URL）；两件运行产物按房规保持未跟踪、不入 manifest。本项只登记探测证据，**非真 SHA 收口、非 O1 收口**：不改代码、不动第 21–25 项既有正文、不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，实测 disk == HEAD == 锁值）；**O1 仍 OPEN——live-candidate 探测证据（CANDIDATE_AUTO）不构成任何 O1/Gate 收口；非 O1/Gate PASS；不换服务器**。本第 26 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 26 项 O1 B 路 NATIONAL_BULLETIN live-candidate 探测证据登记」行补登（per 回执 `512`）。§4.4 intro ⚠ 收据链尾亦已续接至 `→ 512`（per `514`；O1 B 路 21–26 弧 + live-probe，链尾以 `512` 收口）。

> 🔗 **第 27 项（此条）· O1 B 路 NATIONAL_BULLETIN 扩展证据弧收口（第 21–26 项）**（per `516` cc 回执；queue_rev 263 落地）：并列登记本手册 §5 O1 公开源 B 路扩展证据弧六节点——第 21 项 = 🧭 试点轴登记（`stats.gov.cn` / `NATIONAL_BULLETIN` HTML 月度发布；per 回执 `480` 落地 + docs/50 §4.4 第 21 项里程碑行补登 per `482`）；第 22 项 = dry-run 证据登记（connector 入口可执行性，exit code **0** + 无网络 + 无 DB 写；per `492` + 行补登 per `496`）；第 23 项 = local-sample 证据登记（registry 样本摄取链路可执行性，exit code **0** + 无网络 + `intake_status=REGISTRY_SAMPLE_INTAKED`、**`is_demo=true`、sample ≠ live closure 非真 SHA 收口**；per `494` + 行补登 per `498`）；第 24 项 = 21–23 弧收口登记（三节点并列文档汇总；per `500` + 行补登 per `502` + intro 链尾续接 per `504`）；第 25 项 = live-candidate 下一探测轴登记（**只登记不运行**，connector 模式 `--live --confirm-live` 路径文档化；per `506` + 行补登 per `508`）；第 26 项 = live-candidate 探测实跑证据登记（任务书显式授权 `--live --confirm-live`、有网络、exit code **0**、download 180165 B sha256 `a7e4029d…` ≠ registry expected `dea13b8a…` → SHA drift 非静默处理 → **CANDIDATE_AUTO 候选轨（`is_demo=true` 绝不伪装真数据）+ WORM 幂等未覆盖如实披露**；候选轨处置等用户裁定二选一；per `510` + 行补登 per `512`）；链 docs/52 §3 #1（试点轴判定：URL 格式稳定、HTML 可直接 curl、无需 OCR）+ `478`（docs/45 O1 主路径指针登记）+ docs/50 §4.4 intro ⚠ 收据链尾 `→ 512`（per `514`，链尾以 `512` 收口）。第 21–26 项既有正文原样未动，本条仅并列弧收口。本弧收口只做文档节点汇总，不新增任何运行或证据实体，**非真 SHA 收口、非 O1 收口**：SHA drift 候选轨等用户裁定、不 `--live`、不改 registry `enabled` 与哈希、不改代码、不等用户投喂文件、不动第 21–26 项既有正文、不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；**O1 仍 OPEN——扩展弧收口不构成任何 O1/Gate 收口；非 O1/Gate PASS；不换服务器**。本第 27 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 27 项 O1 B 路 NATIONAL_BULLETIN 扩展证据弧收口（第 21–26 项）」行补登（per 回执 `518`）。

> 🔗 **第 28 项（此条）· `510` live-probe SHA drift 候选轨处置分叉登记（本条只登记、不裁定、不改 registry）**（per `520` cc 回执；queue_rev 267 落地）：登记 `510` live-candidate 探测实测 SHA drift 的候选轨处置分叉——实测 download 180165 B sha256=`a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` ≠ registry expected=`dea13b8a4ff116ca…`（stats.gov.cn / NATIONAL_BULLETIN；证据源 = 本手册 §5 第 26 项，per 回执 `510` 落地 + 行补登 per `512`）；分叉二选一：**(a) 更新 registry.csv `file_hash_sha256` 为实测值**（认定源站换版）或 **(b) 改用稳定归档 URL**（避开源站页面滚动漂移）——两选项均须**用户裁定后另起独立刀任务执行**，connector 不自动改 registry（per docs/52 §4 六步流水线守门语义一致）；本条不执行任何其一、不替用户选分叉；registry `enabled` 与 `file_hash_sha256` 本刀均未改。本条只做分叉登记文档节点，不新增任何运行或证据实体，**非真 SHA 收口、非 O1 收口**：drift ≠ 收口（CANDIDATE_AUTO 候选 `is_demo=true` 绝不伪装真数据）、不改代码、不动第 21–27 项既有正文、不等用户投喂文件、不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）；**O1 仍 OPEN——分叉登记不构成任何 O1/Gate 收口；非 O1/Gate PASS；不换服务器**。本第 28 项已同步作为 `docs/50` §4.4 里程碑表「docs/53 §5 第 28 项 SHA drift 候选轨处置分叉登记」行补登（per 回执 `522`）。docs/52 文首互链补登 per `524`。

> 🔗 **第 29 项（此条）· O1 B 路 NATIONAL_BULLETIN 扩展证据弧收口（第 21–28 项）**（per `530` cc 回执；queue_rev 277 落地）：八节点并列汇总——第 21 项 🧭 试点轴登记（per `480`/`482`）；第 22 项 dry-run 证据登记（exit code **0** 无网络无 DB 写；per `492`/`496`）；第 23 项 local-sample 证据登记（exit code **0** 无网络、`intake_status=REGISTRY_SAMPLE_INTAKED`、`is_demo=true` sample ≠ live closure；per `494`/`498`）；第 24 项 21–23 弧收口（三节点并列文档汇总；per `500`/`502`/`504`）；第 25 项 live-candidate 下轴只登记不运行（per `506`/`508`）；第 26 项 live-probe 实跑证据（任务书显式授权 `--live --confirm-live`、有网络、exit code **0**、download 180165 B sha256 `a7e4029d…` ≠ expected `dea13b8a…` → SHA drift 非静默处理 → CANDIDATE_AUTO 候选轨 + WORM 幂等未覆盖如实披露；per `510`/`512`）；第 27 项扩展弧收口 21–26（六节点并列；per `516`/`518`）；第 28 项 SHA drift 候选轨处置分叉登记（**(a) 更新 registry `file_hash_sha256` / (b) 改稳定归档 URL 二选一仍等用户裁定**、connector 不自动改 registry；per `520` 登记 / `522` docs/50 行补登 / `524` docs/52 文首互链 / `526` 尾注回指 / `528` docs/50 行内互链）；链 = docs/52 §3 #1 + `478` 主路径指针 + intro ⚠ 收据链尾 `→ 512` per `514`。本条为文档节点汇总，第 21–28 项既有正文原样未动，**非真 SHA 收口、非 O1 收口**：drift ≠ 收口（CANDIDATE_AUTO 候选 `is_demo=true` 绝不伪装真数据）、不改代码、不等用户投喂文件、不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）；**O1 仍 OPEN——扩展弧收口不构成任何 O1/Gate 收口；非 O1/Gate PASS；不换服务器**。docs/50 里程碑行补登 per `532`。SHA drift 处置 (a) 裁定已执行 per `538`：registry NATIONAL_BULLETIN 行 `file_hash_sha256` → `a7e4029d…` + `file_size_bytes` → 180165（用户 2026-08-27 裁定 (a)——认定源站换版，per 回执 `510` live-probe 实测）；live 复验由用户/Cursor 本机完成 exit 0、download 180165 B、sha256 与 expected 匹配（per `538-stage2-cursor-local-live-reverify-and-deviation-accept-20260827` §1 + D1–D5 偏差交付接受）；registry 更新 ≠ O1 收口，O1 仍 OPEN。

冒烟：`python3 frontend/smoke-check.py`（§12c 门含候选 fixture 在位 + 分轨交叉检查；§12d 门含深圳 fixture 在位 + 三轨交叉检查；§12e 门含湖北 fixture 在位 + 四轨交叉检查；**§12f 门含 overview strip 在位 + 4 锚点 id + 4 锚链 href + demo|candidate 标注 + 守门 13 针**；**§12h 门含四轨行筛选 input（4 testId）+ 客户端包含匹配 + 非权威库检索守门**；**§13c 门含 `site-nav` 容器 + `/public-extracts` 链 + 链 testId + 四轨 demo + 非 O1 + 不宣布 Gate PASS + 不分支 `params.*`**）。

## 6. 红线（运维时同样生效）

- ❌ 不 headless 自动爬取；live 必须显式 `--confirm-live`
- ❌ drift 不自动改 registry、不自动 O1 收口
- ❌ 不覆盖 sample JSON / sample fixture / registry sample 哈希
- ❌ 不宣称 Gate 1/2 或 O1 PASS
- ❌ OCR 阈值 / `gate_thresholds.json` 不动

## 7. 相关测试

```bash
python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q   # 92 cases
python3 frontend/smoke-check.py
```

（全量 `pytest tests/` 需本地 Postgres；日常回归以上面两文件为准。）

— 完 —
