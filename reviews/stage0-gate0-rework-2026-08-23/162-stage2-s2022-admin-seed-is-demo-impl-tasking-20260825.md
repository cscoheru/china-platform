# S2.0.2.2 — admin upload → seed 覆盖 `is_demo` 实现任务书

- 编号：`162-stage2-s2022-admin-seed-is-demo-impl-tasking-20260825`
- 前置：`161` S2.0.2.1 PASS；`docs/35` §4.3 / §11.3
- 用户裁定：**C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 上传 | **复用** S1.13 `/admin/upload`；不新写 API |
| 覆盖语义 | 真实文件 + `compute_file_sha` → seed/观测 `lineage.is_demo` 非 `"true"`；`file_hash_sha256` ≠ 全零 |
| 无真实文件 | **诚实失败**（脚本/测试 skip 或 rc≠0）；**不伪造**样本内容冒充江苏公报 |
| 前端 | **不强制改**；契约已由 DemoBadge 驱动（docs/35 §4.4） |

## NOW

1. 落地可重复流程（脚本或文档化命令 + pytest）：fixture 文件进 allowlist 前缀 → sha →（模拟或真实）upload/seed 路径 → 断言 `is_demo` 清除或等价
2. 回归：`test_compute_file_sha` + `test_demo_sha_sentinel` + `test_admin_upload_s131`（相关）仍绿
3. commit → origin → 回执 **`163`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不爬网；不伪造 SHA / 不造假公报数值冒充 VERIFIED；不 Gate PASS；不改 `gate_thresholds.json`。
