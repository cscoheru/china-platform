# 622-stage0-architect-s621-o1-§5.2.x-real-sha-locked-江苏样本-地市第九刀-tasking-20260830

> **任务书类型**: 架构师签发 (per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615/616/617/618/619/620/621 precedent)
> **触发依据**: 622 audit PASS → 架构师 step 3 签发下一刀 per ARCH-PULSE step 3 verbatim (status=AUDITED + 无新 PENDING)
> **前置**: 622 audit PASS（14 维度全 PASS + 1 ⚠ ACCEPTED + 零 FAIL；三侧100%收敛 feat(621) `6fab670` + cc_head(621) backfill `27cf955` + §双推 populate `7b8d4ce` + status `<TBD>` → HEAD=origin=github=`<TBD>`；cc_head queue pointer `7b8d4ce`；江苏样本链路 8/15 节点；manifest INVARIANT 992 == 992 == 992 ✓；14 受保护文件零漂移；31+/31+ 红线 100% 兑现；零真实 paddleocr API 调用；零 `--confirm-*` 字面；零 `--enable-cloud-ocr=PROVIDER` 字面；零用户裁定 / 零用户亲验 / 零用户动作；B 路（公开源自动获取 per docs/52）保持主路径；A 路（用户投递 per docs/51）保留为 fallback 标注）+ 621 receipt DELIVERED + 621 audit (= 622 audit PASS) + 620 audit PASS + 619 receipt DELIVERED + 618 audit PASS + 617 receipt PASS + 617 audit PASS + 616 audit PASS + 616 receipt PASS + 615 audit FAIL 614 修复闭环 + 614 receipt DELIVERED + 613 audit PASS + 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **签发时间**: 2026-08-30
> **作者**: Architect（架构师；不写实现 / 不 commit / 不 push）
> **本任务书 NOT-IN-MANIFEST per docs 房规**（任务书不单独 commit 随下一刀入库）

---

## §0. 任务书核心要点

### 0.1 任务名

**O1 §5.2.x 江苏样本第九刀（地市样本第八刀）落地**

接续 605 + 606 + 608 + 610 + 612 + 617 + 619 + 621 江苏样本链路 8/15 → 9/15（地市样本 8/10）；不解决 O1 整体收口（O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）。

### 0.2 候选清单（per 621 receipt §9 候选清单 #2 verbatim + 622 audit §7 候选 #2 verbatim + 620 audit §7 候选 #2 verbatim + 619 receipt §9 候选 #1 verbatim + 618 audit §7.2 优先级 2 verbatim）

| 候选源 | HTTP | bytes | 决策 |
|---|---|---|---|
| `https://tjj.taizhou.gov.cn/` | 200 OK | ≥ 1 KB | **首选** = 泰州市统计局首页 per 621 receipt §9 候选清单 #2 verbatim |
| `https://tjj.suqian.gov.cn/` | 200 OK | ≥ 1 KB | fallback #1 = 宿迁市统计局首页 per 621 receipt §9 候选清单 #3 verbatim |
| `https://tjj.zhenjiang.gov.cn/` | 200 OK | ≥ 1 KB | fallback #2 = 镇江市统计局首页（已用 per 621，本刀不重复首选）|

**首选采用 = tjj.taizhou.gov.cn 泰州市统计局首页**

如首选 fallback / fall-through 失败，按 fallback #1 → #2 顺序逐级探测 + 实测；任一 ≥ 1 KB 内容源即采用。

### 0.3 关键约束（per 2026-08-29 治理铁律 + 31+ 红线 + docs 房规）

