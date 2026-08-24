# Stage 0 Gate 0 — P0 / P1 执行回执与终审待确认事项

> 文档日期：2026-08-24
> 适用：Stage 0 Gate 0 第六轮返工（R6）落盘 + commit + pytest 留档
> 编写角色：CC（Claude Code），贴给终审方（用户 / 后续审核员）
> 范围：仅记录"做了什么 / 证据在哪 / 哪里还需要确认"。**不动业务代码 / schema / tests / evidence_pack/manifest.json。**

---

## §0. TL;DR（终审方先看这段）

| 维度 | 状态 | 证据 |
|---|---|---|
| P0 commit | ✅ 已落地 | `f475717`（87 files / 166,132 insertions） |
| P0 pack 同步 | ✅ 0 mismatch / 428 | `evidence_pack/manifest.json` schema_version=`1.1-R3G-R4` |
| P1 pytest 留档 | ✅ 237 passed | `/tmp/stage0-pytest-237.log`（349.77s） |
| Dev rework 总数 | ✅ 20/20 闭环 | R4-1..R4-6（6）+ R5-A..R5-I（9）+ R6-A..R6-E（5） |
| Stage 0 Gate 0 | 🔴 **BLOCKED** | E-1（中文扫描 PDF 缺失）+ P-1/P-2/P-3（用户政策） |
| 是否进入 Stage 1 | ❌ **否** | 等待用户解除 E-1 或调整政策 |

**一句话**：开发返工已 20/20 闭环 + commit 落地 + pytest 留档；Stage 0 因外部样本缺失 + 用户 OCR 政策仍维持 BLOCKED，不得进入 Stage 1。

---

## §1. P0 commit 详情

### 1.1 git log -1

```
f475717 chore(stage0): close R4+R5+R6 dev rework; sync evidence pack to 428/0
```

- **Author**: Claude Code <claude-code@anthropic.com>
- **Date**: 2026-08-24 12:12:30 +0800
- **Stats**: 87 files changed, 166,132 insertions(+)
- **Branch**: main（首次 commit）

### 1.2 commit message 摘录

```
Pack SHA-256 verification: 0 mismatch of 428 artifacts
(schema_version=1.1-R3G-R4). Pytest collect 237; default full suite
applies 01-core.sql + migrations/*.sql via tests/conftest.py autouse
session fixture (R5-A). R5-A..R5-I (9/9) + R6-A..R6-E (5/5) + R4-1..R4-6
(6/6) = 20/20 dev rework closed.

Stage 0 Gate 0 verdict: BLOCKED
- EXTERNAL: E-1 (Chinese scanned PDF missing — only 1909 US archive
  sample, not China-representative)
- USER POLICY: P-1 / P-2 / P-3 (no OCR threshold relaxation, no
  promotion of 1909 US sample to S0/China-representative, Stage 0
  remains BLOCKED until E-1 resolves)

NOT entering Stage 1. Awaiting user approval.
```

### 1.3 git status（commit 后状态）

```
 M .gitignore                                                  ← 初始仓库遗留，本次未授权修改
?? spikes/00-provincial-yearbook-table/data/extracted/        ← 预解压目录（违反 R4-1 tracked-ZIP-only，故意排除）
?? spikes/04-scanned-pdf/.fetch_time_1909.txt                  ← wall-clock 字段（违反返工指令 §6，故意排除）
?? spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf  ← 31M PDF（不在 manifest 收录范围，故意排除）
```

三个未跟踪 ?? 均为**故意排除**，边界如下：

| ?? 路径 | 排除原因 | 引用规则 |
|---|---|---|
| `spikes/00-provincial-yearbook-table/data/extracted/` | R4-1 强制 tracked-ZIP-only + TemporaryDirectory；预解压目录会绕过"测试必须从 ZIP 原件自行解压"的契约 | `docs/11 §7.3 R4-1`、`docs/12 §3.2`、`docs/12 §10 D` |
| `spikes/04-scanned-pdf/.fetch_time_1909.txt` | wall-clock 时间戳；返工指令 §6 禁止不可复现时间字段 | 返工指令 §6、`scripts/build_evidence_pack.py` G-6（commit_timestamp_utc 而非 wall-clock） |
| `spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf` | 31M 原始 PDF；manifest 不收录原始 PDF（收录 .json / .py / .html / .xlsx） | `scripts/build_evidence_pack.py` glob 列表（`spikes/**/*.pdf` 仅命中 sample.pdf 等） |

