# S2.0.2.2 实施 — Cursor 审验 ACK

- 文件编号：`164-stage0-cursor-s2022-impl-audit-PASS-20260825`
- 日期：2026-08-25
- 对象：CC `041c68d` + 回执 `163`
- 任务书：`162`；规划：`docs/35` §4.3 / §11.3

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| wrapper allowlist → `compute_file_sha` → lineage | 源码审阅 | ✅ |
| `is_demo`≠`"true"` + 非全零 SHA | happy-path + contract | ✅ |
| 拒 `--url` / 越权 rc=2 / 缺文件 rc=1 | pytest | ✅ |
| `test_replace_demo_with_real_s2022` | **7 passed** | ✅ |
| 回归 compute_file_sha + demo_sha + admin_upload | **22 passed**（合计 **29/29**） | ✅ |
| pack | **511 / 511 / 511** | ✅ |
| 回执 `163` | `reviews/` | ✅ |

**S2.0.2.2 通过。** 下一刀：**S2.0.2.3**（见 `165`；URL probe `URL_HEALTH_LIVE=1`）。

## §1. 备注

- 交付为 **control-flow witness**（不写 DB）；符合任务书 `162`「模拟或真实」。完整 admin upload → seed `--load` → SQL `is_demo` 仍属生产路径文档步骤，**不**阻塞本刀 PASS。
- **不**宣布 Gate 1/2 PASS。

— End —
