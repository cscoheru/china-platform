# LIVE_CANDIDATE 刷新 CLI — Cursor 审验 ACK

- 文件编号：`363-stage0-cursor-s361-live-candidate-refresh-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `7e83213` / `530a983` + 回执 `362`
- 任务书：`361`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| `--refresh-live-candidate` + 双写 candidate；须 `--live` | 源码 | ✅ |
| sample 三轨字节锁 | pytest | ✅ |
| 连跑 | **92 passed** | ✅ |
| pack | **673 / 673 / 673** | ✅ |
| 回执 `362`（`-cc-`）| reviews | ✅ |

**通过。** 产品主路径齐：公开拉取 → 结构化 → 双轨呈现 → 一键刷新候选。下一刀：短 ops 手册 `docs/53` + docs/45 登记。

— End —
