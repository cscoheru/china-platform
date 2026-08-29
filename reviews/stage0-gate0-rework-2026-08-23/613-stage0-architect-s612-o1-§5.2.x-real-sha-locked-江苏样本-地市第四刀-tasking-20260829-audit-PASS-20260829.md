# 613-stage0-architect-s612-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-audit-PASS-20260829

> **审计类型**: 架构师审计 (per ARCH-PULSE step 2 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612 平行模式)
> **触发依据**: 612 receipt DELIVERED → 架构师 step 2 audit
> **前置**: 612 tasking 签发 + 612 receipt DELIVERED + 612 tasking 落地（执行端自取 tjj.nantong.gov.cn 南通市统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；接续 605 首批省样本 + 606 首批地市样本 + 608 第二批地市样本 + 610 第三批地市样本链路 → 612 第四批地市样本）+ 611 audit PASS（14 维度 + 4 ⚠ ACCEPTED + 1 附加 ⚠ ACCEPTED + 零 FAIL）
> **审计时间**: 2026-08-29
> **作者**: Architect（架构师；不写实现 / 不 commit / 不 push；本审计文件随 613+1 刀入库 per docs 房规）

---

## §1. 审计裁定

**审计裁定 = PASS**

612 tasking 八段交付全部落地 + 双推收敛 + 13 受保护文件零漂移 + Manifest INVARIANT + 31+ 红线 100% 兑现 + 5 ⚠ disclosures ACCEPTED + 零 FAIL。

---

## §2. 14 维度审计清单（per 612 tasking §0.2 + ARCH-PULSE step 2 verbatim precedent）

### 维度 1: 双推收敛 ✓ PASS
- `git ls-remote origin main` = `9dff0e0c64f2a38e140fdc36de166afb233665a9`
- `git ls-remote github main` = `9dff0e0c64f2a38e140fdc36de166afb233665a9`
- 本地 `git rev-parse HEAD` = `9dff0e0c64f2a38e140fdc36de166afb233665a9`
- 三侧 100% 收敛 ✓

### 维度 2: 4 commit 链完整 ✓ PASS
- `bc9c2d8 feat(612): O1 §5.2.x 江苏样本第五刀（地市样本第四刀）落地`
- `bbde4a0 chore(queue): cc_head backfill for 612 O1 §5.2.x 江苏样本第五刀（地市样本第四刀）`
- `7a33f99 chore(queue): populate for 612 O1 §5.2.x 江苏样本第五刀（地市样本第四刀）`
- `9dff0e0 chore(queue): populate fix SHA correction for 612 O1 §5.2.x 江苏样本第五刀（地市样本第四刀）`
- per 599/606/607/608/609/610/611 precedent ✓

### 维度 3: 江苏样本地市第四刀源自取 ✓ PASS
- 候选链实测 (per docs/52 B 路 spec discover → download → sha256 → archive 四步流水线):
  - `https://tjj.wuxi.gov.cn/` 首选 → 实测 `Connection reset by peer` (HTTP 000 / 0 bytes)
  - `https://tjj.xuzhou.gov.cn/` fallback #2 → 实测 `Connection reset by peer` (HTTP 000 / 0 bytes)
  - `https://tjj.nantong.gov.cn/` fallback #1 → ✅ HTTP 200 / 31671 bytes / sha256 `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`
- fall-back chain per 612 §0.1 verbatim「首选 = tjj.wuxi.gov.cn；fallback = tjj.nantong.gov.cn / tjj.xuzhou.gov.cn 任选 ≥ 1 个 ≥ 1 KB 内容源」 ✓
- 零 --confirm-* 字面 ✓
- 零用户动作（用户授权 #1 仍生效无需二次申请） ✓
- 零用户裁定 ✓
- 零公网爬网（非政府/统计局域） ✓

### 维度 4: SHA-locked 落 data/seed_archives/ ✓ PASS
- `data/seed_archives/jiangsu_nantong_tjj_gov_cn_20260829.html` 存在 (31671 bytes; sha256 `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`)
- `shasum -a 256` 实测匹配 ✓
- 既有 605/606/608/610 HTML 字节零修改 ✓

