# 574 — 任务书：O1 docs 收口束（合刀 · 零网络）

- 编号：`574-stage2-o1-docs-closeout-bundle-tasking-20260828`
- 前置：`573-stage0-architect-s572-mart-sha-pilot-audit-PASS-20260828`（架构师审计 PASS；本刀交付 commit 须包含该审计文件）
- 下发：CC 架构师终端（新治理模型首刀；Cursor 退役，`00-CC-CURRENT.md` 冻结，**勿读勿写**）
- 执行端：Claude Code 执行终端
- 日期：2026-08-28
- 验证深度：**全零网络**（无需本地 DB）

---

## §NOW

**(A) docs/53 §5 新增第 39 项**（blockquote，插第 38 项后）——O1 收口条件登记：

内容必须写明：
1. pilot（第 38 项，nanjing+CONDITION 真 SHA `a7e4029d…`）已完成且经 `573` 审计 PASS
2. **不做 60 行铺满 flip**：全 mart 现仅 1 个真实源（stats.gov.cn NATIONAL_BULLETIN）；把单一 SHA 铺满其余 59 行 = 伪造 lineage（踩 docs/53 §6 红线）
3. 其余 59 行真实源缺口登记：需逐城公报经 docs/52 pipeline 入仓后方可逐行 flip；tech-blocked 城市（hubei 等，见 20260826T* 事件文件）停报不绕
4. **O1 收口定义 = pilot 限定域完成 + 缺口清单登记 + 用户裁定**；当前 **O1 仍 OPEN**
5. docs/45 / docs/50 同步行号 + `→ 574` 链尾续接

**(B) docs/50 同步**：
- §4.4 里程碑表 +1 行（第 39 项 · O1 收口条件登记 · **O1 仍 OPEN** 里程碑行）
- intro 收据链尾 `→ 572` 续接 `→ 574`（消除 stale 链尾，保持单链）

**(C) docs/45 同步**（五处模式，沿用 570/572 刀先例）：
- 文首 +1 刷新行（架构师治理模型 + `574` 任务书引用；写明「Cursor 退役、573 起架构师审计」）
- §1 +1 段（第 39 项登记）
- §6.2 行尾注 append（per `574`）
- §7 链头更新 `889 == 889 == 889` + demote 注（knife 574 = 合刀 A–F 同 commit、单槽单回执）
- 所有「O1 仍 OPEN」行数/出现计数**非减**

**(D) manifest bump**：新建 `scripts/_knife574_manifest_bump.py`（沿用 `_knife572` 先例）：
- NEW artifacts **+3**：本 bump 脚本（`spike_helper`）+ `573` 审计文件（`documentation`）+ `574` 回执（`documentation`）
- docs/45/50/53 为已入 manifest 文件 SHA REFRESH（不增计数）
- **886 → 889**；断言 `sum(role_count) == artifact_count == len(artifacts) == 889`

**(E) 零网络核验**（命令 + 输出原样粘贴进回执）：
```bash
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q        # 期望 25 passed / exit 0
python3 frontend/smoke-check.py                                     # 期望 exit 0（本刀未动 frontend，防回归）
grep -o "O1 仍 OPEN" docs/45-*.md | wc -l                           # ≥157
grep -o "O1 仍 OPEN" docs/50-*.md | wc -l                           # ≥21
grep -o "O1 仍 OPEN" docs/53-*.md | wc -l                           # ≥20
shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
                                                                    # e30ee811 9232efdb 937255a5 9056001c
python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
                                                                    # 889 889 889
```

**(F) 回执**：`reviews/stage0-gate0-rework-2026-08-23/574-stage0-cc-o1-docs-closeout-bundle-receipt-20260828.md`
- 文件名含 `-cc-`；**合刀单槽单回执，仅 574 一个回执号**
- 结构沿用 572 回执：§NOW 对照表 + 证据原样粘贴 + 交付清单（role）+ Pack 不变量 + 红线自查

## 交付 commit

单个 commit（conventional，聚焦 why）包含：docs/53、docs/50、docs/45、`scripts/_knife574_manifest_bump.py`、**`573` 审计文件**、本任务书文件、`574` 回执。
随后 cc_head backfill **单独 commit**（勿 amend）。

推送（严格顺序）：
```bash
git push origin HEAD
git push github HEAD
```

## 红线（全部继承，零豁免）

- ❌ 不宣布 Gate 0/1/2 / O1 PASS；**pilot 1 行 + 收口条件登记 ≠ O1 收口；O1 仍 OPEN**
- ❌ 不做 60 行 flip；不改 `mart_city_evidence_chain.sql`（本刀零 SQL 改动）；不改 `mart_city_seven_dim_overview.sql`
- ❌ 不动 registry.csv / gate_thresholds.json / 00-CC-CURRENT.md / 4 fixture 字节
- ❌ 无 --force、无 PAT、无 dbt 实跑、无 --live、无公网 redeploy、无网络爬取
- ❌ 不删减 OPEN 清单（docs/45/50/53 计数非减）
- ❌ 执行端不写架构师资产（573 审计文件、本任务书只读引用，不改内容）
- ✅ Pack 不变量 886 → 889；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 完成后

回执 + 双推完成后**停止**（无下轮心跳；向用户/架构师报告 cc_head）。架构师将审计 574（`575` 号位）后发放 O1 裁定包刀。
