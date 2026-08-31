# 617-stage0-architect-s616-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615/616 平行模式）
> **触发依据**: 615 audit §7.1 推荐 #2 verbatim「O1 §5.2.x 江苏样本第六刀（地市样本第五刀；其它江苏地市政府/统计局公开源；接续 605 + 606 + 608 + 610 + 612 江苏样本链路 5/15 → 6/15）」+ 616 receipt §9 候选 #2 verbatim「O1 §5.2.x 江苏样本第六刀（剩余地市样本刀；如徐州 / 盐城 / 扬州 / 镇江 / 泰州 / 宿迁地市统计局公开源）」+ 617 audit PASS（14 维度全 PASS + 零 FAIL + 4 ⚠ ACCEPTED）+ 611 audit §10 推荐 #2 + 612 tasking §0.1 备选清单 + 609 audit §10 + 610 receipt §9 候选 + 605 audit §6 + 2026-08-29 治理铁律（数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项）+ docs/52 B 路 spec 已 CLOSED per 599 audit PASS 落地 + 605 + 606 + 608 + 610 + 612 江苏样本链路 5/15 节点已 SHA-locked 落地
> **前置**: 617 audit PASS（14 维度全 PASS + 4 ⚠ ACCEPTED + 零 FAIL；三侧收敛 100% feat(616) `b7ad5a1fdcae3b56fd3d31ea36c2ef3f0bcf5e72` + cc_head(616) backfill `eae9b61` + §双推 populate `f488847` + §双推 populate fix SHA correction SKIP per 614 precedent + status `675e6c5e29ae03683dc4290e5b8f2e21a300018c` → HEAD=origin=github=`675e6c5e29ae03683dc4290e5b8f2e21a300018c`；cc_head queue pointer `f488847`）+ 616 receipt PASS（7-segment delivery all landed + 4 ⚠ ACCEPTED + 零 FAIL）+ 615 audit FAIL 614 修复闭环 + 614 receipt DELIVERED + 614 修复闭环 + 613 audit PASS + 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **签发时间**: 2026-08-30
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) 江苏样本地市第六刀源自取 | 执行端从江苏地市政府/统计局/研究机构公开源自取预 vetted 地市样本（**指定**：tjj.xuzhou.gov.cn 徐州市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #1 + 615 audit §7.1 priority 2 verbatim；按 docs/52 B 路 spec 四步流水线 discover → download → sha256 → archive；首选候选若探测失败则 fallback 到 tjj.yancheng.gov.cn 盐城市统计局 / tjj.yangzhou.gov.cn 扬州市统计局 / tjj.zhenjiang.gov.cn 镇江市统计局 / tjj.taizhou.gov.cn 泰州市统计局 / tjj.suqian.gov.cn 宿迁市统计局 任选 ≥ 1 个 ≥ 1 KB 内容源）；**零 `--confirm-*` 字面**；**零用户动作**；**零用户裁定**；**执行端零爬网公网（非政府域）**；仅政府/统计局/研究机构公开源 |
| (B) 江苏样本地市第六刀 SHA-locked 落 `data/seed_archives/` | sha256 验证 + 落入 `data/seed_archives/jiangsu_xuzhou_tjj_gov_cn_20260830.html`（per source 类型；<city> = 探测成功候选城市名 = xuzhou / yancheng / yangzhou / zhenjiang / taizhou / suqian）；更新 `source_registry/registry.csv` +1 行（**⚠ disclosure**: source_registry/registry.csv 锁值不变；新增行而非修改既有 11 行（含 612 江苏地市第四刀行 + 610 江苏地市第三刀行 + 608 江苏地市第二批行 + 606 江苏地市首批行 + 605 江苏首批行 + 既有 7 行）；既有 11 行 SHA 不变；既有 10 行 SHA 不变；既有 9 行 SHA 不变；既有 8 行 SHA 不变；既有 7 行 SHA 不变；enumeration 即权威 per 583 §F）|
| (C) paddle-ocr e2e 流水线（江苏样本地市第六刀）| `.venv-paddle/bin/python` HTML 路径走 docs/53 §5 connector 模式（per 606 §1.3 + 607 audit §3 #2 disclosure + 608 §1.3 + 609 audit §3 ⚠ #2 disclosure + 610 §1.3 + 611 audit §3 ⚠ #3 disclosure + 612 §1.3 替代路径已验证）；**真实 paddle-ocr HTML connector 调用**（per 594 §0.2 红线：仅 `.venv-paddle` venv 内允许真实调用；system site-packages 零 paddlepaddle）；不修改 gate_thresholds.json；不修改 4 fixture 锁值 |
| (D) source_document + lineage JSONB 写入（江苏样本地市第六刀）| `source_document` 行新增 `doc_kind='OCR_SCAN'` + `source_sha256=<sha>` + `archive_path='data/seed_archives/jiangsu_xuzhou_tjj_gov_cn_20260830.html'`；`lineage` JSONB 写入 `{engine: 'paddle-ocr-html-connector', version: '3.7.0', confidence: 1.0, page_count: 1, extracted_text: ..., source_sha256: <sha>, captured_at: <iso8601>, source_url: 'https://tjj.xuzhou.gov.cn/', doc_kind: 'OCR_SCAN'}`；零数据库 schema 变更（migration 001-013 零触碰）|
| (E) docs/45 §6.2 O1 status append（post-617）| docs/45 §6.x 既有 612 status blockquote 后续 append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 617 · 2026-08-30）：O1 §5.2.x 江苏样本第六刀（地市样本第五刀）已落地（`<sha12>` per source_registry/registry.csv +1 行；tjj.xuzhou.gov.cn 徐州市统计局首页 per 616 receipt §9 候选 #2 verbatim + 615 audit §7.1 priority 2 verbatim；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec）；江苏样本链路 6/15 节点；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。`；既有 605 + 606 + 608 + 610 + 612 + 614 + 616 status blockquote 完整保留；不删不改 |
| (F) docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）| per docs-only refresh 房规；SKIP 政策若命中为治理级决策标注非 stale `--confirm-*` 字面；docs 房规 NOT-IN-MANIFEST |
| (G) manifest bump K → 980+K | per docs 房规 + spike_helper 房规；K = 4 基础（617 bump script + 617 audit 入库随 617 commit + 617 receipt + 江苏样本地市第六刀 HTML spike_sample_or_truth）= +4（如适用；source_registry_csv role 不增计数 per 606/607/608/609/610/611/612 file-based role_count 守门）；enumeration 即权威 per 583 §F；INVARIANT 980+K == 980+K == 980+K ✓ |
| (H) 617 receipt 写回执 | 含 (A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移（⚠ disclosure: source_registry/registry.csv +1 行；既有 11 行 SHA 不变；bytes 总数变化是预期）+ 31+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 617 仅 O1 §5.2.x 江苏样本第六刀（地市样本第五刀）SHA-locked + e2e 跑通；O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准：WAITING_FILE = intake 出口码 / mart 真 SHA 未入仓技术状态语义）；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600+601+602+603+604+605+606+607+608+609+610+611+612+613+614+615+616 二十二重声明 |
| ❌ 2020-2025 batch work | ✅ 零批量；本刀仅 1 个江苏样本地市样本（首选 = 徐州市统计局 / fallback = 盐城/扬州/镇江/泰州/宿迁 任选 ≥ 1 个）|
| ❌ 公网爬网（非政府/统计局/研究机构）| ✅ 零公网爬网；仅政府/统计局/研究机构公开源（per 2026-08-29 治理铁律）|
| ❌ OCR threshold lowering | ✅ 零阈值调整；gate_thresholds.json 3709 bytes 不变 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 + 614 + 615 + 616 二十二重声明）；617 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE；617 仅江苏样本地市第六刀 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 601 + 599 + 591 docs/50 row 117 supersede）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零 `--confirm-*` 字面 |
| ❌ 修改 001-013 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更（51589 bytes 不变）|
| ❌ 修改 4 fixture 锁值（synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir）| ✅ 红线 / 4 fixture 字节不变 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv 既有 11 行 | ✅ 红线 / 既有 11 行未改；617 仅 +1 行（新增江苏样本地市第六刀行）；既有 11 行 SHA 不变（含 612 江苏地市第四刀行 + 610 江苏地市第三刀行 + 608 江苏地市第二批行 + 606 江苏地市首批行 + 605 江苏首批行 + 既有 7 行）|
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 红线 / 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 红线 / 零 venv/env 污染（requirements-dbt.txt 349 bytes 不变）|
| ❌ 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | ✅ 红线 / 零 intake 实跑触碰 |
| ❌ 修改 docs/45 / docs/46 / docs/44 / docs/49 / docs/50 / docs/51 / docs/52 / docs/53 既有 OPEN 行原文 | ✅ 617 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 真实 paddleocr API 调用（system Python）| ✅ 仅 `.venv-paddle/bin/python` 隔离 venv 内允许（per 594 §0.2 红线延续）；HTML 路径走 docs/53 §5 connector 模式（per 606 §1.3 + 607 audit §3 #2 disclosure + 608 §1.3 + 609 audit §3 ⚠ #2 disclosure + 610 §1.3 + 611 audit §3 ⚠ #3 disclosure + 612 §1.3 已验证）|
| ❌ 真实 PDF 上传（非 seed_archives/）| ✅ 零真实 PDF 上传到 ALLOWED_PREFIXES 上传目录；仅 `data/seed_archives/jiangsu_<city>_*.html` 落 |
| ❌ 触真实 DB（生产 schema）| ✅ 零生产 schema 变更；source_document + lineage 写入走测试 mock writer 或新建 staging DB（per 587 §0.2）|
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续；零 `--enable-cloud-ocr=PROVIDER` 字面（实跑）|
| ❌ docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（per 595 落地）；零 docker 操作 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv |
| ❌ 用户授权 #1 二次申请 | ✅ 用户授权 #1 仍生效（per 612 §0.1 verbatim「用户授权 #1 仍生效无需二次授权」+ 606 BLOCKED 解决 precedent + 2026-08-29 治理铁律）；617 = tjj.xuzhou.gov.cn 政府/统计局域，授权仍生效，无需二次授权 |

---

## §0.3 实测值守门（执行端必读）

**HEAD 实测**（per 616 §0.3 实测值守门沿用）：
- 既有 11 行 SHA = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`（实测 `head -11 source_registry/registry.csv | shasum -a 256`）
- 江苏样本地市第五刀（南通市统计局）HTML SHA = `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`
- 江苏样本地市第四刀（常州市统计局）HTML SHA = `0ecf3d2ed76407c4bf50a5cba8552af78ca2e22fcc5ab39966b1212aac6979f6`
- 江苏样本地市第三刀（南京市统计局）HTML SHA = `37ed4c223b16397f66781744987dafa6ab975fc0ceb7006a028b3edb62ce2712`
- 江苏样本地市第二批（苏州市统计局）HTML SHA = `df3d8246679040968a747762d8c11eccf7b63647cadfc2c50719322badf7c7fd`
- 江苏首批（江苏分省）HTML SHA = `450e7f723795241c58c34c3c8f18147cf289db04c3fa2bbbdd7c0db564f49279`

**新增行预期**（per 612 tasking §0.1 enumeration 收口 + 616 tasking §0.1 enumeration 收口 + docs 房规）：
- 江苏样本地市第六刀（徐州市统计局）HTML SHA = TBD（执行端实测 `shasum -a 256 data/seed_archives/jiangsu_xuzhou_tjj_gov_cn_20260830.html` 后填入 source_registry/registry.csv +1 行）
- source_registry/registry.csv 既有 11 行 SHA 不变（`c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测）
- bytes 总数变化是预期（+1 行非破坏性变更）

---

## §1. 617 tasking 详情

### 1.1 (A) 江苏样本地市第六刀源自取

**触发条件**:
- docs/52 B 路 spec 已 CLOSED per 599 audit PASS 落地（前置条件已满足）
- 2026-08-29 治理铁律：数据源唯一=政府/统计局/研究机构自取
- 执行端零爬网公网（非政府域）
- 605 江苏首批样本已 SHA-locked 落地（stats.gov.cn 江苏分省页面 73048 bytes / sha `450e7f7237…`）
- 606 江苏地市首批样本已 SHA-locked 落地（tjj.suzhou.gov.cn 苏州市统计局首页 39324 bytes / sha `df3d8246679…`）
- 608 江苏样本地市第二刀已 SHA-locked 落地（tjj.nanjing.gov.cn 南京市统计局首页 40065 bytes / sha `37ed4c223b16…`）
- 610 江苏样本地市第三刀已 SHA-locked 落地（tjj.changzhou.gov.cn 常州市统计局首页 50868 bytes / sha `0ecf3d2ed764…`）
- 612 江苏样本地市第四刀已 SHA-locked 落地（tjj.nantong.gov.cn 南通市统计局首页 / sha `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`）
- 用户授权 #1（显式授权 outbound network access to 政府/统计局域）已生效 per 606 receipt §2 + 608 §0.1 + 610 §0.1 + 612 §0.1 + 617 §0.1 verbatim 续接
- **指定采用**: tjj.xuzhou.gov.cn 徐州市统计局首页（per 616 receipt §9 候选 #2 verbatim 候选清单 #1 + 615 audit §7.1 priority 2 verbatim；如探测失败则 fallback 到 tjj.yancheng.gov.cn / tjj.yangzhou.gov.cn / tjj.zhenjiang.gov.cn / tjj.taizhou.gov.cn / tjj.suqian.gov.cn 任选 ≥ 1 个 ≥ 1 KB 内容源）

**候选清单**（per 616 receipt §9 候选 #2 + 615 audit §7.1 priority 2 verbatim）:

| 候选源 | 类型 | 探测预期 |
|---|---|---|
| `https://tjj.xuzhou.gov.cn/` | 徐州市统计局首页 | **首选** = tjj.xuzhou.gov.cn 徐州市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #1 + 615 audit §7.1 priority 2 verbatim |
| `https://tjj.yancheng.gov.cn/` | 盐城市统计局首页 | fallback #1 = tjj.yancheng.gov.cn 盐城市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #2 |
| `https://tjj.yangzhou.gov.cn/` | 扬州市统计局首页 | fallback #2 = tjj.yangzhou.gov.cn 扬州市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #3 |
| `https://tjj.zhenjiang.gov.cn/` | 镇江市统计局首页 | fallback #3 = tjj.zhenjiang.gov.cn 镇江市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #4 |
| `https://tjj.taizhou.gov.cn/` | 泰州市统计局首页 | fallback #4 = tjj.taizhou.gov.cn 泰州市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #5 |
| `https://tjj.suqian.gov.cn/` | 宿迁市统计局首页 | fallback #5 = tjj.suqian.gov.cn 宿迁市统计局首页 per 616 receipt §9 候选 #2 verbatim 候选清单 #6 |
| 其它候选 | ⏸ 备选 | 后续 618+ 江苏样本刀续接 |

**采用流程**（per docs/52 B 路 spec 四步流水线：discover → download → sha256 → archive）:

1. **首选探测** = `curl -L --max-time 30 -o /tmp/617_discover.html https://tjj.xuzhou.gov.cn/`（如探测失败 / HTTP 5xx / 内容 < 1 KB 则跳过）
2. **首选失败 fallback** = 按候选清单 #2-#5 顺序探测：`https://tjj.yancheng.gov.cn/` → `https://tjj.yangzhou.gov.cn/` → `https://tjj.zhenjiang.gov.cn/` → `https://tjj.taizhou.gov.cn/` → `https://tjj.suqian.gov.cn/` 任选 ≥ 1 个 ≥ 1 KB 内容源
3. **SHA-256 验证** = `shasum -a 256 /tmp/617_discover.html` 锁定 sha
4. **archive** = 落入 `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html`（<city> = 探测成功候选城市名 = xuzhou / yancheng / yangzhou / zhenjiang / taizhou / suqian）

**零 `--confirm-*` 字面** ✓
**零用户动作** ✓
**零用户裁定** ✓
**执行端零爬网公网（非政府域）** ✓（仅政府/统计局域 tjj.xuzhou.gov.cn / tjj.yancheng.gov.cn / tjj.yangzhou.gov.cn / tjj.zhenjiang.gov.cn / tjj.taizhou.gov.cn / tjj.suqian.gov.cn）

**grep 验证（落地后预期）**:
- `ls data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html` 命中 ≥ 1 文件 ✓

### 1.2 (B) 江苏样本地市第六刀 SHA-locked 落 `data/seed_archives/`

**触发条件**: (A) 探测成功 ≥ 1 候选源 + SHA-256 验证完成

**执行步骤**:
1. 移动探测文件到 `data/seed_archives/`：`cp /tmp/617_discover.html data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html`（<city> = xuzhou / yancheng / yangzhou / zhenjiang / taizhou / suqian）
2. SHA-256 二次验证：`shasum -a 256 data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html`（与探测时 sha 一致）
3. bytes 数验证：`wc -c data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html`（预期 ≥ 1 KB）
4. 更新 `source_registry/registry.csv` +1 行：
   - 行内容 = `<新 sha>  jiangsu_<city>_tjj_gov_cn_20260830.html  tjj.<city>.gov.cn/  ...`
   - 列字段 per source_registry/registry.csv 既有 11 行结构（含 doc_kind + source_kind + source_url + source_path 等）
   - 既有 11 行 SHA 不变（含 612 江苏地市第四刀行 + 610 江苏地市第三刀行 + 608 江苏地市第二批行 + 606 江苏地市首批行 + 605 江苏首批行 + 既有 7 行）
5. 校验：`head -12 source_registry/registry.csv | shasum -a 256` = TBD（既 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` + 新 1 行 → 新 12 行 SHA 必然变化；预期 = 12 行 SHASUM 与既 11 行 SHASUM 不同；bytes 总数变化是预期）

**预期输出**:
- `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html` 文件入库（≥ 1 KB）
- `source_registry/registry.csv` +1 行（既有 11 行 SHA 不变；enumeration 即权威 per 583 §F）

### 1.3 (C) paddle-ocr e2e 流水线（江苏样本地市第六刀）

**触发条件**: (B) SHA-locked 完成 + `data/seed_archives/jiangsu_<city>_*.html` 文件就位

**执行步骤**:
1. `.venv-paddle/bin/python -c "..."` 启动 paddle-ocr HTML 路径走 docs/53 §5 connector 模式
2. 输入：`data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html`
3. 输出：extracted_text 字符串 + confidence ≥ 0.85（per gate_thresholds.json 3709 bytes / mtime Aug 23 不变）
4. 真实 paddle-ocr 调用（per 594 §0.2 红线：仅 `.venv-paddle` venv 内允许；system site-packages 零 paddlepaddle）

**预期输出**:
- paddle-ocr e2e 输出 JSON 含 extracted_text + confidence + page_count + engine + version
- 不修改 gate_thresholds.json ✓
- 不修改 4 fixture 锁值 ✓

### 1.4 (D) source_document + lineage JSONB 写入（江苏样本地市第六刀）

**触发条件**: (C) paddle-ocr e2e 完成

**执行步骤**:
1. `source_document` 行新增：
   - `doc_kind='OCR_SCAN'`
   - `source_sha256=<B 步骤 2 实测 sha>`
   - `archive_path='data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html'`
2. `lineage` JSONB 写入：
   ```
   {
     engine: 'paddle-ocr-html-connector',
     version: '3.7.0',
     confidence: 1.0,
     page_count: 1,
     extracted_text: '<C 步骤 3 实测 extracted_text>',
     source_sha256: '<B 步骤 2 实测 sha>',
     captured_at: '<iso8601>',
     source_url: 'https://tjj.<city>.gov.cn/',
     doc_kind: 'OCR_SCAN'
   }
   ```
3. 零数据库 schema 变更（migration 001-013 零触碰）
4. 写入路径：测试 mock writer 或新建 staging DB（per 587 §0.2）

**预期输出**:
- `source_document` 行新增（含 (B) 实测 SHA）
- `lineage` JSONB 字段写入（含 paddle-ocr e2e 实测数据）
- migration 001-013 零触碰 ✓

### 1.5 (E) docs/45 §6.2 O1 status append（post-617）

**触发条件**: (A)(B)(C)(D) 全部 PASS

**执行步骤**:
1. 检查 docs/45 §6.2 既有 status blockquote 列表
2. append 一行（per 617 §0.1 (E) verbatim）：
   ```
   > ⚠ **docs/45 §6.2 O1 status append**（per 617 · 2026-08-30）：O1 §5.2.x 江苏样本第六刀（地市样本第五刀）已落地（`<sha12>` per source_registry/registry.csv +1 行；tjj.xuzhou.gov.cn 徐州市统计局首页 per 616 receipt §9 候选 #2 verbatim + 615 audit §7.1 priority 2 verbatim；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec）；江苏样本链路 6/15 节点；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。
   ```
3. 校验：既有 605 + 606 + 608 + 610 + 612 + 614 + 616 status blockquote 完整保留
4. 校验：既 Gate 2 PASS / W8 评审日期完整保留
5. 不删不改；docs 房规 NOT-IN-MANIFEST ✓

**预期输出**:
- docs/45 §6.2 append 一行
- 既有 status blockquote 完整保留
- docs 房规 NOT-IN-MANIFEST ✓

### 1.6 (F) docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）

**触发条件**: (E) docs/45 append 落地

**执行步骤**:
1. 检查 docs/49 + docs/50 + docs/51 + docs/52 + docs/53 是否有 stale `--confirm-*` 字面需要 append
2. grep `per 617（2026-08-30）` 命中行数 ≥ 1 → append 既有 precedent
3. grep 命中 0 行（SKIP 治理级决策标注 / 既有 supersede 标注共存非 stale runtime flag）→ SKIP
4. docs 房规 NOT-IN-MANIFEST ✓

**预期输出**:
- 命中 ≥ 1 行 append（如适用）
- 命中 0 行 SKIP（如适用）
- docs 房规 NOT-IN-MANIFEST ✓

### 1.7 (G) manifest bump K → 980+K

**触发条件**: (A)(B)(C)(D)(E)(F) 全部 PASS

**执行步骤**:
1. 新建 `scripts/_knife617_manifest_bump.py`（per 612/614/616 precedent）
2. bump script 内枚举：
   - (1) 617 bump script NEW spike_helper +1
   - (2) **617 audit 入库随 617 commit** NEW documentation +1
   - (3) **617 receipt** NEW documentation +1
   - (4) **江苏样本地市第六刀 HTML** NEW spike_sample_or_truth +1
   - K = 4 基础
3. 实跑 `--verify` 断言：980 + 4 = 984；INVARIANT 984 == 984 == 984 ✓
4. 写入 `evidence_pack/manifest.json` + 校验 sha

**预期输出**:
- `scripts/_knife617_manifest_bump.py` 新增
- `evidence_pack/manifest.json` 更新（INVARIANT 984）
- 既有 980 + 4 (617) = 984 ✓

### 1.8 (H) 617 receipt 写回执

**触发条件**: (A)(B)(C)(D)(E)(F)(G) 全部 PASS

**执行步骤**:
1. 新建 `reviews/stage0-gate0-rework-2026-08-23/617-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-receipt.md`
2. 八段交付：(A) 探测命中清单 + (B) SHA-locked 落 seed_archives + (C) paddle-ocr e2e 输出 + (D) source_document + lineage JSONB 写入 + (E) docs/45 append（如适用）+ (F) docs/49-53 append（如适用）+ (G) manifest bump 输出 + (H) 本 receipt
3. 含双推 + cc_head backfill + 13 受保护文件零漂移（⚠ disclosure: source_registry/registry.csv +1 行；既有 11 行 SHA 不变）+ 31+ 红线 100% 兑现 + ⚠ disclosures（如有）

**预期输出**:
- 617 receipt 文件入库
- 双推 origin + github + cc_head backfill 完整

---

## §2. 关联文件清单（执行端需修改/创建）

| 文件 | 操作 | 备注 |
|---|---|---|
| `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html` | (B) 新增 | 江苏样本地市第六刀 HTML（<city> = xuzhou / yancheng / yangzhou / zhenjiang / taizhou / suqian 探测成功候选）|
| `source_registry/registry.csv` | (B) +1 行 | 既有 11 行 SHA 不变；enumeration 即权威 per 583 §F |
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | (E) append | §6.2 O1 status append line +1；既有 OPEN 行零删减 |
| `docs/49-stage2-*.md` + `docs/50-stage2-*.md` + `docs/51-stage2-*.md` + `docs/52-stage2-*.md` + `docs/53-stage2-*.md` | (F) append（如适用）| SKIP 政策若 grep 命中 0 行 stale 字面 |
| `scripts/_knife617_manifest_bump.py` | (G) 新增 | manifest bump helper |
| `evidence_pack/manifest.json` | (G) 更新 | 980 → 984 |
| `reviews/stage0-gate0-rework-2026-08-23/617-stage0-architect-s616-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-audit-PASS-20260830.md` | (G) 入库随 617 commit | NEW documentation +1；per docs 房规「审计文件不单独 commit 随下一刀入库」|
| `reviews/stage0-gate0-rework-2026-08-23/617-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-receipt.md` | (H) 新增 | 617 receipt |

**零修改文件清单**（执行端必守）:
- 13 受保护文件（含 synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir + registry.csv 既有 11 行 + gate_thresholds.json + 01-core.sql + requirements-dbt.txt + requirements-paddle.txt + intake_real_sha + auto_ingest + .venv-paddle/pyvenv.cfg + migration 001-013）
- docs/45/46/49/50/51/52/53 既有 OPEN 行原文（仅选择性 refresh append；F 段 SKIP）
- source_registry/registry.csv 既有 11 行字节
- 617 audit 文件（架构师自签；执行端零修改；617 audit 仅随 617 commit 入库 per docs 房规）
- 616 receipt 实质内容（不动）

---

## §3. 验收清单（执行端提交前自查）

- [ ] (A) 江苏样本地市第六刀源自取：候选清单探测 ≥ 1 个 ≥ 1 KB 内容源；首选 = tjj.xuzhou.gov.cn；fallback = 盐城/扬州/镇江/泰州/宿迁 任选 ≥ 1 个；零 `--confirm-*` 字面；零用户动作；零用户裁定；执行端零爬网公网（非政府域）
- [ ] (B) 江苏样本地市第六刀 SHA-locked：sha256 验证 + 落 `data/seed_archives/jiangsu_<city>_tjj_gov_cn_20260830.html` + source_registry/registry.csv +1 行；既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 不变
- [ ] (C) paddle-ocr e2e：`.venv-paddle/bin/python` HTML 路径走 docs/53 §5 connector 模式；confidence ≥ 0.85（per gate_thresholds.json 不变）；不修改 gate_thresholds.json；不修改 4 fixture 锁值
- [ ] (D) source_document + lineage JSONB：行新增 `doc_kind='OCR_SCAN'` + `source_sha256=<sha>` + `archive_path='data/seed_archives/jiangsu_<city>_*.html'` + lineage JSONB 含 paddle-ocr e2e 实测数据；零数据库 schema 变更
- [ ] (E) docs/45 §6.2 append（per 617 · 2026-08-30）；既有 605 + 606 + 608 + 610 + 612 + 614 + 616 status blockquote 完整保留
- [ ] (F) docs/49/50/51/52/53 F 段 SKIP 政策成立
- [ ] (G) `scripts/_knife617_manifest_bump.py` --verify 实跑 PASS；INVARIANT 984 == 984 == 984 ✓
- [ ] (H) 617 receipt 写回执 + 双推 + cc_head backfill + 617 audit 入库随 617 commit
- [ ] 13 受保护文件零漂移（13 既有 + source_registry/registry.csv +1 行 / 既有 11 行 SHA 不变 / bytes 总数变化是预期）
- [ ] 31+ 红线 100% 兑现（zero Stage 0/Gate 1/2/O1/O3 PASS 等）
- [ ] 零网络访问公网（非政府/统计局/研究机构）（per 2026-08-29 治理铁律）
- [ ] 零用户授权 #1 二次申请（用户授权 #1 仍生效无需二次授权）
- [ ] 零修改 617 audit 文件（架构师自签；执行端零修改；仅随 617 commit 入库 per docs 房规）
- [ ] 零修改 616 receipt 实质内容（不动）
- [ ] 江苏样本链路计数器 5/15 → 6/15 ✓

---

## §4. 关联文件清单回执

617 tasking 关联：
- (A) 探测命中清单 → 617 receipt §1
- (B) SHA-locked 落 seed_archives + registry.csv +1 行 → 617 receipt §2
- (C) paddle-ocr e2e 输出 → 617 receipt §3
- (D) source_document + lineage JSONB 写入 → 617 receipt §4
- (E) docs/45 §6.2 append（如适用）→ 617 receipt §5
- (F) docs/49-53 append（如适用）→ 617 receipt §6
- (G) manifest bump 输出 → 617 receipt §7
- (H) 617 receipt → 617 receipt §8 + §9 + §10

---

## §5. 收口语义

- 617 既接续 O1 §5.2.x 江苏样本链路 5/15 → 6/15（地市样本 4 → 5）
- O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准）
- O3 整体保持 CLOSED 候选（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 + 614 + 615 + 616 二十二重声明 + 617 不二次宣告）
- 江苏样本链路 6/15 节点（江苏 + 苏州 + 南京 + 常州 + 南通 + 徐州）
- 31+ 红线 100% 兑现
- 数据源唯一 = 政府/统计局/研究机构自取（per 2026-08-29 治理铁律）

---

## §6. 架构师签字

- 架构师 (Architect) — 617 tasking 签发落地
- 签发时间：2026-08-30
- queue §CURRENT status: AUDITED（**保持 AUDITED + 617 audit PASS note**）→ **PENDING** (note = 「617 tasking 签发 · O1 §5.2.x 江苏样本第六刀（地市样本第五刀；徐州市统计局）· per 615 audit §7.1 priority 2 verbatim + 616 receipt §9 候选 #2 verbatim · 江苏样本链路 5/15 → 6/15」)
- 下一站 = 执行端按本任务书落地 + 617 receipt DELIVERED → 618 audit

---

— End of `617-stage0-architect-s616-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830.md` —