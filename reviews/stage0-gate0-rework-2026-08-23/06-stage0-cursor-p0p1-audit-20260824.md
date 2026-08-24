# Stage 0 Gate 0 — Cursor P0+P1 终审审核

- 审核日期：2026-08-24
- 文件编号：`06-stage0-cursor-p0p1-audit-20260824`
- 审核方：Cursor（架构/质量审计，只读）
- 对象：CC 完成的 P0 commit + P1 pytest 留档
- 对照文档：`docs/15-stage0-p0p1-handoff-20260824.md`（CC 终审包）
- 上一轮：`reviews/.../05-stage0-cursor复核3-20260824.md`（R6 pack 同步通过；P0 待提交）
- 方法：独立复算 pack 哈希、`git log`/`git status`、读取 `/tmp/stage0-pytest-237.log`；不改业务代码 / schema / tests / `evidence_pack/manifest.json`

---

## §0. TL;DR（终审结论）

| 维度 | CC 声称 | 审计独立验证 | 判定 |
|---|---|---|---|
| P0 commit | `f475717` / 87 files | `git log -1` 一致 | ✅ **通过** |
| Pack 同步 | 0 / 428 | `pack_errors 0 of 428` | ✅ **通过** |
| P1 pytest | 237 passed / 349.77s | `/tmp/stage0-pytest-237.log` 末行一致 | ✅ **通过** |
| Dev rework 20/20 | R4+R5+R6 闭环 | commit message + `docs/13` §8 交叉一致 | ✅ **通过** |
| Stage 0 Gate 0 | BLOCKED（E-1 + P-1/2/3） | 与 `05` / 用户政策一致 | 🔴 **维持 BLOCKED** |
| 进入 Stage 1 | 否 | — | ❌ **否** |

**一句话：** P0+P1 交付物经独立复验**全部通过**；开发返工可宣告终态收口。Stage 0 仍因 E-1 与用户政策阻塞，**不得进入 Stage 1**。

---

## §1. P0 commit 审核

### 1.1 Commit 身份

```
f475717a6ac0b9ff1b635e03807ea32358aeaf99
chore(stage0): close R4+R5+R6 dev rework; sync evidence pack to 428/0
Author: Claude Code <claude-code@anthropic.com>
Date:   Mon Aug 24 12:12:30 2026 +0800
87 files changed, 166132 insertions(+)
```

审计确认：commit message 正确陈述 pack 0/428、`schema_version=1.1-R3G-R4`、pytest collect 237、20/20 dev rework、Stage 0 BLOCKED 及 E-1/P-1/P-2/P-3。**口径合规。**

### 1.2 收录范围抽查（§4.1 回应）

| 类别 | 是否在 commit 内 | 备注 |
|---|---|---|
| `docs/00`–`docs/13` | ✅ 12 份 | 缺 `docs/15`（commit 后新增，见 §6） |
| `schema/01-core.sql` + `002_source_governance.sql` + migration logs | ✅ | I-05 治理链完整 |
| `tests/conftest.py` + 4 测试文件 | ✅ | R5-A apply 链 |
| `scripts/build_evidence_pack.py` | ✅ | R5-B builder |
| `evidence_pack/manifest.json` | ✅ | 428 artifacts |
| `reviews/00`–`05` | ✅ | 含本轮前 Cursor 审核链 |
| 6 spike 目录（脚本 + 样本 + extracted 产物） | ✅ | 不含预解压 / 31M PDF |
| `source_registry/registry.csv` | ✅ | |
| `data/extracts/*` | ✅ | 6 spike 产物 |

**判定 §4.1：P0 commit 内容完整。** R4/R5/R6 涉及的核心交付物均已入库。唯一遗漏为 commit 之后产生的 `docs/15`（见 §6 建议）。

### 1.3 Commit 后工作区状态

```
 M .gitignore
?? docs/15-stage0-p0p1-handoff-20260824.md
?? spikes/00-provincial-yearbook-table/data/extracted/
?? spikes/04-scanned-pdf/.fetch_time_1909.txt
?? spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf
```

