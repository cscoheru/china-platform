# 公开源 live 探测 + SHA 漂移候选 — 缩刀任务书

- 编号：`333-stage2-public-source-live-probe-sha-drift-tasking-20260826`
- 前置：`332` connector PASS；用户：不再等投喂 + AUTH 遇阻报告
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 扩展 `auto_ingest_public_source.py`：live 下载后若 SHA ≠ registry 样本哈希 → **不**伪造、**不**自动改 registry；改为 `intake_status=CANDIDATE_AUTO` + `is_demo=true`，仍 WORM 归档实测字节，并写 `reviews/…sha-drift-…md`（源/URL/computed SHA/expected SHA/建议：用户确认后更新 registry 或改用稳定文件 URL）；(2) SHA 匹配才 `O1_AUTO_INTAKED` + `is_demo=false`；(3) **做一次** NBS zxfb `--live --confirm-live=…` 探测：AUTH→blocked 报告；成功或 drift→证据进回执；(4) 补 ≥4 pytest（drift 路径 / 仍拒 AUTH bypass）；(5) 回执 **`334`** |
| 本刀不做 | 第二省源；改 CF；擅自改 registry 哈希；宣布 Gate/O1 PASS；绕 AUTH |
| 禁止 | 静默吞掉 drift；把 drift 标成 O1_AUTO_INTAKED；headless；伪造 SHA |

## NOW

1. 落地 drift 候选路径 + 一次 live 探测（证据入回执）
2. 补 pack → 回执 **`334`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不绕 AUTH；不伪造；drift ≠ 收口。
