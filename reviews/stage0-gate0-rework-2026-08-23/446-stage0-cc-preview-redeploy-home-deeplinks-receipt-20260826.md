# 446 — china.3strategy.cc 预览 redeploy + 首页 deeplink HTTP 验收 · CC 回执

- 编号：`446-stage0-cc-preview-redeploy-home-deeplinks-receipt-20260826`
- 任务书：`446-stage2-preview-redeploy-home-deeplinks-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：（待双推回填）
- 日期：2026-08-27

---

## §NOW 对照

| 446 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 港服 `china.3strategy.cc` redeploy 前端（`npm ci` + `NEXT_PUBLIC_USE_MOCK=true npm run build`；`nohup` 若 SSH 易超时）| ✅ redeploy 已完成。**执行分工**：源站 = newvps（`207.57.133.177`，`/opt/china-platform/{repo,frontend}`，per 用户 2026-08-27 指示）；redeploy（rsync + npm ci + `NEXT_PUBLIC_USE_MOCK=true npm run build` + restart）由 **ops 侧执行**（per 用户原话「在 newvps 上 rsync + build + restart」）。CC 的自动分类器拦截生产写入（多轮：hk recon 拦截 → newvps 写拦截），CC 未直接跑 deploy 命令；本回执验收的是 ops 部署后的公网结果。验收时点（2026-08-27）公网已含 4/4 deeplink（旧状态仅 `#track-hb` 1/4）→ 证实 build 产物已更新到含 knife 76/78/82 的版本 | curl 输出（§证据）|
| (2) curl/HTTP 验收首页含 `#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb` + `/public-extracts` | ✅ **4/4 首页 deeplink + /public-extracts 全部 200 在位**（见 §证据 curl 输出）：(a) `href="/public-extracts#track-nbs-sample"` + `data-testid="home-public-extracts-nbs-sample"`（knife 76 / 回执 `420`）；(b) `href="/public-extracts#track-nbs-live"` + `data-testid="home-public-extracts-nbs-live"`（knife 78 / 回执 `424`）；(c) `href="/public-extracts#overview"` + `data-testid="home-public-extracts-overview"`（knife 82 / 回执 `432`）；(d) `href="/public-extracts#track-hb"`（knife 67 / 回执 `377`）；`/public-extracts` HTTP 200（105,893 bytes）且页内 5 锚点（`id="overview"` + `id="track-nbs-sample"` + `id="track-nbs-live"` + `id="track-sz"` + `id="track-hb"`）+ `data-testid="site-nav-public-extracts"`（knife 72 / 回执 `410`）+ 4 行筛选 testId（`track-filter-{nbs-sample,nbs-live,sz,hb}`，knife 68 / 回执 `398`）全部在位 | curl 输出（§证据）|
| (3) 回执 `446`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ curl -sL https://china.3strategy.cc/ | grep -oE 'href="/public-extracts#[a-z-]+"|data-testid="home-public-extracts-[a-z-]+"' | sort -u
data-testid="home-public-extracts-nbs-live"
data-testid="home-public-extracts-nbs-sample"
data-testid="home-public-extracts-overview"
href="/public-extracts#overview"
href="/public-extracts#track-hb"
href="/public-extracts#track-nbs-live"
href="/public-extracts#track-nbs-sample"
（4/4 deeplink；redeploy 前仅 href="/public-extracts#track-hb" 1/4）

$ curl -sL -o /tmp/pe.html -w "HTTP %{http_code} size=%{size_download}\n" https://china.3strategy.cc/public-extracts
HTTP 200 size=105893

$ grep -oE 'id="(overview|track-nbs-sample|track-nbs-live|track-sz|track-hb)"|data-testid="site-nav-public-extracts"|data-testid="track-filter-[a-z-]+"' /tmp/pe.html | sort -u
data-testid="site-nav-public-extracts"
data-testid="track-filter-hb"
data-testid="track-filter-nbs-live"
data-testid="track-filter-nbs-sample"
data-testid="track-filter-sz"
id="overview"
id="track-hb"
id="track-nbs-live"
id="track-nbs-sample"
id="track-sz"

$ python3 scripts/_knife89_manifest_bump.py
ADD: scripts/_knife89_manifest_bump.py (…)
ADD: reviews/.../446-…-receipt-20260826.md (…)
UPDATE artifact_count: 758 → 760
INVARIANT: sum(role_count)=760 == artifact_count=760 == len(artifacts)=760
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `scripts/_knife89_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../446-stage0-cc-preview-redeploy-home-deeplinks-receipt-20260826.md` | NEW（本文件）| `documentation` |

（无 repo 内代码/docs 文件修改；本刀交付 = ops 侧 redeploy + CC HTTP 验收。）

## Pack 不变量

`_knife89_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **758 → 760**；`sum(role_count) == artifact_count == len(artifacts) == 760`。

## 验收明细（公网 HTTP，2026-08-27）

| 验收点 | 结果 | 对应回执 |
|---|---|---|
| 首页 `#track-nbs-sample` + testId | ✅ 在位 | `420`（knife 76）|
| 首页 `#track-nbs-live` + testId | ✅ 在位 | `424`（knife 78）|
| 首页 `#overview` + testId | ✅ 在位 | `432`（knife 82）|
| 首页 `#track-hb` | ✅ 在位 | `377`（knife 67）|
| `/public-extracts` HTTP 200 | ✅ 105,893 bytes | `350`/`359`/`368`/`371`/`377` |
| 页内 5 锚点 id | ✅ overview + 4 track | `383`（overview strip）|
| site-nav testId | ✅ 在位 | `410`（knife 72）|
| 4 行筛选 testId | ✅ 在位 | `398`（knife 68）|

## 分工与约束说明

- **源站**：newvps（`207.57.133.177`）`/opt/china-platform/{repo,frontend}`（per 用户 2026-08-27 指示「还是要用 207.57.133.177」；hk `103.59.103.85` 上 `/opt/china-platform` 不存在，先前误查 hk）。
- **redeploy 执行方**：ops 侧（用户）。CC 自动分类器多次拦截生产 SSH 写入（hk recon → newvps deploy），未绕过拦截；改为用户手动执行 rsync + build + restart（per 用户原话「在 newvps 上 rsync + build + restart」），CC 只做公网 HTTP 验收（per 用户裁定「CC 只需 HTTP 验收并交回执 446」）。
- **非 O1/Gate PASS**：本刀是预览部署验收，4/4 deeplink 是 demo/candidate 入口演示；不构成 O1 / Gate 2 收口；未改 fixture / registry 字节。

## 红线自查

- ❌ 未改代码（本刀无 repo 代码改动；只新增 bump + receipt）
- ❌ 未删减 OPEN（无关）
- ❌ 未 Gate/O1 PASS 宣告（§分工与约束说明显式「非 O1/Gate PASS」「不构成 O1 / Gate 2 收口」）
- ❌ 未改 fixture / registry 字节（未触碰）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未索要 PAT
- ❌ 未 --force（无 git 写操作除本刀 commit + 双推）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ HTTP 验收证据（curl 输出）原文贴入 §证据，验收点 ↔ 回执映射完整

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `446`）。