# 合刀：O1 轴 kickoff + mart 真 SHA 入仓下一轴登记 — 任务书

- 编号：`570-stage2-o1-kickoff-mart-sha-next-axis-bundle-tasking-20260828`
- 前置：`569` PASS；用户裁定：**26X 告一段落，准备切 O1**（566/568 已闭环）
- 用户裁定：Stage 2 **C** + **D** + **合刀**；**O1=公开源 B 路**；post-(a) live per `560`（hash 匹配 + `O1_AUTO_INTAKED`/`is_demo=false`）；**O1 仍 OPEN（本刀不宣布收口）**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做（合刀 · 一步交卷） | **A.** `docs/53` §5 新增第 36 项：O1 轴 kickoff 登记（用户 pivot：26X 34–35 已落 per `566`/`568` → O1 活跃轴；下一轴 = mart 真 SHA 入仓 per 第 32–33 项弧 + `560` 证据）；**B.** `docs/53` §5 新增第 37 项：mart 真 SHA 入仓下一刀登记（**只登记不运行**——目标 = dbt mart `lineage.source_file_sha256` 从 `'0'*64` 占位替换为 registry `a7e4029d…`；依赖 `560` lineage `O1_AUTO_INTAKED`/`is_demo=false`；**不等同 O1 收口**）；**C.** `docs/45` 文首/§1/§3/§6.2/§7 四处同步（O1 活跃 + 26X defer 完成 + mart SHA OPEN）；**D.** `docs/50` §4.4 第 36–37 项行 + intro 链尾 `→ 570`；**E.** 证据锚点核验（零网络）：`grep` registry NATIONAL_BULLETIN `a7e4029d` + `shasum` 4 fixture 锁值 + `python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q`（mart skel baseline；粘贴 exit code）；**F.** 回执 **仅 `570`**（`-cc-`）|
| 本刀不做 | 改 dbt mart SQL；mart 真 SHA 实装；Gate/O1 PASS；改 registry；`--live` 重跑；拆多回执 |
| 禁止 | 谎称 O1/mart 已收口；删 OPEN；动 4 fixture 字节 |

## NOW

1. docs（A–D）+ 锚点核验（E）同交卷
2. pack → 回执 **`570`**
3. **必须双推** → **`84` POLL**

## 红线

合刀单槽单回执；`560` hash 匹配 + `O1_AUTO_INTAKED` ≠ O1 收口；mart 真 SHA 入仓登记 ≠ 执行；O1 仍 OPEN 直至用户/Cursor 另裁；不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）。