### 维度 5: source_registry/registry.csv +1 行 + 既有 11 行零漂移 ✓ PASS
- `wc -l source_registry/registry.csv` = 12 (既有 11 + 612 新增)
- `head -11 source_registry/registry.csv | sha256sum` 实测 = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`（既有 11 行零修改）
- 完整 12 行 SHA = `de097cb315e93f21009817a7d773f23102a26d92dff770fc48ae9f57b699f803`（仅 +1 行 bytes 总数变化是预期）
- 新增行: `tjj.nantong.gov.cn,南通市统计局,MUNICIPAL_BULLETIN,...` 18 列 schema 兼容 ✓

### 维度 6: paddle-ocr 隔离 venv 守门 ✓ PASS
- `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` = `2.6.2` ✓
- `.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` = `3.7.0` ✓
- system `python3 -c "import paddle"` = `ModuleNotFoundError` ✓（隔离守门 100%）
- HTML connector mode (per docs/53 §5): extracted_text preview 含 "南通市统计局" references; engine='paddle-ocr-html-connector', version='3.7.0', confidence=1.0, page_count=1, source_sha256=`92e1481c3fea…` ✓

### 维度 7: source_document + lineage JSONB 9 字段完整 ✓ PASS
- source_document row: doc_kind='OCR_SCAN', language='zh-CN', source_sha256=`92e1481c3fea...`, archive_path=`data/seed_archives/jiangsu_nantong_tjj_gov_cn_20260829.html`, page_count=1, upload_user_id='executor_612' ✓
- lineage JSONB 9 字段: engine / version / confidence / page_count / extracted_text / source_sha256 / captured_at / source_url / doc_kind ✓
- mock writer 捕获位置 = `/tmp/612_e2e_capture.json` + `/tmp/612_html_connector.json` (spike_helper 房规 NOT-IN-MANIFEST) ✓

### 维度 8: docs/45 §6.2 O1 status append ✓ PASS
- line 559 append 一行「per 612 · 2026-08-29」 ✓
- 既有 605 status blockquote (line 552) 完整保留 ✓
- 既有 606 status blockquote (line 554) 完整保留 ✓
- 既有 608 status blockquote (line 556) 完整保留 ✓
- 既有 610 status blockquote (line 558) 完整保留 ✓
- 既有 Gate 2 PASS / W8 评审日期 (line 560+) 完整保留 ✓
- 不删不改 ✓

### 维度 9: docs/49/50/51/52/53 status row append — SKIP 政策成立 ✓ PASS
- docs/49 文件路径 mismatch → SKIP per 605 §6 precedent
- docs/50 line 11 (用户裁定：**D**) + 120/121 (591/603 supersede) + 124-127 (605 supersede) + 130+ (606/608/610 supersede) = 治理级决策标注 + 既有 supersede → SKIP
- docs/51 line 183+ (601 既有 supersede) → SKIP
- docs/52 line 287-330+ (599/601/606/608/610 既有 supersede blockquote) → SKIP
- docs/53 line 244-270+ (601/608/610 既有 supersede) → SKIP
- grep `per 612（2026-08-29）` 命中 = 0 行（SKIP 政策成立） ✓
- grep `per 612 · 2026-08-29` 命中 = 1 行（仅 docs/45 §6.2 per (E)） ✓

### 维度 10: Manifest INVARIANT ✓ PASS
- `evidence_pack/manifest.json` artifact_count = 973
- `len(artifacts)` = 973
- `sum(role_count.values())` = 973 (role_count keys: data_contract_suite / documentation / extracted_artifact / research_non_gating_eval_report / research_non_gating_extracted_artifact / schema_ddl / schema_migration_ddl / schema_migration_log / schema_negative_test / source_registry_csv)
- **INVARIANT: 973 == 973 == 973 ✓** (K = 4 基础 → 969 → 969+4 = 973 per scripts/_knife612_manifest_bump.py 实跑断言)
- file-based role_count 守门: source_registry/registry.csv REFRESH 不增计数 ✓

### 维度 11: 13 受保护文件零漂移 ✓ PASS
- `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` sha `f34b2e57ae08620c` / 1007943 bytes ✓
- `spikes/04-scanned-pdf/data/synthetic.png` sha `dea1902a296e16bf` / 14817 bytes / Aug 23 12:36 ✓
- `tests/fixtures/_syn_pdf_585.py` sha `2db0831359606649` / 3980 bytes / Aug 29 08:47 ✓
- `spikes/04-scanned-pdf/data/extracts` 96 bytes / Aug 23 11:35 ✓
- `data/extracts` 288 bytes / Aug 23 15:01 ✓
- `source_registry/registry.csv` 既有 11 行 sha `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 不变（实测 EXISTING 11 ROWS IDENTICAL TO HEAD；既有 10/9/8/7 行 sha 不变；仅 +1 行 bytes 总数变化是预期）✓
- `spikes/04-scanned-pdf/gate_thresholds.json` sha `81f3c83acdd5111b` / 3709 bytes / mtime Aug 23 16:32 不变 ✓
- `schema/01-core.sql` sha `09aa46f9f6713b17` / 51589 bytes / mtime Aug 23 18:50 不变 ✓
- `scripts/requirements-dbt.txt` (路径修正) 未在 612 commit chain 中被改 ✓
- `scripts/requirements-paddle.txt` sha `5d730735957d758e` / 1314 bytes / Aug 29 13:47 ✓
- `scripts/intake_real_sha_if_present.py` sha `239b85c9c968df82` / 14457 bytes ✓
- `scripts/auto_ingest_public_source.py` sha `91a5acf950ba22a2` / 59781 bytes / Aug 26 20:00 ✓
- `.venv-paddle/pyvenv.cfg` sha `73fdd9c537b54d88` / 326 bytes / Aug 29 13:06 ✓
- migration 001-013 零漂移 (git diff 86af7f1..9dff0e0 --stat -- schema/ = empty) ✓

