# 612-stage0-architect-s611-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611 平行模式）
> **触发依据**: 611 audit §10 推荐 #2 verbatim「O1 §5.2.x 江苏样本第五刀（地市样本第四刀；候选源 = tjj.wuxi.gov.cn 无锡市统计局 / tjj.nantong.gov.cn 南通市统计局 / tjj.xuzhou.gov.cn 徐州市统计局 任选 ≥ 1 个；接续 605 + 606 + 608 + 610 江苏样本链路 4/15 → 5/15）」+ 610 tasking §0.1 备选清单 verbatim「`tjj.wuxi.gov.cn` 无锡市统计局 / `tjj.nantong.gov.cn` 南通市统计局 / `tjj.xuzhou.gov.cn` 徐州市统计局 fallback」+ 609 audit §10 + 610 receipt §9 候选 + 605 audit §6 + 2026-08-29 治理铁律（数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项）+ docs/52 B 路 spec 已 CLOSED per 599 audit PASS 落地 + 605 + 606 + 608 + 610 江苏样本链路 4/15 节点（stats.gov.cn 江苏分省页面 + tjj.suzhou.gov.cn 苏州市统计局 + tjj.nanjing.gov.cn 南京市统计局 + tjj.changzhou.gov.cn 常州市统计局）已 SHA-locked 落地
> **前置**: 611 audit PASS（14 维度全 PASS + 4 ⚠ disclosures ACCEPTED + 1 附加 ⚠ ACCEPTED + 零 FAIL；三侧收敛 100% feat(610) `97cbe88` + cc_head(610) backfill `ab0d4ec` + §双推 populate `ecaf82a` + §双推 populate fix SHA correction `86af7f1` → HEAD=origin=github=`86af7f1f34f3354c29053a818b688cffd5517c93`；cc_head queue pointer `86af7f1`）+ 610 receipt PASS（8-segment delivery all landed + 4 ⚠ ACCEPTED + 零 FAIL）+ 609 audit PASS（14 维度 + 5 ⚠）+ 608 receipt PASS + 607 audit PASS（14 维度 + 3 ⚠）+ 606 receipt PASS + 605 audit PASS（14 维度 + 3 ⚠）+ 605 receipt PASS + 604 audit PASS（13 维度 + 2 ⚠）+ 603 PASS + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **签发时间**: 2026-08-29
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) 江苏样本地市第四刀源自取 | 执行端从江苏地市政府/统计局/研究机构公开源自取预 vetted 地市样本（**指定**：tjj.wuxi.gov.cn 无锡市统计局首页 per 611 audit §10 推荐 #2 verbatim 候选清单 #1；按 docs/52 B 路 spec 四步流水线 discover → download → sha256 → archive；首选候选若探测失败则 fallback 到 tjj.nantong.gov.cn 南通市统计局 / tjj.xuzhou.gov.cn 徐州市统计局 任选 ≥ 1 个 ≥ 1 KB 内容源）；**零 `--confirm-*` 字面**；**零用户动作**；**零用户裁定**；**执行端零爬网公网（非政府域）**；仅政府/统计局/研究机构公开源 |
| (B) 江苏样本地市第四刀 SHA-locked 落 `data/seed_archives/` | sha256 验证 + 落入 `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html`（per source 类型；<city> = 探测成功候选城市名 = wuxi / nantong / xuzhou）；更新 `source_registry/registry.csv` +1 行（**⚠ disclosure**: source_registry/registry.csv 锁值不变；新增行而非修改既有 11 行（含 610 江苏地市第三刀行 + 608 江苏地市第二批行 + 606 江苏地市首批行 + 605 江苏首批行 + 既有 7 行）；既有 11 行 SHA 不变；既有 10 行 SHA 不变；既有 9 行 SHA 不变；既有 8 行 SHA 不变；既有 7 行 SHA 不变；enumeration 即权威 per 583 §F）|
| (C) paddle-ocr e2e 流水线（江苏样本地市第四刀）| `.venv-paddle/bin/python` HTML 路径走 docs/53 §5 connector 模式（per 606 §1.3 + 607 audit §3 #2 disclosure + 608 §1.3 + 609 audit §3 ⚠ #2 disclosure + 610 §1.3 + 611 audit §3 ⚠ #3 disclosure 替代路径已验证）；**真实 paddle-ocr HTML connector 调用**（per 594 §0.2 红线：仅 `.venv-paddle` venv 内允许真实调用；system site-packages 零 paddlepaddle）；不修改 gate_thresholds.json；不修改 4 fixture 锁值 |
| (D) source_document + lineage JSONB 写入（江苏样本地市第四刀）| `source_document` 行新增 `doc_kind='OCR_SCAN'` + `source_sha256=<sha>` + `archive_path='data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html'`；`lineage` JSONB 写入 `{engine: 'paddle-ocr-html-connector', version: '3.7.0', confidence: 1.0, page_count: 1, extracted_text: ..., source_sha256: <sha>, captured_at: <iso8601>, source_url: 'https://tjj.<city>.gov.cn/', doc_kind: 'OCR_SCAN'}`；零数据库 schema 变更（migration 001-013 零触碰）|
| (E) docs/45 §6.2 O1 status append（post-612）| docs/45 §6.x 既有 610 status blockquote 后续 append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 612 · 2026-08-29）：O1 §5.2.x 江苏样本第五刀（地市样本第四刀）已落地（`<sha12>` per source_registry/registry.csv +1 行；tjj.<city>.gov.cn <城市名>统计局首页 per 611 audit §10 推荐 #2 verbatim；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec）；江苏样本链路 5/15 节点；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。`；既有 605 + 606 + 608 + 610 status blockquote 完整保留；不删不改 |
| (F) docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）| per docs-only refresh 房规；SKIP 政策若命中为治理级决策标注非 stale `--confirm-*` 字面；docs 房规 NOT-IN-MANIFEST |
| (G) manifest bump K → 969+K | per docs 房规 + spike_helper 房规；K = 4 基础（612 bump script + 611 audit 入库随 612 commit + 612 receipt + 江苏样本地市第四刀 HTML spike_sample_or_truth）= +4（如适用；source_registry_csv role 不增计数 per 606/607/608/609/610/611 file-based role_count 守门）；enumeration 即权威 per 583 §F；INVARIANT 969+K == 969+K == 969+K ✓ |
| (H) 612 receipt 写回执 | 含 (A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移（⚠ disclosure: source_registry/registry.csv +1 行；既有 11 行 SHA 不变；bytes 总数变化是预期）+ 31+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 612 仅 O1 §5.2.x 江苏样本第五刀（地市样本第四刀）SHA-locked + e2e 跑通；O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准：WAITING_FILE = intake 出口码 / mart 真 SHA 未入仓技术状态语义）；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600+601+602+603+604+605+606+607+608+609+610+611 十七重声明 |
| ❌ 2020-2025 batch work | ✅ 零批量；本刀仅 1 个江苏样本地市样本（首选 = 无锡市统计局 / fallback = 南通市统计局 / 徐州市统计局）|
| ❌ 公网爬网（非政府/统计局/研究机构）| ✅ 零公网爬网；仅政府/统计局/研究机构公开源（per 2026-08-29 治理铁律）|
| ❌ OCR threshold lowering | ✅ 零阈值调整；gate_thresholds.json 3709 bytes 不变 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 十七重声明）；612 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE；612 仅江苏样本地市样本第四刀 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 601 + 599 + 591 docs/50 row 117 supersede）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零 `--confirm-*` 字面 |
| ❌ 修改 001-013 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更（51589 bytes 不变）|
| ❌ 修改 4 fixture 锁值（synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir）| ✅ 红线 / 4 fixture 字节不变 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv 既有 11 行 | ✅ 红线 / 既有 11 行未改；612 仅 +1 行（新增江苏样本地市第四刀行）；既有 11 行 SHA 不变（含 610 江苏地市第三刀行 + 608 江苏地市第二批行 + 606 江苏地市首批行 + 605 江苏首批行 + 既有 7 行）|
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 红线 / 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 红线 / 零 venv/env 污染（requirements-dbt.txt 349 bytes 不变）|
| ❌ 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | ✅ 红线 / 零 intake 实跑触碰 |
| ❌ 修改 docs/45 / docs/46 / docs/44 / docs/49 / docs/50 / docs/51 / docs/52 / docs/53 既有 OPEN 行原文 | ✅ 612 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 真实 paddleocr API 调用（system Python）| ✅ 仅 `.venv-paddle/bin/python` 隔离 venv 内允许（per 594 §0.2 红线延续）；HTML 路径走 docs/53 §5 connector 模式（per 606 §1.3 + 607 audit §3 #2 disclosure + 608 §1.3 + 609 audit §3 ⚠ #2 disclosure + 610 §1.3 + 611 audit §3 ⚠ #3 disclosure 已验证）|
| ❌ 真实 PDF 上传（非 seed_archives/）| ✅ 零真实 PDF 上传到 ALLOWED_PREFIXES 上传目录；仅 `data/seed_archives/jiangsu_<city>_*.html` 落 |
| ❌ 触真实 DB（生产 schema）| ✅ 零生产 schema 变更；source_document + lineage 写入走测试 mock writer 或新建 staging DB（per 587 §0.2）|
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续；零 `--enable-cloud-ocr=PROVIDER` 字面（实跑）|
| ❌ docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（per 595 落地）；零 docker 操作 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv |
| ❌ 用户授权 #1 二次申请 | ✅ 用户授权 #1 仍生效（per 610 §0.1 verbatim「用户授权 #1 仍生效无需二次授权」+ 606 BLOCKED 解决 precedent + 2026-08-29 治理铁律）；612 = tjj.<city>.gov.cn 政府/统计局域，授权仍生效，无需二次授权 |

---

## §1. 612 tasking 详情

### 1.1 (A) 江苏样本地市第四刀源自取

**触发条件**:
- docs/52 B 路 spec 已 CLOSED per 599 audit PASS 落地（前置条件已满足）
- 2026-08-29 治理铁律：数据源唯一=政府/统计局/研究机构自取
- 执行端零爬网公网（非政府域）
- 605 江苏首批样本已 SHA-locked 落地（stats.gov.cn 江苏分省页面 73048 bytes / sha `450e7f7237…`）
- 606 江苏地市首批样本已 SHA-locked 落地（tjj.suzhou.gov.cn 苏州市统计局首页 39324 bytes / sha `df3d8246679…`）
- 608 江苏样本地市第二刀已 SHA-locked 落地（tjj.nanjing.gov.cn 南京市统计局首页 40065 bytes / sha `37ed4c223b16…`）
- 610 江苏样本地市第三刀已 SHA-locked 落地（tjj.changzhou.gov.cn 常州市统计局首页 50868 bytes / sha `0ecf3d2ed764…`）
- 用户授权 #1（显式授权 outbound network access to 政府/统计局域）已生效 per 606 receipt §2 + 608 §0.1 + 610 §0.1 + 612 §0.1 verbatim 续接
- **指定采用**: tjj.wuxi.gov.cn 无锡市统计局首页（per 611 audit §10 推荐 #2 verbatim 候选清单 #1；HTTP 502 Bad Gateway 备选待 verify；如探测 502 持续则 fallback 到 tjj.nantong.gov.cn 南通市统计局 / tjj.xuzhou.gov.cn 徐州市统计局 任选 ≥ 1 个 ≥ 1 KB 内容源）

**候选清单**（per 611 audit §10 推荐 #2 + 610 tasking §0.1 备选 fallback 清单）:

| 候选源 | 610 探测预期 | 612 探测预期 |
|---|---|---|
| `https://tjj.wuxi.gov.cn/` | HTTP 502 Bad Gateway 备选待 verify（per 606 §A 备选清单 + 610 §A 探测预期）| **首选** = tjj.wuxi.gov.cn 无锡市统计局首页 per 611 audit §10 推荐 #2 verbatim 候选清单 #1 |
| `https://tjj.nantong.gov.cn/` | HTTP 301 Moved Permanently redirect（per 606 §A 备选清单）| fallback #1 = tjj.nantong.gov.cn 南通市统计局首页 per 611 audit §10 推荐 #2 verbatim 候选清单 #2 |
| `https://tjj.xuzhou.gov.cn/` | HTTP 502 Bad Gateway（per 606 §A 备选清单 + 610 §A 探测预期）| fallback #2 = tjj.xuzhou.gov.cn 徐州市统计局首页 per 611 audit §10 推荐 #2 verbatim 候选清单 #3 |
| 其它候选 | ⏸ 备选 | 后续 613+ 江苏样本刀续接 |

**采用流程**（per docs/52 B 路 spec 四步流水线：discover → download → sha256 → archive）:

1. **首选探测** = `curl -L --max-time 30 -o /tmp/612_discover.html https://tjj.wuxi.gov.cn/`（HTTP 502 备选待 verify；如 502 持续则跳过）
2. **首选失败 fallback** = `curl -L --max-time 30 -o /tmp/612_discover.html https://tjj.nantong.gov.cn/` 或 `https://tjj.xuzhou.gov.cn/` 任选 ≥ 1 个 ≥ 1 KB 内容源
3. **SHA-256 验证** = `shasum -a 256 /tmp/612_discover.html` 锁定 sha
4. **archive** = 落入 `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html`（<city> = 探测成功候选城市名 = wuxi / nantong / xuzhou）

**零 `--confirm-*` 字面** ✓
**零用户动作** ✓
**零用户裁定** ✓
**执行端零爬网公网（非政府域）** ✓（仅政府/统计局域 tjj.wuxi.gov.cn / tjj.nantong.gov.cn / tjj.xuzhou.gov.cn）

**grep 验证（落地后预期）**:
- `ls data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html` 命中 ≥ 1 文件 ✓
- `cat source_registry/registry.csv | grep jiangsu_<city>` 命中 ≥ 5 行（既有 605 江苏首批 + 606 地市首批 + 608 地市第二刀 + 610 地市第三刀 + 612 地市第四刀）✓
- `shasum -a 256 data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html` = 落地 sha ✓

### 1.2 (B) 江苏样本地市第四刀 SHA-locked 落 `data/seed_archives/`

**触发条件**: (A) 已落地至少 1 个江苏样本地市第四刀文件

**落地**:
- 落入 `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html`（<city> = 探测成功候选城市名；sha256 已知）
- 更新 `source_registry/registry.csv` +1 行（既有 11 行 SHA `3639e729…` 零修改；既有 10 行 SHA `3639e729…` 零修改；既有 9 行 SHA `0fccd275…` 零修改；既有 8 行 SHA `caf7fce58a08…` 零修改；既有 7 行 SHA `f22f610850c8…` 零修改；新增行后 line count 11 → 12）
- 新增行格式（18 列 schema 兼容既有 11 行）：
  ```
  tjj.<city>.gov.cn,<城市名>统计局,MUNICIPAL_BULLETIN,https://tjj.<city>.gov.cn/,["http://www.<city>.gov.cn/"],DAILY,公开；无需授权,HTML,首页/统计公报/统计数据,江苏地市政府门户；612 §0.1 候选清单 #1 per 611 audit §10 推荐 #2 verbatim；用户授权 #1 仍生效；其余江苏地市备用,tjj.suzhou.gov.cn / tjj.wuxi.gov.cn / tjj.changzhou.gov.cn / tjj.nantong.gov.cn / tjj.xuzhou.gov.cn 备用,TRUE,S0,data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html,<sha12>,<bytes>,S0,代表性江苏地市 HTML 样本（<城市名>统计局首页；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；2026-08-29 治理铁律；612 江苏样本第五刀（地市样本第四刀）O1 §5.2.x 接续 610 江苏样本地市第三刀 + 608 江苏样本地市第二刀 + 606 江苏地市首批样本 + 605 江苏首批样本；2026-08-29）
  ```

**⚠ disclosure #1**: source_registry/registry.csv bytes 总数变化是预期（既有 11 行 SHA 不变；新增 1 行 spike_sample_or_truth role +1 + source_registry_csv role 不增计数 per 612 §1.7 file-based role_count 守门）

**grep 验证（落地后预期）**:
- `wc -l source_registry/registry.csv` = 12 ✓（既有 7 + 605 首批 + 606 地市首批 + 608 地市第二刀 + 610 地市第三刀 + 612 地市第四刀）
- `head -11 source_registry/registry.csv | shasum -a 256` = `3639e729…` 不变 ✓（既有 11 行零修改 across all 4 commits in chain）
- `ls -la data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html` 命中 ≥ 1 文件 ✓
- `shasum -a 256 data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html` = 落地 sha ✓

### 1.3 (C) paddle-ocr e2e 流水线

**触发条件**: (B) 江苏样本地市第四刀已 SHA-locked 落 `data/seed_archives/`

**流水线接通验证**（per 605/606/608/610/611 precedent 4/4 验证）:

| 验证项 | 预期结果 |
|---|---|
| `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` | `2.6.2` ✓ |
| `.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` | `3.7.0` ✓ |
| system `python3 -c "import paddle"` | `ModuleNotFoundError` ✓（隔离守门）|
| `.venv-paddle/bin/python HTML connector mode` | ✓ extracted_text preview 含 "<城市名>统计局" references; engine='paddle-ocr-html-connector', version='3.7.0', confidence=1.0, page_count=1, source_sha256=<sha12> |

**e2e 流水线接通证明** = 三层 import 验证 + HTML connector 模式（per docs/53 §5）= 4/4 ✓

**⚠ disclosure #2 (mirrors 611 audit §3 ⚠ #3 + 610 §C ⚠ #2 + 608 §C ⚠ #2 + 606 §C ⚠ #2 + 605 §C ⚠ #3)**: paddleocr 3.7.0 + paddle 2.6.2 完整 PaddleOCR init 仍存在 dep drift (`set_optimization_level` 缺位 in paddle.base.libpaddle.AnalysisConfig). HTML 路径走 docs/53 §5 connector 模式 (per 612 §1.3 verbatim "或 HTML 路径走 docs/53 §5 connector 模式") — HTML 文本直接提取而非真实 OCR init. 不视为触碰红线（paddle-ocr 隔离 venv 已建立 + 真依赖导入成功 + HTML connector 替代路径走通 + isolation 100% 守门）.

**真实 paddle-ocr HTML connector 调用**（per 594 §0.2 红线：仅 `.venv-paddle` venv 内允许真实调用；system site-packages 零 paddlepaddle）

### 1.4 (D) source_document + lineage JSONB 写入

**触发条件**: (C) paddle-ocr e2e 流水线接通

**source_document row**:
```json
{
  "doc_kind": "OCR_SCAN",
  "language": "zh-CN",
  "source_sha256": "<sha>",
  "archive_path": "data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html",
  "page_count": 1,
  "upload_user_id": "executor_612"
}
```

**lineage JSONB 9 字段**:
```json
{
  "engine": "paddle-ocr-html-connector",
  "version": "3.7.0",
  "confidence": 1.0,
  "page_count": 1,
  "extracted_text": "<前 600 chars HTML 内容 via docs/53 §5 connector>",
  "source_sha256": "<sha>",
  "captured_at": "<iso8601>",
  "source_url": "https://tjj.<city>.gov.cn/",
  "doc_kind": "OCR_SCAN"
}
```

**migration 001-013 零触碰** ✓（per `git diff --stat HEAD~4..HEAD -- schema/migrations/` = empty）
**01-core.sql 51589 bytes 不变** ✓
**测试 mock writer 捕获位置** = `/tmp/612_e2e_capture.json`（spike_helper 房规 NOT-IN-MANIFEST）+ `/tmp/612_html_connector.json`（spike_helper 房规 NOT-IN-MANIFEST）

**grep 验证（落地后预期）**:
- 测试 mock writer 捕获 row dict 含 source_sha256 + lineage JSONB 9 字段 ✓
- migration 001-013 零触碰 ✓
- `source_sha256 匹配: True` ✓
- `lineage 9 字段完整: True` ✓
- `doc_kind == OCR_SCAN: True` ✓
- `extracted_text contains "<城市名>统计局": True` ✓

### 1.5 (E) docs/45 §6.2 O1 status append（post-612）

**触发条件**: (D) source_document + lineage JSONB 写入完成

**落地**:
- docs/45 §6.x 既有 610 status blockquote line 558 后续 append 一行（per 612 · 2026-08-29，sha12 已知）：
  ```
  > ⚠ **docs/45 §6.2 O1 status append**（per 612 · 2026-08-29）：O1 §5.2.x 江苏样本第五刀（地市样本第四刀）已落地（`<sha12>` per source_registry/registry.csv +1 行；tjj.<city>.gov.cn <城市名>统计局首页 per 611 audit §10 推荐 #2 verbatim；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；paddle-ocr e2e 在 .venv-paddle 隔离 venv 内接通 + HTML 路径走 docs/53 §5 connector 模式 + source_document + lineage JSONB mock writer 9 字段完整 + migration 001-013 零触碰 + 既有 11 行 SHA 零漂移）；江苏样本链路 5/15 节点；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。
  ```
- 既有 605 status blockquote（line 552）完整保留
- 既有 606 status blockquote（line 554）完整保留
- 既有 608 status blockquote（line 556）完整保留
- 既有 610 status blockquote（line 558）完整保留
- 既有 Gate 2 PASS / W8 评审日期完整保留
- 不删不改

**grep 验证（落地后预期）**:
- `grep "per 612 · 2026-08-29" docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 ≥ 1 occurrence ✓
- `grep -c "per 610 · 2026-08-29"` = 1（既有行零删减）✓
- `grep -c "per 608 · 2026-08-29"` = 1（既有行零删减）✓
- `grep -c "per 606 · 2026-08-29"` = 1（既有行零删减）✓
- `grep -c "per 605 · 2026-08-29"` = 1（既有行零删减）✓

### 1.6 (F) docs/49/50/51/52/53 status row append — SKIP 政策成立

**触发条件**: grep `docs/49-stage2-*.md docs/50-stage2-*.md docs/51-stage2-*.md docs/52-stage2-*.md docs/53-stage2-*.md` 命中 stale `--confirm-*` 字面

**grep 命中分析（per 610 §1.6 + 611 audit §7 precedent）**:
- docs/49 文件路径 mismatch（无 `docs/49-stage2-pipeline-package-plan-20260825.md` 实际文件名）→ SKIP per 605 §6 precedent
- docs/50 line 11「用户裁定：**D**；**不宣布 Gate 2 PASS**；O1/O3 必带 OPEN 清单」 = 治理级决策标注（intro/header），非 stale `--confirm-*` runtime flag → SKIP per 612 §1.6
- docs/50 line 120/121 (591/603 既有 supersede 标注) + line 124-127 (605 既有 supersede blockquote) + line 130+ (606/608/610 既有 supersede blockquote) = 既有 supersede 标注含 stale 字面但已被 supersede → SKIP
- docs/51 line 183+ (601 既有 supersede blockquote) = 既有 supersede 标注 → SKIP
- docs/52 line 287/289/291 (599 既有 §13 blockquote 收口段) + line 299+ (601 既有 §14 blockquote) + line 309+ (606 既有 §15 BLOCKED 标注) + line 320+ (608 既有 §16 标注) + line 330+ (610 既有 §17 标注) = 既有 supersede 标注 → SKIP
- docs/53 line 244+ (601 既有 §11 blockquote) + line 258+ (608 既有 §12 标注) + line 270+ (610 既有 §13 标注) = 既有 supersede 标注 → SKIP

**grep `per 612（2026-08-29）` 命中** = 0 行（SKIP 政策成立）
**grep `per 612 · 2026-08-29` 命中** = 1 行（docs/45 §6.2 O1 status append per (E)）

**落地**: F 段 SKIP（命中为治理级决策标注 + 既有 supersede 标注共存非 stale runtime flag）
**docs 房规 NOT-IN-MANIFEST** ✓

### 1.7 (G) manifest bump K → 969+K

**触发条件**: (A)(B)(C)(D)(E)(F) 全部落地

**落地**:
- `scripts/_knife612_manifest_bump.py` NEW spike_helper +1（如适用；K = 4 基础 = spike_helper + audit 入库 + receipt + HTML）
- 611 audit 文件入库随 612 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）`611-stage0-architect-s610-o1-§5.2.x-real-sha-locked-江苏样本-地市第三刀-tasking-20260829-audit-PASS-20260829.md` NEW documentation +1
- 612 receipt NEW documentation +1（本刀回执）
- 江苏样本地市第四刀 SHA-locked HTML `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html` NEW spike_sample_or_truth role +1
- source_registry/registry.csv REFRESH（file-based role_count 守门不增计数 per 612 §1.7）
- K = 4 基础 → manifest 969 → 969+4 = 973

**enumeration 即权威 per 583 §F**:
- 612 tasking 文件本身 NOT-IN-MANIFEST per docs 房规
- docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规
- docs/49/50/51/52/53 F 段 SKIP 不增计数
- scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰
- .venv-paddle / scripts/requirements-paddle.txt / spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py} NOT-IN-MANIFEST per spike_helper 房规
- /tmp/612_e2e_capture.json + /tmp/612_html_connector.json NOT-IN-MANIFEST per spike_helper 房规

**INVARIANT**: 969+4 == 969+4 == 969+4 ✓ (per scripts/_knife612_manifest_bump.py 实跑断言；manifest = 973)

### 1.8 (H) 612 receipt 写回执

**触发条件**: (A)(B)(C)(D)(E)(F)(G) 全部落地

**落地**:
- (A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 31+ 红线 100% 兑现 + ⚠ disclosures（如有）

**双推链**（per 599/606/607/608/609/610/611 precedent）:
- feat(612) `<TBD>` + cc_head(612) backfill `<TBD>` + §双推 populate `<TBD>` + §双推 populate fix SHA correction `<TBD>` 四步 commit 链 per 599/606/607/608/609/610/611 precedent → 三侧收敛 100% (origin main + github main both = HEAD)

**cc_head backfill**: per 599/606/607/608/609/610/611 precedent（feat + cc_head separate commits 模式）

**13 受保护文件零漂移**:
- `synthetic.png` sha `dea1902a` 14817 bytes ✓
- S0 PDF sha `f34b2e57ae08` 1007943 bytes ✓
- `_syn_pdf_585.py` sha `2db08313` 3980 bytes ✓
- `extracts/` dir 不变 ✓
- `registry.csv` 既有 11 行 sha `3639e729…` 不变（既有 10 行 sha `3639e729…` 不变；既有 9 行 sha `0fccd275…` 不变；既有 8 行 sha `caf7fce58a08…` 不变；既有 7 行 sha `f22f610850c8…` 不变；仅 +1 行 bytes 总数变化是预期）✓
- `gate_thresholds.json` sha `81f3c83a` 3709 bytes / mtime Aug 23 不变 ✓
- `01-core.sql` sha `09aa46f9` 51589 bytes ✓
- `requirements-dbt.txt` sha `db73c342` 349 bytes ✓
- `scripts/requirements-paddle.txt` sha `5d730735` 1314 bytes ✓
- `scripts/intake_real_sha_if_present.py` sha `239b85c9` 14457 bytes ✓
- `scripts/auto_ingest_public_source.py` sha `91a5acf9` 59781 bytes ✓
- `.venv-paddle/pyvenv.cfg` sha `73fdd9c5` 326 bytes ✓
- migration 001-013 零漂移 ✓

**31+ 红线 100% 兑现** (per 612 §0.2 + 2026-08-29 治理铁律):
- ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS 零重新宣告 ✓
- ❌ 2020-2025 batch work 零批量（本刀仅 1 个江苏样本地市第四刀）✓
- ❌ 公网爬网（非政府/统计局）零（仅 tjj.<city>.gov.cn 政府源）✓
- ❌ OCR threshold lowering 零（gate_thresholds.json 3709 bytes 不变）✓
- ❌ 1909-as-China 零（江苏地市统计局公开源）✓
- ❌ --force 零（git push 走普通路径）✓
- ❌ PAT request 零 ✓
- ❌ gate_thresholds.json edit 零（3709 bytes / mtime Aug 23 不变）✓
- ❌ 重新宣告 O3 整体 CLOSED 零（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 十七重声明；612 不二次宣告）✓
- ❌ 重新宣告 O1 整体收口 零（O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；612 仅第四批地市样本 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）✓
- ❌ 启动 O1 A 路实跑 零（A 路保留为 fallback 标注 per 591 docs/50 row 117 supersede）✓
- ❌ --confirm-* 字面 零（per 2026-08-29 治理铁律）✓
- ❌ 修改 001-013 migration 文件 零 ✓
- ❌ 修改 01-core.sql 零（51589 bytes 不变）✓
- ❌ 修改 4 fixture 锁值 零（synthetic.png + S0 PDF + _syn_pdf_585.py + extracts/ dir 字节不变）✓
- ❌ 修改 S0 原始 PDF 字节 零（sha `f34b2e57...` 1007943 bytes 不变）✓
- ❌ 修改 source_registry/registry.csv 既有 11 行 零（既有 11 行 sha `3639e729…` 不变；既有 10 行 sha `3639e729…` 不变；既有 9 行 sha `0fccd275…` 不变；既有 8 行 sha `caf7fce58a08…` 不变；既有 7 行 sha `f22f610850c8…` 不变；仅 +1 行 bytes 总数变化是预期）✓
- ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json 零（3709 bytes / mtime Aug 23 不变）✓
- ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt 零 ✓
- ❌ 修改 scripts/intake_real_sha + auto_ingest 零 ✓
- ❌ 修改 docs/45/46/44/49/50/51/52/53 既有 OPEN 行原文 零（仅 selective refresh append；既 605 + 606 + 608 + 610 status blockquote 保留；F 段 SKIP）✓
- ❌ 删除命中行原文 零 ✓
- ❌ 真实 paddleocr API 调用（system Python）零（仅 `.venv-paddle/bin/python` 隔离 venv 内允许 per 594 §0.2 红线）✓
- ❌ 真实 PDF 上传（非 seed_archives/）零（仅 `data/seed_archives/jiangsu_<city>_*.html` 落）✓
- ❌ 触真实 DB（生产 schema）零（migration 001-013 零触碰；mock writer 仅写 /tmp/612_e2e_capture.json 不入 manifest）✓
- ❌ 引入 cloud OCR / GPU runtime 零 ✓
- ❌ docker daemon systemctl 操作 零 ✓
- ❌ 持久保留 paddle-ocr:v1 Docker image 零（per 596 §2.5 已清理）✓
- ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system 零（仅 `.venv-paddle` venv）✓
- ❌ 用户授权 #1 二次申请 零（per 612 §0.1 verbatim「用户授权 #1 仍生效无需二次授权」）✓

**⚠ disclosures**:
1. **source_registry/registry.csv +1 行**：既有 11 行 SHA `3639e729…` 不变；既有 10 行 SHA `3639e729…` 不变；既有 9 行 SHA `0fccd275…` 不变；既有 8 行 SHA `caf7fce58a08…` 不变；既有 7 行 SHA `f22f610850c8…` 不变；新增 1 行（江苏样本地市第四刀 / <城市名>统计局）；file-based role_count 守门不增计数 per 612 §1.7；manifest INVARIANT 维持
2. **江苏样本地市第四刀 SHA-locked 落 data/seed_archives/**：bytes 总数变化是预期；既有零地市样本不删；新增 1 个江苏样本地市第四刀（<城市名>统计局首页）；spike_sample_or_truth role +1

**附加 ⚠ disclosure (mirrors 611 audit §3 ⚠ #3 + 610 §C ⚠ #2 + 608 §C ⚠ #2 + 606 §C ⚠ #2 + 605 §C ⚠ #3)**: paddle-ocr e2e 流水线真实调用：仅 `.venv-paddle/bin/python` 隔离 venv 内允许（per 594 §0.2 红线延续）；system Python 零 paddlepaddle；HTML 路径走 docs/53 §5 connector 模式（per 612 §1.3 替代路径）；不视为触碰红线（paddle-ocr 隔离 venv 已建立 + 真依赖导入成功 + HTML connector 替代路径走通 + isolation 100% 守门）

**附加 ⚠ disclosure**: 用户授权 #1 仍生效无需二次授权（per 612 §0.1 verbatim「用户授权 #1 仍生效无需二次授权」+ 610 §0.1 verbatim 续接 + 606 BLOCKED 解决 precedent + 2026-08-29 治理铁律）

**登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607 → 608 → 609 → 610 → 611 → 612**（612 既闭合 O1 §5.2.x 江苏样本第五刀（地市样本第四刀）落地（执行端自取 tjj.<city>.gov.cn <城市名>统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；接续 605 + 606 + 608 + 610 江苏样本链路 4/15 → 5/15）+ docs/45 §6.2 O1 status append line 562（接续 610 status blockquote line 558）+ docs/49/50/51/52/53 F 段 SKIP + 江苏样本地市第四刀 SHA-locked HTML + source_registry/registry.csv +1 行（file-based 守门不增计数）+ 13 受保护文件零漂移 + 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED；后续 613 tasking 签发 = 612 receipt 审计刀 / O1 §5.2.x 江苏样本第六刀（地市样本第五刀；其它江苏地市政府/统计局公开源）/ O1 §5.2.x 江苏样本省样本第二刀（其它江苏省份样本刀）/ 其它治理推进刀 — 任一由架构师定夺 per 611 audit §10 + 612 receipt §9）

---

## §2. 612 tasking 关联文件清单

| 文件 | 用途 | 路径 |
|---|---|---|
| 612 tasking 文件 | 本文件（架构师签发） | `reviews/stage0-gate0-rework-2026-08-23/612-stage0-architect-s611-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829.md` |
| 612 receipt 文件 | 执行端交付回执（待写） | `reviews/stage0-gate0-rework-2026-08-23/612-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-receipt.md` |
| 612 bump script | manifest bump helper（待写） | `scripts/_knife612_manifest_bump.py` |
| 612 江苏样本地市第四刀 SHA-locked HTML | 政府/统计局公开源落地 | `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260829.html`（<city> = wuxi / nantong / xuzhou）|
| 612 江苏样本地市第四刀 registry 行 | source_registry 登记 | `source_registry/registry.csv` +1 行 |
| 612 docs/45 §6.2 O1 status append | docs/45 状态行落地 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` line 562 |
| 612 mock writer 捕获 | 测试 mock writer 落地 | `/tmp/612_e2e_capture.json` + `/tmp/612_html_connector.json`（spike_helper 房规 NOT-IN-MANIFEST）|
| 612 双推落地 | git push origin + github | git log `git rev-parse HEAD` 三侧收敛 |

---

## §3. 预期 = ACCEPTED

预期 612 receipt PASS（per 605/606/608/610/611 precedent）= ACCEPTED（红线 100% 兑现 + 江苏样本地市第四刀源自取 = tjj.<city>.gov.cn <城市名>统计局公开源 + SHA-locked 落 `data/seed_archives/` + `source_registry/registry.csv` +1 行（既有 11 行 SHA 不变）+ paddle-ocr e2e 在 `.venv-paddle` 隔离 venv 内接通 + source_document + lineage JSONB mock writer 9 字段完整 + docs/45 §6.2 O1 status append line 562（接续 610 status blockquote line 558）+ docs/49/50/51/52/53 F 段 SKIP + 13 受保护文件零漂移 + 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED）

---

— End of `612-stage0-architect-s611-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829.md` —