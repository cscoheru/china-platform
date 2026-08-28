# 合刀：26X 轴 kickoff + mart-shape 预览路径实跑证据 — 任务书

- 编号：`566-stage2-s27b-full-26x-kickoff-mart-fixture-verify-bundle-tasking-20260828`
- 前置：`565` PASS；用户分叉裁定：**先 26X → 保持 C（合刀）→ 再 O1**
- 用户裁定：Stage 2 **C** + **D** + **合刀**；**O1=公开源 B 路**；post-(a) live per `560`（**O1 仍 OPEN，本弧 defer 至 26X 后**）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做（合刀 · 一步交卷） | **A.** `docs/53` §5 新增第 34 项：26X 轴 kickoff 登记（用户分叉 = 先 26X·合刀·再 O1；S2.7-b-full 去 demo 预览路径 = `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 mart-shape 管道；真 mart 真 SHA / person 真数据仍 OPEN → O1 后另刀）；**B.** `docs/45` 文首/§1/§6.2/§7 四处同步 26X 为活跃轴 + O1 defer 序列；**C.** `docs/50` §4.4 里程碑行补登第 34 项 + intro ⚠ 收据链尾续接（链尾以本刀里程碑收口）；**D.** 实跑 mart-shape 预览路径守门：`python3 -m pytest tests/test_mart_city_types_s27bf.py tests/test_frontend_mart_demo_parity_s296.py -q` + `python3 frontend/smoke-check.py`（§10a–§10e mart-shape 门须 PASS；粘贴 exit code + 关键 stdout）；**E.** 回执 **仅 `566`**（`-cc-`）|
| 本刀不做 | mart 真 SHA 入仓；person/tenure 真数据替换；改 registry；`NEXT_PUBLIC_USE_MOCK=false` 公网 redeploy；Gate/O1 PASS；拆多回执 |
| 偏差 | 若 pytest/smoke 失败：回执如实报告失败项 + 不谎称 PASS |
| 禁止 | 谎称 mart/O1 已收口；静默失败；删 OPEN 清单 |

## NOW

1. docs（A+B+C）+ 实跑证据（D）同交卷
2. pack → 回执 **`566`**
3. **必须双推** → **`84` POLL**

## 红线

合刀单槽单回执；`NEXT_PUBLIC_USE_MART_FIXTURE=1` 预览 = demo mart-shape 管道（**非 O1 收口**）；O1 defer 至 26X 后用户序列；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）。
