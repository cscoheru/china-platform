# O1 B 路 NATIONAL_BULLETIN connector dry-run 证据 — 缩刀任务书

- 编号：`492-stage2-o1-bpath-nbs-dry-run-evidence-tasking-20260827`
- 前置：`491` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**；preview 容器化 **择机**；**O1=公开源 B 路（docs/52），不等用户投喂**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 跑 `scripts/auto_ingest_public_source.py --dry-run --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN`（默认 dry-run；**无网络、无 DB 写、不 --live**）；(2) 回执粘贴命令 + exit code + 关键 stdout（OK dry-run 句）；(3) `docs/53` §5 新增 **第 22 项**登记本 dry-run 证据（非 O1 收口）；(4) `docs/45` 刷新四处；(5) 回执 **`492`**（`-cc-`）|
| 本刀不做 | `--live` / `--confirm-live`；改 registry；改 fixture；启用 Hubei；Gate/O1 PASS |
| 禁止 | 谎称 O1 已收口；静默失败不报告；绕过红线 |

## NOW

1. dry-run only（无网络）+ docs
2. pack → 回执 **`492`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；不 live；不等用户投喂。
