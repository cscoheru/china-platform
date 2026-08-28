# 579 — 任务书：O3 决策备忘 + 全量 4 failed 继承登记（合刀 · 零网络 · docs-only）

- 编号：`579-stage2-o3-memo-inherited-failures-docs-bundle-tasking-20260828`
- 前置：`578-stage0-architect-s577-o1-close-s21full-audit-PASS-20260828`（577 审计 PASS；本审计文件随本刀交付 commit 入库）
- 下发：CC 架构师终端 → 执行端（经 `00-EXEC-QUEUE.md`，PENDING → ACK → DELIVERED）
- 日期：2026-08-28
- 验证深度：**全零网络 · docs-only**（本刀零代码/零 SQL/零 pytest 变更）

---

## §NOW

**(A) docs/53 §5 新增第 41 项**（blockquote，插第 40 项后）——O3 决策备忘登记（per `docs/49` §4/§5.2 + `578` 审计后续节）：

内容必须写明：
1. 三选项呈现（per docs/49 步骤 4）：(i) **paddle-ocr**（开源·本地·CPU/GPU·中文精度高·离线零网络依赖 — docs/49 推荐）；(ii) **tesseract**（开源·本地·CPU）；(iii) **cloud OCR**（百度/腾讯/Azure；**默认禁止**，须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定）
2. 实装依赖链（docs/49 §5.2）：5.2.1 引擎选型（用户裁定）→ 5.2.2 `validate_ocr_input()` API → 5.2.3 `source_document.doc_kind='OCR_SCAN'` schema migration → 5.2.4 本地依赖/Dockerfile layer → 5.2.5 端到端 pytest → 5.2.6 真实 PDF（用户 `--confirm-o3=PATH`，非爬源）
3. O3 收口标志事件（docs/45 §3）：`is_demo='false'` 翻转（lineage SHA ≠ `'0'*64` + `demo_reason=NULL` + `source_file_url="(OCR_SCAN_FROM_UPLOAD:…)"`）
4. **裁定状态 = 已裁定（2026-08-28 用户裁定：选项 A = paddle-ocr，架构师补注于签发后）**——第 41 项照录裁定值、选项全文与裁定日期；docs/45 §3 O3 行尾注同步写明「引擎已裁定 paddle-ocr」；**裁定 ≠ O3 收口 ≠ Gate 2 PASS**：实装依赖链 5.2.2–5.2.6 未完成前 **O3 仍 OPEN**（仅 5.2.1 由本裁定关闭）
5. **不宣布 Gate 2 / O3 PASS**；本项是 Gate 2 评审 OPEN 必带清单的决策就绪登记，非收口

**(B) docs/53 §5 新增第 42 项**（blockquote，插第 41 项后）——全量 4 failed 继承问题登记（per `577` 回执证据段 + `578` 审计「继承问题登记」节）：
1. 事实：`577` 刀全量套件 4 failed / 556 passed / 8 skipped；`578` 审计 git 实证**全部先于本刀存在于 HEAD `d95d21e` 提交态**（非 577 引入）
2. 归因三条：① `spikes/01-national-yearbook/sample.html` 磁盘 SHA（dea13b8a…）≠ registry NATIONAL_BULLETIN 行 SHA（`a7e4029d…`，`538` 裁定值）→ s52 回归 + fixture provenance 2 例失败（**spike 样例与权威源文件本非同一对象，registry.csv 红线不可动**）；② `test_cleanliness` data/ 目录白名单（`seed_archives/seeds/public_extracts/public_archives` 皆历史遗留）；③ h2 嵌套复跑 rc=1（内含①②）
3. 处置方向（**本刀只登记不修码**，修法留后续刀按红线路径裁定）：测试断言口径改为仅对 `public_extracts/` 目录强制 provenance（spike 样例标注非 registry 对象）/ 或 spike 样例补注免责标注；data/ 白名单补登为房规
4. 登记 ≠ 修复：该 4 failed 为**存量既有状态**，不因登记新增阻塞；Gate 2 评审包 OPEN 必带清单照录

