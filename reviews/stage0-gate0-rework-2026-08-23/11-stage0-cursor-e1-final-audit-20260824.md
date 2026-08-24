# Stage 0 Gate 0 — Cursor 终态复验（陕西 research-track + U-4 前置）

- 文件编号：`11-stage0-cursor-e1-final-audit-20260824`
- 审核日期：2026-08-24
- 审核方：Cursor（架构/质量审计，只读）
- 对象：CC 声称的陕西集成终态（`docs/16` §6.2 / §7 / §8；`docs/13` §10；pack 440）
- 对照任务：Task #91（等待 Cursor 终态复验 + 用户 U-4）
- 常驻 Git：`10-stage0-cc-git-dual-remote-20260824.md`
- 方法：独立 pack SHA 复算、`pytest --collect-only`、读 eval/provenance/thresholds；**未**重跑 251 全集墙钟、**未**下载 PDF

---

## §0. TL;DR

| 维度 | 判定 |
|---|---|
| 陕西研究轨实现 / 政策口径（U-1/U-2/U-3/P-1/P-2） | ✅ **通过**（磁盘证据与 `docs/16` §0 一致） |
| Eval 数字（Han / all / needs_review / numeric N/A） | ✅ **通过** |
| Pack 440 / roles / `reviews/`=0 | ⚠️ **数量与角色通过；当前哈希 2/440 漂移** |
| CC 声称 `pack_errors=0` | ❌ **当前工作区不成立**（见 §2） |
| Code review tooling | 接受 **BLOCKED_BY_TOOLING** 诚实记录；不冒充 cleared |
| Stage 0 Gate 0 | 🔴 **不由本文件宣布 PASS**；交用户 **U-4** |
| Stage 1 | ❌ **禁止** |
| Commit / push | ❌ **禁止**，直至 §5 P0 修完 pack 漂移 |

**一句话：** 陕西 OCR research-track 工程交付可验收；**commit 前必须 rebuild pack**（`docs/13`/`docs/16` 自漂移）。Gate 0 最终状态只由用户 U-4 裁定。

---

## §1. 独立运行时证据

### 1.1 Pack

```
schema_version = 1.1-R3G-R4
artifact_count = 440
role_count sum = 440
research_non_gating_extracted_artifact = 1
research_non_gating_eval_report        = 1
reviews/ in pack                       = 0
ocr_text_layout.py                     = 已收录
pack_errors (本机独立复算)             = 2
```

| 漂移文件 | 现象 |
|---|---|
| `docs/13-r4-final-verification.md` | manifest size 15410 → disk 16099；SHA 不一致 |
| `docs/16-e1-candidate-report-20260824.md` | manifest size 14708 → disk 16465；SHA 不一致 |

**根因（与历史 R6-E 同类）：** 先 rebuild pack，再编辑 §10 / §6.2 终态叙述 → 入包 docs 哈希过期。CC 报告的「rebuild 当时 0 错」可并存；**当前工作区不得按 0 错验收。**

### 1.2 Eval（读 `shaanxi_text_eval_report.json`）

| 指标 | 磁盘 | `docs/16` / `docs/13` §10 |
|---|---|---|
| Han char % | 93.93 | 一致 |
| all non-whitespace % | 90.05 | 一致 |
| needs_review | 1/4 = 25% | 一致 |
| numeric | `null` / N/A | 一致；**不计 PASS** |
| research_track_result | `MEETS_UNCHANGED_APPLICABLE_THRESHOLDS` | 一致 |
| threshold_values_unchanged | true | 一致 |

### 1.3 门槛文件

`spikes/04-scanned-pdf/gate_thresholds.json`：`char≥90` / `numeric≥80` / `needs_review≤30` **未改**；`spike04_current_eval` 仍记录 1909 FAILED（0% / 3.7% / 100%）——正确，未用陕西结果覆盖门控样本。

### 1.4 Pytest collect

```
251 tests collected
```

与 CC §10「251 passed」**collect 数一致**。本轮**未**独立重跑 450s 全集；以 collect + CC 留档为旁证。U-4 前若用户要求墙钟复跑，见 §5 P1。

### 1.5 Git 状态（未 commit，符合红线）

```
M  docs/03,11,12,13,16 ; evidence_pack/manifest.json ; scripts/build_evidence_pack.py ;
   source_registry/registry.csv ; spikes/04 README + provenance ; tests/test_evidence_builder.py
?? 陕西 PDF/脚本/truth/extracts ; reviews/10（双远程纪律）
remotes: origin (Cursor) + github (cscoheru/china-platform)
```

### 1.6 Provenance（抽查）

`research_samples.shaanxi_fiscal_regulation_flk`：NPC 法规库 URL、role=`chinese_ocr_pressure_sample_non_gating_per_U3`、SHA `f34b2e57...71488`、4 页——与预审候选 1 / `docs/16` C-1 一致。顶层 `source_url` 仍为 1909 archive.org（历史门控样本字段）；**勿混淆**。

