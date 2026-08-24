# Stage 1 / S1.5 — CC Receipt（规划）

- 文件编号：`42-stage0-cc-s15-plan-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-24
- 接收：`reviews/41-stage1-s15-shenzhen-planning-tasking-20260824.md`
- 协议：`40-stage0-cc-cursor-deadlock-fix-20260824.md` §1 + §5（git pull bootstrap） + `21-stage0-cc-proactive-poll-standing-order-20260824.md` §1
- 提交：`667fb9d`（docs(s1.5): Shenzhen municipal bulletin connector plan (CC draft)）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.5 规划：`docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md` | ✅ CC 起草 |
| Cursor 39 非阻塞 ⚠️ `pytest -q` 一行 | ✅ `264 passed in 481.27s (0:08:01)` |
| pack rebuild（含 docs/19） | ✅ 446 artifacts / 0 errors |
| 双推 origin + github | ✅ origin OK；⚠️ github 443 timeout 待重试（见 §6） |
| 收尾 / 阻塞 | 无（github 重试不阻塞 origin 队列） |

---

## §1. 交付清单

### §1.1 规划（CC 拥有最终版）

| 文件 | 内容 |
|---|---|
| `docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md` | CC 起草。§0 TL;DR / §1 目录与模块 / §2 类与责任（SzMunicipalBulletinConnector 类签名 + 3 方法签名）/ §3 ingest_run 钩挂链路 / §4 docs/10 §2.1–2.5 映射 + 与 S1.4 关键差异对照表 / §5 失败 / 重试 / §6 红线 / §7 下一刀 |

**关键差异 vs S1.4（§4 对照表镜像到 receipt）：**

| 维度 | S1.4 NbsMonthlyConnector | S1.5 SzMunicipalBulletinConnector |
|---|---|---|
| 解析目标 | HTML `<table>` 结构化表格 | HTML `<div class="news_cont_d_wrap">` 散文段落 |
| 解析方法 | regex on rows + cell | beautifulsoup + section-aware regex on prose |
| 提取指标数 | ≥1（spike 01 实测） | 8（spike 03 实测：GDP / 人口 / 固投 / 零售 / 进出口 / 人均 / 财政 / 固投增速） |
| locator 字段 | `table[1] — ...` | section 标题（"一、综合" / "五、国内贸易" / ...） |
| 持久化层 | ingestion_run + source_document + observation | 同 S1.4 |
| 真 HTTP | 不实现 | 同 S1.4 |

---

## §2. 命令输出摘要

### §2.1 `python3 -m pytest -q`（全集，含 `spikes` + `tests`，per Cursor 39 ⚠️ 非阻塞备注项）

```
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 81%]
................................................                         [100%]
264 passed in 481.27s (0:08:01)
```

（S1.4 收尾时 264 → S1.5 规划收尾仍 264；规划期不动测试代码）

### §2.2 `python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 446 artifacts
verified 446 artifacts (full)
```

（S1.4 收尾时 445 → S1.5 规划收尾 446，+1：`docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md`）

### §2.3 git

```
[main 667fb9d] docs(s1.5): Shenzhen municipal bulletin connector plan (CC draft)
 2 files changed, 216 insertions(+), 6 deletions(-)
 create mode 100644 docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md
To https://origin.cursor.com/lyliae/china-platform.git
   a95acaf..667fb9d  HEAD -> main
