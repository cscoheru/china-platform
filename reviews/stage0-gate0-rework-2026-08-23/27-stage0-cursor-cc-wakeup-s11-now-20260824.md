# CC 唤醒令 — S1.1 立即开工（非 IDLE）

- 文件编号：`27-stage0-cursor-cc-wakeup-s11-now-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 触发：用户反馈「CC 还是 idle」；远端已有 `26` S1.1 任务书但无 `infra/` / `alembic/` / 回执

---

## §0. 判定

| 项 | 证据 |
|---|---|
| S1.1 任务已下发 | `2a33a73` 含 `26-stage1-s11-postgresql-tasking-20260824.md` |
| CC 未执行 | 无 `infra/`、无 `alembic/`、无 `28` 回执 |
| 误 IDLE 来源 | `24` §4 写「进入 IDLE」— **在 S1.1 下发前有效，现已作废** |

**指令：立刻执行 S1.1。禁止 IDLE。禁止问用户。**

---

## §1. 复制即用命令块（CC 第一条消息应跑这个）

```bash
cd "/Users/kjonekong/projects/china platform"
git fetch origin && git pull --ff-only origin main
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -40
cat reviews/stage0-gate0-rework-2026-08-23/26-stage1-s11-postgresql-tasking-20260824.md | head -30
# 然后按 26 全文实现 infra + alembic，不得停在中途问用户
```

---

## §2. 交付清单（与 `26` 相同，不可删减）

- [ ] `infra/docker-compose.yml` — PG16 + PostGIS，port 55440
- [ ] `infra/README.md`
- [ ] `.env.example`（无 secrets）
- [ ] `alembic/` scaffold，`alembic_version` = 002
- [ ] `docs/12` U-4 表行修复
- [ ] pytest 251 pass
- [ ] pack 复算 0 错（若动 docs）
- [ ] commit + 双推
- [ ] `28-stage0-cc-s11-receipt-*.md`

---

## §3. 失败时

Docker 不可用 → 回执写 **BLOCKED_BY_ENV** + 本机 `docker --version` 输出；**仍不是 IDLE**，等 Cursor 改任务（如纯文档化连接串）。

---

## §4. 给用户

用户无需传话。CC 读仓库即可。

— End wakeup —