---

## §2. 假设检验

| ID | 假设 | 结果 |
|---|---|---|
| H1 | 当前磁盘 pack 全量 SHA 与 manifest 一致 | **REJECTED**（2 错：docs/13、docs/16） |
| H2 | 陕西 eval 数字与文档一致且门槛未降 | **CONFIRMED** |
| H3 | U-3 non-gating：陕西不改写 `spike04_current_eval` | **CONFIRMED** |
| H4 | pack 含陕西 research roles 且不含 `reviews/` | **CONFIRMED** |
| H5 | 工作区已 commit/push | **REJECTED**（正确停等；但不可在漂移下提交） |

---

## §3. 分层判定

| 层级 | 判定 |
|---|---|
| 陕西 C-1～C-4 / 适用研究阈值 | ✅ 通过（读产物；未重下 PDF） |
| U-1/U-2/U-3/P-1/P-2 落地口径 | ✅ 通过 |
| BLOCKED_BY_TOOLING 诚实记录 | ✅ 接受 |
| Evidence pack **当前**可入库 | ❌ **不通过**（须 rebuild） |
| 宣布 Stage 0 PASS | ❌ **否** |
| 建议用户进入 U-4 | ✅ **是**（工程侧在 P0 修完后） |

---

## §4. U-4（仅用户裁定；审计建议选项）

问题（同 `docs/16` §8）：

> 在 U-1/U-2/U-3 已锁定、门槛不降、陕西研究轨适用阈值达标但 numeric N/A 不计 PASS 且不参与 Gate、工程验证透明的前提下，**Stage 0 Gate 0 最终状态是什么？**

| 选项 | 含义 |
|---|---|
| **A** | Gate 0 **关闭为可继续**（E-1/spike04 按 U-3 非门控；Stage 0 其余项以 `docs/12` 为准）——**不是**「OCR 产品 PASS」 |
| **B** | Gate 0 **维持开放/观察**（需补墙钟 251 或人工 code review 后再关） |
| **C** | 其他（用户书面另写） |

审计员：**不预填**。修完 §5 P0 后用户裁定即可。无论 A/B/C，**不得**自动进入 Stage 1。

---

## §5. CC 执行指令（修漂移 → 提交 → 双推）

### P0 — 强制（commit 前门禁）

```bash
# 1) 冻结 docs 后唯一允许的 rebuild（无 SKIP 掩盖；按项目既有 hook 策略）
EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 \
  python3 scripts/build_evidence_pack.py

# 2) 独立复算必须 0
python3 - <<'PY'
import json, hashlib
from pathlib import Path
root=Path('.')
mf=json.loads((root/'evidence_pack/manifest.json').read_text())
err=0
for a in mf['artifacts']:
    p=root/a['path']
    if not p.is_file() or p.stat().st_size!=a['size_bytes'] \
       or hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:
        err+=1; print('BAD', a['path'])
print('pack_errors', err, 'of', len(mf['artifacts']))
raise SystemExit(err!=0)
PY
```

**规则：** rebuild 后 **禁止再改** `docs/13` / `docs/16` / 任何入包 artifact；若必须改 → 再 rebuild。

### P1 — 可选（用户若选 U-4 选项 B）

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider 2>&1 | tee /tmp/stage0-pytest-251.log
# 期望：251 passed
```

### P2 — 授权后 commit（单逻辑提交或拆 2 个，勿混无关）

纳入：陕西脚本/PDF/truth/extracts、builder/registry/docs/03/11/12/13/16、`evidence_pack/manifest.json`、`reviews/10`、`reviews/11`（本文件）、测试改动。

```
feat(spike04): integrate Shaanxi FLK scanned PDF as non-gating research track

Pack 440/0 after docs sync. Per U-3 does not gate Stage 0. Awaiting user U-4.
```

### §G — Git 双推（常驻，见 `10`）

```bash
git push origin HEAD
git push github HEAD
# 一侧失败 → 停报；不得只推 Cursor Origin
# GitHub 首次若非快进 → 停；等用户裁定是否 --force-with-lease
```

回执须含：`git log -1 --oneline`、两侧 push 结果、`pack_errors=0 of 440`、`git status --porcelain`（期望空）。

### P3 — 禁止

- ❌ 宣布 Stage 0 PASS / 进入 Stage 1
- ❌ 降低 `gate_thresholds.json` 或把 numeric N/A 计为 PASS
- ❌ 用陕西结果改写 1909 `spike04_current_eval` 门控字段
- ❌ 在 pack_errors≠0 时 commit/push
- ❌ 篡改 `reviews/03`–`09` 原文

---

## §6. 本文件未做的事

- 未修改业务代码 / pack / docs
- 未 commit / push
- 未重跑 251 全集
- 未代替用户裁定 U-4

— End of Cursor E-1 final audit (2026-08-24) —
