# S2.0.1 实施 — Cursor 审验 FAIL

- 文件编号：`149-stage0-cursor-s201-impl-audit-FAIL-20260825`
- 日期：2026-08-25
- 对象：CC `b24c512` + 回执 `4a20d28`（`147`）；唤醒 `148`
- 任务书：`146`

---

## §0. 判定：**FAIL**（省级页壳不可用）

| 项 | 独立复验 | 判定 |
|---|---|---|
| `frontend/` 骨架 + README | 存在；Next 14 | ✅ |
| mock 开关 + DemoBadge | 代码在 | ✅ |
| smoke pytest | **5 passed** | ✅ |
| pack 504→506 + docs/34 | 504→506；docs/34 在 | ✅ |
| 省级观察页壳可渲染 series | 见 §1 | ❌ |
| frontend 文件入 pack | 回执诚实延期 | ⚠️ |

## §1. 失败证据

路径为**静态** `app/provinces/jiangsu/page.tsx`，但页面逻辑：

```ts
if (params.province !== "jiangsu") { return /* 尚未支持 */; }
```

App Router 静态段**无** `params.province` → 恒为 `undefined` → 恒走「尚未支持」分支 → **series 表 / DemoBadge 永不渲染**。  
smoke 只做文件存在性断言，未覆盖运行时路由行为。

## §2. 修复方向（见 `150`）

- 删掉无意义的 `params.province` 检查（推荐），或改为 `app/provinces/[province]/page.tsx`
- 补最小运行时断言（smoke 读源码断言无错误分支 / 或 Playwright 非本刀强制）

— End —
