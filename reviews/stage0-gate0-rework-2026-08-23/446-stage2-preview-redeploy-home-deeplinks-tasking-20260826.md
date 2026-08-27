# 预览 redeploy + 首页 deeplink 验收 — 缩刀任务书

- 编号：`446-stage2-preview-redeploy-home-deeplinks-tasking-20260826`
- 前置：`445` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) **正确源站**（勿用 hk `103.59.103.85`）：SSH **`newvps`** = `207.57.133.177:52134`，路径 **`/opt/china-platform/frontend`**，systemd **`china-platform-frontend`**，nginx `proxy_pass http://127.0.0.1:3000`（站点 `/etc/nginx/sites-enabled/china.3strategy.cc.conf`）。CF 橙云 A→`207.57.133.177`。redeploy：`npm ci` + `NEXT_PUBLIC_USE_MOCK=true npm run build` + `systemctl restart china-platform-frontend`（`nohup` 若 SSH 易超时）；(2) curl/HTTP 验收首页含 `#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb` + `/public-extracts`；(3) 回执 **`446`**（`-cc-`）|
| 本刀不做 | 改代码；Gate/O1 PASS；live 探测 |
| 禁止 | 删减 OPEN；谎称 O1 |

## NOW

1. redeploy + HTTP 验收
2. pack → 回执 **`446`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；不改 fixture/registry。
