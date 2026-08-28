# 合刀：26X mart-fixture build 路径实跑 + docs 登记 — 任务书

- 编号：`568-stage2-s27b-26x-mart-fixture-build-verify-bundle-tasking-20260828`
- 前置：`567` PASS；用户序列：**先 26X → 合刀 → 再 O1**
- 用户裁定：Stage 2 **C** + **D** + **合刀**；**O1 仍 OPEN（defer）**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做（合刀 · 一步交卷） | **A.** `cd frontend && NEXT_PUBLIC_USE_MART_FIXTURE=1 npm run build`（粘贴 exit code + 关键 stdout；build 须 exit 0）；**B.** `python3 -m pytest tests/test_mart_related_persons_demo_s302.py -q`（15 cases；粘贴 exit code）；**C.** `docs/53` §5 新增第 35 项：26X mart-fixture **build** 路径证据（per A+B）；**D.** `docs/45` 文首/§1/§6.2/§7 四处同步 + `docs/50` §4.4 第 35 项行 + intro 链尾 `→ 568`；**E.** 回执 **仅 `568`**（`-cc-`）|
| 本刀不做 | 公网 redeploy；`NEXT_PUBLIC_USE_MOCK=false`；mart 真 SHA；person 真数据；Gate/O1 PASS；改 registry |
| 偏差 | build 失败：回执如实报告 + 不谎称 PASS |
| 禁止 | 谎称 O1/mart 收口；删 OPEN；动 4 fixture 字节 |

## NOW

1. 实跑（A+B）+ docs（C+D）同交卷
2. pack → 回执 **`568`**
3. **必须双推** → **`84` POLL**

## 红线

合刀单槽单回执；`NEXT_PUBLIC_USE_MART_FIXTURE=1` build = demo mart-shape 管道（**非 O1 收口**）；O1 defer；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）。
