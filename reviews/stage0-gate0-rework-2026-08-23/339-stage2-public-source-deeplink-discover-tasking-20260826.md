# 公开源深链发现（无 headless）— 缩刀任务书

- 编号：`339-stage2-public-source-deeplink-discover-tasking-20260826`
- 前置：`338` Hubei PASS；live 得 71B JS 壳 ≠ xlsx；NBS/Hubei 哈希收口仍等用户
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 在 connector 增加 **deeplink discover**：对 index HTML 用 bs4/`re` 找同域 `.xlsx`/`.xls`/稳定附件 href（允许相对路径拼绝对 URL）；**禁止 headless / 禁止执行 JS**；(2) 若找到 ≥1 条 → 下载首个（或最新可解析）附件 → 走既有 sha/archive/extract/drift；(3) 若 0 条或仅 JS 壳（体积阈值或无表格标记）→ 写 `reviews/…tech-blocked…md`（5 字段：源/URL/现象/需要什么/替代），**停并报告用户**，不绕过；(4) NBS：可选找 zxfb 下稳定 HTML 文章链（同域）作附件候选；(5) ≥6 pytest；(6) 对 Hubei **再 live 一次**；证据入回执 **`340`** |
| 本刀不做 | headless；改 registry 哈希（等用户）；深圳全量；Gate/O1 PASS |
| 禁止 | 执行页面 JS；盲爬外域；静默把 JS 壳当 O1 |

## NOW

1. 落地 deeplink + 阈值/JS 壳检测 + tech-blocked 报告
2. Hubei 再 live 一次；结果入回执
3. 补 pack → 回执 **`340`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不 headless；不绕 AUTH/JS；不伪造。
