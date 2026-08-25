# S2.0.2.1 — `compute_file_sha` 实现任务书

- 编号：`157-stage2-s2021-compute-file-sha-impl-tasking-20260825`
- 前置：`156` 规划通过；`docs/35` §4.2 / §11.2

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | `scripts/compute_file_sha.py` + `tests/test_compute_file_sha.py`（≥5） |
| 允许路径 | `/tmp/cegr_uploads/`（含 `/private/tmp/...`）+ `data/seed_archives/` |
| 禁 | `--url` / 任意 HTTP；路径越权 exit 2；缺文件 exit 1 |
| pack | + docs/35 + 本刀测试（及脚本若入库） |

## NOW

1. 落地 CLI + pytest（合法 / 缺文件 / 越权 / 无 `--url` / SHA 格式）
2. 补 pack（含 docs/35）；`sum(role_count)==artifact_count`
3. commit → origin → 回执 **`158`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不爬网；不伪造 SHA；不 Gate PASS；不改 `gate_thresholds.json`；本刀**不**强制交付真实江苏文件（无文件诚实失败即可）。
