# 454 — docs/50 §4.4 预览 URL 块补登公网 URL · CC 回执

- 编号：`454-stage0-cc-docs50-public-preview-url-block-receipt-20260827`
- 任务书：`454-stage2-docs50-public-preview-url-block-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：（待回填）
- 日期：2026-08-27

---

## §NOW 对照

| 454 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §4.4 预览 URL 块补登公网 URL（`https://china.3strategy.cc` + `/public-extracts` + 首页 4 deeplink 示例；链行 200 / `docs/53` §5 第 16 项 / 回执 `446`）| ✅ 预览 URL 块（行 202 起）新增 **公网预览** 段（行 204-209）：段落头显式「per 行 200 公网预览 redeploy 运维里程碑 + `docs/53` §5 第 16 项 + 回执 `446`；源站 newvps 宿主机 systemd，redeploy 命令链见 `docs/53` §5 🔧 条目」+ bash 块 2 条 `open`（`https://china.3strategy.cc/public-extracts` 四轨 + 一览条 + 行筛选 + JSON/CSV + site-nav（HTTP 200 per 回执 446）；`https://china.3strategy.cc/` 首页 4 deeplink `#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb`） | diff + grep |
| (2) 保留 localhost 段 | ✅ **本地预览** 段（行 211-218）原样保留：`cd frontend && npm run dev` + 4 条 `open http://localhost:3000…` 命令与注释逐字未动（仅段头加粗标记「**本地预览**：」以与公网段并列） | diff |
| (3) 非 O1/Gate PASS | ✅ ⚠ 守门清单首条新增（行 222）：「公网预览与本地预览同构（`NEXT_PUBLIC_USE_MOCK=true` build 的 demo/candidate 数据），公网 URL 仅为运维演示入口，非 O1/Gate PASS（per 行 200 + 回执 `446`）」；既有 5 条 ⚠ 守门 + 「预览路径不构成 O1 / Gate 2 收口」句原样保留；文首「禁止 PASS 措辞」不变 | grep |
| (4) 回执 `454`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "预览 URL（per §4.4）\|公网预览（per 行 200\|open https://china.3strategy.cc\|本地预览：\|公网预览与本地预览同构" docs/50-stage2-gate2-review-packet-draft-20260826.md
  202   （预览 URL 块头）
  204   （公网预览 段头：per 行 200 + docs/53 §5 第 16 项 + 回执 446）
  207   （open https://china.3strategy.cc/public-extracts）
  208   （open https://china.3strategy.cc/  首页 4 deeplink）
  211   （本地预览 段头 —— localhost 段保留）
  222   （⚠ 公网预览与本地预览同构…非 O1/Gate PASS 守门）

$ python3 scripts/_knife93_manifest_bump.py
ADD: scripts/_knife93_manifest_bump.py (…)
ADD: reviews/.../454-…-receipt-20260827.md (…)
UPDATE artifact_count: 766 → 768
INVARIANT: sum(role_count)=768 == artifact_count=768 == len(artifacts)=768
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 预览 URL 块：+公网预览 段（段头 + bash 块 2 条 open）+ 本地预览 段头标记 + ⚠ 守门清单 +1 条）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife93_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../454-stage0-cc-docs50-public-preview-url-block-receipt-20260827.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife93_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **766 → 768**；`sum(role_count) == artifact_count == len(artifacts) == 768`（docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 92 回执 `452` 已落 764 → 766；knife 91 `450` 已落 762 → 764；knife 90 `448` 已落 760 → 762；knife 89 `446` 已落 758 → 760）。

## 红线自查

- ❌ 未改代码（docs only per §NOW「只改 `docs/50`」）
- ❌ 未删减 OPEN（仅增不改：localhost 段 4 条 open 命令逐字保留 + 既有 5 条 ⚠ 守门原样 + §5.1/§5.4 OPEN 清单不动）
- ❌ 未 Gate/O1 PASS 宣告（公网段头链行 200 非 PASS 守门句 + ⚠ 新守门条 + 既有「预览路径不构成 O1 / Gate 2 收口」句）
- ❌ 未做 Docker / 未换服务器（行 200 既有「preview 容器化择机另刀」不动）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 4 fixture byte SHA 前 8 锁显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76/78/81/82/84/85/86/87/89/90/91/92 完全一致，未动 fixture 字节）
- ✅ 公网 URL 事实源：回执 `446` 公网验收基线（2026-08-27 实测：4/4 deeplink + `/public-extracts` HTTP 200 + 5 锚点 + site-nav + 4 track-filter testId），未新发任何 HTTP 请求（本刀 docs only）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `454`）。
