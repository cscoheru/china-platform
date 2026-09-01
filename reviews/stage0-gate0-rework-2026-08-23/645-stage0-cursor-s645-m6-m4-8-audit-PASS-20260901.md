# 645-stage0-cursor-s645-m6-m4-8-audit-PASS — 审验报告 (knife 645, 2026-09-01)

> **角色**: Cursor（审验端）
> **对象**: 645 M6 master + M4.8 v2 双刀 DELIVERED（handoff `645-stage0-cursor-handoff-summary-20260901.md`）
> **裁定**: **PASS（有限通过）** — 7 项 P3 发现，全部非红线、非阻塞
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线）

---

## §A. 审验执行记录（全部独立复跑，非采信回执）

| # | 审验点 | 方法 | 结果 |
|---|--------|------|------|
| A1 | 22/22 pytest | 独立复跑 `pytest tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v` | **22 passed in 1.75s**（Python 3.14.3 / pytest 9.0.2）✓ |
| A2 | 5 commits 链 | `git log --oneline -12` | `51569d7`(tasking) → `8fc0737`(rev75) → `a235f94`(delivery) → `0cc8952`+`73c74bc`(cc_head) → `0677111`(receipt) → `dffdea5`(backfill) → `6383da6`(DELIVERED entries) → `4f05f55`+`2b76850`(handoff 文档) ✓ |
| A3 | 双推 | `git rev-parse HEAD origin/main github/main` + `git branch -r --contains 6383da6` + 双 remote reflog | 三者同 = `2b76850`；origin/github 两份 reflog 均逐条记录 645 全部提交 `update by push`；`6383da6` 含于 origin/main + github/main ✓ |
| A4 | 工作区干净 | `git status -s` | 空 ✓ |
| A5 | delivery 范围 | `git show --stat a235f94` | 15 files / 1866 insertions，与 handoff §A.2 一致；**零前端/fixture 文件** ✓ |
| A6 | chain_id 区分 | 读 `scripts/seed_m4_8_policy_detail_real_v2.sql` 全文 | `real_645_m4_8_policy_detail_v2` 在；`real_644_m4_7_policy_detail` 不在；docs/68 §4 8 个 chain_id 全 distinct ✓ |
| A7 | UUID d≠c 段 | 同上 + grep | d0/d1-d6`eebc99`（d21-d94）在；`c1/c2eebc99` 零命中 ✓ |
| A8 | SHA drift | seed SQL + `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` | lineage 8 处 `source_file_sha256` 全用 645 实抓 SHA（hlj=`6237cd48...` 全 64 hex）；`bad8be51` 仅存在于 prose 注释，不入任何 lineage 值 ✓ |
| A9 | 32 INSERT / 14 语句 | SQL 全文人工计数 | 5 条多行 VALUES（registry/document/policy_document/target/measure ×4 行）+ 4 条 gc INSERT...SELECT + 1 条 cp ×4 行 + 4 条 pe INSERT...SELECT = **14 语句 / 32 行**，与测试正则断言（14 INSERT INTO；8 jsonb_build_object SHA）严丝合缝 ✓ |
| A10 | is_demo sentinel | SQL 全文 | 32 处 lineage 全 `is_demo:'false'`；`is_demo:'true'` 零命中 ✓ |
| A11 | 5 处互链 append-only | 逐文件读原文 + delivery diff（docs/45/50/53/66/67 各 +2 行） | docs/45:571（per 645）/ docs/50:239（§4.4 第48项）/ docs/53:222（§5 第48项 A-G）/ docs/66:166（→645 docs/68）/ docs/67:185（→645 docs/69）✓ 纯 append |
| A12 | EXEC-QUEUE rev75 | 读 §META/§CURRENT/§CHAIN_TAIL/§ACK | status DELIVERED；cc_head 尾 = `51569d7+a235f94+73c74bc+0677111`；last_delivery `a235f94`；last_receipt `0677111`；§CHAIN_TAIL 645 DELIVERED；§ACK 含 645 DELIVERED 条目 — 与 handoff §E 逐字段吻合 ✓ |
| A13 | 红线 12/12 | 上述全部 + 抽查 | 不宣布任何 PASS（15 里程碑）/ 无补零 / 无爬网超界（http_count=4/12，evidence fetch_log 4×HTTP 200）/ 不写 cegr.*（delivery 无 DB 对象）/ geo_entity 用 SELECT 复用 M2-a / ON CONFLICT 幂等 ✓ |
| A14 | 轮询状态 | `dual_poll_status.sh` | HEAD=ORIGIN=`2b76850`；KNIFE=645；`CURSOR_ACTION=AUDIT_NOW`（本报告即响应）✓ |

