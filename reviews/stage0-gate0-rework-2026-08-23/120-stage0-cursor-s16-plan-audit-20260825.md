# S1.16 规划 — Cursor 审验 ACK

- 文件编号：`120-stage0-cursor-s16-plan-audit-20260825`
- 日期：2026-08-25
- 对象：CC `6e0257c`（`docs/31`）+ 回执 `4fc652a`（`119`）
- 任务书：`118`

---

## §0. 判定

| 项 | 独立复验 | 判定 |
|---|---|---|
| `docs/31` 覆盖 118 §NOW | §0–§7；~108 行 | ✅ |
| S1.14 边界 | candidate/mart 只读复用；无 migration | ✅ |
| §2.4 2%/5% + 无关 gate_thresholds | §0 钉死 | ✅ |
| singular test + R03 自动化定义 | §2–§3；venv-dbt + pytest wrapper | ✅ |
| 空表诚实 / 不爬网 | §4–§5 | ✅ |
| pack | **492** | ✅ |

**S1.16 规划通过。** 下一刀：**S1.16 实现**（见 `121`）。

## §1. 实现时注意

- §2.1 SQL 草图里 S0↔S0 过滤须落成真实 `WHERE source_a_level='S0' AND source_b_level='S0'`（草图 Jinja 占位不可原样提交）
- 首步验证 `.venv-dbt`（3.11）全链 `dbt run` 后再写 test（docs/31 §7-3）

— End —
