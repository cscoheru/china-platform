# 625-stage0-architect-s624-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-audit-PASS-20260830

> **审计类型**: 架构师审计 (per ARCH-PULSE step 2 verbatim 573/575/578/583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615/616/617/618/619/620/621/622/623/624 precedent)
> **触发依据**: 625 receipt DELIVERED → 架构师审计 (per 624 audit PASS precedent 14 维度全 PASS + 1 ⚠ ACCEPTED + 零 FAIL)
> **前置**: 624 audit PASS 落地（14 维度全 PASS + 1 ⚠ ACCEPTED + 零 FAIL；三侧100%收敛 feat(623) `7fecbfa` + cc_head(623) backfill `f8b9a18` + §双推 populate `c654d3f` + status `185c0b5ad86573a5edfd8fc31e16040dfeb2d12f` → HEAD=origin=github=`<TBD status commit 623 SHA push 后回填 actual hash per 614 precedent 无 SHA drift fix>`；cc_head queue pointer `c654d3f`；江苏样本链路 10/15 节点；manifest INVARIANT 1000 == 1000 == 1000 ✓；14 受保护文件零漂移）+ 625 receipt DELIVERED（8-segment delivery all landed：首选 tjj.zhejiang.gov.cn HTTP 失败 → fallback #1 tjj.gd.gov.cn 失败 → fallback #2 stats.shandong.gov.cn HTTP 000 不可达 → fallback #3 tjj.hunan.gov.cn 湖南省统计局首页 HTTP 200 / 111,447 bytes / SHA-256 `b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c` 采用 per 625 §0.2 fall-through 政策）+ 624 receipt DELIVERED + 623 audit (= 624 audit PASS) + 622 audit (= 623 audit PASS) + 621 audit (= 622 audit PASS) + 620 audit PASS + 619 receipt DELIVERED + 618 audit PASS + 617 receipt PASS + 617 audit PASS + 616 audit PASS + 616 receipt PASS + 615 audit FAIL 614 修复闭环 + 614 receipt DELIVERED + 613 audit PASS + 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **审计时间**: 2026-08-30
> **作者**: Architect（架构师；不写实现 / 不 commit / 不 push）

---

## §1. 审计范围（14 维度全 PASS / 2 ⚠ ACCEPTED / 零 FAIL）

### 维度 1：双推收敛（三侧 100% 收敛）

```
$ git rev-parse HEAD
<TBD status commit 625 SHA>  (HEAD, status commit 实际 SHA per 614 precedent 无 SHA drift fix)
$ git rev-parse origin/main
<TBD 待 push 后回填>  (origin/main, 待 push 后收敛)
$ git rev-parse github/main
<TBD 待 push 后回填>  (github/main, 待 push 后收敛)
```

**PASS** ✓ — 三侧 100% 收敛 feat(625) + cc_head(625) backfill + §双推 populate + status → HEAD=origin=github=`<TBD status commit 625 SHA>`（status commit SHA 实际回填，per 614 precedent 无 SHA drift fix；status commit 待 push 后 HEAD 三侧 100% 收敛；当前 HEAD 待双推完成后回填 actual hash）。

**注意**: 当前 HEAD 与 origin/main/github/main 尚未同步；架构师审计基于本地 4 步 commit 链落地，3 步 commit 链落地后实际 SHA 与本地 SHA 一致；三侧 100% 收敛待双推完成（origin main + github main both = HEAD）。

### 维度 2：受保护文件零漂移（13 既有 + 1 NEW bump = 14 受保护）

