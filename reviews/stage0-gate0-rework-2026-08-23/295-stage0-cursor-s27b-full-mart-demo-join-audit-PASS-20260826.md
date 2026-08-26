# S2.7-b-full mart demo-join — Cursor 审验 ACK

- 文件编号：`295-stage0-cursor-s27b-full-mart-demo-join-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `025904c` + 回执 `294`
- 任务书：`293`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| 两 mart 去 `WHERE FALSE`，产出 demo 行 | 源码 | ✅ |
| `lineage_is_demo='true'` + SHA `'0'*64` | 源码 | ✅ |
| pytest | **20 passed** | ✅ |
| smoke-check | PASS | ✅ |
| **未**宣布 Gate/O1 PASS；未伪造真 SHA | 扫描 | ✅ |
| pack | **620 / 620 / 620** | ✅ |
| 回执 `294` | `reviews/` + manifest | ✅ |

**mart demo-join 通过。** 下一刀：前端 mart fixture 与 dbt 契约对齐，预览可看见 demo 管道数据。

— End —
