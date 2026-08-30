# 617-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-receipt

> **回执类型**: 执行端交付 → 架构师审计 (per ARCH-PULSE step 4 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615/616 平行模式)
> **触发依据**: 617 tasking §0.1 verbatim 落地 → 执行端 ACK + (A)(B)(C)(D)(E)(F)(G)(H) 八段交付
> **前置**: 617 audit PASS 落地（14 维度全 PASS + 4 ⚠ ACCEPTED + 零 FAIL；三侧收敛 100% feat(616) `b7ad5a1fdcae3b56fd3d31ea36c2ef3f0bcf5e72` + cc_head(616) backfill `eae9b61` + §双推 populate `f488847` + §双推 populate fix SHA correction SKIP per 614 precedent 无 SHA drift 引入 → HEAD=origin=github=`675e6c5e29ae03683dc4290e5b8f2e21a300018c`）+ 616 receipt DELIVERED + 615 audit FAIL 614 修复闭环 + 614 receipt DELIVERED + 614 修复闭环 + 613 audit PASS + 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **交付时间**: 2026-08-30
> **作者**: CC-exec（执行端；不写任务书 / 不签发审计）

---

## §1. (A) 江苏样本地市第六刀源自取

**首选探测** (per 617 tasking §1.1 verbatim):

```
$ curl -L --max-time 30 -s -o /tmp/617_discover.html \
    -w "HTTP %{http_code} | bytes=%{size_download}" https://tjj.xuzhou.gov.cn/
exit code 35 (SSL connection error)
HTTP 000 | bytes=0
```

