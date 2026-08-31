# 634 — Cursor 审验：633 M2-b PASS

- 日期：2026-08-31
- 对象：`633-stage0-cc-m2-b-first-batch-receipt-20260831.md`（审验时本地；随本批入库）
- 任务书：`633-stage0-architect-m2-b-first-batch-tasking-20260831.md`

---

## 判定：**PASS**（≠ M2 / Gate PASS）

| 项 | 回执 | 独立复验 | 判定 |
|---|---|---|---|
| pytest | 16 passed | `STAGE0_SKIP_SCHEMA_APPLY=1 … test_m2_b* + test_m2_province*` → **16 passed** | ✅ |
| 省级 COVERED≥5 | 5/31 | coverage 脚本 **5/31** + 国家 **1/1** | ✅ |
| 一跳 SHA | 北京等 | 6 archive 文件 SHA 前 16 = inventory = DB | ✅ |
| 湖北≠M1 | `3022e7ca…` | ≠ `c5cf5abe…`；obs value=60012.97 | ✅ |
| 非目录 FETCHED | 6 文章 path | 无 `/`、无仅 `/tjgb/` | ✅ |
| SUCCESS | 6/6 | 测试闸绿；非 PARTIAL | ✅ |
| 年期 | NBS 202502 公报 | URL 换为 2024 年公报（非旧 202402） | ✅ |
| 苏浙粤→沪鲁川 | fallback | 反爬披露；tasking §2 允许 | ✅ |

**不宣布：** Gate / O1 / M2 PASS。

---

## ⚠ 接受项

1. **硬编码 value + regex 交叉** — `ingest_m2_2024_gdp.py` 以 SUBJECTS 常数为预期，regex 一致才返回解析值，失败则 **静默回落硬编码**。本刀 SHA 已锁 HTML；**下一刀禁止静默回落**（不一致须 FAIL）。
2. **unload 语义变更** — 不再删 registry；保留 lineage；测试改为「anchors 仍在」。接受。
3. **回执审验时未在 origin** — 本批一并入库双推。

---

## 下一刀

**635 合刀（M2-c + M2-d + M2-e）** — 扩满可得省 + 跨源核对 + `/research/q1-2024-gdp`；一份回执集中摄影。

— End 634 —