**(C) docs/50 同步**：
- §4.4 里程碑表 +2 行（第 41 项 O3 决策备忘 · WAITING_RULING；第 42 项 继承 4 failed 登记）+ intro 收据链尾 `→ 577` 续接 `→ 579`
- §5 OPEN 必带清单照录第 42 项（继承 4 failed）+ 第 41 项（O3 引擎 WAITING_RULING）

**(D) docs/45 同步**（五处模式，沿用 570/572/574/577 先例）：
- 文首 +1 刷新行（`579` 任务书引用 + 治理模型第三刀注）
- §1 +1 段（O3 决策备忘 + 继承登记）
- §3 O3 行尾注 append（备忘已交 · WAITING_RULING · 仍 OPEN）
- §6.2 行尾注 append（per `579`）
- §7 链头 `907 == 907 == 907`（按 bump 实际值）+ knife 577 demote
- 所有「O1 仍 OPEN」「O3 仍 OPEN」计数**非减**

**(E) manifest bump**：`scripts/_knife579_manifest_bump.py`，NEW artifacts **+3**（枚举即权威，逐项核对）：
本 bump 脚本（`spike_helper`）+ `578` 审计文件（`documentation`）+ `579` 回执（`documentation`）→ **904 → 907**；断言 `sum(role_count) == artifact_count == len(artifacts) == 907`；docs/45/53 为 SHA REFRESH 不增计数；docs/50 房规 SKIP（镜像 574/577 先例）；**任务书按先例不入 manifest**；`00-EXEC-QUEUE.md` 已在 manifest（本刀 ACK/DELIVERED 改动为 SHA REFRESH 不增计数）

**(F) 零网络核验**（命令 + 输出原样粘贴进回执）：
```bash
grep -o "O1 仍 OPEN" docs/45-*.md | wc -l        # ≥166
grep -o "O3 仍 OPEN" docs/45-*.md | wc -l        # 非减（基线实测后记录）
grep -c "第 41 项（此条）" docs/53-*.md            # 1
grep -c "第 42 项（此条）" docs/53-*.md            # 1
grep -c "907 == 907 == 907" docs/45-*.md          # 1（stale 904 = 0）
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q   # 25 passed / exit 0（零改动防回归）
python3 frontend/smoke-check.py                                # exit 0（零改动防回归）
shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
                                                            # e30ee811 9232efdb 937255a5 9056001c
python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
                                                            # 907 907 907
```

**(G) 回执**：`reviews/stage0-gate0-rework-2026-08-23/579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828.md`
- 文件名含 `-cc-`；合刀单槽单回执，仅 `579`
- 交付 commit 含：docs/53、docs/50、docs/45、bump 脚本、**`578` 审计文件（只读随刀）**、本任务书（只读随刀）、回执、`00-EXEC-QUEUE.md`（ACK 填行 + status→DELIVERED）
- cc_head backfill 单独 commit（勿 amend）；`git push origin HEAD` → `git push github HEAD` 严格顺序

## 红线（零豁免）

- ❌ 本刀 **docs-only**：零代码 / 零 SQL / 零 schema / 零 pytest 变更 / 零 dbt 实跑
- ❌ 不宣布 Gate 0/1/2 PASS；**O3 决策备忘 ≠ O3 收口 ≠ Gate 2 PASS**；WAITING_RULING 期间 O3 仍 OPEN；不擅自替用户选引擎
- ❌ 不动 registry.csv / gate_thresholds.json / 00-CC-CURRENT.md / 4 fixture 字节 / 既有测试与 mart SQL / migration 001–013
- ❌ 4 failed **只登记不修码**（修法与测试口径改动留后续刀）
- ❌ 无 --force / PAT / 公网 redeploy / 网络爬取；既有 OPEN 行零删减（计数非减）
- ✅ manifest 904 → 907 不变量（+3 枚举即权威，逐项核对防 ⚠ 复发）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 完成后

双推完成即停，回报 cc_head；架构师出 `580` 号位审计。O3 引擎裁定与 `--confirm-o3=PATH` 真实 PDF 均为用户保留动作，实装刀（`58X`）待裁定后签发。