### 维度 12: 江苏样本链路计数器 4/15 → 5/15 ✓ PASS
- `grep -c "jiangsu" source_registry/registry.csv` = 5 ✓
- 江苏样本链路: 605 首批省样本 (stats.gov.cn 江苏分省) + 606 首批地市样本 (tjj.suzhou.gov.cn 苏州市) + 608 第二批地市样本 (tjj.nanjing.gov.cn 南京市) + 610 第三批地市样本 (tjj.changzhou.gov.cn 常州市) + 612 第四批地市样本 (tjj.nantong.gov.cn 南通市) = 5 节点
- 目标 5 省 + 10 地市 = 15 节点；剩余 10 节点待续接

### 维度 13: 31+ 红线 100% 兑现 ✓ PASS
（per 612 tasking §0.2 + 2026-08-29 治理铁律 + 612 receipt §8 verbatim）
- 零重新宣告 Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS ✓
- 零 2020-2025 batch work ✓
- 零公网爬网（非政府/统计局）✓
- 零 OCR threshold lowering ✓
- 零 1909-as-China ✓
- 零 --force ✓
- 零 PAT request ✓
- 零 gate_thresholds.json edit ✓
- 零重新宣告 O3 整体 CLOSED ✓（per 588/590/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611 十七重声明延续）
- 零重新宣告 O1 整体收口 ✓（O1 整体仍 WAITING_FILE per docs/47 §3.1 + 612 仅第四批地市样本 SHA-locked 不构成 O1 整体收口）
- 零启动 O1 A 路实跑 ✓（A 路保留为 fallback 标注 per 591 docs/50 row 117 supersede）
- 零 --confirm-* 字面 ✓
- 零修改 001-013 migration 文件 ✓
- 零修改 01-core.sql ✓
- 零修改 4 fixture 锁值 ✓
- 零修改 S0 原始 PDF 字节 ✓
- 零修改 source_registry/registry.csv 既有 11 行字节（实测 EXISTING 11 ROWS IDENTICAL TO HEAD）✓
- 零修改 spikes/04-scanned-pdf/gate_thresholds.json ✓
- 零修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt ✓
- 零修改 scripts/intake_real_sha + auto_ingest ✓
- 零修改 docs/45/46/44/49/50/51/52/53 既有 OPEN 行原文（仅 selective refresh append；F 段 SKIP）✓
- 零删除命中行原文 ✓
- 零真实 paddleocr API 调用（system Python）✓（仅 .venv-paddle/bin/python 隔离 venv 内允许 per 594 §0.2 红线延续）
- 零真实 PDF 上传（非 seed_archives/）✓
- 零触真实 DB（生产 schema）✓（migration 001-013 零触碰；mock writer 仅写 /tmp/612_e2e_capture.json）
- 零引入 cloud OCR / GPU runtime ✓
- 零 docker daemon systemctl 操作 ✓
- 零持久保留 paddle-ocr:v1 Docker image ✓
- 零启动 584 BLOCKED 实跑 paddle-ocr deps 到 system ✓
- 零用户授权 #1 二次申请 ✓
- docs 房规 NOT-IN-MANIFEST ✓
- spike_helper 房规 NOT-IN-MANIFEST ✓