---

## §2. pack_errors 输出（独立复算）

```
schema_version = 1.1-R3G-R4
artifact_count  = 428
role_count sum = 428
pack_errors = 0
```

- 逐项 SHA-256 + size 对照 `evidence_pack/manifest.json` 内 428 个 artifact
- **0 mismatch**（Cursor `04` §3.1 指出的 7 文件哈希漂移已清零）
- 复算脚本：内联 Python（`hashlib.sha256` 逐文件流式），不依赖 builder

---

## §3. P1 pytest 日志摘要

### 3.1 日志路径

`/tmp/stage0-pytest-237.log`（5 行 / 352 B；不在工作区，gitignore 排除，git status 不变）

### 3.2 关键摘要行

```
........................................................................ [ 30%]
........................................................................ [ 60%]
........................................................................ [ 91%]
.....................                                                    [100%]
237 passed in 349.77s (0:05:49)
```

### 3.3 与已有记录的对照

| 来源 | 壁钟 | 测试数 | 来源文件 |
|---|---|---|---|
| 本次 P1 留档 | **349.77s** | 237 passed | `/tmp/stage0-pytest-237.log` |
| docs/13 §2 R6-A 主记录 | 362.71s | 237 passed | `docs/13-r4-final-verification.md §2` |
| docs/13 §1.1 早期记录 | 342.06s | 237 passed | `docs/13-r4-final-verification.md §1.1` |
| docs/13 §2 早期 R4-6 记录 | 356.81s | 237 passed | `docs/13-r4-final-verification.md §2` |

三次壁钟在同量级（340–365s），差异来自机器状态波动 + PG17 DROP+apply 冷热启动；测试数与 collect 数 237 完全一致。

### 3.4 建议交叉引用（待用户授权）

docs/13 §8 R6-A 当前行：
> "R6-A | ✅ | 全集 pytest 复跑：237 passed in 362.71s（含 H-2 子进程 worktree proof）"

可加一行备注：

> "P1 独立留档：`/tmp/stage0-pytest-237.log`，237 passed in 349.77s（PG17 @55440；2026-08-24 commit f475717 后）"

**本轮未自动修改 docs/13**——用户授权范围只到 P0 + P1。

---

## §4. 需要终审方确认的事项（5 项）

### 4.1 [确认] P0 commit 内容是否完整

- 87 files 覆盖：12 份 docs/、schema（01-core + 002 migration + 2 log）、tests/conftest + 4 测试文件、scripts/build_evidence_pack.py、evidence_pack/manifest.json（428 artifacts）、reviews/ 全目录（00..05）、6 个 spike 目录（脚本 + 真实样本 + extracted 产物，但**不**含预解压）
- 待终审：是否还有 R4/R5/R6 涉及但漏 commit 的文件
- 检查命令：`git log -1 --stat | head -90`

### 4.2 [确认] 三个故意排除的 ?? 是否认可

| ?? 路径 | 排除规则 | 是否认可 |
|---|---|---|
| `spikes/00-provincial-yearbook-table/data/extracted/` | R4-1 tracked-ZIP-only | ⬜ 待终审 |
| `spikes/04-scanned-pdf/.fetch_time_1909.txt` | 返工指令 §6 禁 wall-clock | ⬜ 待终审 |
| `spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf` | manifest 不收录原始 PDF | ⬜ 待终审 |

特别第 3 项：用户政策 P-2 明确"不接受 1909 美国样本代表中国"，即使 .gitignore 允许入库（`!spikes/**/*.pdf`），也属争议决定。建议不入库原始 PDF，**只保留 spike 04 测试用的 truth_p24.json + gate_thresholds.json + safc1909_djvu.txt（OCR 中间产物）**，这三件已 commit。

### 4.3 [决策] 是否将 P1 pytest 留档交叉引用写入 docs/13

- 当前 docs/13 §8 R6-A 仅有 362.71s 一条壁钟
- P1 留档给出 349.77s 新独立证据
- 若用户授权，可加一行交叉引用（详见 §3.4）
- 若不授权，当前留档作为 P0 commit 的旁证使用，docs/13 不动

### 4.4 [决策] 后续工作分支

