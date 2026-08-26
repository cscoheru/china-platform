# 407 — docs/45 + docs/53 CSV 下载登记 · CC 回执

- 编号：`407-stage0-cc-docs45-csv-download-refresh-receipt-20260826`
- 任务书：`406-stage2-docs45-csv-download-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`TODO_BACKFILL`
- 日期：2026-08-26

---

## §NOW 对照

| 406 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` §1/§6.2 登记四轨 **CSV 静态下载**（`gen_public_extracts_csv.py` + `/public-extracts/*.csv`；回执 `404`；与 JSON 并列） | ✅ docs/45 三处：文首 +`刷新 queue_rev 170` 行；§1 回执链 +`→ 404（四轨 CSV 静态下载…）` 段 + 守门句扩为「四轨 + 一览条 + 行筛选 + CSV 下载皆 demo/candidate 演示（行筛选仅为客户端视图过滤，CSV 仅是 fixture 快照确定性导出）」；§6.2 +「`/public-extracts` 四轨 CSV 静态下载（fixture 快照导出）」一行（列头「下载 JSON / CSV」+ 4 同格 CSV 第二链 + 4 CSV 产物 / 生成器 / 13 pytest 表头一致×4 + 行数字段数×4 + 字节重渲×4 + 页面守门 + smoke §12i 15 针 / JSON 链不回归 / 非权威库守门 / 无 `text/csv` 服务端动态导出）；§7 pack invariant 行更新 710 → 720 链（knife 70 + knife 71） | diff |
| (2) 可选 `docs/53` 一句 | ✅ docs/53 两处：§5 预览清单 +第 7 项「各 overview 下载格 = JSON / CSV 双链」（含 4 同格 CSV 第二链 / 4 CSV 产物 63/60/71/21 行 / 生成器 `render_csv_bytes` 纯函数可字节重渲 / 列序=fixture 首行键序不重命名 / UTF-8 无 BOM / 页脚非权威库守门 / build 仍 ○ Static / 回执 `404`）；冒烟行 + §12i 门注记 | diff |
| (3) 显式非 O1/Gate PASS | ✅ 文首刷新行 + §1 守门句 + §6.2 状态列三处显式「CSV 是 fixture 快照确定性导出 (demo/candidate)，非权威库、非 O1/Gate PASS；仍不宣布 Gate 2 PASS」 | diff |
| (4) 回执 `407`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -c "404\|§12i\|gen_public_extracts_csv" docs/45-stage2-s210-lite-gate2-review-index-20260826.md   # ≥4 处登记
$ grep -n "CSV\|§12i" docs/53-stage2-public-ingest-ops-handbook-20260826.md                                # §5 第 7 项 + 冒烟注

$ python3 scripts/_knife71_manifest_bump.py
ADD: scripts/_knife71_manifest_bump.py (…)
ADD: reviews/.../407-…-receipt-20260826.md (…)
UPDATE artifact_count: 718 → 720
INVARIANT: sum(role_count)=720 == artifact_count=720 == len(artifacts)=720
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（+queue_rev 170 刷新行 + §1 回执链 404 段 + 守门句扩为含 CSV + §6.2 CSV 下载行 + §7 不变量链 720） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 +第 7 项 CSV 双链 + 冒烟 §12i 注） | 已入 manifest（SKIP） |
| `scripts/_knife71_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../407-stage0-cc-docs45-csv-download-refresh-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife71_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **718 → 720**；`sum(role_count) == artifact_count == len(artifacts) == 720`（docs/45 / docs/53 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 70 已落 710 → 718）。

## 红线自查

- ❌ 未改页面 / CSV 字节（docs only per §NOW；knife 70 的页面 + CSV 改动已在 `404`/`405` 闭环）
- ❌ 未谎称 CSV=权威库（三处显式「fixture 快照确定性导出 (demo/candidate)，非权威库」）
- ❌ 未删减 OPEN（§3/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（多处显式「仍不宣布 Gate 2 PASS」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 408）。