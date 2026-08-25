# S1.18.1 — pack 不变量修复任务书

- 编号：`137-stage1-s18-pack-invariant-fix-tasking-20260825`
- 前置：`136` FAIL；功能已绿，仅修证据包

## NOW

1. 修正 `evidence_pack/manifest.json`：
   - `artifact_count` → **504**（与 `len(artifacts)` 一致）
   - `role_count`：`documentation` +1（docs/33）、`schema_negative_test` +1（test_demo_sha_sentinel）
   - `sum(role_count) == artifact_count == 504`
   - `commit.commit_sha` 填本修复 commit（勿留 `PENDING-receipt-backfill`）
2. 复验脚本或手工：`len(artifacts)==artifact_count==sum(role_count)`
3. commit → origin → 回执 **`138`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不改业务逻辑 / 不重开功能刀；不 Gate 1 PASS；不改 `gate_thresholds.json`。
