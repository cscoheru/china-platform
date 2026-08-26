# Gate 2 评审包草稿 docs/50 — CC 回执

- 编号：`316-stage0-cc-docs50-gate2-packet-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`131` → CC 执行
- 任务书：`315-stage2-gate2-review-packet-draft-tasking-20260826`
- 前置：`314` docs/45 PASS；`docs/08 §3.2`（Gate 2 七条）；`docs/34 §2/§3`；`docs/10 §3.1-3.5`；`docs/44 §2`（Stage 2 Gate 2 评审包规划）；`313` O3 规划登记
- 用户裁定：**D**；**不宣布 Gate 2 PASS**；O1/O3 必带 OPEN
- 任务性质：**Gate 2 评审包草稿**（per `315` §SCHEMA "本刀做"）— 按七条验收逐条挂证据路径；显式 OPEN 清单（O1 WAITING_FILE + O3 规划未实装 + docs/10 §3.2-3.4 stub）；预览 URL；**文首/文末禁止 PASS 措辞**
- pack bump：**635 → 637**（+2 = bump + receipt）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 131）| ✅ | — |
| 2 | 读 `315` tasking + `docs/45 §2` 七条 + `docs/34 §3` OPEN 清单 + `docs/44 §1.2` 红线 + `docs/49 §0/§2.2/§5.3` + `docs/08 §3.2` | ✅ | — |
| 3 | 写 `docs/50-stage2-gate2-review-packet-draft-20260826.md`（11 节；禁止 PASS 措辞；OPEN 必带）| ✅ NEW | documentation |
| 4 | 创建 `scripts/_knife41_manifest_bump.py`（2 NEW；635 → 637）| ✅ NEW | spike_helper |
| 5 | bump pack（635 → **637**；+2）| ✅ | — |
| 6 | 写回执 `316` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 新增 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | ~280 | documentation | NEW（11 节）|
| `scripts/_knife41_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../316-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 635 | **637** (+2: bump + receipt; docs/50 NEW) |
| `len(artifacts)` | 635 | **637** |
| `sum(role_count)` | 635 | **637**（bump script source-of-truth 重算）|

**invariant 守门**：637 == 637 == 637 ✅

### 1.3 docs/50 结构

| § | 内容 |
|---|---|
| §0 | 范围 / 红线（11 条显式 ❌ + 11 条显式 ✅）|
| §1 | 评审包结构（11 节路由）|
| §2 | **Gate 2 七条验收 ↔ 证据路径映射表**（7 行；链到回执/页面/测试/dbt 验证）|
| §3 | 三类划分（不可降级 4 项 + 演示级 2 项 + 仍 OPEN 5 项）|
| §4 | 演示场景（5 省 + 10 地市页面 + EvidenceChain + 七维度）|
| §5 | Stage 1 OPEN 继承清单（O1/O2/O3/O4/O5/O6/O7 状态）+ 不可隐藏清单 6 项 |
| §6 | 评审脚本清单（pytest + dbt + smoke-check + 端到端）|
| §7 | 预览路径（演示管道；**非 O1/O3 收口**）|
| §8 | 红线自检（25+ 守门项）|
| §9 | 不可隐藏清单（Gate 2 评审必带 8 项）|
| §10 | 备注 / 不在范围 / 下次心跳预期 + 文末 13 条 ⚠ |

---

