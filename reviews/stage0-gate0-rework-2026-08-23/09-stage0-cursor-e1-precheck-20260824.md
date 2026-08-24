# Stage 0 Gate 0 — E-1 候选预审（`docs/16` §5.2）

- 文件编号：`09-stage0-cursor-e1-precheck-20260824`
- 预审日期：2026-08-24
- 预审方：Cursor（架构/质量审计，只读）
- 对象：`docs/16-e1-candidate-report-20260824.md`（草稿，`??` 未 commit）
- 依据：`reviews/07` §5.2 / §4 R-1..R-5；`docs/15` §4a（U-3/U-5 已裁定）
- 方法：审阅 `docs/16` 结构化报告；`git status` 确认未入库；URL 探针（本机 curl 未完整拉取 PDF，见 §1.3）

---

## §0. 预审总表

| 候选 | 标识 | 裁定 | CC 动作 |
|---|---|---|---|
| **1** | 陕西省财政预算管理条例（4 页） | **ACCEPT（有条件）** | U-1/U-2 用户裁定后 → `07` §5.3 |
| **2** | 同站 `dfxfg/PDF/` 目录 | **NEEDS-INFO** | 须逐条补 §5.1 字段后再预审；禁止目录批量下载 |
| **3–7** | Tier 2 born-digital 政府/学术 PDF | **REJECT（E-1 扫描用途）** | 不得作为 spike 04 OCR 主样本；可作未来文本提取基线另立项 |
| **8–10** | Tier 3 国际组织报告 | **REJECT（E-1）** | 非中文扫描表；不符合 R-5 |
| **11** | CRS 英文 6 页扫描 | **REJECT（E-1）** | 非中文；与 P-2 同类风险（非中国代表性 OCR 样本） |

**首选路径：** 候选 1 → 单条下载 → spike 04 集成（研究追踪；**不**解 Gate 0，见 §3）。

---

## §1. 候选 1 — 陕西省财政预算管理条例

### 1.1 字段复核

| 字段 | CC 报告 | 审计意见 |
|---|---|---|
| URL | `wb.flk.npc.gov.cn/.../d31411b562fc4226a7465f1c875afe67.pdf` | 来源可信（全国人大法规库） |
| 许可 | 政府公开 / 默认公共领域 | **弱表述**；§5.3 须在 `provenance.json` 引用站点说明或法规公开属性，勿仅写「无版权声明」 |
| 扫描证据 | Canon SC1011 + JPEG 图像层 1259×1669×4 | **下载后必验**（`pdfinfo` / `file` / Producer 字段）；本机 curl 探针未成功拉取正文（SSL/网络），不以 Agent 叙事单独采信 |
| 真值 | 嵌入文本层 pdftotext 11,387 字符 | **可满足 R-5**；§5.3 须跑 `pdftotext` 留存字符数/hash 作旁证 → **U-2 倾向不需人工全表标注** |
| 体积 | 984 KB | 可入库（非 31M 级） |
| 红线 R-1..R-5 | CC 判 ✅ | **有条件同意**（许可表述 + 下载后元数据复验） |

### 1.2 裁定

```
■ ACCEPT（有条件）— 允许进入 07 §5.3 单条下载 + spike 04 集成

条件（§5.3 步骤 1 内完成，不达标则改 NEEDS-INFO）：
  C-1. HTTP 200 且 magic=%PDF
  C-2. pdfinfo 显示图像层 / Producer 含扫描设备痕迹（与报告一致）
  C-3. pdftotext 提取中文 ≥3000 字（与报告 3,230 量级一致）
  C-4. provenance.json 写明 source_url + license 依据（法规库公开属性）

签名：Cursor 预审   日期：2026-08-24
```

### 1.3 独立探针记录

```
curl -sL wb.flk.npc.gov.cn/...pdf → http_code=000（本环境 SSL 失败，未得 PDF 字节）
```

**不因此否决候选 1**；下载验证责任在 §5.3 第一步，失败则停报。

---

## §2. 其余候选逐条裁定

### 2.1 候选 2（同站目录）

```
□ ACCEPT  ■ NEEDS-INFO  □ REJECT

理由：未逐条验证 URL/扫描属性/许可；「可持续挖掘」≠ 批量下载许可。
CC：若候选 1 集成后仍需扩展，每次只提交**一条**新 URL 走 §5.1→§5.2。
```

### 2.2 候选 3–7（born-digital）

```
□ ACCEPT  □ NEEDS-INFO  ■ REJECT（E-1 扫描 PDF 用途）

理由：R-5 要求真实扫描 PDF；born-digital 无 OCR 压力测试价值。
备注：可记入未来「文本 PDF 提取」spike，不在本次 spike 04 范围。
```

