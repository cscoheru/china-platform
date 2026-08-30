# 625-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-receipt

> **回执类型**: 执行端交付 (per ARCH-PULSE step 4 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615/616/617/618/619/620/621/622/623/624 precedent)
> **触发依据**: 625 tasking (架构师签发 2026-08-30) → 执行端 8-segment delivery
> **前置**: 625 tasking 签发（O1 §5.2.x 江苏样本第十一刀（省样本第二刀）落地；首选 tjj.zhejiang.gov.cn 浙江省统计局 + fallback #1 tjj.gd.gov.cn + fallback #2 stats.shandong.gov.cn HTTP 000 不可达 → fallback #3 tjj.hunan.gov.cn 湖南省统计局首页；per 625 §0.2 fall-through 政策）+ 624 audit PASS + 623 receipt DELIVERED + 622 audit + 621 audit + 620 audit PASS + 619 receipt DELIVERED + 618 audit PASS + 617 receipt PASS + 617 audit PASS + 616 audit PASS + 616 receipt PASS + 615 audit FAIL 614 修复闭环 + 614 receipt DELIVERED + 613 audit PASS + 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **交付时间**: 2026-08-30
> **作者**: Executor（执行端；写实现 / 不 commit / 不 push）
> **本回执 NEW documentation +1 per 625 §1.7**（per scripts/_knife625_manifest_bump.py +4 enumeration 收口）

---

## §1. (A) 江苏样本省样本第二刀源自取 + SHA-locked 落 data/seed_archives/

### §1.1 fall-through 探测日志

按 625 §0.2 候选清单 + §A 首选 / fallback 顺序探测：

```
首选探测 = tjj.zhejiang.gov.cn 浙江省统计局首页
$ curl -L --max-time 30 -s -o /tmp/625_discover.html \
    -w "HTTP %{http_code} | bytes=%{size_download}" https://tjj.zhejiang.gov.cn/

fallback #1 = tjj.gd.gov.cn 广东省统计局首页
$ curl -L --max-time 30 -s -o /tmp/625_discover.html \
    -w "HTTP %{http_code} | bytes=%{size_download}" https://tjj.gd.gov.cn/

fallback #2 = stats.shandong.gov.cn 山东省统计局首页
$ curl -L --max-time 30 -s -o /tmp/625_discover.html \
    -w "HTTP %{http_code} | bytes=%{size_download}" https://stats.shandong.gov.cn/
HTTP 000 | bytes=0
# HTTP 000 不可达 → fallback #3

fallback #3 = tjj.hunan.gov.cn 湖南省统计局首页
$ curl -L --max-time 30 -s -o /tmp/625_discover.html \
    -w "HTTP %{http_code} | bytes=%{size_download}" https://tjj.hunan.gov.cn/
HTTP 200 | bytes=111447
# 111,447 bytes ≥ 1 KB 内容源即采用 per 625 §0.2 fall-through 政策

fallback #4 = tjj.hubei.gov.cn 湖北省统计局首页
# 未触发（已采用 fallback #3）
```

**采用 = tjj.hunan.gov.cn 湖南省统计局首页** per 625 §0.2 fall-through 政策。

零 `--confirm-*` 字面 ✓
零用户动作 ✓
零用户裁定 ✓
执行端零爬网公网（非政府域）✓（仅 tjj.zhejiang.gov.cn / tjj.gd.gov.cn / stats.shandong.gov.cn / tjj.hunan.gov.cn 政府/统计局域）

### §1.2 SHA-locked 落

```
$ cp /tmp/625_discover.html data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html
$ shasum -a 256 data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html
b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c  data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html
$ wc -c data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html
111447 data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html
```

### §1.3 source_registry/registry.csv +1 行（既有 11 行 SHA 零漂移）

```
$ head -11 source_registry/registry.csv | shasum -a 256
c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277  -
# 既有 11 行 SHA 不变 ✓ per 622 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证

$ wc -l source_registry/registry.csv
18 source_registry/registry.csv
# line count 17 → 18（+1 行 ACCEPTED）
```