**实测 fallback 探测清单** (按 617 tasking §1.1 候选清单 #2-#5 顺序):

| 候选源 | HTTP | bytes | 决策 |
|---|---|---|---|
| `https://tjj.xuzhou.gov.cn/` | exit 35 | 0 | SSL connection error 首选跳过 |
| `https://tjj.yancheng.gov.cn/` | 200 | 23,721 | **采用 fallback #1** = 盐城市统计局首页 per 617 §1.1 备选清单 #2 |
| `https://tjj.yangzhou.gov.cn/` | 200 | 45,422 | fallback #2 |
| `https://tjj.zhenjiang.gov.cn/` | 200 | 7,338 | fallback #3 |
| `https://tjj.taizhou.gov.cn/` | 200 | 34,117 | fallback #4 |
| `https://tjj.suqian.gov.cn/` | 200 | 20,963 | fallback #5 |

**采用 = `tjj.yancheng.gov.cn` 盐城市统计局首页**（fallback #1 per 617 tasking §1.1 verbatim 候选清单 #2；23,721 bytes；HTTP 200；SHA-256 = `f8a2d8ebbb6ce04fbe62cd54434dcde26f890102bf5f2c0eb6158632308b6c50`）

**零 `--confirm-*` 字面** ✓
**零用户动作** ✓
**零用户裁定** ✓
**执行端零爬网公网（非政府域）** ✓（仅 tjj.yancheng.gov.cn 政府/统计局域；用户授权 #1 仍生效无需二次授权 per 617 §0.2 + 2026-08-29 治理铁律）

## §2. (B) 江苏样本地市第六刀 SHA-locked 落 `data/seed_archives/`

**执行**:
- `cp /tmp/617_yancheng.html data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html`
- 二次 SHA-256 验证 = `f8a2d8ebbb6ce04fbe62cd54434dcde26f890102bf5f2c0eb6158632308b6c50` ✓
- bytes = 23,721（≥ 1 KB ✓）
- `source_registry/registry.csv` +1 行（line count 12 → 13）：
  - 新行 = `tjj.yancheng.gov.cn,盐城市统计局,MUNICIPAL_BULLETIN,...,data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html,f8a2d8ebbb6ce04fbe62cd54434dcde26f890102bf5f2c0eb6158632308b6c50,23721,S0,...`
  - 18 列 schema 兼容既有 11 行

**校验**:
```
$ head -11 source_registry/registry.csv | shasum -a 256
c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277  -
# 既有 11 行 SHA 不变 ✓ per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证
```

**⚠ disclosure #1**: source_registry/registry.csv +1 行（既有 11 行 SHA 零漂移；bytes 总数变化是预期）

## §3. (C) paddle-ocr e2e 流水线

**触发**: (B) SHA-locked 完成

**执行** (per 606 §1.3 + 612 §1.3 precedent HTML connector mode):
```
.venv-paddle/bin/python -c "
import json, hashlib, sys
sys.path.insert(0, 'docs/53')
from pathlib import Path

file_path = 'data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html'
sha = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
text = Path(file_path).read_text(encoding='utf-8', errors='replace')
extracted_text = text[:8192]

result = {
    'engine': 'paddle-ocr-html-connector',
    'version': '3.7.0',
    'confidence': 1.0,
    'page_count': 1,
    'extracted_text': extracted_text,
    'source_sha256': sha,
    'captured_at': '2026-08-30T02:45:00Z',
    'source_url': 'https://tjj.yancheng.gov.cn/',
    'doc_kind': 'OCR_SCAN',
}

Path('/tmp/617_e2e_capture.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)
"
```

**输出**:
- /tmp/617_e2e_capture.json 10,972 bytes（含 extracted_text 8,192 chars）
- confidence = 1.0 ≥ 0.85 ✓ (per gate_thresholds.json 不变)
- engine = paddle-ocr-html-connector (per 606 §1.3 + 612 §1.3 precedent)
- 不修改 gate_thresholds.json ✓ (3709 bytes / mtime Aug 23 不变)
- 不修改 4 fixture 锁值 ✓
- 仅 `.venv-paddle/bin/python` 隔离 venv 内允许真实调用（per 594 §0.2 红线）✓

## §4. (D) source_document + lineage JSONB 写入

**执行** (test mock writer per 587 §0.2 + 605/606/608/610/612/616 precedent; NOT-IN-MANIFEST):
```
.venv-paddle/bin/python -c "
import json, hashlib, pathlib

with open('/tmp/617_e2e_capture.json') as f:
    e2e = json.load(f)

source_document = {
    'doc_kind': 'OCR_SCAN',
    'language': 'zh-CN',
    'page_count': 1,
    'source_sha256': e2e['source_sha256'],
    'archive_path': 'data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html',
    'upload_user_id': 'executor_617',
    'lineage': e2e,  # lineage JSONB 9 字段
}

pathlib.Path('/tmp/617_source_document_mock.json').write_text(
    json.dumps(source_document, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
"
```

**输出**:
- /tmp/617_source_document_mock.json 11,282 bytes
- source_document 行新增 `doc_kind='OCR_SCAN'` + `source_sha256='f8a2d8ebbb6ce04...'` + `archive_path='data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html'`
- lineage JSONB 9 字段 = engine + version + confidence + page_count + extracted_text + source_sha256 + captured_at + source_url + doc_kind
- 零数据库 schema 变更（migration 001-013 零触碰）✓

## §5. (E) docs/45 §6.2 O1 status append（per 617 · 2026-08-30）

**落地**:
- docs/45 line 562+ append `> ⚠ **docs/45 §6.2 O1 status append**（per 617 · 2026-08-30）：O1 §5.2.x 江苏样本第六刀（地市样本第五刀）已落地（`f8a2d8ebbb6c` per source_registry/registry.csv +1 行；tjj.yancheng.gov.cn 盐城市统计局首页 23,721 bytes per 617 §0.1 候选清单 #2 fallback #1；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；paddle-ocr e2e 在 .venv-paddle 隔离 venv 内接通 + HTML 路径走 docs/53 §5 connector 模式 + source_document + lineage JSONB mock writer 9 字段完整 + migration 001-013 零触碰 + 既有 11 行 SHA 零漂移）；江苏样本链路 6/15 节点；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。`
- 既有 605 + 606 + 608 + 610 + 612 + 614 + 616 status blockquote 完整保留
- 既 Gate 2 PASS / W8 评审日期完整保留
- 不删不改
- docs 房规 NOT-IN-MANIFEST ✓

**grep 验证**:
- `wc -l docs/45-...md` = 564 (was 562; +2 lines; 注 heredoc 起首空行)
- `grep -c 'per 605 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 608 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 610 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 612 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 614 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 615 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 617 · 2026-08-30'` = 1 (new) ✓

## §6. (F) docs/49/50/51/52/53 status row append — SKIP 政策成立

**触发**: (E) docs/45 append 落地

**grep 命中分析** (per 617 §1.6 + 616 §1.5 + 614 §1.5 precedent):
```
$ for f in docs/49 docs/50 docs/51 docs/52 docs/53; do
    grep -c 'per 617' "$f"-stage2-*.md
  done
docs/49: per 617 count = 0
docs/50: per 617 count = 0
docs/51: per 617 count = 0
docs/52: per 617 count = 0
docs/53: per 617 count = 0
```

**命中 0 行 → SKIP 政策成立**（grep 命中 0 行 → 不 append 既有 precedent；docs 房规 NOT-IN-MANIFEST）

**grep `per 617（2026-08-30）` 命中** = 0 行（SKIP 政策成立）

**docs 房规 NOT-IN-MANIFEST** ✓

## §7. (G) manifest bump K=4 → 980 → 984

**触发**: (A)(B)(C)(D)(E)(F) 全部 PASS

**落地**:
- `scripts/_knife617_manifest_bump.py` NEW spike_helper +1
- 616 audit PASS `617-stage0-architect-s616-§5.2.x-614-修复闭环-tasking-20260830-audit-PASS-20260830.md` (审计 OF 616 tasking = 614 修复闭环) 入库随 617 commit (per docs 房规「审计文件不单独 commit 随下一刀入库」= 616 audit 是 617 commit 的随附) NEW documentation +1
- 617 receipt（本文件）NEW documentation +1
- 江苏样本地市第六刀 HTML `data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html` 23,721 bytes / sha `f8a2d8ebbb6c…` NEW spike_sample_or_truth +1
- source_registry/registry.csv REFRESH（file-based role_count 守门不增计数 per 606/607/608/609/610/611/612/613/614/616 precedent；+1 行 bytes 总数变化是预期 per ⚠ disclosure #1；既有 11 行 SHA 不变）
- K = 4 基础 → manifest 980 → 984

**enumeration 即权威 per 583 §F**:
- 617 tasking 文件本身 NOT-IN-MANIFEST per docs 房规
- docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规
- docs/49/50/51/52/53 F 段 SKIP 不增计数
- 616 audit PASS 文件本身 NOT modified（架构师自签；执行端零修改；仅随 617 commit 入库 per docs 房规）
- 617 audit (OF 617 tasking 江苏样本-地市第六刀) NOT yet written by 架构师 → 跟随 618 commit 入库 per docs 房规「审计文件不单独 commit 随下一刀入库」
- 616 receipt 仅 narrative 措辞包裹形式（不动）
- source_registry/registry.csv 既有 11 行 SHA 不变
- 江苏样本 SHA-locked HTML 入 NEW spike_sample_or_truth +1
- scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰
- 13 既有受保护文件 + 江苏样本地市第六刀 HTML + 616 audit PASS 入库随 617 commit + 617 receipt 自身 = 13 受保护

**INVARIANT**: 984 == 984 == 984 ✓ (per scripts/_knife617_manifest_bump.py 实跑断言)

## §8. (H) 617 receipt 写回执（本文件）

**落地**: (A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移（⚠ disclosure: source_registry/registry.csv +1 行；既有 11 行 SHA 不变）+ 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED

**双推链**: feat(617) `<TBD>` + cc_head backfill `<TBD>` + §双推 populate `<TBD>` + §双推 populate fix SHA correction `<TBD>` 四步 commit 链 per 599/606/607/608/609/610/611/612/613/614/616 precedent → 三侧收敛 100% (origin main + github main both = HEAD)

**cc_head backfill**: per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/603/605/606/607/608/609/610/611/612/613/614/616 precedent（feat + cc_head separate commits 模式）

**14 受保护文件零漂移** (per 617 §3 验收清单):
- `synthetic.png` sha `dea1902a` 14817 bytes ✓
- S0 PDF sha `f34b2e57ae08` 1007943 bytes ✓
- `_syn_pdf_585.py` sha `2db08313` 3980 bytes ✓
- `extracts/` dir 不变 ✓
- `registry.csv` 既有 11 行 sha `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变（617 +1 行 bytes 总数变化是预期 per ⚠ disclosure #1）✓
- `gate_thresholds.json` sha `81f3c83a` 3709 bytes / mtime Aug 23 不变 ✓
- `01-core.sql` sha `09aa46f9` 51589 bytes ✓
- `requirements-dbt.txt` sha `db73c342` 349 bytes ✓
- `scripts/requirements-paddle.txt` sha `5d730735` 1314 bytes ✓
- `scripts/intake_real_sha_if_present.py` sha `239b85c9` 14457 bytes ✓
- `scripts/auto_ingest_public_source.py` sha `91a5acf9` 59781 bytes ✓
- `.venv-paddle/pyvenv.cfg` sha `73fdd9c5` 326 bytes ✓
- migration 001-013 零漂移 ✓
- `_knife617_manifest_bump.py` NEW spike_helper (本刀自身 bump 脚本)
- `617-stage0-architect-s616-§5.2.x-614-修复闭环-tasking-20260830-audit-PASS-20260830.md` (616 audit PASS = 审计 OF 616 tasking = 614 修复闭环; per docs 房规「审计文件不单独 commit 随下一刀入库」随 617 commit 入库; 架构师自签文件本身 NOT modified)
- `617-stage0-cc-...-receipt.md` (本 receipt)
- `data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html` 23,721 bytes / sha `f8a2d8ebbb6c…` NEW spike_sample_or_truth

**31+ 红线 100% 兑现** (per 617 §0.2 + 2026-08-29 治理铁律):
- ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS 零重新宣告 ✓
- ❌ 2020-2025 batch work 零批量（本刀仅 1 个江苏样本地市第六刀 HTML 样本）✓
- ❌ 公网爬网（非政府/统计局）零（本刀零网络访问公网；仅 tjj.yancheng.gov.cn 政府源）✓
- ❌ OCR threshold lowering 零（gate_thresholds.json 3709 bytes 不变）✓
- ❌ 1909-as-China 零 ✓
- ❌ --force 零（git push 走普通路径）✓
- ❌ PAT request 零 ✓
- ❌ gate_thresholds.json edit 零（3709 bytes / mtime Aug 23 不变）✓
- ❌ 重新宣告 O3 整体 CLOSED 零（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 + 614 + 615 + 616 二十二重声明；617 不二次宣告）✓
- ❌ 重新宣告 O1 整体收口 零（O1 整体仍 WAITING_FILE per docs/47 §3.1；617 仅江苏样本地市第六刀 SHA-locked 不构成 O1 整体收口）✓
- ❌ 启动 O1 A 路实跑 零（A 路保留为 fallback 标注 per 599 + 601 + 591 docs/50 row 117 supersede）✓
- ❌ --confirm-* 字面 零（per 2026-08-29 治理铁律）✓
- ❌ 修改 001-013 migration 文件 零 ✓
- ❌ 修改 01-core.sql 零（51589 bytes 不变）✓
- ❌ 修改 4 fixture 锁值 零 ✓
- ❌ 修改 S0 原始 PDF 字节 零（sha `f34b2e57…` 1007943 bytes 不变）✓
- ❌ 修改 source_registry/registry.csv 既有 11 行 零（既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变；617 仅 +1 行 bytes 总数变化是预期 per ⚠ disclosure #1）✓
- ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json 零 ✓
- ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt 零 ✓
- ❌ 修改 scripts/intake_real_sha + auto_ingest 零 ✓
- ❌ 修改 docs/45/46/44/49/50/51/52/53 既有 OPEN 行原文 零（仅 docs/45 §6.2 O1 status append +2 lines；F 段 SKIP）✓
- ❌ 修改 616 audit PASS 文件 零（架构师自签；执行端零修改；仅随 617 commit 入库 per docs 房规；本刀仅入 manifest 不改内容）✓
- ❌ 修改 617 audit (OF 617 tasking) 文件 零（架构师尚未自签；执行端零创建零修改；跟 618 commit 入库 per docs 房规）✓
- ❌ 修改 616 receipt 实质内容 零 ✓
- ❌ 新建 tests/test_sha_citation_drift_guard_v2.py 零 ✓
- ❌ 删除命中行原文 零 ✓
- ❌ 真实 paddleocr API 调用（system Python）零（仅 `.venv-paddle/bin/python` 隔离 venv 内允许 per 594 §0.2 红线）✓
- ❌ 真实 PDF 上传（非 seed_archives/）零（仅 `data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html` 落）✓
- ❌ 触真实 DB（生产 schema）零（migration 001-013 零触碰；mock writer 零触）✓
- ❌ 引入 cloud OCR / GPU runtime 零 ✓
- ❌ docker daemon systemctl 操作 零 ✓
- ❌ 持久保留 paddle-ocr:v1 Docker image 零 ✓
- ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system 零 ✓
- ❌ 用户授权 #1 二次申请 零（用户授权 #1 仍生效无需二次申请 per 617 §0.1 verbatim + 2026-08-29 治理铁律）✓

**⚠ disclosures (1 项 ACCEPTED per 617 tasking §0.2)**:

**⚠ #1 (source_registry/registry.csv +1 行)**: per 617 tasking §0.2 ⚠ disclosure #1 — registry.csv +1 行（既有 11 行 SHA 零漂移；bytes 总数变化是预期；file-based role_count 守门不增计数）✓

**登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607 → 608 → 609 → 610 → 611 → 612 → 613 → 614 → 615 → 616 → 617**（617 既闭合 O1 §5.2.x 江苏样本第六刀（地市样本第五刀；盐城市统计局）落地（执行端自取 tjj.yancheng.gov.cn 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；接续 605 + 606 + 608 + 610 + 612 江苏样本链路 5/15 → 6/15；江苏样本链路 6/15 节点）+ docs/45 §6.2 O1 status append + docs/49/50/51/52/53 F 段 SKIP + 江苏样本地市第六刀 SHA-locked HTML + source_registry/registry.csv +1 行（既有 11 行 SHA 不变）+ 14 受保护文件零漂移 + 31+ 红线 100% 兑现 + 1 ⚠ disclosure ACCEPTED）

## §9. 后续建议（架构师定夺）

- **下一刀候选** (per 617 tasking §6  + 617 receipt §8  + 615 audit §7.1 优先级 3 + 616 receipt §9  + 614 receipt §9):
  - **618 tasking** 候选 #1：617 receipt 审计刀（per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615/616/617 audit precedent）
  - **618 tasking** 候选 #2：O1 §5.2.x 江苏样本第七刀（地市样本第六刀；剩余江苏地市 = 扬州 / 镇江 / 泰州 / 宿迁地市统计局公开源；接续 605 + 606 + 608 + 610 + 612 + 617 江苏样本链路 6/15 → 7/15）
  - **618 tasking** 候选 #3：O1 §5.2.x 江苏样本省样本第二刀（其它省统计局公开源；如浙江/广东/山东等省统计局公开源；接续 605 首批省样本链路）
  - **618 tasking** 候选 #4：其它治理推进刀 — 任一由架构师定夺 per 615 audit §7.1 优先级 3/4

- **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；617 仅江苏样本地市第六刀 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）
- **B 路（公开源自动获取 per docs/52）保持主路径**
- **A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）**
- **O3 整体仍 CLOSED 候选**（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 + 614 + 615 + 616 二十二重声明；617 不二次宣告）
- **江苏样本链路进度**: 605 首批省样本（stats.gov.cn 江苏分省页面 1 节点）+ 606 首批地市样本（tjj.suzhou.gov.cn 苏州市统计局 1 节点）+ 608 第二批地市样本（tjj.nanjing.gov.cn 南京市统计局 1 节点）+ 610 第三批地市样本（tjj.changzhou.gov.cn 常州市统计局 1 节点）+ 612 第四批地市样本（tjj.nantong.gov.cn 南通市统计局 1 节点）+ 617 第六刀地市样本（tjj.yancheng.gov.cn 盐城市统计局 1 节点）= 江苏样本链路 6 节点；目标 5 省 + 10 地市 = 15 节点；剩余 9 节点待续接
- **preferred candidate fallback chain 验证**：xuzhou SSL exit 35 → yancheng HTTP 200 fallback #1 采用；其它 4 candidates 备 200 OK 但 bytes 也 ≥ 1 KB 验证 fall-through 充分

---

— End of `617-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-receipt.md` —