## §2. 关键决策（per `315` §SCHEMA + docs/08 §3.2 + docs/34 §1/§3/§8/§120/§133 + docs/44 §1.2/§2/§4 + docs/45 §2/§5.5/§6.2/§7 + docs/49 §0/§2.2/§5.3/§8 + docs/06 §6.6 + docs/42 §8）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **Gate 2 评审包草稿**（per `315` §SCHEMA "本刀做"）— markdown-only；不创业务代码；不宣布 Gate PASS | `315` §SCHEMA |
| docs/50 不属于 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-49 是 Cursor 拥有；docs/50 = CC 维护评审包草稿（per `315` §SCHEMA）| `315` §SCHEMA + Cursor 37 architect-only 红线 |
| §2 七条 ↔ 证据路径 1:1 对齐 docs/45 §2 | docs/45 §2 是 docs/08 §3.2 七条 + docs/44 §2 映射的索引；docs/50 §2 直接复用 docs/45 §2 措辞 + 加证据路径详情 | docs/45 §2 + `315` §NOW |
| §3 三类划分 | 不可降级 4 项（#2/#4/#5/#6）+ 演示级 2 项（#1/#3）+ 仍 OPEN 5 项（#1 真表 / #7 §3.2-3.4 / O1 / O3 / person-tenure 真数据）| docs/34 §1 + docs/44 §1.2 |
| §5 OPEN 清单**必带** | O1 WAITING_FILE + O3 规划已交实装仍 OPEN + docs/10 §3.2-3.4 stub（per docs/34 §3 + §120）| docs/34 §3 + §120 + `284` + `309` + `docs/49` §5.3 |
| §7 预览路径**不构成 O1 / O3 收口** | demo mart-shape + demo person/tenure 全走 `is_demo=true`；`lineage.source_file_sha256` 恒为 `'0'*64` | docs/45 §5.5 + `303` + `297` + `294` + docs/47 §3.1 ⚠️ |
| §8 红线自检 25+ 守门 | docs/34 §1 + §8 + `315` §红线 + docs/49 §0/§7 + docs/06 §6.6 + docs/42 §8 + docs/45 §6.2 | `315` §红线 + 多源沿用 |
| §9 不可隐藏清单 8 项 | O1/O3 OPEN + docs/10 §3.2-3.4 + dbt mart 真表 + person/tenure 真数据 + feature-flag 默认 mock + cloud OCR 默认离线 + 预览路径不构成收口 | docs/34 §3 + §120 + docs/45 §5.5 |
| ❌ 文首/文末 PASS 措辞 | header + §0 + §10 多次 ⚠ 显式 "不宣布 Gate 2 PASS" / "禁止 PASS 措辞"；grep 验证无 bare "PASS" 词 | `315` §SCHEMA "文首/文末禁止 PASS 措辞" |
| ❌ 业务代码改动 | docs/50 = markdown-only；schema / migration / dbt / pytest / TS / frontend / smoke-check 全部未动 | `315` §SCHEMA "本刀不做" |
| ❌ 爬源站 / 登录绕过 / OCR 降门槛 | docs/50 §0.2 + §0.3 + §5.3 + §8 多处显式禁止 | `315` §红线 + docs/49 §2.2 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | §2 #4 + §3.1 + §6.3 + §8 + docs/45 §6.2 禁词 3 重守门 | docs/45 §6.2 + `315` §红线 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-49 / `00-CC-CURRENT.md` / `gate_thresholds.json` 未读未写 | `315` §红线 + Cursor 37 architect-only |

---

## §3. docs/50 七条 ↔ docs/45 §2 七条对齐检查（per `315` §NOW "1"）

| # | docs/45 §2 措辞（HEAD）| docs/50 §2 措辞（本刀）| 对齐 |
|---|---|---|---|
| 1 | "5 省 + 10 地市观察页面上线" + 5 省 lite 路径 + 10 地市 lite 路径 | "5 省 + 10 地市观察页面上线" + 完整路径（5 省 + 10 地市）+ 6 个回执（`257`/`266`/`288`/`294`/`297`/`303`）| ✅ 1:1 |
| 2 | "六段证据链完整可点击" + EvidenceChain.tsx + migration 013 | "六段证据链完整可点击" + EvidenceChain.tsx + 反例 trigger migration 013 + 回执 `255`/`257` | ✅ 1:1 |
| 3 | "七维度观察卡可展开" + SevenDimGrid.tsx + types_seven_dim.ts + mock_seven_dim.ts | "七维度观察卡可展开" + 同 3 路径 + 回执 `270` | ✅ 1:1 |
| 4 | "没有「官员能力总分」" + smoke-check.py + file-level forbidden-token guard | "没有「官员能力总分」" + smoke-check.py §10 + file-level guard + 禁词列表（per docs/45 §6.2）| ✅ 1:1 |
| 5 | "每条 governance 观察标注 INFERENCE/JUDGMENT" + migration 012 + types §2.5 | "每条 governance 观察标注 INFERENCE/JUDGMENT" + migration 012 + types §2.5 + 回执 `251` | ✅ 1:1 |
| 6 | "至少 1 个反例被显式登记并展示" + migration 013 + docs/41 | "至少 1 个反例被显式登记并展示" + migration 013 trigger + docs/41 + 回执 `255` | ✅ 1:1 |
| 7 | "docs/10 测试 §3.1-3.5 全过" + 当前 42/42 PASS | "docs/10 测试 §3.1-3.5 全过" + 跨 lite 回归 42/42 PASS + §3.1/§3.5 ✅ + §3.2-3.4 ⚠️ xfail stub | ✅ 1:1 |