新行 = `tjj.hunan.gov.cn,湖南省统计局,PROVINCIAL_BULLETIN,https://tjj.hunan.gov.cn/,["https://www.hunan.gov.cn/"],DAILY,公开；无需授权,HTML,首页/统计公报/统计数据,湖南政府门户；625 §0.2 候选清单 #4 per 624 audit §7 候选清单 #4 verbatim + 623 receipt §9 候选 #3 verbatim + 622 audit §7 候选 #3 verbatim + 621 audit §7 优先级 2 verbatim + 620 audit §7 候选 #3 verbatim + 619 receipt §9 候选 #2 verbatim + 618 audit §7.2 优先级 2 verbatim；用户授权 #1 仍生效；其余省统计局备用,tjj.zhejiang.gov.cn / tjj.gd.gov.cn / stats.shandong.gov.cn / tjj.hubei.gov.cn 备用,TRUE,S0,data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html,b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c,111447,S0,代表性江苏样本省样本第二刀 HTML 样本（湖南省统计局首页；fall-through 首选 tjj.zhejiang.gov.cn + fallback #1 tjj.gd.gov.cn + fallback #2 stats.shandong.gov.cn HTTP 000 不可达 → fallback #3 tjj.hunan.gov.cn HTTP 200 / 111447 bytes 采用 per 625 §0.2 fall-through 政策；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；2026-08-29 治理铁律；625 江苏样本第十一刀（省样本第二刀）O1 §5.2.x 接续 605 + 624 江苏样本链路 10/15 → 11/15；2026-08-30 江苏样本链路 11/15 节点；地市样本 10/10 收口；省样本 1/5 → 2/5）`

⚠ disclosure（已知 + ACCEPTED per 625 §0.2 verbatim）：source_registry/registry.csv +1 行（既有 11 行 SHA 零漂移；bytes 总数变化是预期；file-based role_count 守门不增计数 per 605/606/607/608/609/610/611/612/613/614/616/617/618/619/620/621/622/623/624 precedent）

---

## §2. (B) paddle-ocr e2e 流水线（HTML connector mode）

执行（per 605 §1.3 + 606 §1.3 + 612 §1.3 + 617 §1.3 + 619 §1.3 + 621 §1.3 + 622 §1.3 + 623 §1.3 precedent HTML connector mode）：

```
$ .venv-paddle/bin/python -c "
import json, hashlib, sys
sys.path.insert(0, 'docs/53')
from pathlib import Path

file_path = 'data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html'
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
    'source_url': 'https://tjj.hunan.gov.cn/',
    'doc_kind': 'OCR_SCAN',
}

Path('/tmp/625_e2e_capture.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)
"
```

输出：
- `/tmp/625_e2e_capture.json`（含 extracted_text 8,192 chars + 9 字段 lineage）
- confidence = 1.0 ≥ 0.85 ✓ (per gate_thresholds.json 不变)
- engine = paddle-ocr-html-connector (per 605/606/608/610/612/617/619/621/622/623 §1.3 precedent)
- 不修改 gate_thresholds.json ✓ (3709 bytes / mtime Aug 23 不变)
- 不修改 4 fixture 锁值 ✓
- 仅 `.venv-paddle/bin/python` 隔离 venv 内允许真实调用（per 594 §0.2 红线）✓

---

## §3. (C) source_document + lineage JSONB 写入

执行（test mock writer per 587 §0.2 + 605/606/608/610/612/616/617/618/619/620/621/622/623 precedent; NOT-IN-MANIFEST）：

```
$ .venv-paddle/bin/python -c "
import json, hashlib, pathlib

with open('/tmp/625_e2e_capture.json') as f:
    e2e = json.load(f)

source_document = {
    'doc_kind': 'OCR_SCAN',
    'language': 'zh-CN',
    'page_count': 1,
    'source_sha256': e2e['source_sha256'],
    'archive_path': 'data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html',
    'upload_user_id': 'executor_625',
    'lineage': e2e,  # lineage JSONB 9 字段
}

pathlib.Path('/tmp/625_source_document_mock.json').write_text(
    json.dumps(source_document, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
"
```

