# 656 审计 + 657 任务书 合并件（knife 656 AUDIT / knife 657 TASKING, 2026-09-02）

> **刀号**: 656（PART 1 审计）/ 657（PART 2 任务书）
> **角色**: Cursor 审验端（架构师审计 + 签发）
> **日期**: 2026-09-02
> **前置**: 656 DELIVERED+C 完成（rev98; 7 commits `4f08bed→7a9968d`）+ U6 用户裁定登记（`1e3ec9d`; docs/81 + docs/54 §8; 红黑统计公报库接受为 M2/M3 observation 源, 含金丝雀守门）
> **本件模式**: 单文件（PART 1 审计 + PART 2 任务书; 沿用 654/655 合并件模式）

---

# PART 1 — 656 审计（M4.19 v13 GUANGXI+HAINAN 华南双省对 + 656-A.2 O-1 根因修复）

## §0. 裁定（定案）

**PASS（有限通过）** — 0×P3 + **1×P4**（§NOW 尾段残留陈旧中间态完成清单〔"待 5+6+7 收口 + 双推 + 三 ref 全等"——而 C.5/C.6/C.7〔`ec60cdc/80ca9e8/7a9968d`〕实际已全部完成且三 ref 已全等; 655 P4-1 同类**新位置**变体: 不在 tasking 行/status 行而在 §NOW 尾段完成清单行; v3.2 首签刀即同类复发〕）→ **rev99 修正**（§NOW 整段刷新为 657 终态, 残留随段消除 ✓）+ **规范 v3.3**（§NOW 尾段完成清单终态化; 见 PART 2 §1.657-A.0）。

**656-A.2 O-1 根因修复 = 验证通过（机制保障实锤）**: 审验端独立复跑 16 文件集**两遍**, `docs/reports/m2_2024_gdp_crosscheck_20260831.md` git diff **零漂移×2**（run1=0 / run2=0; 树净）——防线从"人工还原"正式升级为"机制保障"（crosscheck 脚本 `--output tmp_path` + tracked 报告 SHA 零漂移断言锁定, `tests/test_m2_report_hygiene.py` 10 cases 含 5 新只读化锁定）。**O-1 三次复发链路就此封死（待 657+ 回归持续验证）。**

## §A. 审计复现矩阵（独立复跑, 2026-09-02 本机）

| # | 项 | 结果 | 判 |
|---|---|---|---|
| A1 | pytest 16 文件集（test_m4_19 + 15 回归）run1 | **273 passed in 1.74s**（= 25 新 m4_19 + 5 新 hygiene 锁定 + 243 回归; ≥253 达成 +7.9%, 底限 ≥249 超 9.6%） | ✓ |
| A2 | 同集 run2 | **273 passed in 1.41s**（两遍同数零漂移） | ✓ |
| A3 | **O-1 验证: 连跑两遍 m2 零 diff×2** | run1 diff=0 / run2 diff=0 / git status 树净 | **✓ 机制修复实锤** |
| A4 | 主 evidence JSON 实证 | guangxi `BLOCKED_NO_POOL`（file_hash 空 + actual_province null）+ hainan `REACHABLE` SHA=`83a13d18…87938`; `http_count=3` `blocked_no_pool_count=1` `substitute_used_count=0` | ✓ |
| A5 | seed SQL 实证 | **8 INSERT**（HAINAN 1 样本 × 8 表）; GUANGXI 0 INSERT 留痕; UUID **o 段** 7 unique（o0-o6; 655 n 段同构形态; tests UUID 守门 25/25 过）; `real_656_m4_19_policy_detail_v13` 三文件一致 | ✓ |
| A6 | git 链 | 7 commits `4f08bed→7a9968d` 三 ref 全等 + U6 登记 `1e3ec9d` 叠加干净（2 files; 零执行端文件卷入） | ✓ |
| A7 | 七字段原子 rev98 | header line 3 rev98 ✓ / §META 五字段（rev / status 零 SHA / last_audit / tasking / last_delivery `4f08bed` / last_receipt `2613e2a`）✓ / §CHAIN_TAIL 同步 ✓ | ✓ |
| A8 | 交付面文件 | 8 文件全在（fetch/seed/docs 80/reports/evidence/tests ×2/receipt 13 节） | ✓ |

## §P. 问题清单