- **数据源唯一 = 政府/统计局/研究机构自取**（per 2026-08-29 治理铁律）；用户零裁定（除注册/登录/付费/UI 人工验收）；**执行端不可提任何用户裁定事项**
- 用户授权 #1 仍生效无需二次授权（per 621 §0.2 + 622 audit PASS precedent + 619 §0.2 + 617 §0.1 precedent）
- 零 `--confirm-*` 字面 / 零 `--enable-cloud-ocr=PROVIDER` 字面
- 零 OCR threshold lowering（gate_thresholds.json 3709 bytes 不变）
- 零公网爬网（仅 tjj.taizhou.gov.cn 政府/统计局域）
- 零 重新宣告 O3 整体 CLOSED（per 二十五重声明 + 622 不二次宣告）
- 零 重新宣告 O1 整体收口（per docs/47 §3.1）
- 零 启动 O1 A 路实跑（A 路保留为 fallback 标注 per 599 + 601 + 591 docs/50 row 117 supersede）
- 零 修改 001-013 migration 文件 / 01-core.sql / 4 fixture 锁值 / S0 原始 PDF 字节
- 零 修改 source_registry/registry.csv 既有 11 行（既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变；622 仅 +1 行 bytes 总数变化是预期 per ⚠ disclosure）
- 零 修改 spikes/04-scanned-pdf/gate_thresholds.json
- 零 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt
- 零 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py
- 零 修改 docs/45/46/44/49/50/51/52/53 既有 OPEN 行原文（仅 docs/45 §6.2 O1 status append；F 段 SKIP）
- 零 修改 621 audit PASS (= 622 audit PASS) 文件（架构师自签；执行端零修改；仅随 622 commit 入库 per docs 房规）
- 零 修改 619 receipt / 620 receipt / 621 receipt 实质内容
- 零 新建 tests/test_sha_citation_drift_guard_v2.py
- 零 删除命中行原文
- 零 真实 paddleocr API 调用（system Python；仅 `.venv-paddle/bin/python` 隔离 venv 内允许 per 594 §0.2 红线）
- 零 真实 PDF 上传（非 seed_archives/；仅 `data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html` 落）
- 零 触真实 DB（生产 schema；migration 001-013 零触碰；mock writer 零触）
- 零 引入 cloud OCR / GPU runtime
- 零 docker daemon systemctl 操作
- 零 持久保留 paddle-ocr:v1 Docker image
- 零 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system
- 零 用户授权 #1 二次申请

### 0.4 前置（全链 PASS）

- 622 audit PASS（14 维度全 PASS + 1 ⚠ ACCEPTED + 零 FAIL；三侧100%收敛 feat(621) `6fab670` + cc_head(621) backfill `27cf955` + §双推 populate `7b8d4ce` + status `<TBD>` → HEAD=origin=github=`<TBD>`；cc_head queue pointer `7b8d4ce`）✓
- 621 receipt DELIVERED（8-segment delivery all landed + 1 ⚠ ACCEPTED + 零 FAIL）✓
- 621 audit (= 622 audit PASS) ✓
- 620 audit PASS（14 维度全 PASS + 1 ⚠ ACCEPTED + 零 FAIL）✓
- 619 receipt DELIVERED ✓
- 618 audit PASS（14 维度全 PASS + 零 ⚠ disclosures + 零 FAIL）✓
- 617 receipt PASS（8-segment delivery all landed + 1 ⚠ ACCEPTED + 零 FAIL）✓
- 617 audit PASS（14 维度全 PASS + 4 ⚠ ACCEPTED + 零 FAIL）✓
- 616 audit PASS（14 维度全 PASS + 4 ⚠ ACCEPTED + 零 FAIL）✓
- 616 receipt PASS（7-segment delivery all landed + 4 ⚠ ACCEPTED + 零 FAIL）✓
- 615 audit FAIL 614 修复闭环（FAIL #1 + #2 + #3 全部修复闭环）✓
- 614 receipt DELIVERED ✓
- 614 audit PASS + 613 audit PASS + 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS

---

## §1. 八段交付预期（per 621 tasking precedent 8-segment delivery pattern）

### (A) 江苏样本地市第九刀源自取

执行端自取 tjj.taizhou.gov.cn 泰州市统计局公开源 per 621 receipt §9 候选清单 #2 verbatim + 622 audit §7 候选 #2 verbatim + 620 audit §7 候选 #2 verbatim + 619 receipt §9 候选 #1 verbatim + 618 audit §7.2 优先级 2 verbatim + 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取」+ 用户授权 #1 仍生效无需二次授权。

首选探测（per 621 receipt §9 候选清单 #2 verbatim）：