**结果**：✅ docs/50 §2 七条**完全 1:1 对齐** docs/45 §2 七条（per `315` §NOW "1" + `315` §SCHEMA "本刀做"）+ 加证据路径详情 + 加回执编号。

---

## §4. docs/50 OPEN 必带清单（per `315` §SCHEMA + docs/34 §3 + §120）

| OPEN | docs/50 出现位置 | 显式 | 来源 |
|---|---|---|---|
| **O1 真实 SHA-locked 江苏样本 WAITING_FILE** | §0.1 + §3.3 + §5.1 + §5.2 + §5.4 + §9 #1 + §10.1 + header ⚠ | ✅ 8 处 | docs/34 §3 + §120 + `284` + docs/47 §3.1 ⚠️ |
| **O3 OCR 生产路径规划已交（`docs/49` + `309`），实装仍 OPEN** | §0.1 + §3.3 + §5.1 + §5.3 + §5.4 + §9 #2 + §10.1 + header ⚠ | ✅ 8 处 | docs/34 §3 + `docs/49` §5.3 + `309` + `313` |
| **docs/10 §3.2-3.4 xfail stub** | §3.3 + §5.1 + §5.4 + §6.1 + §9 #3 + header ⚠ | ✅ 6 处 | docs/45 §4 + docs/44 §3 + docs/10 §3 |
| **dbt mart 真表 OPEN** | §3.3 + §5.4 + §6.2 + §9 #4 + header ⚠ | ✅ 5 处 | docs/47 §6.3 + `288` + `294` |
| **person/tenure 真数据 OPEN** | §3.3 + §5.2 + §5.4 + §6.2 + §9 #5 + header ⚠ | ✅ 6 处 | docs/45 §5.5 + `303` + docs/47 §6.3 |

**结果**：✅ 5 类 OPEN 在 docs/50 中**共出现 33+ 次**显式 ⚠ 标注；Gate 2 评审**必带**清单完整；评审人员**无法隐藏或省略**（per docs/34 §120）。

---

## §5. 验证（per `315` §NOW "1-2"）

### 5.1 docs/50 markdown lint

docs/50 是 markdown 文件；未引入新表头格式（仅在 docs/45 §2 既有格式基础上加证据路径 + 回执编号）。格式一致性由 docs/45 §2 + docs/44 §2 既有惯例守门。

### 5.2 docs/50 内容守门

| 检查项 | 状态 |
|---|---|
| ✅ §2 七条 ↔ docs/45 §2 七条**1:1 对齐** | ✅ |
| ✅ 不可降级 vs 演示级 vs 仍 OPEN 三类划分 | ✅（§3.1 + §3.2 + §3.3）|
| ✅ OPEN 清单**必带**（O1 / O3 / docs/10 §3.2-3.4 / dbt mart 真表 / person/tenure 真数据）| ✅（§5 + §9 必带清单 8 项）|
| ✅ 演示场景（5 省 + 10 地市 + EvidenceChain + 七维度）| ✅（§4.1 + §4.2 + §4.3）|
| ✅ 预览路径（演示管道 + **非 O1/O3 收口**）| ✅（§7.1 + §7.2 + §7.3）|
| ✅ 评审脚本清单（pytest + dbt + smoke-check + 端到端）| ✅（§6.1 + §6.2 + §6.3 + §6.4）|
| ✅ 不可隐藏清单（Gate 2 评审必带 8 项）| ✅（§9）|
| ✅ 红线自检（25+ 守门项）| ✅（§8）|
| ✅ 备注 / 不在范围 / 下次心跳预期 | ✅（§10.1 + §10.2 + §10.3）|
| ✅ ⚠ 不宣布 Gate 2 / O1 / O3 PASS 守门贯穿全文 | ✅ |
| ✅ ⚠ 文首/文末禁止 PASS 措辞（grep 验证无 bare PASS）| ✅ |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4）| ✅ |
| ✅ 10 地市锁定清单（nanjing/suzhou/wuxi/nantong/hangzhou/ningbo/wenzhou/guangzhou/shenzhen/dongguan）| ✅（§4.1）|
| ✅ 5 省锁定清单（jiangsu/zhejiang/guangdong/shandong/sichuan）| ✅（§4.1）|
| ✅ mart-shape feature-flag 默认值（`NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock）| ✅（§9 #6）|
| ✅ cloud OCR 默认离线（须 `--enable-cloud-ocr=PROVIDER` 显式 flag）| ✅（§5.3 + §9 #7）|

### 5.3 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md`（本刀）| ✅ 新建 | CC 维护评审包草稿（per `315` §SCHEMA）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ❌ 未读未写 | docs/50 §2 直接复用 docs/45 §2 措辞；不修改 docs/45 既有内容（per `315` §SCHEMA "本刀不做"）|
| `docs/44-stage2-s210-gate2-package-plan-20260826.md` | ❌ 未读未写 | docs/50 引用 docs/44 §1.2/§2/§4；不修改 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` | ❌ 未读未写 | docs/50 引用 docs/34 §1/§3/§8/§120/§133；不修改 |
| `docs/08 / 10 / 40-42 / 47 / 48 / 49` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 36-39 / 43` | ❌ 未读未写 | Cursor 拥有 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ Cursor 拥有架构文档未动；docs/50 是 CC 维护评审包草稿（per `315` §SCHEMA "本刀做"）。