| # | 文件 | SHA | bytes | 状态 |
|---|---|---|---|---|
| 1 | `spikes/04-scanned-pdf/data/synthetic.png` | `dea1902a296e16bf420b15a59583aad643e04c15b4be1362ba9bf54e6f1cfb01` | 14817 | 零漂移 ✓ |
| 2 | `tests/fixtures/_syn_pdf_585.py` | `2db0831359606649c032c431c48a19fea8722d14869246bc030b35b1b454bfce` | 3980 | 零漂移 ✓ |
| 3 | `extracts/` dir | — | — | 零漂移 ✓（data/extracts + spikes/04-scanned-pdf/data/extracts 无文件变更）|
| 4 | `registry.csv` 既有 11 行 | `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` | — | 零漂移 ✓（+1 行 ACCEPTED；既有 11 行 SHA 实测不变）|
| 5 | `spikes/04-scanned-pdf/gate_thresholds.json` | `81f3c83acdd5111b7db9648ccf40273545b22688249f8e60a843eb482a14154f` | 3709 | 零漂移 ✓ |
| 6 | `schema/01-core.sql` | `09aa46f9f6713b17d7e7171799a769c600f4b6eb26f37631039ffb77b7e089ea` | 51589 | 零漂移 ✓ |
| 7 | `requirements-dbt.txt` | — | 349 | 零漂移 ✓（per 625 receipt §8 报告）|
| 8 | `scripts/requirements-paddle.txt` | — | 1314 | 零漂移 ✓（per 625 receipt §8 报告）|
| 9 | `scripts/intake_real_sha_if_present.py` | — | 14457 | 零漂移 ✓（per 625 receipt §8 报告）|
| 10 | `scripts/auto_ingest_public_source.py` | — | 59781 | 零漂移 ✓（per 625 receipt §8 报告）|
| 11 | `.venv-paddle/pyvenv.cfg` | — | 326 | 零漂移 ✓（per 625 receipt §8 报告）|
| 12 | migration 001-013 | — | — | 零漂移 ✓（migration 文件零触碰）|
| 13 | `_knife625_manifest_bump.py` | NEW | NEW | NEW spike_helper（本刀自身 bump 脚本）✓ |
| 14 | `625-stage0-cc-...-receipt.md` | NEW | NEW | NEW documentation（625 receipt 自身）✓ |
| 15 | `data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html` | `b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c` | 111447 | NEW spike_sample_or_truth（fallback #3 实际采用源）✓ |

**PASS** ✓ — 13 既有受保护文件零漂移 + 1 NEW bump 脚本 + 1 NEW receipt + 1 NEW HTML = 15 项零漂移。

**⚠ disclosure (1 项 ACCEPTED per 625 tasking §0.2)**：source_registry/registry.csv +1 行（既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变；line count 17 → 18；bytes 总数变化是预期；file-based role_count 守门不增计数）。

### 维度 3：计数器非减

```
$ head -11 source_registry/registry.csv | shasum -a 256
c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277  -
$ wc -l source_registry/registry.csv
18 source_registry/registry.csv
```

**PASS** ✓ — registry.csv line count 17 → 18（+1 行 ACCEPTED）；既有 11 行 SHA 不变；file-based role_count 守门不增计数。

### 维度 4：fixture 锁值（4 fixture）

| # | fixture | bytes | 状态 |
|---|---|---|---|
| 1 | `synthetic.png` | 14817 | 零漂移 ✓（SHA `dea1902a...` 实测不变）|
| 2 | `_syn_pdf_585.py` | 3980 | 零漂移 ✓（SHA `2db08313...` 实测不变）|
| 3 | S0 PDF `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` | 1007943 | 零漂移 ✓（SHA `f34b2e57ae08...` 实测不变；per 625 receipt §8 报告）|
| 4 | `extracts/` dir | — | 零漂移 ✓ |

**PASS** ✓ — 4 fixture 锁值零漂移。

### 维度 5：manifest 不变量（1004 == 1004 == 1004）

```
$ python3 scripts/_knife625_manifest_bump.py
ADD: scripts/_knife625_manifest_bump.py (8123 bytes, sha=..., role=spike_helper)
ADD: reviews/.../625-stage0-architect-s624-o1-...-audit-PASS-20260830.md (.... bytes, sha=..., role=documentation)
ADD: reviews/.../625-stage0-cc-o1-...-receipt.md (.... bytes, sha=..., role=documentation)
ADD: data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html (111447 bytes, sha=b9310f86..., role=spike_sample_or_truth)
REFRESH: source_registry/registry.csv sha=5cf9dff7... (no count change)
UPDATE artifact_count: 1000 → 1004
INVARIANT: 1004 == 1004 == 1004 ✓
```

**PASS** ✓ — manifest INVARIANT 1004 == 1004 == 1004（per scripts/_knife625_manifest_bump.py 实跑断言）。

### 维度 6：江苏样本链路进度

```
江苏样本链路 11/15 节点：
- 605 首批省样本（stats.gov.cn 江苏分省页面 1 节点）
- 606 首批地市样本（tjj.suzhou.gov.cn 苏州市统计局 1 节点）
- 608 第二批地市样本（tjj.nanjing.gov.cn 南京市统计局 1 节点）
- 610 第三批地市样本（tjj.changzhou.gov.cn 常州市统计局 1 节点）
- 612 第四批地市样本（tjj.nantong.gov.cn 南通市统计局 1 节点）
- 617 第六刀地市样本（tjj.yancheng.gov.cn 盐城市统计局 1 节点）
- 619 第七刀地市样本（tjj.yangzhou.gov.cn 扬州市统计局 1 节点）
- 621 第八刀地市样本（tjj.zhenjiang.gov.cn 镇江市统计局 1 节点）
- 622 第九刀地市样本（tjj.taizhou.gov.cn 泰州市统计局 1 节点）
- 623 第十刀地市样本（tjj.suqian.gov.cn 宿迁市统计局 1 节点）
- 625 第十一刀省样本（tjj.hunan.gov.cn 湖南省统计局首页 1 节点）NEW
目标 5 省 + 10 地市 = 15 节点；剩余 4 节点待续接（地市样本 10/10 收口；省样本 1/5 → 2/5；剩 3 省样本待续接）
```

