# docs/53 §5 预览 redeploy 运维登记 — 缩刀任务书

- 编号：`448-stage2-docs53-preview-redeploy-ops-tasking-20260827`
- 前置：`447` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**；preview 容器化 **择机**（本刀不做）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `docs/53` §5 补登 **公网预览部署**（`https://china.3strategy.cc`）：源站 = SSH **`newvps`**（`207.57.133.177:52134`），路径 **`/opt/china-platform/frontend`**，**宿主机 systemd** `china-platform-frontend` → `127.0.0.1:3000`，nginx `/etc/nginx/sites-enabled/china.3strategy.cc.conf`；CF 橙云 A→`207.57.133.177`；**勿用** `hk`/`103.59.103.85`（无本站路径）；(2) 写明 redeploy 命令链（rsync 或 git pull + `npm ci` + `NEXT_PUBLIC_USE_MOCK=true npm run build` + `systemctl restart china-platform-frontend`；SSH 易超时用 `nohup`）；(3) 链回执 **`446`**（4/4 首页 deeplink HTTP 验收）；(4) 非 O1/Gate PASS；(5) 回执 **`448`**（`-cc-`）|
| 本刀不做 | 改代码；Docker 容器化；Gate/O1 PASS |
| 禁止 | 删减 OPEN；谎称 O1；换服务器 |

## NOW

1. docs/53 only
2. pack → 回执 **`448`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；容器迁移另刀。