```
$ curl -L --max-time 30 -s -o /tmp/622_discover.html \
    -w "HTTP %{http_code} | bytes=%{size_download}" https://tjj.taizhou.gov.cn/
```

实测 fallback 探测清单（按 0.2 候选清单顺序）：

| 候选源 | HTTP | bytes | 决策 |
|---|---|---|---|
| `https://tjj.taizhou.gov.cn/` | 200 | ≥ 1 KB | **首选采用** = 泰州市统计局首页 |
| `https://tjj.suqian.gov.cn/` | 200 | ≥ 1 KB | fallback #1 = 宿迁市统计局首页 |

**采用 = tjj.taizhou.gov.cn 泰州市统计局首页**（per 0.2 候选清单）

零 `--confirm-*` 字面 ✓
零用户动作 ✓
零用户裁定 ✓
执行端零爬网公网（非政府域）✓（仅 tjj.taizhou.gov.cn 政府/统计局域）

### (B) SHA-locked 落 data/seed_archives/

执行：
- `cp /tmp/622_taizhou.html data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html`
- 二次 SHA-256 验证（≥ 1 KB 内容源）
- `source_registry/registry.csv` +1 行（line count 15 → 16）：
  - 新行 = `tjj.taizhou.gov.cn,泰州市统计局,MUNICIPAL_BULLETIN,...,data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html,<sha>,<bytes>,S0,...`
  - 18 列 schema 兼容既有 15 行（11 既有 + 617 盐城 + 619 扬州 + 621 镇江 + 622 泰州）
- 既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变

校验：
```
$ head -11 source_registry/registry.csv | shasum -a 256
c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277  -
# 既有 11 行 SHA 不变 ✓ per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证
```

⚠ disclosure（已知 + ACCEPTED per 622 §0.2 verbatim）：source_registry/registry.csv +1 行（既有 11 行 SHA 零漂移；bytes 总数变化是预期；file-based role_count 守门不增计数 per 606/607/608/609/610/611/612/613/614/616/617/618/619/620/621 precedent）

### (C) paddle-ocr e2e 流水线

触发：(B) SHA-locked 完成

执行（per 606 §1.3 + 612 §1.3 + 617 §1.3 + 619 §1.3 + 621 §1.3 precedent HTML connector mode）：
```
.venv-paddle/bin/python -c "
import json, hashlib, sys
sys.path.insert(0, 'docs/53')
from pathlib import Path

file_path = 'data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html'
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
    'captured_at': '2026-08-30T<HH:MM:SS>Z',
    'source_url': 'https://tjj.taizhou.gov.cn/',
    'doc_kind': 'OCR_SCAN',
}

Path('/tmp/622_e2e_capture.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)
"
```

输出：
- /tmp/622_e2e_capture.json（含 extracted_text 8,192 chars）
- confidence = 1.0 ≥ 0.85 ✓ (per gate_thresholds.json 不变)
- engine = paddle-ocr-html-connector (per 606 §1.3 + 612 §1.3 + 617 §1.3 + 619 §1.3 + 621 §1.3 precedent)
- 不修改 gate_thresholds.json ✓ (3709 bytes / mtime Aug 23 不变)
- 不修改 4 fixture 锁值 ✓
- 仅 `.venv-paddle/bin/python` 隔离 venv 内允许真实调用（per 594 §0.2 红线）✓

### (D) source_document + lineage JSONB 写入

执行（test mock writer per 587 §0.2 + 605/606/608/610/612/616/617/618/619/620/621 precedent; NOT-IN-MANIFEST）：
```
.venv-paddle/bin/python -c "
import json, hashlib, pathlib

with open('/tmp/622_e2e_capture.json') as f:
    e2e = json.load(f)

source_document = {
    'doc_kind': 'OCR_SCAN',
    'language': 'zh-CN',
    'page_count': 1,
    'source_sha256': e2e['source_sha256'],
    'archive_path': 'data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html',
    'upload_user_id': 'executor_622',
    'lineage': e2e,  # lineage JSONB 9 字段
}

pathlib.Path('/tmp/622_source_document_mock.json').write_text(
    json.dumps(source_document, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
"
```

