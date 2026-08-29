# 48 — Stage 2 / 真 SHA 投递上线 / O1 intake 操作手册

> 起草：CC · 2026-08-26 · queue_rev 122
> 前置：`289` dbt mart skel PASS；`docs/35` §4；`scripts/compute_file_sha.py` + `scripts/replace_demo_with_real.py` 已交
> 用户裁定：Stage 2 **C**；缩刀 **D**；自主推进；**尽快真实数据**；**O1 无材料 OPEN，不伪造，不爬网**
> 任务书：`290-stage2-real-sha-intake-live-tasking-20260826`

---

## §1. 目标

把「合法持有江苏文件 → 真 SHA → 清 `is_demo` → seed」打成**单步可执行**流程。本刀仅交付脚本+手册+pytest 三件套；**真数据物理依赖用户把文件投递到 allowlist**。

---

## §2. allowlist（路径白名单）

| 路径 | 用途 | 来源 |
|---|---|---|
| `/tmp/cegr_uploads/` | 管理员 upload 落盘目录 | 复用 `scripts/compute_file_sha.py` `ALLOWED_PREFIXES` |
| `/private/tmp/cegr_uploads/` | macOS `/tmp` → `/private/tmp` symlink 解析 | 同上 |
| `data/seed_archives/` | 开发 fixture（**仅控制流**，**非 O1 样本**）| 同上 |

**裁决**：脚本只扫描这 3 个前缀。任何 `Path.resolve()` 后不在白名单的文件，脚本拒绝并报 rc=2（与 `compute_file_sha` 一致）。

---

## §3. 单步命令

```bash
# 1. 用户投递文件到白名单（人工或 admin upload 端点）
cp /path/to/jiangsu_2022_gdp.csv /tmp/cegr_uploads/

# 2. 单步 intake
python3 scripts/intake_real_sha_if_present.py

# 退出码：
#   0 = WAITING_FILE（白名单内无合法 O1 样本；仍是诚实路径）
#   2 = 发现候选文件 + SHA 成功 + lineage 已写（候选待用户裁定「此即 O1」）
#   3 = contract 违反（如有候选但 SHA=全 0 / is_demo 未清除）
#   4 = 内部错误（subprocess / JSON 解析失败）
```

> ⚠ **rc=0 表示"无文件可吃"，并非"成功收口 O1"。** 这是诚实路径（per `290` §红线）。

---

## §4.「发现候选」判定契约

### 4.1 控制流 fixture（**不算 O1 候选**）

文件满足以下任一条件 → 视为控制流 fixture，**不算 O1 候选**：

| 判定 | 触发条件 |
|---|---|
| 文件名含 `fixture` 或 `test_fixture` | case-insensitive 子串匹配 |
| 文件名前缀 `test_` 或 `_test.` | 启动或结束含 test |
| 文件内容首 32 字节含 `NOT a forged` 或 `placeholder bytes` | 字面 substring |
| 文件 < 1 KiB 且 mtime 在最近 7 天 | 控制流窗口 |

### 4.2 真 O1 候选（**待用户裁定**）

文件满足以下**全部**条件 → 视为候选，但仍**不擅自**宣布 O1 收口：

| 判定 | 触发条件 |
|---|---|
| 不在 §4.1 任一 fixture 判定中 | — |
| ≥ 1 KiB | — |
| 文件内容不含 `NOT a forged` / `placeholder bytes` | 真数据自证 |
| mtime 在最近 90 天内 | 防止过期 |

> ⚠ **即使发现候选**，回执必须明示「**用户需明示该文件即 O1 后方可收口**」。

### 4.3 candidate → O1 收口闸门

| 状态 | 是否触发 |
|---|---|
| 无文件 | rc=0, WAITING_FILE |
| 只有 fixture（§4.1）| rc=0, WAITING_FILE（fixture 跑通 contract，但不收口）|
| 有候选但未获用户明示 | rc=2, CANDIDATE_FOUND（用户裁定闸门 OPEN）|
| 用户已明示某候选 = O1 | rc=0, O1_INTAKED（仅在用户用 CLI flag `--confirm-o1=PATH` 时）|

---

## §5. contract 守门

每条候选都必须满足：

| 字段 | 要求 |
|---|---|
| `lineage.is_demo` | 必须 ≠ `"true"`（per `S1.18` sentinel 契约）|
| `lineage.source_file_sha256` | 必须 64-char lowercase hex；≠ 全 0 |
| `lineage.source_file_path` | 必须 `Path.resolve()` 后在 §2 白名单 |
| `lineage.source_agency` | 默认 `"江苏省统计局"`（CLI 可覆盖）|
| `lineage.intake_ts` | ISO 8601 + tz（脚本生成）|
| `lineage.intake_status` | `"WAITING_FILE"` / `"CANDIDATE_FOUND"` / `"O1_INTAKED"` |

不满足任一条 → rc=3（contract violation）。

---

## §6. 与前置脚本的关系

| 脚本 | 复用方式 |
|---|---|
| `scripts/compute_file_sha.py` | 通过 subprocess 调用 `python3 scripts/compute_file_sha.py <path>`（**不并行实现** SHA）|
| `scripts/replace_demo_with_real.py` | `build_lineage()` 复用其 JSON 形状；新增 `intake_status` / `intake_ts` 字段 |
| `scripts/seed_jiangsu_gdp_demo.py` | **不直接调用**；本刀只做契约见证（control-flow witness）；真 seed re-load 由 admin upload pipeline 触发 |

