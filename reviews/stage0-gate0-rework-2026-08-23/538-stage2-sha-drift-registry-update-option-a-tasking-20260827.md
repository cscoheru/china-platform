# SHA drift registry 更新（用户裁定 a）— 实现刀任务书

- 编号：`538-stage2-sha-drift-registry-update-option-a-tasking-20260827`
- 前置：`537` PASS；**用户 2026-08-27 裁定 (a)**
- 用户裁定：**(a) 更新 registry.csv `file_hash_sha256`**（认定源站换版；per knife `510` live-probe 证据）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `source_registry/registry.csv` **stats.gov.cn / NATIONAL_BULLETIN** 行：`file_hash_sha256` → `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb`；`file_size_bytes` → `180165`（per 回执 `510`）；(2) 实跑 `--live --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl` 验证 hash **匹配**（exit 0）；(3) `docs/45` + `docs/53` 刷新（用户裁定 (a) 已执行）；(4) 回执 **`538`**（`-cc-`）|
| 本刀不做 | Gate/O1 PASS；改 `enabled`；动 4 frontend fixture 字节；选 (b) |
| 禁止 | 删减 OPEN；`is_demo=false` 宣称；谎称 O1 已收口 |

## NOW

1. registry 更新 + live 复验
2. docs 刷新
3. pack → 回执 **`538`**
4. **必须双推** → **`84` POLL**

## 红线

registry 更新 ≠ O1 收口；drift 处置后 O1 仍 OPEN 直至 mart 真 SHA 入仓。