### 维度 14: 登记→实装闭环延续 ✓ PASS
- 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607 → 608 → 609 → 610 → 611 → 612 全链 PASS
- 612 既闭合 O1 §5.2.x 江苏样本第五刀（地市样本第四刀）落地

---

## §3. 5 ⚠ disclosures ACCEPTED

### ⚠ disclosure #1: source_registry/registry.csv +1 行（既有 11 行 SHA 零漂移）
- 既有 11 行 SHA 实测 = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 不变（EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证）
- 既有 10/9/8/7 行 SHA 不变
- 新增 1 行（江苏样本地市第四刀 / 南通市统计局）→ line count 11 → 12
- file-based role_count 守门不增计数 per 612 §1.7
- Manifest INVARIANT 维持（973 == 973 == 973）

### ⚠ disclosure #2: 江苏样本地市第四刀 SHA-locked 落 data/seed_archives/
- bytes 总数变化是预期
- 既有零地市样本不删（605/606/608/610 保留）
- 新增 1 个江苏样本地市第四刀（南通市统计局首页 31671 bytes）
- spike_sample_or_truth role +1

### ⚠ disclosure #3 (drift): §CURRENT/历史 receipt SHA 串号问题
- 文本层面（§CURRENT + 612 tasking line 110/120/266 + 611 audit + 610 receipt）：标注"既有 11 行 SHA `3639e729…`"
- HEAD 实测：既有 11 行 SHA = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`
- 差异：文本 SHA ≠ 实测 SHA；但实测既有 11 行字节零修改（diff 验证 EXISTING 11 ROWS IDENTICAL TO HEAD）
- 根因：60X receipt 误把 `head -10`/`head -12` 等不同 SHA 串号传递（per 612 receipt §3 候选根因）
- 处置：以实测字节为准 per 583 §F "enumeration 即权威"
- 影响范围：纯文档 drift，不影响 delivery correctness
- 后续建议：614 tasking 另刀审议 SHA 串号治理（per 612 receipt §9 候选 #4 + 612 tasking §4 关联文件清单）
- **本审计不视为 FAIL**（delivery 字节层正确；文档 drift 隔离到后续刀审议）

### ⚠ disclosure #4 (mirrors 611/610/608/606/605): paddle-ocr e2e dep drift
- paddleocr 3.7.0 + paddle 2.6.2 完整 PaddleOCR init 仍存在 dep drift (`set_optimization_level` 缺位)
- HTML 路径走 docs/53 §5 connector 模式（per 612 §1.3 替代路径 + 611 audit §3 ⚠ #3 disclosure 已验证）
- HTML 文本直接提取而非真实 OCR init
- 隔离守门 100% (.venv-paddle venv + system Python 零 paddle)
- 不视为触碰红线（paddle-ocr 隔离 venv 已建立 + 真依赖导入成功 + HTML connector 替代路径走通 + isolation 100% 守门）

### ⚠ disclosure #5: 用户授权 #1 续接生效
- per 612 §0.1 verbatim「用户授权 #1 仍生效无需二次授权」
- per 610 §0.1 verbatim 续接 + 606 BLOCKED 解决 precedent + 2026-08-29 治理铁律
- 零用户动作；零用户裁定

---

## §4. 0 FAIL

无 FAIL。

---

## §5. 三侧收敛验证

- HEAD = origin main = github main = `9dff0e0c64f2a38e140fdc36de166afb233665a9` ✓
- 三侧 100% 收敛（架构师实测 + git ls-remote origin + git ls-remote github）

---

## §6. 红线自查汇总

- ❌ 重新宣告 Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS：**零** ✓
- ❌ 2020-2025 batch work：**零** ✓
- ❌ 公网爬网（非政府/统计局）：**零**（仅 tjj.nantong.gov.cn 政府源） ✓
- ❌ OCR threshold lowering：**零** ✓
- ❌ 1909-as-China：**零** ✓
- ❌ --force / PAT request / gate_thresholds.json edit：**零** ✓
- ❌ --confirm-* 字面：**零** ✓
- ❌ 修改 001-013 migration / 01-core.sql / 4 fixture / S0 PDF / registry.csv 既有 11 行字节：**零** ✓
- ❌ 启动 O1 A 路实跑 / 584 BLOCKED deps 到 system：**零** ✓
- ❌ 引入 cloud OCR / GPU runtime / docker daemon 操作：**零** ✓

---

## §7. 后续建议（架构师定夺）

per 612 receipt §9 + 612 tasking §4 关联文件清单 + 611 audit §10:

- **614 tasking 候选 #1（最高优先）**：§CURRENT/历史 receipt SHA 串号问题治理刀（per §3 ⚠ disclosure #3；候选根因：60X receipt 误把 `head -10`/`head -12` 等不同 SHA 串号传递；§CURRENT/612 tasking line 110/120/266 + 611 audit + 610 receipt 文本 SHA `3639e729…` 与 HEAD 实测 `c404980f1eb542…` 不符；以实测为准；建议 614 audit 一次性 git grep + 全文校对修复 + 增单元测试守门）
- **614 tasking 候选 #2**：O1 §5.2.x 江苏样本第六刀（剩余地市样本刀；如徐州 / 盐城 / 扬州 / 镇江 / 泰州 / 宿迁地市统计局公开源；接续 605 + 606 + 608 + 610 + 612 江苏样本链路 5/15 → 6/15）
- **614 tasking 候选 #3**：O1 §5.2.x 江苏样本省样本第二刀（其它江苏省份样本刀；如浙江/广东/山东等省统计局公开源；接续 605 首批省样本链路）
- **614 tasking 候选 #4**：其它治理推进刀 — 任一由架构师定夺

**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；612 仅第四批地市样本 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）
**B 路（公开源自动获取 per docs/52）保持主路径**
**A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）**
**O3 整体仍 CLOSED 候选**（per 588/590/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611 十七重声明；612/613 不二次宣告）

---

## §8. 审计签字

- 架构师 (Architect) — 审计 PASS 签发
- 审计时间：2026-08-29
- 本审计文件随 614+1 刀入库 per docs 房规「审计文件不单独 commit 随下一刀入库」
- queue §CURRENT status: PENDING → **AUDITED** (note = 「613 audit PASS · 612 落地验收 · 江苏样本链路 5/15 · Manifest INVARIANT 973 ✓ · 31+ 红线 100% · 5 ⚠ ACCEPTED · 零 FAIL」)

---

— End of `613-stage0-architect-s612-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-audit-PASS-20260829.md` —
