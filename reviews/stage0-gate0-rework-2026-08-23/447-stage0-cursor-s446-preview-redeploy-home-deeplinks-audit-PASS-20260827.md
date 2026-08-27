# 预览 redeploy + 首页 deeplink — Cursor 审验 ACK

- 文件编号：`447-stage0-cursor-s446-preview-redeploy-home-deeplinks-audit-PASS-20260827`
- 日期：2026-08-27
- 对象：CC `1ab09a7` / `21f6b19` + 回执 `446`
- 任务书：`446`

---

## §0. 判定：**PASS**

| 项 | 判定 |
|---|---|
| 源站纠正（newvps，非 hk）已对齐 | ✅ |
| 公网首页 4/4 deeplink + testId | ✅（Cursor 复验） |
| `/public-extracts` HTTP 200 | ✅ |
| 未宣称 Gate/O1 PASS；OPEN 在位 | ✅ |
| pack | **760** |
| 回执 `446` | ✅ |

**通过。** CC **POLL**。

注：redeploy 由 Cursor/ops 在 `newvps` 执行；CC 因生产写入拦截仅做 HTTP 验收——本刀可接受。

— End —
