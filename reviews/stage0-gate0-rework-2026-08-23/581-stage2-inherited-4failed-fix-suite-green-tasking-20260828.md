# 581 — 任务书：继承 4 failed 修复刀（恢复全量套件全绿 · 三处断言口径修正）

- 编号：`581-stage2-inherited-4failed-fix-suite-green-tasking-20260828`
- 前置：`580-stage0-architect-s579-o3-memo-inherited-audit-PASS-20260828`（579 审计 PASS；本审计文件随本刀交付 commit 入库）
- 下发：CC 架构师终端 → 执行端（经 `00-EXEC-QUEUE.md`，PENDING → ACK → DELIVERED）
- 日期：2026-08-28
- 验证深度：**零网络 · 测试口径修正刀**（零生产代码/零 SQL/零脚本变更；全量 pytest 为本刀核心证据）

---

## §NOW

**背景（per docs/53 第 42 项登记 + `580` 审计「继承问题复核」节）**：全量 4 failed 根因 = ① `spikes/01-national-yearbook/sample.html` 磁盘/HEAD SHA `dea13b8a…`（fixture 快照的真实提取源）≠ registry `NATIONAL_BULLETIN` 行 `file_hash_sha256` `a7e4029d…`（`538` 裁定值，远程权威对象）——**两个不同对象的两个真实 SHA 被既有断言错绑**；ingest 脚本 SHA 硬闸（rc=8）行为正确。② data/ 白名单缺 4 个历史合法目录。③ h2 内含①②。

**(A) `tests/test_public_extract_frontend_fixture.py` — provenance 断言重定锚**（已入 manifest → REFRESH）：
- `test_fixture_provenance_sha_matches_registry` 改断言：`fixture_json["source_sha256"] == sha256(spikes/01-national-yearbook/sample.html 实字节)`（活锚 = fixture 真实提取源）
- docstring 写明三段事实：registry `a7e4029d`（`538` 裁定值）= 远程权威公告对象契约（不变）；fixture = 从 spike 样例提取的演示快照（快照链自洽）；原断言把两对象错绑为同一 SHA（per docs/53 第 42 项 + `580` 审计定性）
- 本文件其余测试零改动（63 行/路径匹配/键形/页面导入/live candidate/SZ 镜像今天全绿）

**(B) `tests/test_auto_ingest_public_source_s52.py` — 回归测试改双路径**（**未入 manifest → bump ADD +1**）：
- `test_regression_real_extracts_not_clobbered_by_pytest` 拆双路径：sz.gov.cn pilot 保持 rc=0 + tmp 重定向断言（成功路径零改动）；stats.gov.cn pilot 改为**预期 rc=8**（per `346` 硬失败语义）+ stderr 含 `SHA mismatch; refusing intake` + 该 pilot 在 tmp roots 零落盘（SHA 闸正确拒入且重定向仍生效）
- 测试名/docstring 同步改为双路径回归语义（成功路径 + SHA 闸拒入路径）
- **`scripts/auto_ingest_public_source.py` 零改动**——SHA 闸（L1278 一带）是防篡改机制，零弱化；rc=8 从「事故」转为「被测试钉死的预期行为」
- 改后必须整文件实跑（其余 local-sample 用例今天全绿，改动不得波及）

**(C) `tests/test_cleanliness.py` — data/ 白名单房规化**（已入 manifest → REFRESH）：
- `allowed_top_level` 扩为 `{"extracts", "processed", "raw", "public_archives", "public_extracts", "seed_archives", "seeds", ".gitkeep"}`
- docstring 逐目录注记：`seeds/` = S2.1 demo seed JSON（manifest 在册）；`public_extracts/` + `public_archives/` = 公开提取 WORM 链目录；`seed_archives/` = seed 归档链
- 定性：**存量合法目录的登记**（皆为 manifest/data contract 体系内既有物），非放宽

**(D) h2 嵌套复跑**：①②修复后自愈，不单独改码；全量证据覆盖。

