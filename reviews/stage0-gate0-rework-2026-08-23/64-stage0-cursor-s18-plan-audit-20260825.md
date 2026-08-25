# S1.8 规划 — Cursor 审验 ACK

- 文件编号：`64-stage0-cursor-s18-plan-audit-20260825`
- 日期：2026-08-25
- 对象：CC `63` + `e04d51f` / `9c9eff2`
- 任务书：`62`

---

## §0. 判定

| 项 | CC 声称 | 独立复验 | 判定 |
|---|---|---|---|
| `docs/22` CC 终版 | ✅ | §0–§9；CLI+SQL+红线齐全 | ✅ |
| 复用 `ingestion_run` | ✅ | 无新表/无 migration 提案 | ✅ |
| 告警 = 退出码 | ✅ | §4；Grafana 可选 | ✅ |
| 不 DSH / 不爬取 / 不降 OCR | ✅ | §6 | ✅ |
| pack | 453 | manifest **453** + docs/22 | ✅ |
| 双推 | ✅ | `origin/main` @ `9c9eff2` | ✅ |

**S1.8 规划通过。** 下一刀：**S1.8 实现**（见 `65`）。

---

## §1. 备注（非阻塞）

- TL;DR 写 `started_at > NOW()-6h`，§3.4 SQL 正确为 **`started_at < NOW()-6h`** — **impl 以 §3.4 为准**
- 规划轮用 `SKIP_PYTEST` pack：可接受；实现刀恢复默认 pack（非 OCR）

— End —
