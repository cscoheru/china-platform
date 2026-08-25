# 155 — Stage 2 / CC / S2.0.2 Planning Receipt

**Tasking**: Cursor 154 §NOW（draft `docs/35`；回执 `155` 进 `reviews/`）
**Date (UTC)**: 2026-08-25
**Branch**: main
**Plan**: `docs/35-stage2-s202-real-sha-probe-plan-20260825.md` (11 sections, 12.7 KB)

---

## §NOW items completed (tasking 154)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 154-1 | 起草 `docs/35-stage2-s202-real-sha-probe-plan-20260825.md` | ✅ | docs/35（CC 拥有） |
| 154-2 | 覆盖本地/用户上传样本路径（复用 S1.13 admin；不爬网） | ✅ | §4（4.1 三来源 / 4.2 compute_file_sha / 4.3 replace flow） |
| 154-3 | `compute_file_sha` / `replace_demo_with_real` 最小设计；无文件时诚实失败 | ✅ | §4.2（exit 0/1/2 三码 + 拒绝 `--url`） |
| 154-4 | 前端：真实 SHA 时 DemoBadge 隐藏 / live API 串联验收 | ✅ | §4.4 + §4.5（7 项验收） |
| 154-5 | URL probe「真实化」范围（vs docs/32 红线） | ✅ | §5（5.1 三模式 + 5.2 docs/32 §2.1 上限逐条核对） |
| 154-6 | 与 S2.0.1 / S1.18 边界 | ✅ | §6（7 项边界表） |
| 154-7 | 不宣布 Gate PASS | ✅ | §7 红线 + §8 红线 + §1 状态声明 |
| 154-8 | commit → origin → 回执 `155` | ✅ | 见 §1 |
| 154-9 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — docs/35 章节结构

| § | 标题 | 来源/依据 |
|---|------|-----------|
| 1 | S2.0.2 目标 | `154` §NOW + `docs/34` §4.1 序 2 |
| 2 | Gate 2 收口所需 | docs/08 §3.2 |
| 3 | 继承的 Stage 1 OPEN 清单 | 142 §书面接受 |
| 4 | 真实 SHA 样本路径（不爬网） | `154` §NOW.2 + docs/28 (S1.13) |
| 5 | URL probe 真实化范围 | `154` §NOW.2 + docs/32 §2.1/§5 |
| 6 | 与 S2.0.1 / S1.18 边界 | docs/34 §5 + S1.18 sentinel |
| 7 | 关键风险与回滚点 | CC 自评 |
| 8 | 不做什么（14 项红线） | docs/08 §3.3 + PRD + 142 + docs/32 §6 |
| 9 | 验收策略 | docs/08 §3.2 |
| 10 | 与现有文档的关系 | docs/28/32/33/24/04 |
| 11 | CC 建议（供 Cursor 审阅 / 用户裁定） | 154 §NOW |

**红线审计**：
- ✅ 不宣布 Gate 1 PASS（§8 红线 5）
- ✅ 不宣布 Gate 2 PASS（§8 红线 6）
- ✅ 不爬源站 / 不 HTTP 抓业务数据（§4.1 路径 (c) 标 🚫 + §8 红线 1）
- ✅ 不绕验证码 / 付费墙（§8 红线 2；引用 docs/32 §2.1）
- ✅ 不接生产 cron（§5.1 模式 3 标 🚫 + §8 红线 3）
- ✅ 不批量 2020-2025（§8 红线 4）
- ✅ 不改 `gate_thresholds.json`（§8 红线 7）
- ✅ Cursor 不写 docs/35 正文（§8 红线 14）

---

## §2 — CC 关键论证（被采纳进 §4）

1. **三来源路径钉死上限**：
   - (a) S1.13 admin upload（**默认**）— 走既有契约
   - (b) 本地归档 `data/seed_archives/...` — 仅 dev fixture
   - (c) HTTP 抓取 **🚫 禁止** — 写进红线表

2. **`compute_file_sha.py` ALLOWED_PREFIXES 双白名单**：
   - `/tmp/cegr_uploads/`（S1.13 默认落盘目录 per `backend/src/china_platform/api/config.py`）
   - `data/seed_archives/`（dev fixture）
   - 不在白名单 → exit 2（**显式失败**，不静默成功）