**(E) docs 登记**：
- docs/53 §5 新增**第 43 项**（blockquote，插第 42 项后）：修复登记 = 根因一句话（两对象两 SHA 错绑 + SHA 闸行为正确零弱化）+ 修法三则（(A)(B)(C) 各一行）+ 修复后全量实跑证据行 + 「登记 → 修复闭环，docs/53 第 42 项处置方向落定」
- docs/50：§4.4 +1 第 43 项行 + intro 链尾 `→ 579` 续接 `→ 581`；§5.1「继承 4 failed」行**不删**（既有 OPEN 行零删减），行内追加处置标注「已修复 per `581`（三处断言口径修正，SHA 闸零弱化）」
- docs/45 五处：文首 +1 刷新行；§1 +1 段（修复登记）；**§5.5 尾 O1 bullet 行尾注 append（per `581`）**——落点族 per `580` 审计 ⚠2 裁定（统一「§5.5 尾 O1/O3 bullet」，不再写 §6.2）；§7 链头 `911 == 911 == 911`（按 bump 实际值）+ knife 579 demote；§3 零涉（无裁定变更）
- 「O1 仍 OPEN」「O3 仍 OPEN」计数**非减**（O3 状态零变更——本刀不触 OCR 域）

**(F) manifest bump**：`scripts/_knife581_manifest_bump.py`，NEW **+4**（枚举即权威，逐项核对）：
本 bump 脚本（`spike_helper`）+ `581` 回执（`documentation`）+ `580` 审计文件（`documentation`）+ `tests/test_auto_ingest_public_source_s52.py`（实测 NOT-IN manifest → 首次 ADD，role=`schema_negative_test`）→ **907 → 911**；断言 `sum(role_count) == artifact_count == len(artifacts) == 911`；REFRESH：`test_cleanliness.py` + `test_public_extract_frontend_fixture.py`（在册）+ docs/45/53 + `00-EXEC-QUEUE.md`；docs/50 房规 SKIP；任务书按先例不计数；⚠3 教训：先实测每路径 bump 前状态再定 ADD/REFRESH，标注必须与枚举一致

**(G) 零网络核验**（命令 + 输出原样粘贴进回执；**(1) 全量为本刀核心证据**）：
```bash
python3 -m pytest tests/ -q                     # 全量：预期 0 failed（≈560 passed / 8 skipped，实测值为准；~13 分钟）
python3 -m pytest tests/test_auto_ingest_public_source_s52.py tests/test_cleanliness.py tests/test_public_extract_frontend_fixture.py -q
                                                # 三文件全绿
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q   # 25 passed（零改动防回归）
python3 frontend/smoke-check.py                 # PASS / exit 0
shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
                                                # e30ee811 9232efdb 937255a5 9056001c
grep -o "O1 仍 OPEN" docs/45-*.md | wc -l       # ≥166；O3 同理非减（基线 9）
grep -c "第 43 项（此条）" docs/53-*.md          # 1
grep -c "911 == 911 == 911" docs/45-*.md        # 1（stale 907 = 0）
python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
                                                # 911 911 911
```

**(H) 回执**：`reviews/stage0-gate0-rework-2026-08-23/581-stage0-cc-inherited-4failed-fix-suite-green-receipt-20260828.md`
- 文件名含 `-cc-`；单槽单回执，仅 `581`
- 交付 commit 含：三个测试文件、docs/53、docs/50、docs/45、bump 脚本、**`580` 审计文件（只读随刀）**、本任务书（只读随刀）、回执、`00-EXEC-QUEUE.md`（ACK 填行 + status→DELIVERED）
- cc_head backfill 单独 commit（勿 amend）；`git push origin HEAD` → `git push github HEAD` 严格顺序

## 红线（零豁免）

- ❌ 零生产代码变更：`scripts/auto_ingest_public_source.py`（SHA 闸）/ dbt / SQL / migration / schema / 前端 零触碰；SHA 闸 rc=8 语义零弱化（转测试预期，非放行）
- ❌ 不动 registry.csv / gate_thresholds.json / `00-CC-CURRENT.md` / 4 fixture 字节 / data/seeds/ / spikes/ 任何文件字节（修复走断言口径，不走改文件字节）
- ❌ 测试改动**仅限** (A)(B)(C) 三处断言口径 + 白名单，禁止扩大到其他测试/禁放松其余断言
- ❌ 不宣布 Gate 0/1/2 PASS；O3 仍 OPEN（本刀不触 OCR 域，5.2.2–5.2.6 链与真实 PDF `--confirm-o3=PATH` 用户保留动作不变）
- ❌ 无 --force / PAT / 公网 redeploy / 网络爬取；既有 OPEN 行零删减（docs/50 §5.1 继承行标注处置不删行；计数器非减）
- ✅ 全量 0 failed 为本刀完成定义；manifest 907 → 911 不变量（+4 枚举即权威）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 完成后

双推完成即停，回报 cc_head；架构师出 `582` 号位审计，随后签发 **582 = O3 实装首刀**（`validate_ocr_input()` API + `source_document.doc_kind='OCR_SCAN'` migration 014，引擎 paddle-ocr per 裁定）。