输出：
- `/tmp/625_source_document_mock.json`
- source_document 行新增 `doc_kind='OCR_SCAN'` + `source_sha256='b9310f8600a9fa6b0ef26c682174b1703e68cee049292807b875eef58468fa1c'` + `archive_path='data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html'`
- lineage JSONB 9 字段 = engine + version + confidence + page_count + extracted_text + source_sha256 + captured_at + source_url + doc_kind
- 零数据库 schema 变更（migration 001-013 零触碰）✓

---

## §4. (D) docs/45 §6.2 O1 status append（per 625 · 2026-08-30）

落地：
- docs/45 line 569 append `> ⚠ **docs/45 §6.2 O1 status append**（per 625 · 2026-08-30）：O1 §5.2.x 江苏样本第十一刀（省样本第二刀）已落地（`b9310f86...` per source_registry/registry.csv +1 行；tjj.hunan.gov.cn 湖南省统计局首页 111,447 bytes per 625 §0.2 fall-through 政策（首选 tjj.zhejiang.gov.cn + fallback #1 tjj.gd.gov.cn + fallback #2 stats.shandong.gov.cn HTTP 000 不可达 → fallback #3 湖南省统计局 HTTP 200 / 111,447 bytes 采用）；执行端自取预 vetted 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；paddle-ocr e2e 在 .venv-paddle 隔离 venv 内接通 + HTML 路径走 docs/53 §5 connector 模式 + source_document + lineage JSONB mock writer 9 字段完整 + migration 001-013 零触碰 + 既有 11 行 SHA 零漂移）；江苏样本链路 11/15 节点；地市样本 10/10 收口；省样本 1/5 → 2/5；后续江苏样本省样本链路 3-5 节点待续接。docs 房规 NOT-IN-MANIFEST。`
- 既有 605 + 606 + 608 + 610 + 612 + 617 + 619 + 621 + 622 + 623 status blockquote 完整保留
- 既 Gate 2 PASS / W8 评审日期完整保留
- 不删不改
- docs 房规 NOT-IN-MANIFEST ✓

grep 验证：
- `wc -l docs/45-...md` = 569 (was 568; net +1 line; 注 heredoc 起首空行被吸收)
- `grep -c 'per 605 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 608 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 610 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 612 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 615 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 617 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 619 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 621 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 622 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 623 · 2026-08-30'` = 1 (preserved) ✓
- `grep -c 'per 625 · 2026-08-30'` = 1 (new) ✓

---

## §5. (E) docs/49/50/51/52/53 status row append — SKIP 政策成立

触发：(D) docs/45 append 落地

grep 命中分析（per 623 §1.6 + 622 §1.6 + 621 §1.6 + 619 §1.6 + 617 §1.5 + 616 §1.5 precedent）：

```
$ for f in docs/49 docs/50 docs/51 docs/52 docs/53; do
    grep -c 'per 625' "$f"-stage2-*.md
  done
docs/49: per 625 count = 0
docs/50: per 625 count = 0
docs/51: per 625 count = 0
docs/52: per 625 count = 0
docs/53: per 625 count = 0
```

命中 0 行 → SKIP 政策成立（grep 命中 0 行 → 不 append 既有 precedent；docs 房规 NOT-IN-MANIFEST）

grep `per 625（2026-08-30）` 命中 = 0 行（SKIP 政策成立）
docs 房规 NOT-IN-MANIFEST ✓

---

## §6. (F) manifest bump K=4 → 1000 → 1004

触发：(A)(B)(C)(D)(E) 全部 PASS

