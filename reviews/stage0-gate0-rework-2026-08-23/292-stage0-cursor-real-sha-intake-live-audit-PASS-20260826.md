# 真 SHA 投递上线 — Cursor 审验 ACK

- 文件编号：`292-stage0-cursor-real-sha-intake-live-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `8d673c2` / `0ba8477` + 回执 `291`
- 任务书：`290`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| `docs/48` 投递手册 | 源码 | ✅ |
| `scripts/intake_real_sha_if_present.py` allowlist + fixture/candidate + 无 `--url` | 源码 + 跑通 | ✅ |
| `tests/test_intake_real_sha_live_s2022.py` | **8 passed** | ✅ |
| 现场 `intake_real_sha_if_present.py` → **`WAITING_FILE`**（仅 fixture）| CLI | ✅ |
| **未**宣布 O1/Gate PASS；未伪造；未爬网 | 扫描 | ✅ |
| pack | **618 / 618 / 618** | ✅ |
| 回执 `291` | `reviews/` + manifest | ✅ |

**真 SHA 投递管道通过。** O1 仍 OPEN（`WAITING_FILE`）。下一刀：mart 接 demo 行，让城市页先吃到管道数据（仍标 `is_demo`）。

— End —
