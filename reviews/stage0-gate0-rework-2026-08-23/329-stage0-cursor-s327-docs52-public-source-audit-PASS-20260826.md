# docs/52 官方公开源自动获取规划 — Cursor 审验 ACK

- 文件编号：`329-stage0-cursor-s327-docs52-public-source-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `8579a3a` / `2c566be` + 回执 `328`
- 任务书：`327`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| `docs/52`：允许 3 类公开源 + 禁止绕 AUTH/盲爬/伪造 | 源码 | ✅ |
| §3 首批试点：NBS HTML → Hubei xlsx → Shenzhen HTML | 源码 + registry 对齐 | ✅ |
| §4 六步流水线 + `is_demo=false` 闸门（对齐 docs/48） | 源码 | ✅ |
| §5 A（docs/51 投递）+ B（自动获取）并存；命名空间不混用 | 源码 | ✅ |
| §6 AUTH 升级：触发 / 5 报告字段 / 4 用户裁定；不静默失败 | 源码 | ✅ |
| 本刀 markdown-only；未改 registry / docs/48/51 / CF | diff | ✅ |
| 未宣布 Gate/O1 PASS；无 bare PASS | grep | ✅ |
| pack | **645 / 645 / 645** | ✅ |
| 回执 `328` | `reviews/` + manifest | ✅ |

**规划通过。** 下一刀：落地首个 connector（NBS `NATIONAL_BULLETIN` HTML）。

— End —
