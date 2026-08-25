# S2.0.1.1 — 江苏观察页路由修复任务书

- 编号：`150-stage2-s201-jiangsu-route-fix-tasking-20260825`
- 前置：`149` FAIL

## NOW

1. 修 `frontend/app/provinces/jiangsu/page.tsx`：去掉错误的 `params.province` 门闩（或改为 `[province]` 动态路由且正确取值）
2. 保证默认 mock 下该页渲染 GDP series 表 + `DemoBadge`
3. 扩展 smoke / pytest：断言源码**不再**出现「恒失败」门闩（或等价运行时检查）
4. commit → origin → 回执 **`151`** 进 `reviews/`
5. → **`84` POLL**

## 红线

不扩 S2.1；不 Gate PASS；不改 `gate_thresholds.json`；不爬网。
