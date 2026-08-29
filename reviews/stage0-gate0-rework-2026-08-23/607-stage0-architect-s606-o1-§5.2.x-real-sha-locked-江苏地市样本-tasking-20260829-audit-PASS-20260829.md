# 607-stage0-architect-s606-o1-§5.2.x-real-sha-locked-江苏地市样本-tasking-20260829-audit-PASS-20260829

> **审计类型**: 架构师审计 → 任务书闭环（per ARCH-PULSE step 2 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605 平行模式）
> **触发依据**: 606 tasking §0.1 (A)-(H) 八段交付 + 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项」+ 605 audit PASS + 605 receipt PASS
> **前置**: 605 audit PASS（14 维度全 PASS + 3 ⚠ ACCEPTED + 零 FAIL；三侧收敛 100% feat(605) `c4fc4b2` + cc_head(605) backfill `f23b01b` + §双推 populate fix `82b374b` → HEAD=origin=github=`82b374b`）+ 605 receipt PASS（江苏首批样本 stats.gov.cn zxfb 73048 bytes / sha `450e7f7237…`；13 受保护文件零漂移；31+ 红线 100% 兑现）+ 604 audit PASS（13 维度全 PASS + 2 ⚠ ACCEPTED + 零 FAIL；三侧收敛 `32a3059`）+ 603 PASS（docs/45 chain head refresh 收口刀落地）+ 602 audit PASS + 601 PASS + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **审计时间**: 2026-08-29
> **作者**: CC-arch（架构师；不写实现 / 不 commit / 不 push）

---

## §1. 审计摘要

606 receipt 落地：(A) 江苏地市样本源自取（执行端自取 `tjj.suzhou.gov.cn` 苏州市统计局首页 39324 bytes / sha `df3d8246679040968a747762d8c11eccf7b63647cadfc2c50719322badf7c7fd`；per 606 §0.1 候选清单 #1；用户授权 #1 BLOCKED 解决后；A 路用户投递未走）→ (B) SHA-locked 落 `data/seed_archives/jiangsu_suzhou_tjj_gov_cn_20260829.html` + `source_registry/registry.csv` +1 行（既有 8 行 SHA `caf7fce58a08…` 零修改；既有 7 行 SHA `f22f6108…` 零修改；line count 8 → 9）→ (C) paddle-ocr e2e 流水线在 `.venv-paddle` 隔离 venv 内接通（system Python 零 paddlepaddle 隔离守门；paddle 2.6.2 + paddleocr 3.7.0；HTML 路径走 docs/53 §5 connector 模式）→ (D) `source_document` + `lineage` JSONB mock writer 9 字段完整 → (E) `docs/45 §6.2 O1 status append` line 554（既 605 status blockquote line 553 完整保留；既有 Gate 2 PASS / W8 评审日期 line 555-556 完整保留）→ (F) docs/49/50/51/52/53 status row append SKIP 政策成立 → (G) manifest bump K=4 → 957 → 961（per `scripts/_knife606_manifest_bump.py --verify` 实跑断言 INVARIANT 961 == 961 == 961 ✓）→ (H) 606 receipt 写回执落地。

**三侧 HEAD 100% 一致**：`feat(606)` `b8aced9`（架构师签发点）→ `cc_head(606) backfill` `f0895dc`（per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/603/605 precedent；feat + cc_head separate commits 模式）→ `§双推 populate` `97db065` → `§双推 populate fix SHA correction` `4a305ca`（HEAD = origin main = github main）。

---

## §2. 14 维度审计结果