### 2.3 候选 8–10（国际组织）

```
■ REJECT — 非中文扫描统计材料；不符合 E-1 / R-5 中文扫描定位。
```

### 2.4 候选 11（CRS 英文扫描）

```
■ REJECT — 英文；6 页；非中国治理统计代表性；与 1909 美国样本同类（非目标语料）。
```

---

## §3. Stage 0 / U-3 口径（预审员确认）

依据 `docs/15` §4a（用户已裁定 U-3）：

| 项 | 口径 |
|---|---|
| spike 04 | **非 Stage 0 验收项**；OCR 管线研究追踪 |
| E-1 | **不再是 Gate 0 BLOCKED 根因**（待 docs 落地，见 §5 CC 任务 A） |
| 候选 1 集成成功 | **不得**自动宣布 Stage 0 PASS |
| P-1 / P-2 | **不变**（门槛不降；1909 不标中国代表性） |
| U-4 | eval 跑出后用户裁定；预审不预判 PASS |

`docs/16` §0 写「Stage 0 仍 BLOCKED」在 U-3 未落地前可接受；**U-3 docs 落地后**应改为「Gate 0 待 Cursor 复验 U-3 条款是否生效」。

---

## §4. 用户裁定项（停等，CC 不得下载）

| # | 事项 | 预审员建议 | 用户 |
|---|---|---|---|
| **U-1** | PRD「代表性」（统计年鉴/公报/扫描**表**） | 候选 1 **不满足**原 B-01 统计表代表性；**满足** U-3 后「中文 OCR 压力样本」 | ⬜ 待裁定 |
| **U-2** | 人工标注 ground truth | 候选 1 有嵌入文本层 → **建议不需要**全人工表标注；§5.3 用 pdftotext 作对照 | ⬜ 待裁定 |
| **U-4** | eval 后是否 Stage 0 PASS | U-3 已选移除 spike 04 验收 → **不应**因 eval 单独 PASS Gate 0 | ⬜ 待 eval 后确认 |

**CC 闸门：** `ACCEPT` 已给，但 **U-1 + U-2 用户书面/口头确认前仍禁止下载**（`07` §7 + `docs/16` §8）。

---

## §5. CC 下一步指令

### 任务 A — U-3 文档落地（可与 E-1 并行，**用户已裁定**）

按 `docs/15` §4a.2 修改 `docs/11` / `docs/12` / `docs/13`（PRD 不动）→ 单独 commit：

```
docs(stage0): apply U-3 — spike 04 non-gating for Gate 0

Per user ruling docs/15 §4a: E-1 no longer blocks Stage 0; spike 04
retained as OCR research track only. P-1/P-2 unchanged.
```

改后 **不强制** rebuild pack（U-5：维持 429）；若改了 pack 内 docs 则必须 rebuild。

### 任务 B — 更新 `docs/16` §5 预审记录

将本文件 §1.2 / §2 裁定抄入 `docs/16` §5（替换空白模板）→ **仍不 commit**，直至 U-1/U-2 确认后与 §5.3 成果一并 commit。

### 任务 C — U-1/U-2 确认后执行 `07` §5.3

1. 单条 `curl -O` 至 `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`（文件名可调整）
2. 验证 C-1..C-4（§1.2）
3. 更新 `provenance.json`；**禁止** `.fetch_time_*.txt`
4. 用 pdftotext 层生成/更新 `truth_*.json`（按 README）
5. `extract_04` → `evaluate_04` → 记录 eval（**不改** `gate_thresholds.json`）
6. pytest spike04 + 全集 237
7. 更新 `docs/03` §4.4（标注「非验收项 / 压力样本」）
8. rebuild pack → `pack_errors=0`
9. commit：`feat(spike04): add Chinese scanned PDF (Shaanxi fiscal regulation, research track)`
10. 请求 Cursor 复验（`10-stage0-cursor-e1-integration-*`）

### 任务 D — 禁止

- ❌ 未经 U-1/U-2 下载
- ❌ 批量拉取候选 2 目录
- ❌ 用候选 3–11 顶替候选 1 而不重新预审
- ❌ eval 不达标时改门槛
- ❌ 宣布 Stage 0 PASS

---

## §6. 审计证据

```
git status --porcelain
?? docs/16-e1-candidate-report-20260824.md

pack: 429 artifacts, 0 errors（未 rebuild）
```

---

## §7. 本文件未做的事

- 未下载 PDF
- 未修改 `docs/16` / spike 04 / pack
- 未代替用户裁定 U-1 / U-2 / U-4

— End of E-1 precheck (2026-08-24) —