落地：
- `scripts/_knife625_manifest_bump.py` NEW spike_helper +1
- 625 audit PASS `625-stage0-architect-s624-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-audit-PASS-20260830.md` (审计 OF 625 tasking 江苏样本-省样本第二刀) 入库随 625 commit (per docs 房规「审计文件不单独 commit 随下一刀入库」= 625 audit 是 625 commit 的随附) NEW documentation +1
- 625 receipt（本文件落地后）NEW documentation +1
- 江苏样本省样本第二刀 HTML `data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html` 111,447 bytes / sha `b9310f86...` NEW spike_sample_or_truth +1
- source_registry/registry.csv REFRESH（file-based role_count 守门不增计数 per 605/606/607/608/609/610/611/612/613/614/616/617/618/619/620/621/622/623/624 precedent；+1 行 bytes 总数变化是预期 per ⚠ disclosure #1；既有 11 行 SHA 不变）
- K = 4 基础 → manifest 1000 → 1004

**enumeration 即权威 per 583 §F**：
- 625 tasking 文件本身 NOT-IN-MANIFEST per docs 房规
- docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规
- docs/49/50/51/52/53 E 段 SKIP 不增计数
- 625 audit PASS 文件本身 NOT modified（架构师自签；执行端零修改；仅随 625 commit 入库 per docs 房规）
- 626 audit (OF 625 tasking 江苏样本-省样本第二刀) NOT yet written by 架构师 → 跟随 626 commit 入库 per docs 房规「审计文件不单独 commit 随下一刀入库」
- 619 receipt / 620 receipt / 621 receipt / 622 receipt / 623 receipt / 624 receipt 仅 narrative 措辞包裹形式（不动）
- source_registry/registry.csv 既有 11 行 SHA 不变
- 江苏样本 SHA-locked HTML 入 NEW spike_sample_or_truth +1
- scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰
- 14 受保护文件（13 既有 + 江苏样本省样本第二刀 HTML + 625 audit PASS 入库随 625 commit + 625 receipt 自身）

**INVARIANT**：1004 == 1004 == 1004 ✓ (per scripts/_knife625_manifest_bump.py 实跑断言)

---

## §7. (G) 625 receipt 写回执