---

## §7. pytest 守门（per `290` §红线）

| 场景 | 期望 |
|---|---|
| 白名单空 | rc=0, status=WAITING_FILE |
| 白名单只有 fixture | rc=0, status=WAITING_FILE；SHA 非 0；is_demo=false |
| 白名单有 fixture + 候选（无 user confirm） | rc=2, status=CANDIDATE_FOUND；显式「用户裁定 OPEN」|
| 白名单有候选 + `--confirm-o1=PATH` | rc=0, status=O1_INTAKED |
| 候选违反 contract（SHA 全 0 / is_demo=true）| rc=3, contract violation |
| 路径不在白名单 | rc=2（与 `compute_file_sha` 对齐）|

**禁止**：
- ❌ pytest 把控制流 fixture 冒充江苏政府样本
- ❌ pytest 自动 `--confirm-o1`（必须显式 flag）
- ❌ pytest 不验真数据就写 rc=0 O1_INTAKED

---

## §8. 红线（per `290` §红线 + docs/34 §1/§8 + docs/35 §4）

- ❌ 不宣布 Gate 1 / Gate 2 PASS
- ❌ 不伪造 SHA / 不伪造样本内容
- ❌ 不爬网（HTTP / URL 选项不在 CLI 注册；argparse 自动拒绝）
- ❌ 无文件必须诚实 `WAITING_FILE`
- ❌ 不擅自把 fixture 收口为真 O1
- ❌ 不擅自宣布 O1 CLOSED（除非用户用 `--confirm-o1=PATH` 显式确认）
- ❌ 不改 `gate_thresholds.json`
- ❌ 不动 Cursor 拥有文档（docs/35 / 40-47 由 Cursor 拥有；docs/48 是 CC 起草的操作手册）

---

## §9. 下次 heartbeat 预期

- Knife 33 → 回执 `291`（脚本 + pytest + 手册 + WAITING_FILE）
- 若 PASS：intake 脚本入 CI 路径；前端 `mart_city_evidence_chain` 仍消费 `is_demo=true` mock
- 等待用户投递真文件到 `/tmp/cegr_uploads/` 或 `data/seed_archives/`
- 若 FAIL：`291-correction` 回合

— End of `docs/48` —

## §10. Stale user-action 表述收口（per 599 · 2026-08-29）

> [superseded per 599（2026-08-29）· per 2026-08-29 治理铁律：数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 公开源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；user-action 表述保留为治理教训（不删除、不调用）；docs/48 内 stale `--confirm-o1=PATH`（line 81 `rc=0, O1_INTAKED` + line 119 `rc=0, status=O1_INTAKED` + line 125 `❌ pytest 自动 --confirm-o1` + line 137 `❌ 不擅自宣布 O1 CLOSED`）+ line 39/61/80/118 `用户裁定` 闸门 OPEN 表述均 supersede；本节 user-action 表述为 intake 出口码技术状态语义（per docs/52 §0 状态语义对齐），并非「等用户投喂才可继续」；O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露；B 路（公开源自动获取 per docs/52）保持主路径；A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）；执行端自取路径无法取得样本时方由架构师夜间授权下自主评估是否启动 user-action；O3 整体 CLOSED 候选 per 588 PASS + 590 PASS + 597 三重声明；supersede 链 = `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 user-action `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 端到端 e2e 收口）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` docs/50 row 119 supersede + `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` PASS audit + `591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829.md` docs/50 row 117 A 路 supersede + `592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md` PASS audit + `593-stage0-architect-s592-o3-impl-docs-sync-full-sweep-tasking-20260829.md` docs/45/49 五处 supersede + `593-stage0-cc-o3-impl-docs-sync-full-sweep-tasking-20260829-receipt.md` + `594-stage0-architect-s593-docs-sync-full-sweep-audit-PASS-20260829.md` PASS audit + `594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md` + `595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md` 584 BLOCKER 解除刀 + `595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md` + `596-stage0-architect-s595-584-reack-ready-tasking-20260829.md` 584 re-ACK 准备就绪刀 + `596-stage0-cc-584-reack-ready-tasking-20260829-receipt.md` + `597-stage0-architect-s596-584-reack-impl-tasking-20260829.md` 584 §5.2.4 paddle-ocr 引擎依赖实施刀 + `597-stage0-cc-584-reack-impl-tasking-20260829-receipt.md` + `598-stage0-architect-s597-584-impl-audit-PASS-20260829.md` PASS audit；本 docs/48 原文（line 39 / 61 / 80 / 81 / 118 / 119 / 125 / 137）不删不改（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式），supersede 标注与原文共存（per 589 + 591 + 593 + 595 + 596 + 597 平行模式）]

> ⚠ **B 路（公开源自动获取）保持主路径**（per 599 · 2026-08-29；执行端自取 = B 路主路径；A 路用户投递 = fallback 标注）。
>
> ⚠ **执行端自取预 vetted 公开源走完整 e2e 流水线**（per 599 · 2026-08-29）。