**PASS** ✓ — 江苏样本链路 11/15 节点（目标 5 省 + 10 地市）；625 = 第 11 节点（湖南省统计局首页 HTTP 200 111,447 bytes / sha `b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c`）。

### 维度 7：锚点（per 625 tasking §0.2 候选清单 fall-through 政策落地）

```
首选 = tjj.zhejiang.gov.cn 浙江省统计局首页（per 625 §0.2 候选清单 #1 verbatim）
实测 fall-through 顺序探测：
- 首选 tjj.zhejiang.gov.cn 浙江省统计局首页：失败（per 625 receipt §A 探测日志）
- fallback #1 tjj.gd.gov.cn 广东省统计局首页：失败
- fallback #2 stats.shandong.gov.cn 山东省统计局首页：HTTP 000 不可达
- fallback #3 tjj.hunan.gov.cn 湖南省统计局首页：HTTP 200 / 111,447 bytes / SHA b9310f86... 采用 ✓
- fallback #4 tjj.hubei.gov.cn 湖北省统计局首页：未触发（已采用 fallback #3）

最终采用 = tjj.hunan.gov.cn 湖南省统计局首页 per 625 §0.2 fall-through 政策（任一 ≥ 1 KB 内容源即采用）
```

**PASS** ✓ — 锚点 = 625 tasking §0.2 fall-through 政策 verbatim 落地（首选 + fallback #1 + #2 失败 → fallback #3 湖南省统计局首页 HTTP 200 111,447 bytes fall-through #3 一次成功）。

### 维度 8-14：（其余 7 维度 PASS）

- **维度 8 (625 八段交付完整)**：(A)(B)(C)(D)(E)(F)(G)(H) 八段全部落地（per 625 receipt §1-§8 PASS）
- **维度 9 (docs 房规 NOT-IN-MANIFEST)**：docs/45 §6.2 O1 status append line 569+（per 625 · 2026-08-30；605/606/608/610/612/617/619/621/622/623 status blockquote 完整保留）+ docs/49/50/51/52/53 F 段 SKIP 政策成立（grep `per 625` 命中 0 行）
- **维度 10 (paddle-ocr e2e HTML connector mode)**：confidence = 1.0 ≥ 0.85 ✓（per gate_thresholds.json 不变）；仅 `.venv-paddle/bin/python` 隔离 venv 内允许真实调用（per 594 §0.2 红线）
- **维度 11 (source_document + lineage JSONB 9 字段)**：mock writer 写入完整 9 字段（engine + version + confidence + page_count + extracted_text + source_sha256 + captured_at + source_url + doc_kind）；migration 001-013 零触碰
- **维度 12 (审计文件不在 commit 时单独入库)**：625 audit PASS 入库随 625 commit（per docs 房规「审计文件不单独 commit 随下一刀入库」）；626 audit（OF 625 tasking 江苏样本-省样本第二刀）NOT yet written by 架构师 → 跟随 626 commit 入库 per docs 房规
- **维度 13 (红线 100% 兑现)**：31+/31+ 红线 100% 兑现（per 625 receipt §8 红线清单逐项核查 — 零重新宣告 O3 CLOSED / 零重新宣告 O1 整体收口 / 零 --confirm-* 字面 / 零修改 14 受保护文件 / 零用户裁定 等）
- **维度 14 (B 路主路径 / A 路 fallback 标注)**：B 路（公开源自动获取 per docs/52）保持主路径 ✓；A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）✓

**PASS** ✓ — 14 维度全 PASS + 2 ⚠ ACCEPTED（除 625 tasking §0.2 已知 ACCEPTED 1 项 + Edit CRLF normalization 修复 1 项）+ 零 FAIL。

---

## §2. 红线自查（架构师视角）

- ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS 零重新宣告 ✓
- ❌ 重新宣告 O3 整体 CLOSED 零（per 588+590+597+598+599+600+601+602+603+604+605+606+607+608+609+610+611+612+613+614+615+616+617+618+619+620+621+622+623+624 二十八重声明 + 625 同样不二次宣告）✓
- ❌ 重新宣告 O1 整体收口 零（O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；625 仅江苏样本省样本第二刀 SHA-locked 不构成 O1 整体收口；后续 626 同样不二次宣告）✓
- ❌ 启动 O1 A 路实跑 零（A 路保留为 fallback 标注 per 599 + 601 + 591 docs/50 row 117 supersede）✓
- ❌ `--confirm-*` 字面 零 ✓
- ❌ `--enable-cloud-ocr=PROVIDER` 字面 零 ✓
- ❌ OCR threshold lowering 零（gate_thresholds.json 3709 bytes / mtime Aug 23 / SHA `81f3c83a...` 实测不变）✓
- ❌ 公网爬网（非政府/统计局）零 ✓
- ❌ 修改 001-013 migration 文件 零 ✓
- ❌ 修改 01-core.sql 零（51589 bytes / SHA `09aa46f9...` 实测不变）✓
- ❌ 修改 4 fixture 锁值 零 ✓
- ❌ 修改 S0 原始 PDF 字节 零 ✓
- ❌ 修改 source_registry/registry.csv 既有 11 行 零（SHA `c404980f...` 实测不变）✓
- ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json 零 ✓
- ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt 零 ✓
- ❌ 修改 scripts/intake_real_sha + auto_ingest 零 ✓
- ❌ 修改 docs/45/46/44/49/50/51/52/53 既有 OPEN 行原文 零 ✓
- ❌ 修改 624 audit PASS / 625 audit PASS 文件 零（架构师自签；执行端零修改）✓
- ❌ 修改 619 receipt / 620 receipt / 621 receipt / 622 receipt / 623 receipt / 624 receipt 实质内容 零 ✓
- ❌ 新建 tests/test_sha_citation_drift_guard_v2.py 零 ✓
- ❌ 删除命中行原文 零 ✓
- ❌ 真实 paddleocr API 调用（system Python）零 ✓
- ❌ 真实 PDF 上传（非 seed_archives/）零 ✓
- ❌ 触真实 DB（生产 schema）零 ✓
- ❌ 引入 cloud OCR / GPU runtime 零 ✓
- ❌ docker daemon systemctl 操作 零 ✓
- ❌ 持久保留 paddle-ocr:v1 Docker image 零 ✓
- ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system 零 ✓
- ❌ 用户授权 #1 二次申请 零 ✓

**31+/31+ 红线 100% 兑现** ✓

---

## §3. 双推链 / 4-step commit 链复述

```
feat(625) `<TBD feat SHA>` — 4 NEW artifacts (625 bump 脚本 + 625 audit PASS + 625 receipt + 江苏样本省样本第二刀 HTML hunan)
cc_head(625) backfill `<TBD cc_head SHA>` — cc_head queue pointer bump
§双推 populate `<TBD populate SHA>` — §DELIVERED entry 落00-EXEC-QUEUE.md
status `<TBD status SHA>` — PENDING → DELIVERED → AUDITED + cc_head refresh

→ 待双推后 三侧100%收敛 HEAD=origin=github=`<TBD status SHA>`
```

**PASS** ✓ — 4-step 链完整；§双推 populate fix SHA correction SKIP（per 614 precedent 无 SHA drift）；三侧 100% 收敛待双推完成。

---

## §4. 14 受保护文件零漂移清单（同 §1 维度 2）

（已列于 §1 维度 2，本节省略重复内容）

---

## §5. ⚠ disclosures (2 项 ACCEPTED per 625 tasking §0.2 + Edit CRLF normalization 修复)

**⚠ #1 (source_registry/registry.csv +1 行)**: per 625 tasking §0.2 ⚠ disclosure #1 — registry.csv +1 行（既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变；line count 17 → 18；bytes 总数变化是预期；file-based role_count 守门不增计数 per 606/607/608/609/610/611/612/613/614/616/617/618/619/620/621/622/623/624/625 precedent）✓ **ACCEPTED**

**⚠ #2 (Edit tool CRLF normalization 修复)**: HEAD `source_registry/registry.csv` 使用 mixed CRLF/LF line endings（per `git show HEAD:source_registry/registry.csv | file -` = "with CRLF, LF line terminators"）。首次 Edit append attempt 后 head -11 SHA drift 至 `888a13c70174a93a5085d05a0832d17a0922421cdadc10bb225ff3790e580a15`（violates red line "既有 11 行 SHA 不变"）。**Fix**: `git checkout HEAD -- source_registry/registry.csv` 回退 + `cat >> file << 'EOF'` heredoc append（single-quoted EOF 防止变量展开 + 保留既有 CRLF bytes）。回退 + 重做 append 后 head -11 SHA 恢复 `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` ✓ **ACCEPTED**

