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
7. **各 overview 下载格 = JSON / CSV 双链**（列头「下载 JSON / CSV」；4 行同格第二链 `<a href="/public-extracts/{name}.csv" download>⬇ {name}.csv</a>`；CSV 产物 `frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv`（63 / 60 / 71 / 21 数据行；列序=fixture 首行键序不重命名；UTF-8 无 BOM / `\n` / QUOTE_MINIMAL；生成器 `scripts/gen_public_extracts_csv.py` `render_csv_bytes` 纯函数可字节重渲）；JSON 4 链不破坏；页脚「JSON / CSV 下载皆为 fixture 快照确定性导出 (demo/candidate), 非权威库」；**CSV 是 fixture 快照确定性导出, 非权威库；build 仍 ○ Static 公共静态产物**；per 回执 `404`；smoke §12i 门）

冒烟：`python3 frontend/smoke-check.py`（§12c 门含候选 fixture 在位 + 分轨交叉检查；§12d 门含深圳 fixture 在位 + 三轨交叉检查；§12e 门含湖北 fixture 在位 + 四轨交叉检查；§12f 门含 overview strip 在位 + 4 锚点 id + 4 锚链 href + demo|candidate 标注 + 守门 13 针；§12h 门含四轨行筛选 input（4 testId）+ 客户端包含匹配 + 非权威库检索守门；**§12i 门含 4 CSV 在位非空 + 4 href + 4 download attr + 列头含 `下载 JSON / CSV` + JSON 4 链不回归 + 非权威库守门 + 无 `text/csv` 服务端动态导出**）。

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