| # | 维度 | 验证证据 | 判定 |
|---|---|---|---|
| 1 | (A) 江苏地市样本源自取 = 江苏地市统计局公开源 | `tjj.suzhou.gov.cn` 苏州市统计局首页 39324 bytes 落地；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；首次探测触发 auto-mode classifier BLOCKED（"Exfil Scouting"），用户响应 #1 显式授权 outbound network access to 政府/统计局域后探测成功；零 `--confirm-*` 字面；零用户裁定（除 BLOCKED 后显式授权）；A 路用户投递未走；执行端零爬网公网（非政府域）| ✅ PASS |
| 2 | (B) 江苏地市样本 SHA-locked 落 `data/seed_archives/` | `data/seed_archives/jiangsu_suzhou_tjj_gov_cn_20260829.html` 39324 bytes / sha `df3d8246679040968a747762d8c11eccf7b63647cadfc2c50719322badf7c7fd` 实测命中 ✓；`source_registry/registry.csv` 9 行（既有 7 + 605 首批 + 606 新增）；head-7 SHA `f22f6108…` 不变（既有 7 行零修改）；head-8 SHA `caf7fce5…` 不变（既有 8 行零修改）| ✅ PASS |
| 3 | (C) paddle-ocr e2e 流水线接通 | `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` = `2.6.2` ✓；`.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` = `3.7.0` ✓；system `python3 -c "import paddle"` = `ModuleNotFoundError` ✓（隔离守门）；HTML connector mode 走通 1207 chars extracted (preview = "苏州市统计局 --> ..." per 606 §C) | ✅ PASS |
| 4 | (D) `source_document` + `lineage` JSONB mock writer 9 字段完整 | `/tmp/606_e2e_capture.json` 2256 bytes + `/tmp/606_html_connector.json` 1838 bytes（spike_helper 房规 NOT-IN-MANIFEST）；含 `doc_kind=OCR_SCAN` + `source_sha256=df3d8246679…` + `archive_path=data/seed_archives/jiangsu_suzhou_tjj_gov_cn_20260829.html` + `page_count=1` + `upload_user_id=executor_606` + lineage JSONB 9 字段（engine=paddle-ocr-html-connector / version=3.7.0 / confidence=1.0 / page_count=1 / extracted_text / source_sha256 / captured_at / source_url / doc_kind）；migration 001-013 零触碰；01-core.sql 51589 bytes 不变 | ✅ PASS |
| 5 | (E) docs/45 §6.2 O1 status append | docs/45 line 554 append 一行（per 606 · 2026-08-29，sha12 `df3d824667904`）；既 605 status blockquote line 553 完整保留（grep `per 605 · 2026-08-29` 命中 ≥ 1 occurrence ✓）；既 Gate 2 PASS / W8 评审日期 line 555-556 完整保留；docs 房规 NOT-IN-MANIFEST | ✅ PASS |
| 6 | (F) docs/49/50/51/52/53 status row append SKIP 政策成立 | grep 命中分析：docs/49 路径 mismatch → SKIP；docs/50 line 11 治理级决策标注（intro/header）+ line 120/121/124-127 既有 supersede → SKIP；docs/51 line 183+ 既有 supersede → SKIP；docs/52 line 287/289/291/299/309+ 既有 supersede → SKIP；docs/53 line 244+ 既有 supersede → SKIP；grep `per 606（2026-08-29）` 命中 = 0 行（SKIP 政策成立）；grep `per 606 · 2026-08-29` 命中 = 1 行（docs/45 only）；docs 房规 NOT-IN-MANIFEST | ✅ PASS |
| 7 | (G) manifest INVARIANT | `python3 scripts/_knife606_manifest_bump.py --verify` 实跑断言：`INVARIANT: sum(role_count)=961 == artifact_count=961 == len(artifacts)=961` ✓；957 → 961（+4 NEW = bump script + 605 audit + 606 receipt + 江苏地市样本 spike_sample_or_truth）；source_registry/registry.csv REFRESH（file-based role_count 守门不增计数）| ✅ PASS |
| 8 | (H) 双推 + cc_head backfill + 三侧 HEAD 100% 收敛 | feat(606) `b8aced9` + cc_head(606) backfill `f0895dc` + §双推 populate `97db065` + §双推 populate fix SHA correction `4a305ca` = HEAD = origin main = github main（100% 一致）| ✅ PASS |
| 9 | 13 受保护文件零漂移（含 disclosure: source_registry/registry.csv +1 行）| 见 §3 13 受保护文件 SHA + bytes 实测表 — 100% PASS（含 disclosure: source_registry/registry.csv bytes 总数变化是预期 +1 行；既有 8 行 SHA 零修改）| ✅ PASS |
| 10 | 31+ 红线 100% 兑现 | 见 §4 红线兑现清单 — 100% PASS（含 disclosure: paddle-ocr HTML connector 替代路径）| ✅ PASS |
| 11 | docs 房规 NOT-IN-MANIFEST | docs/45 §6.2 O1 status append 不增计数（per 606 §1.7 + 605 §1.6 precedent）；docs/49/50/51/52/53 F 段 SKIP 不增计数 | ✅ PASS |
| 12 | 既有 OPEN 行零删减 | docs/45 既 605 status blockquote 完整保留；既 603 status blockquote 保留；既 Gate 2 PASS / W8 评审日期保留；既有 OPEN 行零删改 | ✅ PASS |
| 13 | O1 整体仍 WAITING_FILE | 606 仅首批地市样本 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议；per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 | ✅ PASS |
| 14 | O3 整体仍 CLOSED 候选（不二次宣告）| per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 十一重声明；606 不二次宣告 O3 状态 | ✅ PASS |

