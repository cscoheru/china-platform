# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。超标先删再写。**
> 新会话 / `/compact` 后：只读本文件。深读按 §POINTERS 一次一个。

## 愿景（PRD）

国家—省级—试点城市的**可查询、可回溯**研究底座。事实/派生/推断/判断分层。不建官员总分。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` |
| 阶段 | **M2**（M1 有限通过） |
| 拆分 | `docs/56` |
| NOW | **633 M2-b** 首批 ≥5 省 2024 GDP 表 ingest |
| 北极星 | 2024 年 31 省 GDP 一致率（08b） |
| Gate | **未 PASS** |

## 红线

禁：首页/目录当 FETCHED；PARTIAL 当完成；补零；湖北 2024 复用 M1 `c5cf5abe`；自动 Gate/M2 PASS。

KPI：`geo×indicator×year=2024` COVERED≥5（本刀）；缺省写 `missing_reason`。

## NOW（本阶段）

633：修 unload → 国家+苏浙粤+鄂(2024) 定稿表 SHA → observation SUCCESS → coverage≥5/31。详见任务书 `633`。

## POINTERS（冷）

- `docs/54` · `docs/56` · `docs/08b` §1.2
- 任务书：`reviews/…/633-stage0-architect-m2-b-first-batch-tasking-20260831.md`
- 调度：`00-EXEC-QUEUE.md` §NOW
- 轮询：`00-DUAL-POLL-PROTOCOL-20260831.md` + `scripts/dual_poll_status.sh`

## 压缩后自检

阶段？NOW 三步？禁做什么？