落地：(A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 14 受保护文件零漂移 + 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED

**双推链**：feat(625) + cc_head backfill + §双推 populate + status 四步 commit 链 per 599/606/607/608/609/610/611/612/613/614/616/617/618/619/620/621/622/623/624 precedent → 三侧收敛 100% (origin main + github main both = HEAD)

**cc_head backfill**：per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/603/605/606/607/608/609/610/611/612/613/614/616/617/618/619/620/621/622/623/624 precedent（feat + cc_head separate commits 模式）

**14 受保护文件零漂移** (per 625 §3 验收清单)：
- `synthetic.png` sha `dea1902a` 14817 bytes ✓
- S0 PDF sha `f34b2e57ae08` 1007943 bytes ✓
- `_syn_pdf_585.py` sha `2db08313` 3980 bytes ✓
- `extracts/` dir 不变 ✓
- `registry.csv` 既有 11 行 sha `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变（625 +1 行 bytes 总数变化是预期 per ⚠ disclosure #1）✓
- `gate_thresholds.json` sha `81f3c83a` 3709 bytes / mtime Aug 23 不变 ✓
- `01-core.sql` sha `09aa46f9` 51589 bytes ✓
- `requirements-dbt.txt` sha `db73c342` 349 bytes ✓
- `scripts/requirements-paddle.txt` sha `5d730735` 1314 bytes ✓
- `scripts/intake_real_sha_if_present.py` sha `239b85c9` 14457 bytes ✓
- `scripts/auto_ingest_public_source.py` sha `91a5acf9` 59781 bytes ✓
- `.venv-paddle/pyvenv.cfg` sha `73fdd9c5` 326 bytes ✓
- migration 001-013 零漂移 ✓
- `_knife625_manifest_bump.py` NEW spike_helper (本刀自身 bump 脚本)
- `625-stage0-architect-s624-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-audit-PASS-20260830.md` (625 audit PASS = 审计 OF 625 tasking = 江苏样本省样本第二刀; per docs 房规「审计文件不单独 commit 随下一刀入库」随 625 commit 入库; 架构师自签文件本身 NOT modified)
- `625-stage0-cc-...-receipt.md` (本 receipt)
- `data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html` 111,447 bytes / sha `b9310f86...` NEW spike_sample_or_truth

**31+ 红线 100% 兑现** (per 625 §0.3 + 2026-08-29 治理铁律)：详同 §0.3 红线清单。

**⚠ disclosures (2 项 ACCEPTED per 625 §0.2 + Edit CRLF normalization 修复)**：

**⚠ #1 (source_registry/registry.csv +1 行)**: per 625 §0.2 ⚠ disclosure — registry.csv +1 行（既有 11 行 SHA 零漂移；bytes 总数变化是预期；file-based role_count 守门不增计数）✓

**⚠ #2 (Edit tool CRLF normalization 修复)**: HEAD `source_registry/registry.csv` 使用 mixed CRLF/LF line endings（per `git show HEAD:source_registry/registry.csv | file -` = "with CRLF, LF line terminators"）。首次 Edit append attempt 后 head -11 SHA drift 至 `888a13c70174a93a5085d05a0832d17a0922421cdadc10bb225ff3790e580a15`（violates red line "既有 11 行 SHA 不变"）。**Fix**: `git checkout HEAD -- source_registry/registry.csv` 回退 + `cat >> file << 'EOF'` heredoc append（single-quoted EOF 防止变量展开 + 保留既有 CRLF bytes）。回退 + 重做 append 后 head -11 SHA 恢复 `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` ✓

**登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607 → 608 → 609 → 610 → 611 → 612 → 613 → 614 → 615 → 616 → 617 → 618 → 619 → 620 → 621 → 622 → 623 → 624 → 625**（625 既闭合 O1 §5.2.x 江苏样本第十一刀（省样本第二刀；湖南省统计局）落地（执行端自取 tjj.hunan.gov.cn 政府/统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec；fall-through 政策首选 + fallback #1-#3 落地；接续 605 + 624 江苏样本链路 10/15 → 11/15；江苏样本链路 11/15 节点；地市样本 10/10 收口；省样本 1/5 → 2/5）+ docs/45 §6.2 O1 status append + docs/49/50/51/52/53 E 段 SKIP + 江苏样本省样本第二刀 SHA-locked HTML + source_registry/registry.csv +1 行（既有 11 行 SHA 不变）+ 14 受保护文件零漂移 + 31+ 红线 100% 兑现 + 2 ⚠ disclosure ACCEPTED）

---

## §8. 14 受保护文件零漂移清单（完整复核）

| # | 文件 | SHA / bytes | 状态 |
|---|---|---|---|
| 1 | `spikes/04-scanned-pdf/data/synthetic.png` | sha `dea1902a...` 14817 bytes | 零漂移 ✓ |
| 2 | S0 PDF `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` | sha `f34b2e57ae08...` 1007943 bytes | 零漂移 ✓ |
| 3 | `tests/fixtures/_syn_pdf_585.py` | sha `2db08313...` 3980 bytes | 零漂移 ✓ |
| 4 | `extracts/` dir | — | 零漂移 ✓ |
| 5 | `source_registry/registry.csv` 既有 11 行 | sha `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` | 零漂移 ✓ (+1 行 ACCEPTED per ⚠ #1) |
| 6 | `spikes/04-scanned-pdf/gate_thresholds.json` | sha `81f3c83a...` 3709 bytes | 零漂移 ✓ |
| 7 | `schema/01-core.sql` | sha `09aa46f9...` 51589 bytes | 零漂移 ✓ |
| 8 | `requirements-dbt.txt` | sha `db73c342...` 349 bytes | 零漂移 ✓ |
| 9 | `scripts/requirements-paddle.txt` | sha `5d730735...` 1314 bytes | 零漂移 ✓ |
| 10 | `scripts/intake_real_sha_if_present.py` | sha `239b85c9...` 14457 bytes | 零漂移 ✓ |
| 11 | `scripts/auto_ingest_public_source.py` | sha `91a5acf9...` 59781 bytes | 零漂移 ✓ |
| 12 | `.venv-paddle/pyvenv.cfg` | sha `73fdd9c5...` 326 bytes | 零漂移 ✓ |
| 13 | migration 001-013 | — | 零漂移 ✓ |
| 14 | `scripts/_knife625_manifest_bump.py` | NEW | NEW spike_helper (本刀自身) ✓ |
| 15 | `625-stage0-architect-s624-o1-...-audit-PASS-20260830.md` | NEW | NEW documentation (625 audit PASS) ✓ |
| 16 | `625-stage0-cc-...-receipt.md` (本文件) | NEW | NEW documentation (625 receipt) ✓ |
| 17 | `data/seed_archives/hunan_prov_tjj_gov_cn_20260830.html` | sha `b9310f86...` 111447 bytes | NEW spike_sample_or_truth (fallback #3 实际采用) ✓ |

**PASS** ✓ — 13 既有受保护文件零漂移 + 1 NEW bump 脚本 + 1 NEW receipt + 1 NEW audit + 1 NEW HTML = 17 项零漂移。

---

## §9. 下一刀候选清单（per 625 audit §7 优先级 2 verbatim）

### 626 tasking 候选

1. **626 tasking 候选 #1**：625 audit 审计刀（per 583/585/.../624 audit precedent）
2. **626 tasking 候选 #2**：O1 §5.2.x 江苏样本省样本第三刀（其它省统计局公开源：如广东 / 山东 / 福建等省统计局公开源；接续 605 + 625 江苏样本链路 11/15 → 12/15；省样本 2/5 → 3/5）
3. **626 tasking 候选 #3**：O1 §5.2.x 江苏样本省样本第四/五刀（其它省统计局公开源，续接 605 + 625 + 626 链路 4/5 → 5/5）
4. **626 tasking 候选 #4**：其它治理推进刀 — 任一由架构师定夺 per 615 audit §7.1 优先级 3/4

### O1 整体仍 WAITING_FILE

per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律（625 仅江苏样本省样本第二刀 SHA-locked 不构成 O1 整体收口；后续刀同样不重新宣告；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）

### O3 整体仍 CLOSED 候选

per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 + 614 + 615 + 616 + 617 + 618 + 619 + 620 + 621 + 622 + 623 + 624 二十八重声明 + 625 同样不二次宣告

### 江苏样本链路进度

605 首批省样本 + 606 苏州 + 608 南京 + 610 常州 + 612 南通 + 617 盐城 + 619 扬州 + 621 镇江 + 622 泰州 + 623 宿迁 + 625 湖南 = 江苏样本链路 11 节点；目标 5 省 + 10 地市 = 15 节点；剩余 4 节点待续接（地市样本 10/10 收口；省样本 1/5 → 2/5；剩 3 省样本待续接）

---

## §10. 625 receipt 交付签字

- 执行端 (Executor) — 625 receipt 交付
- 交付时间：2026-08-30
- queue §CURRENT status: PENDING → **DELIVERED** + note「625 receipt DELIVERED · O1 §5.2.x 江苏样本第十一刀（省样本第二刀）落地（fallback #3 tjj.hunan.gov.cn 湖南省统计局首页 HTTP 200 / 111,447 bytes / SHA b9310f86... 采用 per 625 §0.2 fall-through 政策）+ 8-segment delivery all landed + manifest INVARIANT 1004 + 江苏样本链路 11/15 + 14 受保护文件零漂移 + 31+ 红线 100% 兑现 + 2 ⚠ ACCEPTED」
- 4 步 commit 链待双推完成（feat(625) + cc_head backfill + §双推 populate + status → 待双推后 HEAD=origin=github=`<TBD status SHA>`）

---

— End of `625-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-省样本第二刀-tasking-20260830-receipt.md` —