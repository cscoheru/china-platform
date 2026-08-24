# Stage 1 启动任务书（Gate 0 关闭后）

- 文件编号：`23-stage1-kickoff-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 授权依据：用户 U-4=A + 本会话「可以开始 Stage 1 了么」→ **是**

---

## §0. TL;DR

| 项 | 判定 |
|---|---|
| Gate 0 | ✅ **CLOSED** |
| Stage 1 | ✅ **已授权启动**（数据底座，4–6 周，见 `docs/08` §2） |
| Stage 1 范围 | S1.1–S1.12；**试点**，非全国市县全量 |
| 红线 | 不全国抓取；不官员评分；不 DSH；不降 OCR 门槛；1909 不代表中国 |

---

## §1. Gate 0 关闭口径（写入文档用）

**Verdict（供 `docs/12` §1 更新）：**

> Stage 0 Gate 0 **CLOSED**（2026-08-24）。  
> 依据：12/13 缺陷闭环（B-01 按 U-3 移出 spike 04 门控）；251 tests；pack 440/0；陕西 research-track 集成；用户 U-4=A；用户授权启动 Stage 1。  
> **不等于** OCR 产品全 PASS 或统计表代表性样本齐备；Stage 1 继续诚实记录 BLOCKED 质量项（如 spike 00 needs_review 56%、1909 eval FAILED）。

---

## §2. CC 立即任务（Kickoff）

### S1-K0 — Gate 0 正式收口（文档）

修改并 commit：

| 文件 | 变更 |
|---|---|
| `docs/12-stage0-closure-and-report.md` | §1 Verdict → **CLOSED**；§12.2 U-4 → 已裁定 A |
| `docs/08-mvp-plan.md` | 文末 checklist：`Stage 1：已启动（2026-08-24）` |
| `docs/13-r4-final-verification.md` | 文首 Gate 状态一句同步 CLOSED |

**不**改 PRD 本体。改完若动 pack 内 docs → rebuild pack → `pack_errors=0`。

Commit 示例：

```
docs(stage0): close Gate 0; authorize Stage 1 kickoff

Per user U-4=A and explicit Stage 1 start request. Gate 0 CLOSED;
spike 04 non-gating per U-3. P-1/P-2 unchanged.
```

### S1-K1 — Stage 1 规划（不动生产库）

1. 读 `docs/08-mvp-plan.md` §2.1–§2.4、`docs/10-acceptance-tests.md` Gate 1 相关项
2. 新建 **`docs/17-stage1-kickoff-plan-20260824.md`**（CC 起草，Cursor 审验）含：
   - W1 范围：S1.1–S1.3 分解
   - 与现有 `schema/01-core.sql` + `002` 的关系（Alembic vs 现有 migration 策略）
   - 首批 5 来源登记清单（4 spike 已验证 + 1 待定）
   - 已知 Stage 0 遗留质量债：spike 00 BLOCKED、1909 FAILED、陕西 research-only
   - Gate 1 退出标准对照表（`docs/08` §2.3）
3. **禁止**本任务内：Docker 部署生产 PG、批量爬取、改 `gate_thresholds.json`

Commit + 双推；回执 `24-stage0-cc-stage1-kickoff-receipt-*.md`。

---

## §3. Stage 1 后续（Cursor 审验 S1-K1 后下发）

按 `docs/08` 顺序，预计：

| 周 | 任务 |
|---|---|
| W1 | S1.1 PostgreSQL 16 + PostGIS；S1.2 migration 工具链；S1.3 source_registry 生产化 |
| W2+ | S1.4–S1.7 连接器（试点源） |

Cursor 将在审验 `docs/17` 后更新 `00-CC-CURRENT` §NOW = S1.1。

---

## §4. Git（常驻 `10` / `21`）

每个逻辑 commit：`git push origin HEAD && git push github HEAD`

---

## §5. 红线

- ❌ 不宣布 Gate 1 PASS（仅启动 Stage 1 工作）
- ❌ 不把陕西/1909 标为统计表代表性 PASS
- ❌ 不 skip-as-PASS / 不降门槛

— End Stage 1 kickoff —
