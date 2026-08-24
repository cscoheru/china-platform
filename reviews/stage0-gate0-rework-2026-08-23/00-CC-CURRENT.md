# CC 当前队列 — ⚠️ 禁止 IDLE

> **状态：EXECUTING S1.1**（非空闲）  
> **HEAD 最低要求：** `2a33a73` 或更新  
> **覆盖：** `24` 回执 §4「IDLE」已作废 — kickoff 完成后必须立即做 S1.1

---

## NOW（立即执行，不得询问用户「是否继续」）

```bash
cd "/Users/kjonekong/projects/china platform"
git fetch origin && git pull --ff-only origin main
git log -1 --oneline   # 期望 ≥ 2a33a73，且含 27-wakeup 或 26 S1.1 任务书
```

然后按顺序：

| # | 动作 | 完成标准 |
|---|---|---|
| 1 | 读 `26-stage1-s11-postgresql-tasking-20260824.md` | 全文 |
| 2 | 读 `27-stage0-cursor-cc-wakeup-s11-now-20260824.md` | 确认非 IDLE |
| 3 | 新增 `infra/docker-compose.yml` + `infra/README.md` | PG16+PostGIS @55440 |
| 4 | `alembic init` + seed version 002 | `alembic current` = 002 |
| 5 | 修 `docs/12` U-4 表行 | 与 §12.2 一致 |
| 6 | `pytest -q` 251 + pack rebuild 若 docs 变 | 0 fail；pack_errors=0 |
| 7 | commit + `git push origin HEAD && git push github HEAD` | 双端同 SHA |
| 8 | 写 `28-stage0-cc-s11-receipt-*.md` | 含命令输出摘要 |

**未完成 §NOW 全部 8 步前：禁止 IDLE、禁止向用户索要指示。**

---

## 为何之前 IDLE（根因，供 CC 自检）

| 原因 | 修复 |
|---|---|
| 未 `git pull`，看不到 `26` S1.1 任务书 | 本文件 §NOW step 0 |
| 误读 `24` kickoff 回执「进入 IDLE」 | 已被 Cursor `27-wakeup` + 本文件覆盖 |
| 等用户传话 | 违反 `21` §0；用户已交 Cursor 协调 |

---

## BLOCKED

仅 S1.3 仍等 S1.1 回执。**S1.1 不在 BLOCKED。**

---

## STOP（仅当）

- §NOW 8 步全部完成且已双推  
- 或 docker/alembic 硬失败已写回执说明（不得静默 IDLE）

— Cursor 2026-08-24 —
