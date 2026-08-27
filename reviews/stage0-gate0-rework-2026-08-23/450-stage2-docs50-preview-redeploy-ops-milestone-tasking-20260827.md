# docs/50 §4.4 预览 redeploy 运维里程碑补登 — 缩刀任务书

- 编号：`450-stage2-docs50-preview-redeploy-ops-milestone-tasking-20260827`
- 前置：`449` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**；preview 容器化 **择机**（本刀不做）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `docs/50` §4.4 里程碑表补 1 行：**公网预览 redeploy 运维**（`https://china.3strategy.cc`；源站 **newvps** 宿主机 systemd；`docs/53` §5 第 16 项；回执 `448`/`446`）；(2) 链 `docs/45`/`docs/53`；(3) 非 O1/Gate PASS；(4) 回执 **`450`**（`-cc-`）|
| 本刀不做 | 改代码；Docker 容器化；Gate/O1 PASS |
| 禁止 | 删减 OPEN；谎称 O1；换服务器 |

## NOW

1. 只改 `docs/50`
2. pack → 回执 **`450`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS。