- 当前在 `main` 分支首次 commit
- 是否需要切分支（如 `stage0-r6-closure`）保留 main 干净
- 是否还有未提交的 R6 衍生工作（如 spike 04 .fetch_time 文件是否需要 gitignore 正式化）

### 4.5 [确认] Stage 0 BLOCKED 口径与用户政策是否一致

- E-1：中文扫描 PDF 缺失（spike 04）— 唯一可用样本 1909 美国统计摘要（archive.org），非中国研究平台代表性
- P-1：不降低 OCR 门槛（numeric ≥80% / char ≥90% / needs_review ≤30%）
- P-2：不接受 1909 美国样本代表中国（仅留作 OCR 管线压力样本，archive.org 等级 S0→S3）
- P-3：Stage 0 维持 BLOCKED 直到中文扫描 PDF 提供

终审方需要确认这四项与自身理解一致；如有歧义需在 Stage 1 启动前对齐。

---

## §5. 阅读路径建议（终审方按需查阅）

### 5.1 最少阅读路径（确认 P0+P1 落地即可）

1. `git log -1 --stat | head -10` — 看 commit hash + 文件数
2. `git status --porcelain` — 看是否只剩 3 个故意排除的 ??
3. `/tmp/stage0-pytest-237.log`（cat 或 Read）— 看 237 passed 摘要
4. 本文件 §0 TL;DR 表 — 看 6 个维度的状态

### 5.2 完整阅读路径（理解 Stage 0 整体返工）

1. 本文件 — §0 TL;DR + §1..§4
2. `docs/13-r4-final-verification.md` — R4-6 / R5-A / R6-A..E 完整闭环证据链（§1.1/§1.2 索引 + §8 三张闭环表）
3. `docs/12-stage0-closure-and-report.md` — Stage 0 整体状态、B/I/R2/R3/R4/R5/R6 编号映射、§11 R4 返工
4. `docs/11-stage0-review.md` — Stage 0 交付物总览、§7.3 R4 闭环、§9.4 评审清单
5. `reviews/stage0-gate0-rework-2026-08-23/04-stage0-cursor复核2-20260824.md` — Cursor 第二轮复核（R5 技术过 / "全修"叙事不过）
6. `reviews/stage0-gate0-rework-2026-08-23/05-stage0-cursor复核3-20260824.md` — Cursor 第三轮收口复核（R6 pack 同步通过 / Stage 0 仍 BLOCKED）

### 5.3 历史/审计需求路径

- `reviews/stage0-gate0-rework-2026-08-23/00-CC-返工任务指令.md` — 返工任务下发
- `reviews/stage0-gate0-rework-2026-08-23/01-Stage0-评审缺陷与证据.md` — Gate 0 首轮评审原始缺陷 B/I
- `reviews/stage0-gate0-rework-2026-08-23/02-Stage0-复验清单.md` — 复验清单
- `reviews/stage0-gate0-rework-2026-08-23/03-stage0-cursor复验.md` — Cursor 首轮复验（R4 未全过）
- `docs/09-risk-register.md` — 26 风险完整登记表（含 R22–R26 R4/R5 返工新增）

---

## §6. 红线（重申不得违反）

- ❌ 不得降低 OCR 门槛或将 spike 04 标为产品 PASS
- ❌ 不得将 1909 美国样本提升为 S0/中国代表性
- ❌ 不得批量爬取或构建官方记分卡
- ❌ 不得在未重建 pack 的情况下编辑 `docs/13` 或 pack 内 artifact
- ❌ 不得宣布 Stage 0 通过或启动 Stage 1
- ❌ 不得编辑 `reviews/` 目录（保留审计员原文）

---

## §7. 后续可执行项（等用户授权）

1. **§4.1** 用户复审 P0 commit 内容 → 若漏文件 → 新 commit 补齐
2. **§4.2** 用户对 3 个故意排除的 ?? 给出最终态度 → 若认可 → 当前 commit 为终态；若不认可（如希望入库 1909 PDF）→ 新 commit 含该文件
3. **§4.3** 用户授权 docs/13 §8 R6-A 行加 P1 交叉引用 → CC 写一行备注
4. **§4.4** 用户决定是否切分支 / 是否需要把 `.fetch_time_1909.txt` 写入 .gitignore
5. **§4.5** 用户确认 Stage 0 BLOCKED 口径 → 若一致 → 等 E-1 解除；若不一致 → 重新对齐

---

— End of P0+P1 handoff document —