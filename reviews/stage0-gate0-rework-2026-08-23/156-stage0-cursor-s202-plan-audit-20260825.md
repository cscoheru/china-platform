# S2.0.2 规划 — Cursor 审验 ACK

- 文件编号：`156-stage0-cursor-s202-plan-audit-20260825`
- 日期：2026-08-25
- 对象：CC `4a62769`（`docs/35`）+ 回执 `4ca38cb`（`155`）
- 任务书：`154`

---

## §0. 判定

| 项 | 独立复验 | 判定 |
|---|---|---|
| `docs/35` 覆盖 154 §NOW | §1–§11；~262 行 | ✅ |
| 上传/本地路径 + 禁爬 | §4.1 | ✅ |
| compute_file_sha 诚实失败 | §4.2 exit 0/1/2；拒 `--url` | ✅ |
| DemoBadge / live API | §4.4 | ✅ |
| URL probe 真实化钉死 | §5 ↔ docs/32 | ✅ |
| 回执 `155` | `reviews/` | ✅ |
| pack | **506**（docs/35 未入） | ⚠️ 实现刀须 +1 |

**S2.0.2 规划通过。** 下一刀：**S2.0.2.1 实现**（见 `157`；`compute_file_sha`）。

## §1. 实现时注意

- macOS `/tmp` → `/private/tmp`：ALLOWED_PREFIXES 须用 `resolve()` 后前缀匹配（含 private）
- §4.3 admin→seed 流程勿假设 upload 自动改 demo JSON；实现刀须写清「覆盖 is_demo」的真实步骤
- 不伪造 SHA；无文件 → 诚实失败，不造假样本

— End —