3. **`--url` 选项**根本**不实现**——即便用户尝试传 URL 也忽略；防误用门槛。

4. **前端零修改**：DemoBadge 自动隐藏契约由 `lineage.is_demo === "true"` 单字段驱动；S2.0.2 仅验证契约成立，不写新前端代码。

5. **URL probe 三模式钉死**：
   - mock / fixture（默认；既有测试）
   - 本地真实 HEAD（dev 机；遵守 docs/32 §2.1 全部 8 项上限）
   - 生产 cron 🚫（属 Stage 2 运维刀移交）

---

## §3 — 关键边界声明（§6 摘要）

| 边界 | S2.0.2 行为 |
|------|------------|
| S2.0.1 骨架（frontend/） | **不动**；DemoBadge 自动隐藏契约由 lineage.is_demo 驱动 |
| S1.18 `is_demo` sentinel | **复用**；真实 SHA 喂回 loader 即覆盖 sentinel |
| S1.13 admin upload | **复用为唯一上传路径**；不绕 admin |
| S1.10 FastAPI | **复用读 API**；不写新写 API |
| S1.17 URL probe | **复用为库**；S2.0.2 仅切换 mode（mock ↔ live） |
| `evidence_pack` | +1 documentation（docs/35）+1 schema_negative_test（test_compute_file_sha.py）= 506 → 508 |
| `00-CC-CURRENT.md` | 不碰（Cursor 拥有） |

---

## §4 — 预计 pack delta

| 角色 | 当前 | +1 docs/35 | +1 test | 后 |
|---|---|---|---|---|
| documentation | 37 | +1 | — | 38 |
| schema_negative_test | 19 | — | +1 | 20 |
| **artifact_count** | 506 | +1 | +1 | **508** |
| **invariant** | ✅ | | | ✅ |

实现刀落地后由 `scripts/update_manifest_s202.py` 一次性写入。

---

## §5 — §154 §NOW.2 5 项覆盖核对

| 154 §NOW.2 子项 | docs/35 对应章节 | 状态 |
|---|---|---|
| 本地/用户上传样本路径（复用 S1.13 admin；不爬网） | §4.1 三来源表 | ✅ |
| `compute_file_sha` / `replace_demo_with_real` 最小设计；无文件时诚实失败 | §4.2 + §4.3 + exit 0/1/2 + 拒绝 `--url` | ✅ |
| 前端：真实 SHA 时 DemoBadge 隐藏 / live API 串联验收 | §4.4 + §4.5 验收清单 7 项 | ✅ |
| URL probe「真实化」范围（可选 HEAD vs 仍 mock；钉死 vs docs/32 红线） | §5.1 三模式 + §5.2 docs/32 §2.1 逐条 8 项 | ✅ |
| 与 S2.0.1 / S1.18 边界；不宣布 Gate PASS | §6 + §8 红线 14 项 | ✅ |

---

## §6 — 不动业务逻辑 / 不重开功能刀（per 154 红线）

- ❌ 未修改 frontend/ 任何文件（S2.0.1 已交）
- ❌ 未修改 `scripts/seed_jiangsu_gdp_demo.py`（S1.18 已交）
- ❌ 未修改 `dbt/models/staging/stg_source_disagreement_candidate.sql`（S1.18 已交）
- ❌ 未修改 `backend/src/china_platform/api/...`（S1.10/S1.13 已交）
- ❌ 未修改 `evidence_pack/manifest.json`（在 S2.0.2 实现刀落地后再 update）
- ❌ 未宣布 Stage 0 / Stage 1 / Gate 1 / Gate 2 PASS
- ❌ 未修改 `gate_thresholds.json`
- ❌ 未修改 `00-CC-CURRENT.md`
- ✅ 仅新增 `docs/35-stage2-s202-real-sha-probe-plan-20260825.md`（规划 only）

---

## §7 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。等待 Cursor 对 S2.0.2 规划的审验（预期 queue_rev 56+ → audit `156-stage0-cursor-s202-plan-audit-...md`）。

— CC @ queue_rev 55, S2.0.2 规划已交付 —