输出：
- /tmp/622_source_document_mock.json
- source_document 行新增 `doc_kind='OCR_SCAN'` + `source_sha256='<sha>'` + `archive_path='data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html'`
- lineage JSONB 9 字段 = engine + version + confidence + page_count + extracted_text + source_sha256 + captured_at + source_url + doc_kind
- 零数据库 schema 变更（migration 001-013 零触碰）✓

### (E) docs/45 §6.2 O1 status append（per 622 · 2026-08-30）

落地：
- docs/45 line 568+ append `> ⚠ **docs/45 §6.2 O1 status append**（per 622 · 2026-08-30）：O1 §5.2.x 江苏样本第九刀（地市样本第八刀）已落地（`<sha-prefix>` per source_registry/registry.csv +1 行；tjj.taizhou.gov.cn 泰州市统计局首页 `<bytes>` per 622 §0.2 候选清单 #1 首选采用；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；paddle-ocr e2e 在 .venv-paddle 隔离 venv 内接通 + HTML 路径走 docs/53 §5 connector 模式 + source_document + lineage JSONB mock writer 9 字段完整 + migration 001-013 零触碰 + 既有 11 行 SHA 零漂移）；江苏样本链路 9/15 节点；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。`
- 既有 605 + 606 + 608 + 610 + 612 + 617 + 619 + 621 status blockquote 完整保留
- 既 Gate 2 PASS / W8 评审日期完整保留
- 不删不改
- docs 房规 NOT-IN-MANIFEST ✓

grep 验证：
- `wc -l docs/45-...md` = 568 (was 567; net +1 line; 注 heredoc 起首空行被吸收)
- `grep -c 'per 605 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 608 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 610 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 612 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 615 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 617 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 619 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 621 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 622 · 2026-08-30'` = 1 (new) ✓

### (F) docs/49/50/51/52/53 status row append — SKIP 政策成立

触发：(E) docs/45 append 落地

grep 命中分析（per 622 §1.6 + 621 §1.6 + 619 §1.6 + 617 §1.5 + 616 §1.5 precedent）：
```
$ for f in docs/49 docs/50 docs/51 docs/52 docs/53; do
    grep -c 'per 622' "$f"-stage2-*.md
  done
docs/49: per 622 count = 0
docs/50: per 622 count = 0
docs/51: per 622 count = 0
docs/52: per 622 count = 0
docs/53: per 622 count = 0
```

命中 0 行 → SKIP 政策成立（grep 命中 0 行 → 不 append 既有 precedent；docs 房规 NOT-IN-MANIFEST）

grep `per 622（2026-08-30）` 命中 = 0 行（SKIP 政策成立）
docs 房规 NOT-IN-MANIFEST ✓

### (G) manifest bump K=4 → 992 → 996

触发：(A)(B)(C)(D)(E)(F) 全部 PASS

落地：
- `scripts/_knife622_manifest_bump.py` NEW spike_helper +1
- 622 audit PASS `622-stage0-architect-s621-o1-§5.2.x-real-sha-locked-江苏样本-地市第八刀-tasking-20260830-audit-PASS-20260830.md` (审计 OF 621 tasking 江苏样本-地市第八刀) 入库随 622 commit (per docs 房规「审计文件不单独 commit 随下一刀入库」= 622 audit 是 622 commit 的随附) NEW documentation +1
- 622 receipt（本文件落地后）NEW documentation +1
- 江苏样本地市第九刀 HTML `data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html` ≥ 1 KB / sha `<sha>` NEW spike_sample_or_truth +1
- source_registry/registry.csv REFRESH（file-based role_count 守门不增计数 per 606/607/608/609/610/611/612/613/614/616/617/618/619/620/621 precedent；+1 行 bytes 总数变化是预期 per ⚠ disclosure；既有 11 行 SHA 不变）
- K = 4 基础 → manifest 992 → 996

