# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列

> **rev 56 · 2026-08-31。** 历史：`00-EXEC-QUEUE.archive-rev53-20260831.md`。
> `00-CC-CURRENT.md` 冻结 rev 320。热记忆：`docs/00-COMPASS.md`。
> **禁止宣布 Gate / O1 / M2 PASS。禁止首页/目录 HTML 当 FETCHED 完成。**

## §META

- rev: 56
- updated: 2026-08-31
- ruling: 632 PASS；用户签 **M2-b = 633**

## §CURRENT

- status: **M2-b（633）NOW**
- cc_head: `ee8e285`（631；633 交付后回填）
- last_audit: `632-stage0-cursor-s631-m2-a-audit-PASS-20260831.md`
- tasking: `633-stage0-architect-m2-b-first-batch-tasking-20260831.md`

## §NOW

执行 **633（M2-b）**：

1. 修 `seed_m2` `unload()`：`DOC_ID` → `REGISTRY_ID`（+ 删对应 source_document）
2. 首批：**国家 + 苏 + 浙 + 粤 + 湖北(另取 2024 年度，禁 c5cf5abe)**  
3. 定稿表字节 → SHA → observation **SUCCESS**；coverage **COVERED≥5/31**
4. 校验国家 URL 统计期是否真为 2024（疑似 2023 公报须更换）

禁：目录/首页 FETCHED；补零；PARTIAL 当完成；宣布 M2/Gate PASS。

## §CHAIN_TAIL

| 刀 | 状态 | 一句话 |
|---|---|---|
| M1 | 有限通过 | 用户 2026-08-31 |
| 631 | AUDITED | M2-a；632 PASS |
| 633 | **NOW** | M2-b 首批 ≥5 表 ingest |
| M2-c | — | 扩 31 省 |
| M2-d | — | 跨源核对 |

## §ACK

- 2026-08-31 / 用户 / 签 M2-b
- 不宣布 Gate / O1 / M2 PASS