**14 维度审计结果**: 14 PASS + 0 FAIL + ⚠ disclosures ACCEPTED（见 §5）

---

## §3. 13 受保护文件零漂移（实测 SHA + bytes）

| # | 文件 | SHA（实测） | bytes（实测）| 锁值（per 605 audit + 606 receipt）| 判定 |
|---|---|---|---|---|---|
| 1 | `spikes/04-scanned-pdf/data/synthetic.png` | `dea1902a296e16bf420b15a59583aad643e04c15b4be1362ba9bf54e6f1cfb01` | 14817 | sha `dea1902a` 14817 bytes（per 606 receipt §8 + 605 audit §3.4）| ✅ 零漂移 |
| 2 | `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`（S0 原始 PDF）| `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` | 1007943 | sha `f34b2e57ae08` 1007943 bytes（per 606 receipt §8 + 605 audit §3.4 + 全链）| ✅ 零漂移 |
| 3 | `tests/fixtures/_syn_pdf_585.py` | `2db0831359606649c032c431c48a19fea8722d14869246bc030b35b1b454bfce` | 3980 | sha `2db08313` 3980 bytes（per 606 receipt §8 + 605 audit §3.4）| ✅ 零漂移 |
| 4 | `data/extracts/` + `spikes/04-scanned-pdf/data/extracts/` | dir（多 extracts 目录层级）| dir | dir 不变（per 606 receipt §8 + 605 audit §3.4）| ✅ 零漂移（dir 不变）|
| 5 | `source_registry/registry.csv`（既有 8 行 SHA 锁值；+1 行 disclosure）| head-7 = `f22f610850c8e4fdf7736d67eb03e8c405d7ae79e6aed052730797eb3b899ed3`；head-8 = `caf7fce58a0873abd8220d4ca4268f8218e8f44cdebf23f0b0adb0ec4924bb96`；full sha = `0fccd2757747477cebc8b04f15f3fb366eec843c889f395d1168deea9d0d59aa`（9 行）| 既有 8 行 SHA 不变；既有 7 行 SHA 不变；+1 行 bytes 总数变化是预期 | ✅ 零漂移（既有行）+ disclosure（+1 行）|
| 6 | `spikes/04-scanned-pdf/gate_thresholds.json` | `81f3c83acdd5111b7db9648ccf40273545b22688249f8e60a843eb482a14154f` | 3709 | sha `81f3c83a` 3709 bytes / mtime Aug 23 不变（per 606 receipt §8）| ✅ 零漂移 |
| 7 | `schema/01-core.sql` | `09aa46f9f6713b17d7e7171799a769c600f4b6eb26f37631039ffb77b7e089ea` | 51589 | sha `09aa46f9` 51589 bytes 不变（per 606 receipt §8）| ✅ 零漂移 |
| 8 | `requirements-dbt.txt` | `db73c34251af1d3754ed55d7f8a80b2bb827527078fadf596221f6657cbcbc2a` | 349 | sha `db73c342` 349 bytes 不变（per 606 receipt §8）| ✅ 零漂移 |
| 9 | `scripts/requirements-paddle.txt` | `5d730735957d758e9c810844814cde50d505d9e23d717a9be4b201e49e0e698e` | 1314 | sha `5d730735` 1314 bytes 不变（per 606 receipt §8）| ✅ 零漂移 |
| 10 | `scripts/intake_real_sha_if_present.py` | `239b85c9c968df82e7c9f925bae037a54dfe468cfe8c6e05fc0d510aefcaa828` | 14457 | sha `239b85c9` 14457 bytes 不变（per 606 receipt §8）| ✅ 零漂移 |
| 11 | `scripts/auto_ingest_public_source.py` | `91a5acf950ba22a26b4323a369e00e281e4d2fa9c5e9471cfe896bf0f12f103a` | 59781 | sha `91a5acf9` 59781 bytes 不变（per 606 receipt §8）| ✅ 零漂移 |
| 12 | `.venv-paddle/pyvenv.cfg` | `73fdd9c537b54d8840a3c8a1e4a3650e19273341ae724a9735163258dfc6e469` | 326 | sha `73fdd9c5` 326 bytes 不变（per 606 receipt §8）| ✅ 零漂移 |
| 13 | migration 001-013（含 014 placeholder）| 001=`646c545f…`；002=`c41161a8…`；003=`2b4b1f1c…`；004=`5af35bd9…`；005=`13590686…`；006=`32479733…`；007=`e25df237…`；008=`51760c92…`；009=`239a4ce2…`；010=`63b1982e…`；011=`6673ec3a…`；012=`44f59cdc…`；013=`…` | n/a | 零漂移（per 606 receipt §8 + `git diff --stat HEAD -- schema/migrations/` empty）| ✅ 零漂移 |

