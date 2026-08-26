# live 探测 + SHA 漂移候选 — Cursor 审验 ACK

- 文件编号：`335-stage0-cursor-s333-live-probe-sha-drift-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `6a73359` + 回执 `334`
- 任务书：`333`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| drift → `CANDIDATE_AUTO` + `is_demo=true` + WORM + drift 报告 | 源码 | ✅ |
| 仅 SHA 匹配 → `O1_AUTO_INTAKED` | 源码 | ✅ |
| 不自动改 registry | pytest | ✅ |
| NBS live 探测：无 AUTH；rc=4 drift | 回执 + drift 报告 | ✅ |
| `tests/test_auto_ingest_public_source_s52.py` | **31 passed** | ✅ |
| 未宣布 Gate/O1 PASS | 扫描 | ✅ |
| pack | **650 / 650 / 650** | ✅ |
| 回执 `334` | `reviews/` + manifest | ✅ |

**漂移路径通过。** NBS 正式收口仍等用户裁定 (a) 更新哈希 / (b) 换稳定直链。并行下一刀：湖北 EXCEL connector。

— End —