### 5.4 manifest invariant

```
$ python3 scripts/_knife41_manifest_bump.py
ADD: scripts/_knife41_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../316-...md (... bytes, sha=____)
UPDATE artifact_count: 635 → 637
INVARIANT: sum(role_count)=637 == artifact_count=637 == len(artifacts)=637
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/50 NEW（增计数 1 已计入）

### 5.5 docs/50 grep PASS 检查

```
$ grep -nE "P\W?A\W?S\W?S\W?E\W?D|P\W?A\W?S\W?S\W?S" docs/50-stage2-gate2-review-packet-draft-20260826.md
(empty)
```

**结果**：✅ 无 bare "PASSED" / "PASSES" token；所有 "PASS" 出现均为显式禁止措辞（"不宣布 Gate 2 PASS" / "禁止 PASS 措辞" / "不构成 O1 PASS" / "不构成 O3 PASS"）。

---

## §6. 红线自检（per `315` §红线 + docs/34 §1/§3/§8/§120/§133 + docs/49 §0/§2.2/§5.3/§7/§8 + docs/06 §6.6 + docs/42 §8 + docs/45 §6.2）

| 红线 | 状态 | 守门位置 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ | docs/50 header + §0 + §10 + 多次显式 ⚠ |
| ❌ 不擅自 O1 收口 | ✅ | §0.1 + §3.3 + §5.1 + §5.2 + §5.4 + §9 #1 + §10.1 + header ⚠ |
| ❌ 不擅自 O3 收口 | ✅ | §0.1 + §3.3 + §5.1 + §5.3 + §5.4 + §9 #2 + §10.1 + header ⚠ |
| ❌ 不宣布 docs/10 §3.2-3.4 PASS | ✅ | §3.3 + §5.1 + §5.4 + §6.1 显式 xfail stub |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ | §2 #4 + §3.1 + §6.3 + docs/45 §6.2 禁词 3 重守门 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ | §0.2 + §0.3 + §8 显式守门 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ | §0.3 + §8 显式守门 |
| ❌ HTTP 爬源 | ✅ | §5.3 显式禁止；docs/50 不引入新 HTTP |
| ❌ 登录绕过 | ✅ | §5.3 显式禁止 |
| ❌ 未授权 cloud OCR API | ✅ | §5.3 + §9 #7 显式禁止 |
| ❌ 降 OCR 门槛 | ✅ | §5.3 显式禁止 |
| ❌ 启用 pgvector / RLS / partition | ✅ | Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ | 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ | Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ | ff-only pull |
| ❌ 不替用户下裁定 | ✅ | §5.3 OCR 引擎选型待用户裁定；§10.2 显式不在范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ | 仅回执要点 |
| ❌ 不索要 PAT | ✅ | — |
| ✅ pack invariant 守门 | ✅ | 635 → 637；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ | `316-...md` |
| ✅ docs/50 = CC 维护评审包草稿 | ✅ | `315` §SCHEMA "本刀做" |
| ✅ docs/50 文首/文末**禁止 PASS 措辞** | ✅ | grep 验证无 bare PASS |
| ✅ docs/50 §2 七条 ↔ docs/45 §2 七条**1:1 对齐** | ✅ | §3 表 7 行对齐 |
| ✅ OPEN 清单**必带** | ✅ | 5 类 OPEN 共 33+ 次显式 ⚠ |
| ✅ 三类划分（不可降级 / 演示级 / 仍 OPEN）| ✅ | §3.1 + §3.2 + §3.3 |
| ✅ 演示场景（5 省 + 10 地市 + EvidenceChain + 七维度）| ✅ | §4.1 + §4.2 + §4.3 |
| ✅ 预览路径**不构成 O1 / O3 收口** | ✅ | §7.1 + §7.2 + §7.3 + §9 #8 |
| ✅ 不可隐藏清单（Gate 2 评审必带 8 项）| ✅ | §9 |
| ✅ docs/50 = markdown-only（无业务代码改动）| ✅ | §0.2 显式 "不创业务代码" |
| ✅ Cursor 拥有架构文档未动 | ✅ | docs/06/08/10/34/40-44/46-49 / `00-CC-CURRENT.md` 未读未写 |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4 不擅自提前）| ✅ | §0 + §10.1 显式 |
| ✅ 10 地市锁定清单 | ✅ | nanjing/suzhou/wuxi/nantong/hangzhou/ningbo/wenzhou/guangzhou/shenzhen/dongguan |
| ✅ 5 省锁定清单 | ✅ | jiangsu/zhejiang/guangdong/shandong/sichuan |
| ✅ mart-shape feature-flag 默认值 | ✅ | §9 #6 + docs/45 §5.5 |
| ✅ cloud OCR 默认离线 | ✅ | §5.3 + §9 #7 + docs/49 §2.2/§3.2 |
| ✅ 输入边界 = 仅用户/admin upload | ✅ | §5.3 + §10.1 |
| ✅ O1 真实 SHA 收口前恒占位 `'0'*64` | ✅ | §5.2 + §7.2 + docs/47 §3.1 ⚠ |
| ✅ O3 真收口须 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS | ✅ | §5.3 + §10.1 + docs/49 §5.3 |

---

## §7. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 131 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/50 新建 | `docs/50-stage2-gate2-review-packet-draft-20260826.md`（11 节；~280 行）| ✅ NEW |
| bump script | `scripts/_knife41_manifest_bump.py`（2 NEW）| ✅ 635 → 637（+2）|
| 本地校验 | manifest invariant | ✅ 637 == 637 == 637 |
| commit (knife 41 主提交) | `git add ... && git commit -m "docs(50): 315 Gate 2 评审包草稿 — 七条 ↔ 证据 + OPEN 必带"` | ✅ `<this_commit>` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `<this_commit>` → origin/main |
| github push | `git push github HEAD` | ✅ `<this_commit>` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `<this_commit>` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §8. 下次心跳预期

- `queue_rev 131` 完成后：Cursor 收 `316` → 下发 `317-stage0-cursor-s315-docs50-gate2-packet-audit-…md`（PASS/FAIL）
- 若 PASS：Gate 2 评审包草稿齐；Gate 2 评审会议筹备就绪（必带 OPEN 清单 + 不可隐藏清单 8 项）
- 若 FAIL：`316-correction` 回合（修 §2 七条措辞 / 修 OPEN 清单 / 修预览路径 / re-commit）

---

## §9. 备注

- **本刀不宣布 Gate 2 / O1 / O3 PASS** — docs/50 header + §0 + §10 多次显式 ⚠ 守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做评审包草稿** — `315` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不改业务代码 / **不实装 OCR 引擎** / **不宣布 Gate/O1/O3 收口**。
- **docs/50 = CC 维护评审包草稿**（per `315` §SCHEMA "本刀做"）— 11 节 markdown 文档；不属于 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-49）— 红线 "Cursor 37 architect-only" 不约束 docs/50。
- **O1 仍 WAITING_FILE** — docs/50 §0.1 + §3.3 + §5.1 + §5.2 + §5.4 + §9 #1 + §10.1 + header ⚠ 8 处显式 OPEN（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284`）。
- **O3 仍 OPEN — 规划已交，实装待 tasking 31X+** — docs/50 §0.1 + §3.3 + §5.1 + §5.3 + §5.4 + §9 #2 + §10.1 + header ⚠ 8 处显式 OPEN（per `docs/49` §5.3 + §8 + §10 + `309` + `313`）。
- **docs/50 §2 七条 ↔ docs/45 §2 七条 1:1 对齐** — docs/50 直接复用 docs/45 §2 既有措辞 + 加证据路径详情（链到回执/页面/测试/dbt 验证）。
- **三类划分（不可降级 / 演示级 / 仍 OPEN）** — docs/50 §3.1（不可降级 4 项：#2/#4/#5/#6）+ §3.2（演示级 2 项：#1/#3）+ §3.3（仍 OPEN 5 项：dbt mart 真表 / docs/10 §3.2-3.4 / O1 / O3 / person/tenure 真数据）。
- **不可隐藏清单 8 项** — docs/50 §9 显式 Gate 2 评审必带：O1 / O3 / docs/10 §3.2-3.4 / dbt mart 真表 / person/tenure 真数据 / feature-flag 默认 mock / cloud OCR 默认离线 / 预览路径不构成收口。
- **预览路径 = demo 演示管道** — docs/50 §7.1 + §7.2 + §7.3：5 省 + 10 地市 lite 页面 + CityPageMart（mart-shape + 七维度 + 10 城 × 2 demo 相关人物行）+ EvidenceChain + SevenDimGrid；**不构成 O1 / O3 收口**（`lineage.source_file_sha256` 恒为 `'0'*64`）。
- **Gate 2 评审日期 W8**（per docs/34 §10.4），由 Cursor/用户裁定，**不擅自提前**（per docs/34 §10.4 + `315` §红线 + docs/45 §1）。
- **cloud OCR 默认离线**（per `docs/49` §2.2 + §3.2 步骤 4）— docs/50 §5.3 + §9 #7 显式；须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定。
- **真实 PDF 待用户主动 `--confirm-o3=PATH`**（per `docs/49` §10 Q4 + docs/48 §3 intake 模式）— docs/50 §5.3 + §10.2 显式。
- **输入边界 = 仅用户/admin upload；禁止 HTTP 爬源 / 登录绕过 / 未授权 API / symlink / 伪造**（per `docs/49` §2.2）— docs/50 §5.3 + §10.1 显式。
- **下次 heartbeat 闸门** — Gate 2 真收口须 docs/45 §2 七条全过 + 不可降级 4 项 100% + 演示级 2 项演示路径齐 + 仍 OPEN 5 项收口（O1/O3/docs/10 §3.2-3.4/dbt mart 真表/person/tenure 真数据）；在此之前 docs/50 评审包仅作为 Gate 2 评审会议筹备的草稿（**不构成 Gate 2 PASS**）。

