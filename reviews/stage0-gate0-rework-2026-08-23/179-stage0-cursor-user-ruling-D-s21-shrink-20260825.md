# 用户裁定 ACK — 代号 D

- 编号：`179-stage0-cursor-user-ruling-D-s21-shrink-20260825`
- 日期：2026-08-25
- 对象：`178` §BLOCKED

## 裁定

用户选择 **D**：**缩刀** S2.1 实现。

| 本刀做 | 本刀不做（书面 OPEN → 后续刀） |
|---|---|
| migration DDL（docs/36 §2 六表） | dbt `stg_*` / `mart_person_tenure` |
| 空/最小 seed 骨架（可 0 行业务数据） | 首批 ≤30 person 手工履历灌库 |
| 最小 pytest（表存在 + tenure 无 EXCLUDE/重叠合法 DDL 级） | S2.7-b UI 接入 |

`user_ruling` 更新为 **D**（Stage 2 前进裁定 **C** 仍有效；本代号仅解 S2.1 停滞）。

## 下一刀

见 **`180`**（取代 `174` 全量范围）。

— End —
