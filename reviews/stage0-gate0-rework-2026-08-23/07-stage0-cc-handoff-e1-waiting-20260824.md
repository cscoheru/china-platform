# Stage 0 Gate 0 — CC 执行指令（E-1 等待期）

- 文件编号：`07-stage0-cc-handoff-e1-waiting-20260824`
- 下发方：Cursor（架构/质量审计）
- 下发日期：2026-08-24
- 适用对象：Claude Code（CC）
- 前置审核链：`03` → `04` → `05` → `06`（P0+P1 终审通过）
- 状态：**开发返工已终态收口；Stage 0 Gate 0 仍 BLOCKED（E-1）；等待 E-1 研究 Agent 结果**

---

## §0. TL;DR（CC 先看）

| 维度 | 状态 | 证据 |
|---|---|---|
| Dev rework R4+R5+R6 | ✅ 20/20 终态 | `f475717` |
| P0+P1 文档/pack | ✅ 已落地 | `0ac4661` |
| Pack 哈希 | ✅ 0 / 429 | `evidence_pack/manifest.json` |
| Stage 0 Gate 0 | 🔴 BLOCKED | E-1 + P-1/P-2/P-3 |
| Stage 1 | ❌ 禁止启动 | 等用户解除 E-1 或改 PRD |
| 当前任务 | ⏳ 等待 E-1 研究 Agent | 见 §4–§6 |

**CC 此刻应做：** 保持仓库干净（§3 可立即执行项）；**不要**自行下载中文 PDF、改 spike 04 门槛、或宣布 Stage 0 通过。研究 Agent 有结论后按 §5 流程执行，缺用户裁定的项停等（§7）。

---

## §1. 基线快照（审计独立复验，2026-08-24）

### 1.1 Git

```
0ac4661 chore(docs+pack): add P0+P1 handoff, Cursor final audit, P1 cross-ref
f475717 chore(stage0): close R4+R5+R6 dev rework; sync evidence pack to 428/0
```

`0ac4661` 变更（5 files）：

| 文件 | 作用 |
|---|---|
| `.gitignore` | 显式排除三路径（§3.2）；含 broad `!spikes/**/*.pdf` 但被显式 exclude 覆盖 |
| `docs/15-stage0-p0p1-handoff-20260824.md` | CC P0+P1 终审包 |
| `reviews/06-stage0-cursor-p0p1-audit-20260824.md` | Cursor P0+P1 终审 |
| `docs/13-r4-final-verification.md` | §8 R6-A 加 P1 旁注（349.77s） |
| `evidence_pack/manifest.json` | 428 → **429**（+`docs/15`） |

### 1.2 Pack

```
schema_version     = 1.1-R3G-R4
artifact_count     = 429
pack_errors        = 0
commit_meta (stale)= f475717a6ac0   ← 见 §3.3
```

### 1.3 工作区残留

```
?? .firecrawl/    ← 研究 Agent 工具缓存；应清理或 gitignore
```

三路径 `??`（extracted / `.fetch_time` / 1909 PDF）已由 `.gitignore` 排除，**不应**出现在 `git status`。

### 1.4 已知非阻塞缺口

| 缺口 | 严重性 | 说明 |
|---|---|---|
| `reviews/06` 不在 pack 429 内 | 低 | builder 未 glob `reviews/`；git 已 track |
| manifest `commit` 元数据仍指 `f475717` | 低 | 哈希 0/429 成立；下次 rebuild 应刷新 |
| `docs/15` §0 仍写 pack 428 | 低 | 历史快照；以 manifest 429 为准 |

---

## §2. 已关闭项（CC 勿再返工）

- R4-1..R4-6、R5-A..R5-I、R6-A..R6-E：**20/20 闭环**
- 默认 apply 链（`01-core.sql` + `migrations/*.sql` via `tests/conftest.py`）
- I-05 治理 schema + 测试
- Pack 哈希漂移（`04` 的 7/428 问题）
- P0 commit + P1 pytest 留档（237 passed / 349.77s，`/tmp/stage0-pytest-237.log`）
- `docs/15` + `reviews/06` 入库
- `.gitignore` 显式排除三路径（`06` §4.2 裁定）

---

## §3. CC 可立即执行（无需用户裁定）

### 3.1 清理 `.firecrawl/`

```bash
# 若目录仅为研究 Agent 临时缓存：
rm -rf .firecrawl/
# 或追加 .gitignore：
echo ".firecrawl/" >> .gitignore
```