与 `docs/15` §1.3 描述一致。**另有一项 CC 未在 handoff 中强调：**

- `.gitignore` 有 **未提交** 的 staged-diff（`!schema/migrations/*.log`、`!spikes/**/*.pdf` 等 R4 返工规则）。committed 版 `.gitignore` 不含这些例外；当前工作区 diff 若合入会使 `statistical_abstract_foreign_countries_1909.pdf` 变为可 track 状态——与 §4.2 审计建议（不入库 31M PDF）**冲突**。建议：**不要**将含 `!spikes/**/*.pdf` 的 `.gitignore` 变更与 1909 PDF 一并提交；若需 formalize 排除规则，应加显式 ignore 行而非 broad un-ignore。

---

## §2. pack_errors 独立复算

```
schema_version = 1.1-R3G-R4
artifact_count = 428
pack_errors    = 0
```

方法与 `05` §1 相同：`hashlib.sha256` 流式逐 artifact 对照 `evidence_pack/manifest.json`。

**判定：通过。** Cursor `04` §3.1 的 7 文件漂移问题在 commit `f475717` 中已终态关闭。

---

## §3. P1 pytest 日志审核

### 3.1 日志路径与摘要

`/tmp/stage0-pytest-237.log`（工作区外；不影响 git status）

```
237 passed in 349.77s (0:05:49)
```

### 3.2 与历史记录对照

| 来源 | 壁钟 | 测试数 |
|---|---|---|
| **本次 P1（审计读取）** | **349.77s** | **237 passed** |
| docs/13 §8 R6-A | 362.71s | 237 passed |
| docs/13 §1.1 早期 | 342.06s | 237 passed |

壁钟 340–365s 波动属 PG17 冷热启动与机器负载正常范围；**测试数 237 与 `--collect-only` 一致**。

**判定：P1 通过。** 填补了 `05` §0「证据不足：未独立重跑全集 237」缺口。

---

## §4. 五项待确认事项 — 审计员裁定

### 4.1 [确认] P0 commit 内容是否完整

| 裁定 | ✅ **认可完整** |
|---|---|
| 依据 | §1.2 抽查表；87 files 覆盖 docs/schema/tests/spikes/pack/reviews |
| 残留 | `docs/15` 未入 commit（post-commit 产物）；`.gitignore` 有未提交 diff（见 §1.3） |

### 4.2 [确认] 三个故意排除的 `??` 是否认可

| 路径 | 审计裁定 | 理由 |
|---|---|---|
| `spikes/00-provincial-yearbook-table/data/extracted/` | ✅ **认可排除** | R4-1 tracked-ZIP-only；预解压绕过解压契约 |
| `spikes/04-scanned-pdf/.fetch_time_1909.txt` | ✅ **认可排除** | 返工指令 §6 禁 wall-clock；应 gitignore 或删除，不入库 |
| `spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf` | ✅ **认可排除** | 31M 原始 PDF；P-2 禁止代表中国；manifest 不收录；OCR 中间产物（`safc1909_djvu.txt` + `truth_p24.json`）已 commit 足够 |

**补充：** 勿将 broad `!spikes/**/*.pdf` 合入 `.gitignore` 后再 add 1909 PDF——与 P-2 及仓库体积策略冲突。若需 formalize，建议显式 ignore：

```
spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf
spikes/04-scanned-pdf/.fetch_time_1909.txt
spikes/00-provincial-yearbook-table/data/extracted/
```

### 4.3 [决策] 是否将 P1 交叉引用写入 docs/13

| 裁定 | ⬜ **可选；审计不强制** |
|---|---|
| 建议 | 若用户授权 CC 改 docs/13，可加一行旁注（`docs/15` §3.4 草稿已给出）；**改后必须重建 pack** |
| 不授权时 | P1 日志 + 本审核文件 + `docs/15` 已构成足够旁证链 |

### 4.4 [决策] 后续工作分支

