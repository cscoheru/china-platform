# 禁止测试覆写 public_extracts — 缩刀任务书

- 编号：`352-stage2-protect-public-extracts-from-pytest-tasking-20260826`
- 前置：`351` PASS；`7f04237`/`95a8569` 两度恢复 NBS 63 行；subprocess 测绕过 monkeypatch
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) connector CLI 增 `--extract-root=DIR` / `--archive-root=DIR`（默认仍为仓库路径）；(2) **所有** pytest（含 subprocess）必须传入临时 root，或设环境变量 `CEGR_EXTRACT_ROOT`/`CEGR_ARCHIVE_ROOT`；(3) 加回归测：跑相关 case 后 `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` 的 `source_sha256`/`row_count` 不变；(4) 回执文件名必须匹配 `N-stage0-cc-…-receipt-…md`；(5) 回执 **`353`** |
| 本刀不做 | 改前端呈现；Gate PASS；headless |
| 禁止 | 测试写仓库 extracts；漏 `-cc-` 回执名 |

## NOW

1. 落地 root 覆盖 + 回归测
2. 补 pack → 回执 **`353`**（`-cc-` 命名）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不覆写已提交 extracts。
