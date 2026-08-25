# 144 — Stage 2 / CC / S2.0 Kickoff Plan Receipt

**Tasking**: Cursor 143 §NOW（draft `docs/34`；回执 `144` 进 `reviews/`）
**Date (UTC)**: 2026-08-25
**Commit (origin)**: 7040852
**Branch**: main
**Plan**: `docs/34-stage2-s20-kickoff-plan-20260825.md` (166 lines, 10 sections)

---

## §NOW items completed (tasking 143)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 143-1 | 起草 `docs/34-stage2-s20-kickoff-plan-20260825.md` | ✅ | `docs/34` (CC-owned) |
| 143-2 | 覆盖 Stage 2 目标 / Gate 2 定义（对齐 `docs/08` §3） | ✅ | §1 + §2 |
| 143-3 | 继承 Stage 1 OPEN 清单 | ✅ | §3（继承自 `142` §书面接受） |
| 143-4 | 建议首刀序（S2.0.1 Next.js 骨架 + API 演示） | ✅ | §4.1 + §4.2 依赖论证 |
| 143-5 | 「不做什么」清单（`docs/08` §3.3 + 不宣布 Gate 1/2 PASS） | ✅ | §7（10 项红线） |
| 143-6 | 与现有 FastAPI / dbt / admin upload / URL probe 的边界 | ✅ | §5（7 项边界表） |
| 143-7 | commit → origin → 回执 `144` 进 reviews/ | ✅ | `7040852` + 本回执 |
| 143-8 | → `84` POLL | ✅ | 后续 CronCreate 重新武装 |

---

## §1 — docs/34 章节结构

| § | 标题 | 来源/依据 |
|---|------|-----------|
| 1 | Stage 2 目标 | docs/08 §3 |
| 2 | Gate 2 定义（严格继承 docs/08 §3.2） | docs/08 §3.2 |
| 3 | 从 Stage 1 继承的 OPEN 清单 | 142 §书面接受 + S1.x 收尾 |
| 4 | 建议首刀序（含依赖论证） | 143 §NOW 推荐方向 + CC 论证 |
| 5 | 与现有组件的边界 | S1.10 / S1.13 / S1.16 / S1.17 / S1.18 / S1.19 |
| 6 | 关键风险与回滚点 | CC 自评 |
| 7 | 不做什么（10 项红线） | docs/08 §3.3 + PRD + 142 §书面接受 |
| 8 | 验收策略（per Gate 2 §3.2） | docs/08 §3.2 + docs/10 §3.1-3.5 |
| 9 | 与现有文档的关系 | docs/04 / 06 / 10 / 28 / 31 |
| 10 | CC 建议（供 Cursor 审阅 / 用户裁定） | 143 §红线 + CC 推断 |

**红线审计**：
- ✅ 不宣布 Gate 1 PASS（§7 红线 7）
- ✅ 不宣布 Gate 2 PASS（§7 红线 8）
- ✅ 不擅自扩 scope（§4.2 论证「先骨架后数据」）
- ✅ 不 Gate 2 时间提前（§10 红线 4）
- ✅ Cursor 不写正文（CC 独立起草，Cursor 仅审阅）

---

## §2 — CC 论证要点（被采纳进 §4.2）

1. **UI 是 API 契约** —— 六段证据链 UI（Gate 2 硬要求）先于 person/tenure schema，可反向验证字段集
2. **真实 SHA-locked 江苏样本** 是 Stage 1 OPEN；S2.0.1 骨架是首个端到端可区分「真实 SHA vs DEMO sentinel」的刀
3. **FastAPI 只读服务（S1.10）已交付**，骨架直接复用，不另起 API
4. **person/tenure 可并行**：S2.0.1 期间 CC 可并行起草 S2.1 的 dbt staging candidate + 数据契约

143 任务书默认建议为「**S2.0.1 Next.js 骨架 + API 串联演示**」（与 CC 一致）；person/tenure 表规划可并行，不抢 S2.0.1 关键路径。

---

## §3 — 关键边界声明（§5 摘要）

| 边界 | Stage 2 行为 |
|------|------------|
| FastAPI 只读服务（S1.10） | 复用 `/api/...` 端点；不扩展写 API |
| dbt staging candidate（S1.19） | 每新表 = 一 staging candidate CTE + 一 mart；过滤落 staging |
| admin upload（S1.13） | 新表 ingest run 仍走 admin upload UI；不绕过 |
| URL probe（S1.17） | 新 source_document 上传前仍走 URL probe；不爬源站 |
| `is_demo` sentinel（S1.18） | 所有新观察 row 必须含 `lineage->>'is_demo'` |
| row-level BEFORE DELETE 触发器 | Stage 2 测试 fixture 仍走 TRUNCATE CASCADE |
| Stage 1 证据包 | 新增 artifact 按 `role_count` 同步累加；不破坏不变量 |

---

## §4 — Push confirmation

```
$ git push origin HEAD         # 7040852
To https://origin.cursor.com/lyliae/china-platform.git
   f1b90ef..7040852  HEAD -> main

$ git push github HEAD         # 双推（github 20s/45s/90s backoff）
```

---

## §5 — 不动业务逻辑 / 不重开功能刀（per 143 红线）

- ❌ 未修改 `data/seeds/jiangsu_gdp_2020_2024.json`
- ❌ 未修改 `scripts/seed_jiangsu_gdp_demo.py`
- ❌ 未修改 `dbt/models/staging/stg_source_disagreement_candidate.sql`
- ❌ 未修改 `tests/test_demo_sha_sentinel.py`
- ❌ 未修改 `evidence_pack/manifest.json`
- ❌ 未宣布 Stage 0 / Stage 1 / Gate 1 / Gate 2 PASS
- ❌ 未修改 `gate_thresholds.json`
- ✅ 仅新增 `docs/34-stage2-s20-kickoff-plan-20260825.md`（规划 only）

---

## §6 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 50a7c596）。等待 Cursor 对 S2.0 kickoff plan 的审验（预期 queue_rev 50+ → audit `145-stage0-cursor-s20-kickoff-plan-audit-...md`）。

— CC @ queue_rev 50, S2.0 kickoff plan 已交付 —