验证：`git status --porcelain` 应为空。

**若清理/ignore 后 status 仍非空 → 停报，勿 commit 未知文件。**

### 3.2 禁止操作清单（等待期）

- ❌ 下载或入库任何中文扫描 PDF（等 §5 预审通过）
- ❌ 修改 `gate_thresholds.json` 或降低 OCR 门槛
- ❌ 将 1909 美国样本标为中国代表性或 S0
- ❌ 批量爬取、绕墙、商业库接入
- ❌ 编辑 `docs/13` 或 pack artifact 后不重建 pack
- ❌ 宣布 Stage 0 PASS 或启动 Stage 1
- ❌ 修改 `reviews/03`–`06` 既有审核原文

### 3.3 下次 rebuild pack 时刷新 manifest commit 元数据

任何触发 `scripts/build_evidence_pack.py` 时，确认输出含当前 `git rev-parse HEAD`；期望 `0ac4661` 或更新 commit。

```bash
EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 python3 scripts/build_evidence_pack.py
# 验证：pack_errors=0 of N
```

---

## §4. E-1 研究 Agent — 红线（已告知 Agent，CC 复核）

| # | 约束 |
|---|---|
| R-1 | 不爬取 / 不绕墙 / 不批量 |
| R-2 | 不使用商业 OCR 库或付费数据源 |
| R-3 | 不合成 PDF / 不用 HTML 打印冒充扫描 |
| R-4 | 不降低 `gate_thresholds.json` 门槛 |
| R-5 | 必须：**真实中文扫描 PDF** + **授权明确** + **真值可对照** |

---

## §5. E-1 候选源 — CC 执行流程（研究 Agent 回报后）

### 5.1 第一步：整理候选报告（不下载）

向 Cursor 审核员提交结构化报告（可写 `docs/16-e1-candidate-report-YYYYMMDD.md` 草稿，**勿 commit 直至预审通过**）：

```markdown
## 候选 N
- URL:
- 来源机构:
- 许可依据: (PD / CC-BY / 政府开放 / ToS 条款引用)
- 文件类型证据: (扫描 PDF / 页数 / 是否图像层)
- 真值对照: (同页 HTML / DjVu txt / 手工表 / 无)
- 代表性说明: (统计年鉴/公报/普查表等)
- 体积:
- 风险: (绕墙 / 批量 / 商业库 / 无许可)
```

### 5.2 第二步：等 Cursor 预审裁定

| 裁定 | CC 动作 |
|---|---|
| **ACCEPT** | 进入 §5.3 单条下载 |
| **REJECT** | 放弃该候选；记录原因；试下一候选或 §6 失败路径 |
| **NEEDS_INFO** | 补许可/真值证据后重新提交 |

**CC 不得在未经 Cursor ACCEPT 的情况下下载或入库 PDF。**

### 5.3 第三步：单条下载 + spike 04 集成（仅 ACCEPT 后）

1. **下载**至 `spikes/04-scanned-pdf/data/<source>_<page>.pdf`（单文件）
2. **更新** `spikes/04-scanned-pdf/provenance.json`：
   - `source_url`、`license`、`fetched_at` 用 ISO UTC（**禁止** wall-clock `.fetch_time_*.txt` 风格文件）
3. **重建真值**：
   - 若有机器可读对照 → `build_truth_p*.py` 或等价脚本生成 `truth_p*.json`
   - 若无对照 → **停**，回报 Cursor + 用户（§7.1）
4. **跑管线**：
   ```bash
   python3 spikes/04-scanned-pdf/extract_04_scanned_pdf.py  # 按 README
   python3 spikes/04-scanned-pdf/evaluate_04.py
   ```
5. **读** `data/extracts/04-scanned-pdf/eval_report.json` + `gate_thresholds.json`：
   - numeric ≥80%、char ≥90%、needs_review ≤30%（**P-1 不变**）
   - 不达标 → spike 04 仍 BLOCKED；**不得**改门槛换 PASS
6. **测试**：
   ```bash
   python3 -m pytest spikes/04-scanned-pdf/ -q -p no:cacheprovider
   python3 -m pytest -q -p no:cacheprovider   # 全集 237
   ```
7. **更新文档**（用户授权后）：
   - `docs/03-source-registry.md` §4.4 spike 04 状态
   - `docs/12` / `docs/11` E-1 行
   - **不自动**改 Stage 0 总判定为 PASS