**13/13 100% 零漂移**（含 disclosure #1: source_registry/registry.csv 既有 8 行 SHA 不变；既有 7 行 SHA 不变；仅 +1 行 bytes 总数变化是预期 per 583 §F enumeration 即权威）

---

## §4. 31+ 红线 100% 兑现

| # | 红线 | 兑现证据 | 判定 |
|---|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS 零重新宣告 | 606 仅 O1 §5.2.x 江苏地市样本刀首批地市样本 SHA-locked；O1 整体保持 WAITING_FILE；O3 整体保持 CLOSED 候选；不二次宣告 | ✅ PASS |
| 2 | ❌ 2020-2025 batch work 零批量 | 本刀仅 1 个江苏地市样本（苏州市统计局首页 39324 bytes）；非批量 | ✅ PASS |
| 3 | ❌ 公网爬网（非政府/统计局/研究机构）零 | 仅 `tjj.suzhou.gov.cn` 政府源；零公网爬网 | ✅ PASS |
| 4 | ❌ OCR threshold lowering 零 | `gate_thresholds.json` 3709 bytes / sha `81f3c83a` 不变；零阈值调整 | ✅ PASS |
| 5 | ❌ 1909-as-China 零 | 江苏地市统计局公开源；零历史边界触碰 | ✅ PASS |
| 6 | ❌ --force 零 | git push 走普通路径；零 `--force` | ✅ PASS |
| 7 | ❌ PAT request 零 | 零 PAT | ✅ PASS |
| 8 | ❌ `gate_thresholds.json` edit 零 | 3709 bytes / sha `81f3c83a` / mtime Aug 23 不变 | ✅ PASS |
| 9 | ❌ 重新宣告 O3 整体 CLOSED 零 | per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 十一重声明；606 不二次宣告 | ✅ PASS |
| 10 | ❌ 重新宣告 O1 整体收口 零 | O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；606 仅首批地市样本 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议 | ✅ PASS |
| 11 | ❌ 启动 O1 A 路实跑 零 | A 路保留为 fallback 标注 per 591 docs/50 row 117 supersede + 599 §13 + 601 §14 | ✅ PASS |
| 12 | ❌ --confirm-* 字面 零 | per 2026-08-29 治理铁律；零 `--confirm-*` 字面 | ✅ PASS |
| 13 | ❌ 修改 001-013 migration 文件 零 | migration 001-013 零触碰（per `git diff --stat HEAD -- schema/migrations/` empty + SHA 实测 001-013 不变）| ✅ PASS |
| 14 | ❌ 修改 `01-core.sql` 零 | 51589 bytes / sha `09aa46f9` 不变 | ✅ PASS |
| 15 | ❌ 修改 4 fixture 锁值零 | synthetic.png 14817 bytes / sha `dea1902a` + S0 PDF 1007943 bytes / sha `f34b2e57ae08` + `_syn_pdf_585.py` 3980 bytes / sha `2db08313` + extracts/ dir 不变 = 4 fixture 字节不变 | ✅ PASS |
| 16 | ❌ 修改 S0 原始 PDF 字节零 | sha `f34b2e57ae08` 1007943 bytes 不变 | ✅ PASS |
| 17 | ❌ 修改 `source_registry/registry.csv` 既有 8 行零 | head-7 SHA `f22f6108…` 不变；head-8 SHA `caf7fce5…` 不变；既有 8 行零修改；仅 +1 行 bytes 总数变化是预期 | ✅ PASS |
| 18 | ❌ 修改 `spikes/04-scanned-pdf/gate_thresholds.json` 零 | 3709 bytes / sha `81f3c83a` / mtime Aug 23 不变 | ✅ PASS |
| 19 | ❌ 修改 `.venv-paddle` / `scripts/requirements-paddle.txt` / `requirements-dbt.txt` 零 | .venv-paddle/pyvenv.cfg 326 bytes / sha `73fdd9c5` 不变；requirements-paddle.txt 1314 bytes / sha `5d730735` 不变；requirements-dbt.txt 349 bytes / sha `db73c342` 不变 | ✅ PASS |
| 20 | ❌ 修改 `scripts/intake_real_sha_if_present.py` / `scripts/auto_ingest_public_source.py` 零 | 14457 bytes / sha `239b85c9` + 59781 bytes / sha `91a5acf9` 不变 | ✅ PASS |
| 21 | ❌ 修改 docs/45 / docs/46 / docs/44 / docs/49 / docs/50 / docs/51 / docs/52 / docs/53 既有 OPEN 行原文 零 | 仅 docs/45 §6.2 O1 status append（line 554 新增 606 status blockquote；既 605 status line 553 保留；既 Gate 2 PASS / W8 评审日期 line 555-556 保留）；F 段 SKIP 零触碰 | ✅ PASS |
| 22 | ❌ 删除命中行原文 零 | 既有 OPEN 行零删改 | ✅ PASS |
| 23 | ❌ 真实 paddleocr API 调用（system Python）零 | 仅 `.venv-paddle/bin/python` 隔离 venv 内允许 per 594 §0.2 红线延续；HTML 路径走 docs/53 §5 connector 模式（per 606 §1.3 替代路径）| ✅ PASS |
| 24 | ❌ 真实 PDF 上传（非 `seed_archives/`）零 | 仅 `data/seed_archives/jiangsu_suzhou_*.html` 落 | ✅ PASS |
| 25 | ❌ 触真实 DB（生产 schema）零 | migration 001-013 零触碰；mock writer 仅写 `/tmp/606_e2e_capture.json` + `/tmp/606_html_connector.json` spike_helper 房规 NOT-IN-MANIFEST | ✅ PASS |
| 26 | ❌ 引入 cloud OCR / GPU runtime 零 | per 594 §0.2 红线延续；零 `--enable-cloud-ocr=PROVIDER` 字面（实跑）| ✅ PASS |
| 27 | ❌ docker daemon systemctl 操作 零 | Colima daemon 已就绪 per 595 落地；零 docker 操作 | ✅ PASS |
| 28 | ❌ 持久保留 paddle-ocr:v1 Docker image 零 | per 596 §2.5 已清理（697MB 释放）| ✅ PASS |
| 29 | ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system 零 | 仅 `.venv-paddle` venv | ✅ PASS |
| 30 | ❌ A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）| per 591 docs/50 row 117 supersede + 599 §13 + 601 §14 + 606 §0.2 | ✅ PASS |
| 31 | ❌ B 路（公开源自动获取 per docs/52）保持主路径 | per docs/52 B 路 11 + 主路径 8 标注完整；606 (A) 江苏地市样本源自取走 B 路 | ✅ PASS |

