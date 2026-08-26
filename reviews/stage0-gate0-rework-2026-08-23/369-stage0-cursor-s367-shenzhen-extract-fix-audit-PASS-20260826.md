# 深圳样本抽取修复 — Cursor 审验 ACK

- 文件编号：`369-stage0-cursor-s367-shenzhen-extract-fix-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `543d180` / `3cdd12e` + 回执 `368`
- 任务书：`367`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| 深圳 prose 回退 → **71 行**；PNG 表不伪造 | 源码 + 抽取 | ✅ |
| NBS 仍 **63 行** | 抽取 + JSON | ✅ |
| `tests/…s52.py` | **86 passed** | ✅ |
| pack | **679 / 679 / 679** | ✅ |
| 回执 `368`（`-cc-`）| reviews | ✅ |

**通过。** 下一刀：深圳 REGISTRY_SAMPLE 上 `/public-extracts`（与 NBS 分节，不覆盖双轨）。

— End —