| 级 | 数 | 内容 | 处置 |
|---|---|---|---|
| P3 | 0 | — | — |
| P4 | 1 | **§NOW 尾段陈旧中间态完成清单**: "4 commits … 已完成, **待 5+6+7 收口〔§NOW 五字段原子同步 + amend-first + 链补终同步〕+ 双推 + 三 ref 全等**"——写于 4/7 时点, C.5/C.6/C.7 完成后未同 commit 刷新; v3.2"中间态零残留"在 §NOW **尾段完成清单行**未覆盖到位（655 P4-1 在 tasking 行/§NOW 首段, 本刀移位尾段——同类第三型） | rev99 §NOW 整段刷新（残留随段消除 ✓）; **规范 v3.3** 固化（PART 2 §1.657-A.0） |
| N-1 | 注记 | §META ruling 行 + §NOW 首段两处「进行中 4/7 / 待 commit / 待 user 授权」= **655 P4-1 历史引用**（引号内描述 655 审计发现）, 非活动中间态, 不记违例; v3.3 起历史引述加「〔655-P4-1 引述〕」标记防 grep 误报 | 无需修正 |

## §RED. 红线 14 项复核（656）

1 不补零 ✓（GUANGXI 0 INSERT 按实报留痕）/ 2 不静默硬编码 ✓ / 3 不爬网 ✓（HTTP 3/12 = 25%）/ 4 不改既有 docs ✓（docs/79 零改动; docs/81 为本端 U6 新建非 656 改动）/ 5 SHA 全等 ✓（NEW 1 枚; fixture 4 锁值未碰）/ 6 数据源政府自取 ✓（本刀未涉 hongheiku; U6 属用户裁定例外, 657 起挂金丝雀守门）/ 7 lineage 全行 ✓（retry_of=N/A 双首试省）/ 8 中间产物本地 ✓ / 9 三重留痕 ✓（evidence/docs 80 §2/receipt）/ 10 回执 13 节 ✓ / 11 spike 真 SHA 不入库 ✓（红线 11 沿用）/ 12 m2 报告零 diff ✓✓（**机制保障首验**）/ 13 gate 不自动宣布 ✓（24 里程碑不宣布）/ 14 BLOCKED_NO_POOL 留痕 ✓（GUANGXI 首试省首触发第四例, [EXHAUSTED] 不可代换, 留痕不代换）。

## §VERDICT

- ☑ **PASS（有限通过）**【定案 2026-09-02】— 656 链路实交付、可复跑、可追溯: 16 文件集 **273/273 两遍独立复跑 green**; **O-1 机制修复实锤（m2 零 diff×2）**; 混合态 PARTIAL_BLOCKED 第二例（HAINAN REACHABLE + GUANGXI SSL `error:1404B458 tlsv1 unrecognized name` 第四例首见失败形式）; 8 INSERT; HTTP 3/12; 7 commits 三 ref 全等; **1×P4**（§NOW 尾段中间态残留）→ rev99 修正 + 规范 v3.3。
- **已用省（REACHABLE actual）**: 20 + 3 BLOCKED 留痕; 剩余未试省 **2（HEBEI/SHANXI）→ 657 全国 31 省收官**。

---

# PART 2 — 657 任务书（M4.20 v14 HEBEI+SHANXI 全国收官 + 657-A U6 金丝雀 spike）

## §1.657 主体: M4.20 v14 HEBEI+SHANXI（第 27/28 样本, 全国 31 省收官刀）

- **对象**: HEBEI（河北, `www.hebei.gov.cn`）+ SHANXI（山西, `www.shanxi.gov.cn`）——全国 31 省 spike 链**收官刀**; 双首试省 retry_of=N/A
- **chain_id**: `real_657_m4_20_policy_detail_v14`; **UUID p 段**（沿 o 段模式递增）
- **产物**（v13 模式全沿）: `scripts/fetch_m4_20_policy_detail_v14_2024.py` + `scripts/seed_m4_20_policy_detail_real_v14.sql` + `evidence_pack/m4_20_policy_detail_real_v14_20260902.json` + **`docs/82-m4-20-policy-detail-real-v14-20260902.md`**（§1-§6; **81 已被 U6 ruling 占用, 必用 82**）+ `docs/reports/m4_20_policy_detail_real_v14_20260902.md` + `tests/test_m4_20_policy_detail_real_v14.py` ≥25 cases + receipt
- **HTTP 预算**: ≤12（双省 × 两级 fallback）; 三态合法沿用; 递补池 [EXHAUSTED] 沿用
- **收官叙事**: docs/82 §1 落定表 = **全国 31 省总对账表**（actual_province 口径: spike 链 R/B + M2 5 主体 + 剩余省状态; 差额列 BLOCKED 留痕省）

