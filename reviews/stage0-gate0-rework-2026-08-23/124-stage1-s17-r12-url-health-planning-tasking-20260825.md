# S1.17 — R12 URL 健康探针 / ingest 失败率 规划任务书

- 编号：`124-stage1-s17-r12-url-health-planning-tasking-20260825`
- 前置：`123` S1.16 PASS；用户裁定 **A**；`docs/27` §4.1 剩余缺口
- 范围：**规划 only**

## 背景

- R08 `/admin/upload` 已交（S1.13）；R03/§2.4 已交（S1.16）
- **仍缺**（`docs/26` §1.4 / `docs/27` §4）：R12 **URL 健康探针** + `ingest_run` 失败率告警自动化（现仅 spike `monitor_ingest` 雏形）

## NOW（CC 交付）

1. 起草 **`docs/32-stage1-s17-r12-url-health-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - 与现有 `tests/test_ingest_monitor.py` / spike monitor 的边界（复用 vs 新）
   - 探针范围（`source_registry` URL / backup_urls）；**不爬业务数据**、不绕验证码
   - 失败率告警最小可验收（pytest 或脚本 + 退出码；本地/fixture 诚实）
   - 空表 / 无网环境策略；与 Stage 2 监控的边界
3. 规划 only — 实现另开；回执 **`125`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网（探针可 HEAD/GET 元数据，须在规划中钉死上限）；不改 `gate_thresholds.json`；Cursor 不写 `docs/32` 正文。