| 裁定 | **维持 `main` 首次 commit 即可** |
|---|---|
| 理由 | 单 commit 里程碑清晰；切 `stage0-r6-closure` 分支无额外收益除非并行 Stage 1 开发 |
| `.fetch_time` gitignore | 建议采纳 §4.2 显式 ignore 行（用户授权后 CC 执行） |

### 4.5 [确认] Stage 0 BLOCKED 口径

| 项 | 审计确认 |
|---|---|
| E-1 中文扫描 PDF 缺失 | ✅ 与 spike 04 `eval_report` BLOCKED 一致 |
| P-1 不降低 OCR 门槛 | ✅ `gate_thresholds.json` 未改动 |
| P-2 1909 美国样本不代表中国 | ✅ registry S3 + commit message 明示 |
| P-3 Stage 0 BLOCKED 直至 E-1 | ✅ commit message + `docs/12` 一致 |

**裁定：口径与用户政策完全一致。**

---

## §5. 阅读路径建议

### 5.1 最少路径（确认 P0+P1 落地）

1. 本文件 §0 TL;DR
2. `docs/15-stage0-p0p1-handoff-20260824.md` §0
3. `git log -1 --oneline` → `f475717`
4. `git status --porcelain` → 1×`M` + 4×`??`
5. `cat /tmp/stage0-pytest-237.log` → 237 passed

### 5.2 完整审计链

1. `reviews/.../03` → R4 首轮（apply 链断裂）
2. `reviews/.../04` → R5（技术过 / pack 不过）
3. `reviews/.../05` → R6 pack 同步（0/428）
4. **`reviews/.../06`（本文件）** → P0+P1 终验
5. `docs/13-r4-final-verification.md` §8 → 20/20 闭环表
6. `docs/12-stage0-closure-and-report.md` → Stage 0 总状态

---

## §6. 红线（重申）

- ❌ 不得降低 OCR 门槛或将 spike 04 标为产品 PASS
- ❌ 不得将 1909 美国样本提升为 S0/中国代表性
- ❌ 不得批量爬取或构建官方记分卡
- ❌ 不得在未重建 pack 的情况下编辑 `docs/13` 或 pack 内 artifact
- ❌ 不得宣布 Stage 0 通过或启动 Stage 1
- ❌ 不得篡改 `reviews/` 既有审核原文（本文件为新增 `06`，合规）

---

## §7. 后续可执行项（给用户 / CC）

| 优先级 | 项 | 执行方 | 说明 |
|---|---|---|---|
| P0+ | 提交 `docs/15` + 本文件 `06` | CC（用户授权后） | `chore(docs): add P0+P1 handoff and Cursor final audit` |
| P1 | 显式 gitignore 三路径 | CC（用户授权后） | 见 §4.2；**不要** broad `!spikes/**/*.pdf` + add 1909 PDF |
| P2 | 决定是否 docs/13 §8 R6-A 加 P1 旁注 | **用户决策** | 若改 → 重建 pack → 新 commit |
| P3 | 提供中文扫描 PDF（E-1） | **用户** | 唯一 Gate 0 外部解除路径 |
| P4 | 明确「开始 Stage 1」指令 | **用户** | 当前审计口径：**不得启动** |

---

## §8. 评审输出（per PRD 16.3）

| 项 | 判定 |
|---|---|
| **P0 commit** | ✅ **通过** |
| **P1 pytest 留档** | ✅ **通过** |
| **Dev rework R4+R5+R6** | ✅ **20/20 终态收口** |
| **Stage 0 Gate 0** | 🔴 **BLOCKED**（E-1 + P-1/P-2/P-3） |
| **进入 Stage 1** | ❌ **否** |

---

## §9. 本文件未做的事

- 未修改业务代码、schema、测试、`evidence_pack/manifest.json`
- 未执行 git commit
- 未将 Stage 0 BLOCKED 改写成 PASS
- 未覆盖 `/tmp/stage0-pytest-237.log`

— End of Cursor P0+P1 final audit (2026-08-24) —
