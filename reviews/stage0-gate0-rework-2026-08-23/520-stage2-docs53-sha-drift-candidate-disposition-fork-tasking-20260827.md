# docs/53 §5 第 28 项 SHA drift 候选轨处置分叉登记 — 缩刀任务书

- 编号：`520-stage2-docs53-sha-drift-candidate-disposition-fork-tasking-20260827`
- 前置：`519` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**；preview 容器化 **择机**；**O1=公开源 B 路（docs/52），不等用户投喂**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `docs/53` §5 新增 **第 28 项（此条）** blockquote：登记 `510` live-probe SHA drift 候选轨处置分叉（实测 `a7e4029d…` ≠ expected `dea13b8a…`；选项 (a) 更新 registry `file_hash_sha256` (b) 改稳定归档 URL；**本刀只登记、不改 registry**；**等用户裁定**）；(2) `docs/45` 刷新四处；(3) 非 O1/Gate PASS；(4) 回执 **`520`**（`-cc-`）|
| 本刀不做 | 改 registry；改代码；Gate/O1 PASS；替用户选分叉 |
| 禁止 | 删减 OPEN；谎称真 SHA 已收口 |

## NOW

1. docs only
2. pack → 回执 **`520`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；drift ≠ 收口；registry 变更须用户裁定后另刀。