8. **重建 pack** → `pack_errors=0`
9. **Commit**（单独 logical commit）：
   ```
   feat(spike04): add Chinese scanned PDF sample for E-1 validation
   
   Source: <机构> (<license>). Eval: <pass|blocked>. Stage 0 Gate 0
   remains <BLOCKED|条件解除> pending Cursor re-audit.
   ```

### 5.4 第四步：请求 Cursor 复验

提交给审核员：

- 新 `eval_report.json` 摘要
- `provenance.json`
- `git log -1 --stat`
- `pack_errors` 输出
- pytest 04 + 全集结果

**仅 Cursor 复验 + 用户确认后，方可讨论 Stage 0 E-1 是否解除。**

---

## §6. E-1 全部失败 — CC 报告模板（不擅自改 PRD）

研究 Agent 无 ACCEPT 级候选时，CC 撰写报告（`docs/16-e1-search-negative-report-YYYYMMDD.md` 草稿）：

```markdown
# E-1 中文扫描 PDF 检索 — 负面结果

## 检索范围
- 日期 / 方法 / 关键词

## 否决候选摘要（每条一行：URL + 否决原因）

## 结论
无法在红线内找到合法免费中文扫描 PDF + 真值对照。

## 替代路径（需用户裁定，CC 不自行选择）
1. 用户上传 PDF
2. 授权库接入（需书面许可）
3. PRD 缩小 Stage 0 OCR 验收范围（需用户书面批准）
```

**停等用户裁定。** CC 不得自行选路径 3 或宣布缩小范围。

---

## §7. 需用户裁定项（CC 停等，写入报告即可）

| # | 事项 | CC 动作 |
|---|---|---|
| U-1 | 候选 PDF 是否满足 PRD「代表性」 | 附 §5.1 报告；等用户 + Cursor |
| U-2 | 无真值对照时是否接受人工标注 ground truth | 停等；不得自行标注入库 |
| U-3 | E-1 失败后选上传 / 授权库 / 改 PRD | 列选项；不替用户决定 |
| U-4 | eval 达标后是否宣布 Stage 0 PASS | **禁止** CC 自行宣布；等 Cursor 复验 + 用户 |
| U-5 | 是否将 `reviews/06` 纳入 pack glob | 低优；用户授权后改 builder |

---

## §8. 红线（完整）

- ❌ 不得降低 OCR 门槛或将 spike 04 标为产品 PASS（除非 eval 真达标且 Cursor+用户确认）
- ❌ 不得将 1909 美国样本提升为 S0/中国代表性
- ❌ 不得批量爬取或构建官方记分卡
- ❌ 不得在未重建 pack 的情况下编辑 pack 内 artifact
- ❌ 不得宣布 Stage 0 通过或启动 Stage 1（无 Cursor 复验 + 用户指令）
- ❌ 不得篡改 `reviews/03`–`06` 原文
- ❌ 不得入库 `statistical_abstract_foreign_countries_1909.pdf`（31M；P-2）
- ❌ 不得创建 wall-clock `.fetch_time_*.txt` 入库

---

## §9. 阅读路径（CC 按需）

| 优先级 | 文件 | 用途 |
|---|---|---|
| P0 | **本文件** | 当前指令 |
| P0 | `reviews/06-stage0-cursor-p0p1-audit-20260824.md` | P0+P1 终审结论 |
| P1 | `docs/15-stage0-p0p1-handoff-20260824.md` | CC 自己的 P0+P1 回执 |
| P1 | `spikes/04-scanned-pdf/README.md` | spike 04 管线 |
| P1 | `spikes/04-scanned-pdf/gate_thresholds.json` | 门槛（勿改） |
| P2 | `docs/03-source-registry.md` §4.4 / §9 | I-05 + spike 04 状态 |
| P2 | `reviews/05` | R6 pack 同步背景 |

---

## §10. 验收口令（CC 自检）

等待期结束条件（`git status` 干净）：

```bash
git status --porcelain          # 期望：空
git log --oneline -2            # 期望：0ac4661, f475717
python3 -c "..."                # pack_errors=0 of 429（见 §1.2 脚本）
```

E-1 集成后额外口令：

```bash
python3 -m pytest -q -p no:cacheprovider   # 237 passed
# eval_report 数字对照 gate_thresholds.json
# pack_errors=0 of N（N 可能 >429）
```

---

— End of CC handoff (E-1 waiting, 2026-08-24) —