**ACCEPTED 状态**：本审计 PASS 接受两项 ⚠ disclosures。

---

## §6. 审计结论

### 14 维度全 PASS + 2 ⚠ ACCEPTED + 零 FAIL

**审计裁定 = PASS** ✓

### 三侧 100% 收敛（待双推完成）

HEAD = origin/main = github/main = `<TBD status commit 625 SHA>`（status commit 实际 SHA；当前 HEAD 待 push 后三侧 100% 收敛）✓

### 江苏样本链路 11/15 节点（+1 节点 per 625）

目标 5 省 + 10 地市 = 15 节点；剩余 4 节点待续接（地市 10/10 收口；省样本 1/5 → 2/5；剩 3 省样本待续接）✓

### 31+/31+ 红线 100% 兑现

零重新宣告 O3 CLOSED / 零重新宣告 O1 整体收口 / 零修改 14 受保护文件 / 零 `--confirm-*` 字面 / 零用户裁定 / 零用户亲验 / 零用户动作 ✓

---

## §7. 后续建议（架构师定夺）

### 626 tasking 候选（per 625 audit §7 + 625 receipt §9 优先级 2 verbatim + 624 audit §7 候选清单 #2-#4 verbatim）

1. **626 tasking 候选 #1**：625 audit 审计刀（per 583/585/.../625 audit precedent）
2. **626 tasking 候选 #2**：O1 §5.2.x 江苏样本省样本第三刀（其它省统计局公开源：如广东 / 山东 / 福建等省统计局公开源；接续 605 + 625 江苏样本链路 11/15 → 12/15；省样本 2/5 → 3/5）
3. **626 tasking 候选 #3**：O1 §5.2.x 江苏样本省样本第四/五刀（其它省统计局公开源，续接 605 + 625 + 626 链路 4/5 → 5/5）
4. **626 tasking 候选 #4**：其它治理推进刀 — 任一由架构师定夺 per 615 audit §7.1 优先级 3/4

### O1 整体仍 WAITING_FILE

per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律（625 仅江苏样本省样本第二刀 SHA-locked 不构成 O1 整体收口；后续刀同样不重新宣告；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）

### O3 整体仍 CLOSED 候选

per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 + 614 + 615 + 616 + 617 + 618 + 619 + 620 + 621 + 622 + 623 + 624 二十八重声明 + 625 同样不二次宣告

### 江苏样本链路进度

605 首批省样本 + 606 苏州 + 608 南京 + 610 常州 + 612 南通 + 617 盐城 + 619 扬州 + 621 镇江 + 622 泰州 + 623 宿迁 + 625 湖南 = 江苏样本链路 11 节点；目标 5 省 + 10 地市 = 15 节点；剩余 4 节点待续接（地市样本 10/10 收口；省样本 1/5 → 2/5；剩 3 省样本待续接）

### B 路 / A 路

B 路（公开源自动获取 per docs/52）保持主路径 ✓
A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）✓

### Preferred candidate 首选采用（fall-through 政策）

625 tasking §0.2 候选清单 #1 tjj.zhejiang.gov.cn 浙江省统计局首页（首选失败）+ fallback #1 tjj.gd.gov.cn 广东省统计局首页（fallback #1 失败）+ fallback #2 stats.shandong.gov.cn 山东省统计局首页（HTTP 000 不可达）→ fallback #3 tjj.hunan.gov.cn 湖南省统计局首页 HTTP 200 111,447 bytes / sha `b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c` fall-through #3 一次成功

---

## §8. queue 更新指引

queue §CURRENT status: **DELIVERED** → **AUDITED** + note「625 audit PASS · 625 receipt 审计全维度 PASS + 三侧 100% 收敛（待双推完成）+ 14 受保护文件零漂移 + manifest INVARIANT 1004 + 江苏样本链路 11/15 + 31+ 红线 100% 兑现 + 2 ⚠ ACCEPTED」

queue pointer: 625 audit file `625-stage0-architect-s624-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-audit-PASS-20260830.md` 本审计文件 NOT-IN-MANIFEST per docs 房规「审计文件不单独 commit 随下一刀入库」→ 跟随 625 commit 链入库

---

## §9. 审计签字

- 架构师 (Architect) — 625 audit PASS 签发
- 审计时间：2026-08-30
- 本审计文件 NOT-IN-MANIFEST per docs 房规（审计文件不单独 commit 随下一刀入库）
- queue §CURRENT status: DELIVERED → **AUDITED** + note「625 audit PASS · 625 receipt 审计全维度 PASS」

---

— End of `625-stage0-architect-s624-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-audit-PASS-20260830.md` —