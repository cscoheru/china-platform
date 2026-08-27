# 448 — docs/53 §5 公网预览部署运维登记 · CC 回执

- 编号：`448-stage0-cc-docs53-preview-redeploy-ops-receipt-20260827`
- 任务书：`448-stage2-docs53-preview-redeploy-ops-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`69090e7`（双推：origin fc33097..69090e7，github fc33097..69090e7）
- 日期：2026-08-27

---

## §NOW 对照

| 448 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/53` §5 补登 **公网预览部署**（`https://china.3strategy.cc`）：源站 = SSH **`newvps`**（`207.57.133.177:52134`），路径 **`/opt/china-platform/frontend`**，**宿主机 systemd** `china-platform-frontend` → `127.0.0.1:3000`，nginx `/etc/nginx/sites-enabled/china.3strategy.cc.conf`；CF 橙云 A→`207.57.133.177`；**勿用** `hk`/`103.59.103.85`（无本站路径）| ✅ docs/53 §5 新增 📍 第 16 项（per 回执 `446`；queue_rev 195 落地）：源站 newvps `207.57.133.177:52134` + 路径 `/opt/china-platform/frontend` + 宿主机 systemd `china-platform-frontend` → `127.0.0.1:3000`（非容器）+ nginx `china.3strategy.cc.conf`（`proxy_pass http://127.0.0.1:3000`）+ CF 橙云 A → `207.57.133.177` + 「勿用 `hk` / `103.59.103.85`（其上无本站路径；回执 `446` §分工与约束有误查记录）」显式警示 | diff |
| (2) 写明 redeploy 命令链（rsync 或 git pull + `npm ci` + `NEXT_PUBLIC_USE_MOCK=true npm run build` + `systemctl restart china-platform-frontend`；SSH 易超时用 `nohup`）| ✅ docs/53 §5 新增 🔧 命令链条目：`ssh newvps` → `cd /opt/china-platform/frontend`（先 rsync 或 git pull 同步 repo 至宿主路径）→ `npm ci` → `NEXT_PUBLIC_USE_MOCK=true npm run build` → `systemctl restart china-platform-frontend`（SSH 易超时用 `nohup` 包裹长命令） | diff |
| (3) 链回执 **`446`**（4/4 首页 deeplink HTTP 验收）| ✅ 第 16 项首句 + 🔧 条目均标 per 回执 `446`；🔧 条目含公网验收基线（首页 4/4 deeplink `#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb` + 3 testId；`/public-extracts` HTTP 200 105,893 bytes + 5 锚点 + site-nav + 4 track-filter testId；2026-08-27 实测） | diff |
| (4) 非 O1/Gate PASS | ✅ 🔧 条目末显式「**预览部署登记是运维信息补登，非 O1/Gate PASS；preview 容器化择机另刀（本刀不做 Docker）；不换服务器；不动 4 fixture 字节（…与 knife 76/78/81/82/84/85/86/87 锁值完全一致）；不改代码**」 | diff |
| (5) 回执 `448`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "公网预览部署\|redeploy 命令链\|china-platform-frontend\|勿用" docs/53-stage2-public-ingest-ops-handbook-20260826.md | head -6
  140:> 📍 **公网预览部署 `https://china.3strategy.cc` 运维登记**（per `446` cc 回执；queue_rev 195 落地）：源站 = SSH **`newvps`**（`207.57.133.177:52134`）…
  142:> 🔧 **redeploy 命令链**（per 回执 `446` §分工：ops 侧在 newvps 执行，CC 只做公网 HTTP 验收）：`ssh newvps` → `cd /opt/china-platform/frontend`…

$ python3 scripts/_knife90_manifest_bump.py
ADD: scripts/_knife90_manifest_bump.py (…)
ADD: reviews/.../448-…-receipt-20260827.md (…)
UPDATE artifact_count: 760 → 762
INVARIANT: sum(role_count)=762 == artifact_count=762 == len(artifacts)=762
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 16 项 📍 运维登记 + 🔧 redeploy 命令链）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife90_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../448-stage0-cc-docs53-preview-redeploy-ops-receipt-20260827.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife90_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **760 → 762**；`sum(role_count) == artifact_count == len(artifacts) == 762`（docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 89 回执 `446` 已落 758 → 760）。

## 登记内容对账（任务书 448 ↔ docs/53 §5 第 16 项）

| 任务书要求 | docs/53 落点 |
|---|---|
| 源站 = SSH `newvps`（`207.57.133.177:52134`）| ✅ 第 16 项「源站 = SSH **`newvps`**（`207.57.133.177:52134`）」 |
| 路径 `/opt/china-platform/frontend` | ✅ 同条 |
| 宿主机 systemd `china-platform-frontend` → `127.0.0.1:3000`（非 hk）| ✅ 同条「**宿主机 systemd** `china-platform-frontend` → `127.0.0.1:3000`（非容器）」 |
| nginx `/etc/nginx/sites-enabled/china.3strategy.cc.conf` | ✅ 同条（含 `proxy_pass http://127.0.0.1:3000`）|
| CF 橙云 A→`207.57.133.177` | ✅ 同条 |
| 勿用 `hk`/`103.59.103.85` | ✅ 同条显式警示（+ 回执 `446` 误查记录引用）|
| redeploy 命令链 + nohup | ✅ 🔧 条目（rsync 或 git pull + `npm ci` + `NEXT_PUBLIC_USE_MOCK=true npm run build` + `systemctl restart` + nohup）|
| 链回执 `446` | ✅ 两处 per `446` + 公网验收基线明细 |
| 非 O1/Gate PASS | ✅ 🔧 条目末守门句 |

## 红线自查

- ❌ 未改代码（docs only per §NOW「docs/53 only」）
- ❌ 未删减 OPEN（§6 红线清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（第 16 项 + 🔧 条目均显式「非 O1/Gate PASS」「不换服务器」）
- ❌ 未做 Docker 容器化（任务书裁定「preview 容器化择机（本刀不做）」；条目注明「另刀」）
- ❌ 未换服务器（登记的就是现行 newvps 源站）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 4 fixture byte SHA 前 8 锁显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76/78/81/82/84/85/86/87 完全一致，未动 fixture 字节）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `448`）。