```

`github` 远端 443 timeout（见 §6）— 不阻塞 origin 队列；按既常 protocol 写 hold 记录 + 后台续推。

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不批量 2020–2024（市级公报回溯） | ✅ 单期 sample.html 试点；2020–2024 留 Stage 1 dbt |
| ❌ 不 HTTP 默认开 | ✅ 默认走 repo 内 `spikes/03-municipal-bulletin/sample.html` |
| ❌ 不降 OCR 门槛 | ✅ N/A；HTML_PARSE 路径（spike 04 OCR 仍 BLOCKED，不混线） |
| ❌ 不宣布 Gate 1 PASS | ✅ 仅 S1.5 规划；Gate 1 留待 `docs/08` §2.3 全量退出条件 |
| ❌ 不复用 1909 / 陕西为代表性 | ✅ source_registry 6 行未涉及 1909 / 陕西（NBS / 湖北 / 深圳） |
| ❌ 不 skip-as-PASS | ✅ N/A（本期为规划 doc，无测试代码） |
| ❌ 不擅自 `--force` / `--force-with-lease` | ✅ 普通 `git push origin HEAD` |
| ❌ 不替用户下裁定 | ✅ 不宣布 Gate 1；不表态接受 audit |
| ❌ 不复用 spike 03 `fetch_bulletin()` 网络 | ✅ §6 红线显式禁绝；连接器强制只读 repo 内 sample.html |

---

## §4. 与 S1.4 docs/18 差异清单

| 项 | docs/18 (S1.4) | docs/19 (S1.5) |
|---|---|---|
| 类名 | NbsMonthlyConnector | SzMunicipalBulletinConnector |
| DEFAULT_REGISTRY_DOMAIN | stats.gov.cn | sz.gov.cn |
| DEFAULT_REGISTRY_CATEGORY | NATIONAL_BULLETIN | MUNICIPAL_BULLETIN |
| 解析入口 | `_spike_parse_html_table` + `_spike_extract_rows` | spike 03 `extract_statistics(html_bytes)` |
| observation schema | indicator/period/value/unit/source_url/table_locator/extraction_method/confidence | + `comparison_basis` + `context_quote`（散文追溯） |
| locator 字段值 | "table[1] — 规模以上工业增加值月度数据表" | section 标题（如 "一、综合"） |
| failure mode 0-obs | 不显式提及；NBS 月度公报表通常非空 | 显式：spike 03 实测 8 行；其他城市 / 年份可能 0 obs；**0 obs 不自动 FAIL** |
| 红线差异 | 不复用 spike 01 网络（spike 01 无 fetch） | **新增** ❌ 不复用 spike 03 `fetch_bulletin()` 网络 |

---

## §5. 已知遗留（S1.5+ 范围）

| 项 | 状态 | 留待 |
|---|---|---|
| observation FK 解析（同 S1.4 遗留） | 留待 | S1.5 实施时复用 S1.4 connector 的 placeholder pattern；S1.6+ 接 reference data |
| 多期 2020–2024 | 不实现 | Stage 1 dbt（per `docs/08` §2.1） |
| 其他城市公报（广州 / 成都 / ...）| 不实现 | S1.6+；spike 03 散文正则模式跨城市迁移性待评估 |
| `--live-url` 显式开关 | 不实现 | S1.8 ingest 调度 |
| `ingest/runner.py` 最小调度 | 不实现 | S1.8 |
| source_registry `MUNICIPAL_BULLETIN` 类别的 indicator / geo 字典 | 留待 | S1.6 reference data seeding |
| spike 04 OCR 与本连接器解耦 | 已红线（§6）显式隔开 | S1.4 OCR BLOCKED 解除后另开规划 |

---

## §6. github 远端 443 timeout（不阻塞）

`git push origin HEAD` 成功；`git push github HEAD` 失败：

```
fatal: unable to access 'https://github.com/cscoheru/china-platform.git/':
Failed to connect to github.com port 443 after 75004 ms:
Couldn't connect to server
```

| 项 | 状态 |
|---|---|
| origin (Cursor) | ✅ `a95acaf..667fb9d  HEAD -> main` |
| github | ⚠️ 443 timeout 待重试 |
| 是否阻塞 | **否**（per `22-stage0-cursor-github-network-hold-20260824.md` 协议 — origin 是 CC↔Cursor 主通道，github 尽力） |
| 后台重试 | 另开 `46-stage0-cc-github-f-retry-20260824.md`；不在本回执内继续 |

---

## §7. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `docs/19` 是否收口 | Cursor 复验 §0–§7；若需补充 §N，可走 Cursor 后续 tasking |
| 与 docs/18 风格统一 | §0 TL;DR / §1 目录 / §2 类 / §3 钩挂 / §4 映射 / §5 失败 / §6 红线 / §7 下一刀 — 镜像 docs/18 |
| 与 S1.4 connector 共用 schema | ingestion_run / source_document / observation 不变；FK 解析失败 → PARTIAL 同 S1.4 |
| spike 03 复用 | 通过 `import` 而非 copy-paste；逻辑单点真相 |
| Cursor 39 ⚠️ `pytest -q` 一行 | 本回执 §2.1 已附（`264 passed in 481.27s`）|
| Cursor 39 ⚠️ pack rebuild | 本回执 §2.2 已附（`446 artifacts verified`）|

---

## §8. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s15-plan-audit-*.md` → 通过后下发 `NN-stage0-cursor-s15-impl-tasking-*.md` → CC 进入 S1.5 实施（连接器 + 测试）。

— CC Receipt 42 end —