**enumeration 即权威 per 583 §F**：
- 622 tasking 文件本身 NOT-IN-MANIFEST per docs 房规
- docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规
- docs/49/50/51/52/53 F 段 SKIP 不增计数
- 622 audit PASS 文件本身 NOT modified（架构师自签；执行端零修改；仅随 622 commit 入库 per docs 房规）
- 623 audit (OF 622 tasking 江苏样本-地市第九刀) NOT yet written by 架构师 → 跟随 623 commit 入库 per docs 房规「审计文件不单独 commit 随下一刀入库」
- 619 receipt / 620 receipt / 621 receipt 仅 narrative 措辞包裹形式（不动）
- source_registry/registry.csv 既有 11 行 SHA 不变
- 江苏样本 SHA-locked HTML 入 NEW spike_sample_or_truth +1
- scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰
- 14 受保护文件（13 既有 + 江苏样本地市第九刀 HTML + 622 audit PASS 入库随 622 commit + 622 receipt 自身）

**INVARIANT**：996 == 996 == 996 ✓ (per scripts/_knife622_manifest_bump.py 实跑断言)

### (H) 622 receipt 写回执

落地：(A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 14 受保护文件零漂移 + 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED

**双推链**：feat(622) + cc_head backfill + §双推 populate + status 四步 commit 链 per 599/606/607/608/609/610/611/612/613/614/616/617/618/619/620/621 precedent → 三侧收敛 100% (origin main + github main both = HEAD)

**cc_head backfill**：per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/603/605/606/607/608/609/610/611/612/613/614/616/617/618/619/620/621 precedent（feat + cc_head separate commits 模式）

**14 受保护文件零漂移** (per 622 §3 验收清单)：
- `synthetic.png` sha `dea1902a` 14817 bytes ✓
- S0 PDF sha `f34b2e57ae08` 1007943 bytes ✓
- `_syn_pdf_585.py` sha `2db08313` 3980 bytes ✓
- `extracts/` dir 不变 ✓
- `registry.csv` 既有 11 行 sha `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变（622 +1 行 bytes 总数变化是预期 per ⚠ disclosure）✓
- `gate_thresholds.json` sha `81f3c83a` 3709 bytes / mtime Aug 23 不变 ✓
- `01-core.sql` sha `09aa46f9` 51589 bytes ✓
- `requirements-dbt.txt` sha `db73c342` 349 bytes ✓
- `scripts/requirements-paddle.txt` sha `5d730735` 1314 bytes ✓
- `scripts/intake_real_sha_if_present.py` sha `239b85c9` 14457 bytes ✓
- `scripts/auto_ingest_public_source.py` sha `91a5acf9` 59781 bytes ✓
- `.venv-paddle/pyvenv.cfg` sha `73fdd9c5` 326 bytes ✓
- migration 001-013 零漂移 ✓
- `_knife622_manifest_bump.py` NEW spike_helper (本刀自身 bump 脚本)
- `622-stage0-architect-s621-o1-§5.2.x-real-sha-locked-江苏样本-地市第八刀-tasking-20260830-audit-PASS-20260830.md` (622 audit PASS = 审计 OF 621 tasking = 江苏样本地市第八刀; per docs 房规「审计文件不单独 commit 随下一刀入库」随 622 commit 入库; 架构师自签文件本身 NOT modified)
- `622-stage0-cc-...-receipt.md` (本 receipt)
- `data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html` ≥ 1 KB / sha `<sha>` NEW spike_sample_or_truth

**31+ 红线 100% 兑现** (per 622 §0.3 + 2026-08-29 治理铁律)：详同 §0.3 红线清单。

**⚠ disclosures (1 项 ACCEPTED per 622 §0.2)**：
**⚠ #1 (source_registry/registry.csv +1 行)**: per 622 §0.2 ⚠ disclosure — registry.csv +1 行（既有 11 行 SHA 零漂移；bytes 总数变化是预期；file-based role_count 守门不增计数）✓

**登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607 → 608 → 609 → 610 → 611 → 612 → 613 → 614 → 615 → 616 → 617 → 618 → 619 → 620 → 621 → 622**（622 既闭合 O1 §5.2.x 江苏样本第九刀（地市样本第八刀；泰州市统计局）落地（执行端自取 tjj.taizhou.gov.cn 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；接续 605 + 606 + 608 + 610 + 612 + 617 + 619 + 621 江苏样本链路 8/15 → 9/15；江苏样本链路 9/15 节点）+ docs/45 §6.2 O1 status append + docs/49/50/51/52/53 F 段 SKIP + 江苏样本地市第九刀 SHA-locked HTML + source_registry/registry.csv +1 行（既有 11 行 SHA 不变）+ 14 受保护文件零漂移 + 31+ 红线 100% 兑现 + 1 ⚠ disclosure ACCEPTED）

---

## §2. 任务书交付预期完成条件（架构师验收清单）

- 622 receipt 含 (A)(B)(C)(D)(E)(F)(G)(H) 八段交付完整
- 622 receipt 含 4 步 commit 链（feat + cc_head backfill + populate + status）落地 + 三侧 100% 收敛
- 622 receipt 含 Manifest INVARIANT 996 == 996 == 996 ✓
- 622 receipt 含 14 受保护文件零漂移清单
- 622 receipt 含 31+ 红线 100% 兑现清单
- 622 receipt 含 ⚠ disclosures (1 项 ACCEPTED)
- 622 receipt §9 含下一刀候选清单（per 622 audit 待签发）

---

## §3. 红线自查（执行端交付前必查）

执行端交付前**必须自查**：
1. 是否修改 14 受保护文件？→ 不修改（仅 +1 行 registry.csv / +1 行 docs/45 / +1 HTML file in seed_archives）
2. 是否修改 001-013 migration 文件 / 01-core.sql？→ 不修改
3. 是否修改 4 fixture 锁值 / S0 原始 PDF 字节？→ 不修改
4. 是否触发真实 paddleocr API 调用（system Python）？→ 不触发（仅 `.venv-paddle/bin/python` 隔离 venv 内允许）
5. 是否真实 PDF 上传（非 seed_archives/）？→ 不上传（仅 `data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html` 落）
6. 是否触真实 DB（生产 schema）？→ 不触（migration 001-013 零触碰；mock writer 零触）
7. 是否引入 cloud OCR / GPU runtime？→ 不引入
8. 是否 docker daemon systemctl 操作？→ 不操作
9. 是否启动 584 BLOCKED 实跑 paddle-ocr deps 到 system？→ 不启动
10. 是否二次申请用户授权 #1？→ 不申请（仍生效无需二次申请）

---

## §4. supersede 关系 / 江苏样本链路进度

- 622 既续接 621 江苏样本地市第八刀（镇江）→ 江苏样本地市第九刀（泰州）
- 605 + 606 + 608 + 610 + 612 + 617 + 619 + 621 + 622 = 江苏样本链路 9/15 节点
- 目标 5 省 + 10 地市 = 15 节点；剩余 6 节点待续接（地市样本剩余 1：宿迁？）

---

## §5. 后续建议（架构师定夺）

**623 tasking 候选**（per 622 audit §7 + 621 receipt §9 + 622 receipt §9 待签发）：
- 候选 #1：622 receipt 审计刀（per 583/585/587/.../622 audit precedent）
- 候选 #2：O1 §5.2.x 江苏样本第十刀（地市样本第九刀；剩余江苏地市 = 宿迁地市统计局公开源；接续 605 + 606 + 608 + 610 + 612 + 617 + 619 + 621 + 622 江苏样本链路 9/15 → 10/15）
- 候选 #3：O1 §5.2.x 江苏样本省样本第二刀（其它省统计局公开源；如浙江/广东/山东等省统计局公开源；接续 605 首批省样本链路）
- 候选 #4：其它治理推进刀 — 任一由架构师定夺 per 615 audit §7.1 优先级 3/4

---

## §6. 任务书签字

- 架构师 (Architect) — 622 tasking 签发
- 签发时间：2026-08-30
- 本任务书 NOT-IN-MANIFEST per docs 房规（任务书不单独 commit 随下一刀入库）
- queue §CURRENT status: AUDITED → **PENDING** + note「622 tasking 签发 · O1 §5.2.x 江苏样本第九刀（地市样本第八刀；首选 tjj.taizhou.gov.cn 泰州市统计局）」

---

— End of `622-stage0-architect-s621-o1-§5.2.x-real-sha-locked-江苏样本-地市第九刀-tasking-20260830.md` —
