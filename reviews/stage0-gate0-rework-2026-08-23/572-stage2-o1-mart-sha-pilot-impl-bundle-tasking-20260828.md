# 合刀：mart 真 SHA 入仓 pilot（nanjing CONDITION）+ docs — 任务书

- 编号：`572-stage2-o1-mart-sha-pilot-impl-bundle-tasking-20260828`
- 前置：`571` PASS；`570` 第 37 项下一刀登记
- 用户裁定：自主推进 O1 序列；**O1 仍 OPEN（本刀不宣布收口）**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做（合刀 · 一步交卷） | **A.** `dbt/models/marts/mart_city_evidence_chain.sql`：pilot 行 = `nanjing` + `CONDITION` 段 — `lineage_source_file_sha256` = registry `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb`（per `538`/`560`）；`lineage_is_demo` = `'false'`；其余 59 行保持 demo + `'0'*64`；**B.** 扩 `tests/test_mart_city_dbt_skel_s27bf.py`：新增/调整 cases 锁定 pilot 行 + 其余行 demo 占位不变；**C.** `docs/53` §5 第 38 项：mart SHA pilot 实装证据；**D.** `docs/45` + `docs/50` 同步 + intro `→ 572`；**E.** `python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q` exit 0；**F.** 回执 **仅 `572`** |
| 本刀不做 | 全量 60 行 flip；person 真数据；Gate/O1 PASS；改 registry；公网 redeploy |
| 偏差 | pytest 失败：回执如实报告 |
| 禁止 | 谎称 O1 收口；伪造 SHA；删 OPEN |

## NOW

1. impl（A+B）+ docs（C+D）+ pytest（E）同交卷
2. pack → 回执 **`572`**
3. **必须双推** → **`84` POLL**

## 红线

合刀单槽单回执；pilot 1 行真 SHA ≠ O1 收口（mart 全量真 SHA / person 真数据仍 OPEN）；不动 4 fixture 字节。