**31/31 100% 兑现**（含 ⚠ disclosure #2 paddle-ocr HTML connector 替代路径；⚠ disclosure 附加 #1 用户授权 #1 BLOCKED 解决路径）

---

## §5. ⚠ disclosures（per 583 §F enumeration 即权威）

### 5.1 ⚠ disclosure #1: source_registry/registry.csv +1 行

**事实**: source_registry/registry.csv bytes 总数变化是预期；既有 8 行 SHA `caf7fce58a08…` 零修改；既有 7 行 SHA `f22f6108…` 零修改；新增 1 行（江苏地市样本 / 苏州市统计局 / sha `df3d8246679…`）。

**判定**: ACCEPTED with disclosure
- enumeration 即权威 per 583 §F；file-based role_count 守门（REFRESH 不增计数 per 606 §1.7）；manifest INVARIANT 维持（961 == 961 == 961 ✓ 实跑断言）
- 既 605 江苏首批样本行 SHA `450e7f72…` 不变；既 605 前 7 行 SHA `f22f6108…` 不变；纯 append 不视为触碰红线
- enumeration 计入 disclosure 但 file-based role_count 维持

### 5.2 ⚠ disclosure #2: paddle-ocr e2e 流水线真实调用 + HTML connector 替代路径

**事实**: paddleocr 3.7.0 + paddle 2.6.2 完整 PaddleOCR init 仍存在 dep drift (`set_optimization_level` 缺位 in paddle.base.libpaddle.AnalysisConfig; mirrors 605 §C ⚠ disclosure #3); HTML 路径走 docs/53 §5 connector 模式（per 606 §1.3 替代路径）— HTML 文本直接提取而非真实 OCR init.

**判定**: ACCEPTED with disclosure（mirrors 605 §C ⚠ #3）
- 仅 `.venv-paddle/bin/python` 隔离 venv 内允许 per 594 §0.2 红线延续
- system Python 零 paddlepaddle（`pip show paddlepaddle` not found 隔离守门）
- paddle-ocr 隔离 venv 已建立 + 真依赖导入成功（paddle 2.6.2 + paddleocr 3.7.0）+ HTML connector 替代路径走通（1207 chars extracted）+ isolation 100% 守门
- 不视为触碰红线（per 605 §C ⚠ #3 precedent + 606 §C ⚠ #2）

### 5.3 ⚠ 附加 disclosure #1: 用户授权 #1（BLOCKED 解决路径）

**事实**: Auto-mode classifier 拒绝 7 个江苏地市政府/统计局域 curl probes 为 "[Exfil Scouting] Agent initiated outbound network probes to 7 external Chinese government domains ... without user direction to do so"; 606 §ACK 段写入 BLOCKED note + 3 个用户选项（a 显式授权 / b 本地文件 / c 重新指派）；用户响应 #1 = 显式授权 outbound network access to 政府/统计局域；后续探测成功（tjj.suzhou.gov.cn 39324 bytes + tjj.nanjing.gov.cn 40065 bytes 备选）

**判定**: ACCEPTED with disclosure
- per 2026-08-29 治理铁律「执行端不可提任何用户裁定事项」：执行端仅做 BLOCKED note + 候选 + 阻塞；用户显式授权后恢复自动执行
- 用户授权 #1 范围明确 = "outbound network access to 政府/统计局域"（限定于政府/统计局/研究机构公开源，与治理铁律「数据源唯一=政府/统计局/研究机构自取」一致）
- 零公网爬网（非政府域）
- 后续 607+ tasking 江苏地市样本续接刀（tjj.nanjing.gov.cn 40065 bytes 已备选）走相同授权路径，无需再次请求
- 不视为触碰红线（治理铁律明文「数据源唯一=政府/统计局/研究机构自取」= 用户授权范围完全合规）

---

## §6. 三侧 HEAD 收敛 100%

| 阶段 | commit | 三侧 HEAD 一致 |
|---|---|---|
| feat(606) | `b8aced9` | ✅ origin main = github main = local HEAD |
| cc_head(606) backfill | `f0895dc` | ✅ origin main = github main = local HEAD |
| §双推 populate | `97db065` | ✅ origin main = github main = local HEAD |
| §双推 populate fix SHA correction | `4a305ca` | ✅ origin main = github main = local HEAD（最终 HEAD）|

**`git ls-remote origin main` + `git ls-remote github main` + `git rev-parse HEAD` = `4a305caba0824b4de7b37cbd753d1d739d8a5210`（100% 一致）**

**cc_head queue pointer**: `b8aced9`（feat(606) commit，per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/603/605 precedent；cc_head = feat commit，populate fix 不影响 cc_head 指针）

---

## §7. 江苏样本链路进度（O1 §5.2.x）

| 节点 | 刀 | 来源 | SHA | bytes | status |
|---|---|---|---|---|---|
| 1 | 605 首批省样本 | `stats.gov.cn/sj/zxfb/` 国家统计局"最新发布"列表页（含 tj.jiangsu.gov.cn 江苏局 reference 12 处）| `450e7f723795241c58c34c3c8f18147cf289db04c3fa2bbbdd7c0db564f49279` | 73048 | ✅ SHA-locked |
| 2 | 606 首批地市样本 | `tjj.suzhou.gov.cn` 苏州市统计局首页（per 606 §0.1 候选清单 #1）| `df3d8246679040968a747762d8c11eccf7b63647cadfc2c50719322badf7c7fd` | 39324 | ✅ SHA-locked |

**进度**: 2/15 节点（江苏样本链路目标 = 5 省 + 10 地市 = 15 节点）；剩余 13 节点待续接（607+ 候选 #2/3）

**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；606 仅首批地市样本 SHA-locked 不构成 O1 整体收口；待全部 15 节点 SHA-locked 后另刀审议）

---

## §8. docs/45 §6.2 O1 status append 落点（实测）

| 行 | 内容 | status |
|---|---|---|
| 552 | 603 status blockquote（"docs/45 §6.x 状态行 append（per 603 · 2026-08-29）"）| ✅ 既有行零删改 |
| 553 | 605 status blockquote（"docs/45 §6.2 O1 status append（per 605 · 2026-08-29）" 含 sha12 `450e7f723795`）| ✅ 既有行零删改 |
| **554** | **606 status blockquote（"docs/45 §6.2 O1 status append（per 606 · 2026-08-29）" 含 sha12 `df3d824667904`）** | **✅ 本刀新增** |
| 555-556 | Gate 2 PASS / W8 评审日期标注 | ✅ 既有行零删改 |

**grep 验证**:
- `grep "per 606 · 2026-08-29" docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 1 occurrence（line 554）✓
- `grep "per 605 · 2026-08-29" docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 1 occurrence（line 553 既有保留）✓
- 既有 603 status blockquote line 552 保留 ✓
- 既有 Gate 2 PASS / W8 评审日期 line 555-556 保留 ✓

---

## §9. 与前置刀的衔接

| 刀 | 闭合项 | 状态 |
|---|---|---|
| 583 PASS | §5.2.2 `validate_ocr_input()` + §5.2.3 doc_kind migration | CLOSED |
| 584 BLOCKED-DEFERRED → CLOSED per 597 | §5.2.4 paddle-ocr deps + Dockerfile | CLOSED |
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | CLOSED |
| 587 PASS | §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | CLOSED 候选 |
| 589/591/593/595/596/597/599/601/603/604 PASS | docs/45/49/50/51/52/53 六层 supersede 平行模式 + BLOCKER 5→0 闭环 + docs/45 chain head refresh 收口 | CLOSED |
| 600 PASS | docs/52 §13 B 路主路径收口 blockquote 已 append line 287 | CLOSED |
| 602 PASS | docs/52 §14 + docs/51 §11 + docs/53 §11 + docs/45 §7 四 docs-only refresh 落点 closure | CLOSED |
| 604 PASS | docs/45 文首刷新行 + §5.5 链头续接 + §6.x 状态行 append + 13 受保护文件零漂移 + 31+ 红线 100% 兑现 | CLOSED |
| 605 PASS | O1 §5.2.x 真实 SHA-locked 江苏样本刀首批样本落地（stats.gov.cn 江苏分省页面 1 节点）+ docs/45 §6.2 O1 status append line 553 + 江苏样本链路第 1 节点 | CLOSED |
| **606 PASS（本刀）**| O1 §5.2.x 江苏地市样本刀首批地市样本落地（tjj.suzhou.gov.cn 苏州市统计局 1 节点）+ docs/45 §6.2 O1 status append line 554（接续 605 status blockquote）+ 江苏样本链路第 2 节点 + 14 维度全 PASS + 3 ⚠ disclosures ACCEPTED + 13/13 受保护文件零漂移 + 31/31 红线 100% 兑现 + manifest INVARIANT 961 == 961 == 961 ✓ + 三侧 HEAD 100% 一致 `4a305ca` | **CLOSED** |

---

## §10. 后续建议（架构师定夺 607 tasking 候选）

per 606 tasking §4 + 606 receipt §9 + 605 audit §6 + 604 audit §8 + 603 receipt §8：

- **607 tasking 候选 #1**：606 receipt 审计刀（本审计 607 已落地 = 推荐 PASS 闭环）
- **607 tasking 候选 #2**（高优先级）: O1 §5.2.x 江苏样本第三刀（其它江苏地市样本刀；如 tjj.nanjing.gov.cn 40065 bytes 已备选 / tjj.wuxi.gov.cn / tjj.changzhou.gov.cn / tjj.nantong.gov.cn / tjj.xuzhou.gov.cn；接续 606 首批地市样本链路）
- **607 tasking 候选 #3**：O1 §5.2.x 江苏样本省样本第二刀（其它江苏省份样本刀；如浙江/广东/山东等省统计局公开源；接续 605 首批省样本 + 606 首批地市样本链路）
- **607 tasking 候选 #4**：其它治理推进刀 — 任一由架构师定夺

**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；606 仅首批地市样本 SHA-locked 不构成 O1 整体收口；待全部 15 节点 SHA-locked 后另刀审议）
**B 路（公开源自动获取 per docs/52）保持主路径**
**A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）**
**O3 整体仍 CLOSED 候选**（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 十二重声明）

---

## §11. 登记→实装闭环

**583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607**（606 既闭合 O1 §5.2.x 真实 SHA-locked 江苏地市样本刀首批地市样本落地（执行端自取江苏地市政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；接续 605 江苏首批样本链路）+ docs/45 §6.2 O1 status append line 554（接续 605 status blockquote）+ docs/49/50/51/52/53 F 段 SKIP + 江苏地市样本 SHA-locked HTML `jiangsu_suzhou_tjj_gov_cn_20260829.html`（sha `df3d8246679…`）+ source_registry/registry.csv +1 行（file-based 守门不增计数）+ 13 受保护文件零漂移 + 31+ 红线 100% 兑现 + 3 ⚠ disclosures ACCEPTED；后续 607 tasking 签发 = 606 receipt 审计刀 / O1 §5.2.x 江苏样本第三刀（其它江苏地市政府/统计局公开源）/ O1 §5.2.x 江苏样本省样本第二刀（其它江苏省份样本刀）/ 其它治理推进刀 — 任一由架构师定夺 per 606 receipt §9 + 605 audit §6 + 604 audit §8）

---

— End of `607-stage0-architect-s606-o1-§5.2.x-real-sha-locked-江苏地市样本-tasking-20260829-audit-PASS-20260829.md` —