## §B. handoff §H 四问裁定

1. **认可** 645 全链路：5 提交 + 后续 2 提交（`4f05f55`/`2b76850` = handoff 文档自身）全部双推完成。
2. **认可** chain_id 区分（`_v2` 末段 + 8 chain_id 全 distinct）与 UUID d 段 ≠ 644 c 段（含 e 段预留可扩展）。
3. **认可** hlj SHA drift 处理：seed SQL 用 645 实抓 `6237cd48`，不沿用 644 stale `bad8be51`，符合 docs/52 (a) 更新路；drift 不影响 `is_demo='false'` 判定。
4. **认可 646 scope A**（M6 收口延续 + M4.9 v3 扩展 + docs/52 B 路 live-candidate 探测），附加本报告 §C 修正项，详见 `646-stage0-architect-m4-9-v3-o1-live-candidate-tasking-20260901.md`。

## §C. P3 发现（7 项，非阻塞；646-A.0 顺带修正）

| # | 发现 | 位置 | 处置 |
|---|------|------|------|
| F1 | "7 个 distinct chain_id" 计数错（表列 8 行、测试断言 8） | docs/68 §4 尾行；docs/50 §4.4 第48项；docs/53 §5 第48项 | 646 行内 append 尾注更正为 8 |
| F2 | 638 行 §2 标 chain_id "n/a (probe only)" vs §4 列 `real_638_m4_1_people` 自相矛盾 | docs/68 §2 vs §4 | 646 尾注统一口径（§4 计 8、§2 备注 probe 刀无独立 spike 边界） |
| F3 | §CHAIN_TAIL 645 DELIVERED 行 prose 仍写 "4 新真实 SHA bad8be51/... 复用 644 SHA"（tasking 时旧文，与实交付 `6237cd48` drift 矛盾；§ACK 条目本身正确） | 00-EXEC-QUEUE §CHAIN_TAIL | 不改既有行（红线）；以本审计报告为准登记 |
| F4 | "12/12 pytest green planned" 未刷新为实交付 22/22 | docs/50 §4.4 第48项；docs/53 §5 第48项 | 646 行内 append 尾注 |
| F5 | **docs/00-COMPASS.md 滞后 10 刀**（NOW 仍 635/M2-c+d+e、COVERED 5/31，EXEC-QUEUE 已 rev75/645 DELIVERED/635 已 31/31 AUDITED） | docs/00-COMPASS.md | **本审计顺带已刷新**（见同 commit） |
| F6 | 计数/拼写 cosmetic：handoff 称回执 175 行实 174；seed SQL 头注释 "is demo" 少下划线（L5） | handoff §A.2 / seed SQL L5 | 免修（登记即可；seed SQL 注释不动） |
| F7 | henan-zwgk 样本 evidence `publication_date=2026-08-20` vs seed SQL policy_document `2026-08-30` | evidence JSON cell vs seed SQL | 646 尾注登记（SHA/大小一致，纯元数据日期） |

## §D. 观察（沿用既有模式，无需处置）

- commitment_progress `progress_value=0.5` 为 641-645 一贯 spike 标记值（非 KPI 补零；domain 值全 NULL 透明占位）。
- 全套 `pytest tests/` 在本机审验时段挂起（疑似个别用例等网络/DB），与 645 交付无关；645 守门以 22 例定向套件为准（D.1 口径）。

## §E. 结论

**645 = PASS（有限通过，零红线违反）**。M6 master + M4.8 v2 双交付成立；下一刀 **646 tasking OPEN**（scope A + §C 修正项），等执行端/架构师自交付。

— End 645 audit PASS 20260901 —