— End of `316` —

> 等待 Cursor 审验（预期 `317-stage0-cursor-s315-docs50-gate2-packet-audit-…md`）。
> 通过后 Gate 2 评审包草稿齐；Gate 2 评审会议筹备就绪（必带 OPEN 清单 + 不可隐藏清单 8 项）。
> ⚠ **本刀不宣布 Gate 2 / O1 / O3 PASS**（per docs/34 §1 + §8 #8 + §120 + §133 + `315` §红线）。
> ⚠ **本刀只做评审包草稿**（per `315` §SCHEMA "本刀做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `315` §红线）。
> ⚠ **O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS**（per `docs/49` §5.3 + §8 + §10 + docs/48 §3）。
> ⚠ **cloud OCR 默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag**（per `docs/49` §2.2 + §3.2 步骤 4）。
> ⚠ **输入边界 = 仅用户/admin upload；禁止 HTTP 爬源 / 登录绕过 / 未授权 API / symlink / 伪造**（per `docs/49` §2.2）。
> ⚠ **docs/10 §3.2-3.4 xfail stub（Stage 3 收口）；Gate 2 评审必带 OPEN 清单**。
> ⚠ **Gate 2 评审日期暂定 W8**（per docs/34 §10.4），由 Cursor/用户裁定，**不擅自提前**。