## §1.657-A: U6 金丝雀 spike（用户裁定 2026-09-02; docs/81 §3 守门）

- **对象**: `tjgb.hongheiku.com`（红黑统计公报库, 站内转载库, **非 .gov.cn 域本机实测可达**）× 5 金丝雀省 = **北京 / 上海 / 山东 / 湖北 / 四川**（库内已有官方 observation 的 5 主体）
- **步骤**: ① 定位 5 省 2024 公报文章 URL（tag 页模式实测: `https://tjgb.hongheiku.com/tag/{省名URL编码}` → 「2024 年 XX 省国民经济和社会发展统计公报」; 江苏样例 `/sjtjgb/57215.html` 已验）② fetch 5 文章页（限速 sleep ≥1s）③ 提取: GDP 总量(亿元) + 增速(%) + 一/二/三产增加值(亿元) ④ 与库内 M2 官方 observation 逐值比对（GDP 总量为主锚; 三次产业库内有则比对、无则登记 658 批量候选）⑤ 产出 5/5 比对表
- **HTTP 预算**: **≤10**（5 tag + 5 article）; **总预算 = 主体 ≤12 + 金丝雀 ≤10 = ≤22**
- **verdict 三态**: `CANARY_PASS`（5/5 一致 → **658 批量授权解锁, 26 省 + 三次产业**）/ `CANARY_FAIL`（≥1 不一致 → **停批量, 回报用户复裁**）/ `CANARY_UNREACHABLE`（站点不可达 → 停, 回报复裁）
- **产物**: `evidence_pack/u6_canary_5province_20260902.json`（每省: url/sha256/bytes/gdp_total/gdp_growth/primary/secondary/tertiary/库内官方值/一致位/mismatch_detail）+ `docs/reports/u6_canary_5province_20260902.md`（5/5 表 + lineage 三重标注预演: `source='hongheiku_tjgb' + origin='XX省统计局' + ruling='U6 2026-09-02'`）+ `tests/test_u6_canary.py` ≥5 cases（evidence schema / 5 省齐 / SHA 锁转载字节 / lineage 字段 / verdict 守门）
- **红线（U6 §5 附加五条）**: ① 金丝雀阶段**不 INSERT observation 表**（只 evidence + report; 入库留 658 批量刀）② SHA 锁 hongheiku 转载字节并如实标注（非官方字节）③ 不绕过任何反爬（本域无 WAF 无需绕过）④ docs/81 既有正文零改动（红线 4）⑤ CANARY_FAIL 时**禁止**部分采信

## §1.657-A.0: 规范 v3.3（§NOW 尾段完成清单终态化）

- ✓ 沿用 v3.1 七字段原子 + v3.2 status 零 SHA / 中间态零残留
- ✓ **新增**: 零残留范围明确 = **§NOW 全段含尾段完成清单行**——任何「待 N/M 收口」「待 X+Y+Z」清单式文本, 对应 C.x 全部落地后必须**同 commit** 刷新为终态句; 历史引述加「〔655-P4-1 引述〕」标记防误报（656 审计 N-1）

## §657-B. 测试与复现口径

- 16 文件集 273 回归 + `test_m4_20` ≥25 + `test_u6_canary` ≥5 = **≥303 green（底限 ≥298）**
- **连跑两遍 m2 零 diff×2 沿用**（656-A.2 机制回归验证）
- 审计复跑按 18 文件集（16 + test_m4_20 + test_u6_canary）

## §657-C. 链与收口

- 七字段原子 rev99→rev100; amend-first 沿用; receipt 13 节模式; backfill 完整性三齐; 双推三 ref 全等
- §NOW 尾段完成清单按 v3.3 终态化（本刀首签）

## §657-D. 红线

红线 1-14 全沿用 + U6 §5 附加五条（§1.657-A）; 24 里程碑不宣布; O1 仍 OPEN 零动作。

---

— End 656 审计 + 657 任务书 20260902 —

