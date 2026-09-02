# 657 审计 + 658 任务书 合并件（knife 657 AUDIT / knife 658 TASKING, 2026-09-02）

> **刀号**: 657（PART 1 审计）/ 658（PART 2 任务书）
> **角色**: Cursor 审验端（架构师审计 + 签发）
> **日期**: 2026-09-02
> **前置**: 657 DELIVERED+C 完成（rev100; 6 commits `dfceab9→e7f6ce6` 三 ref 全等）+ U6 金丝雀 CANARY_PASS（5/5 delta=0）
> **本件模式**: 单文件（PART 1 审计 + PART 2 任务书）

---

# PART 1 — 657 审计（M4.20 v14 HEBEI+SHANXI 收官 + 657-A U6 金丝雀）

## §0. 裁定（定案）

**PASS（有限通过）** — **1×P3 + 2×P4**（P3-1: docs/82 §1.2 全国总对账表系统性账目错误〔刀号错配 ≥4 处 + NINGXIA 错置"待 658+"〔实为 655 已 BLOCKED 留痕〕+ TIBET 重复行 + GANSU/QINGHAI/SHANDONG/HUBEI 缺行 + "剩余 9 省+特殊行政"虚构 + 22/23/25 计数自相矛盾——**真实账 = 25 spike REACHABLE + 4 spike BLOCKED + 2 M2-only〔京/沪〕= 31/31 全落定, 收官实际达成**; P4-1: §META `last_delivery` 漏更〔仍 4f08bed/656, 应 dfceab9/657——七字段原子漏更第三例, 类比 654 header/CHAIN_TAIL〕; P4-2: 金丝雀 HTTP 超预算 12/10〔+2, tag 路径假设 404×5 绕道; 已自报 + 失败形式第 5 例 TAG_PATH_ASSUMPTION_ERROR 登记〕）→ **rev101 修正 P4-1（本端）+ 658 内修正 P3-1（行内更正 per 650/651 先例）+ 规范 v3.4（§META 五字段与链对账自检）**。

**U6 金丝雀 CANARY_PASS 独立验证 ✓**: evidence 逐字段核验 5 省 × 5 字段（GDP 总量+增速+一产+二产+三产）**全 delta=0.0 match=True**（京 49843.1 / 沪 53926.71 / 鲁 98565.8 / 鄂 60012.97 / 川 64697.0 + 三次产业全值）——hongheiku 转载与库内官方字节全等。**→ 658 批量授权解锁（26 省 + 三次产业, per U6 + 用户 2026-09-02 指令）。**

## §A. 审计复现矩阵（独立复跑, 2026-09-02 本机）

| # | 项 | 结果 | 判 |
|---|---|---|---|
| A1 | pytest 18 文件集（test_m4_20 27 + test_u6_canary 11 + 16 回归）run1 | **311 passed in 2.03s**（= 27 + 11 + 273; ≥303 达成 +2.6%, 底限 ≥298 超 4.4%） | ✓ |
| A2 | 同集 run2 | **311 passed in 1.51s**（两遍同数） | ✓ |
| A3 | O-1 机制回归: m2 零 diff×2 | run1=0 / run2=0 / 树净 | ✓ |
| A4 | 金丝雀 evidence 逐字段核验 | 5 省 × 5 字段 delta=0.0 match=True 全等; SHA 5 枚锁定（bac6101c/68d7f2c9/e52b07cd/4c70e3cf/afce7e74）; overall=CANARY_PASS | ✓ |
| A5 | m4_20 evidence | HEBEI+SHANXI 双 REACHABLE（SHA 508824f8 + 29dbf293）; http_count=4/12; 16 INSERT（2 样本 × 8 表）双 R 口径 ✓ | ✓ |
| A6 | git 链 | 6 commits `dfceab9→e7f6ce6` 三 ref 全等; rev100 v3.3 首签 §NOW 零中间态残留 ✓ | ✓ |
| A7 | 七字段原子 rev100 | header ✓ / rev ✓ / status 零 SHA ✓ / last_audit ✓ / tasking ✓ / last_receipt bcd3cc2 ✓ / **last_delivery ✗（漏更 → P4-1）** | 6/7 |
| A8 | 交付面文件 | 10 文件全在（fetch/seed/docs 82/reports ×2/evidence ×2/tests ×2/receipt 13 节） | ✓ |

## §P. 问题清单

| 级 | 数 | 内容 | 处置 |
|---|---|---|---|
| P3 | 1 | **docs/82 §1.2 总对账表系统性错误**: ① 刀号错配 ≥4 处（表称 651=辽/吉/黔〔三省!〕、652=江苏、654=陕/川、655=新/蒙/藏——链内 commit 实证 **651=SHAANXI/SICHUAN、652=XINJIANG/NEI_MENGGU**）② NINGXIA 错置"待 658+ TBD"（实为 655 BLOCKED 已留痕）③ TIBET 与 XIZANG 重复行 ④ GANSU/QINGHAI（654 双 B）/SHANDONG/HUBEI（647/649 R + 653 复试 B）缺行 ⑤ "剩余 9 省+海南三沙特殊行政待 658+"虚构——**真相 = 31/31 全落定（25 spike R + 4 spike B + 2 M2-only 京/沪）, 收官叙事实际成立但表格把它写破了** ⑥ "22/31（21→23）"计数自相矛盾（§1.2 内 22 vs §1.3 内 21→23 vs 真值 25） | **658 内修正**: §1.2 重写 31 行全对账（29 spike 行真刀号 + 2 M2-only 行）+ §5 计数更正 + 删虚构行（红线 4 事实错误行内更正例外 per 650 P4×2 / 651 P3-1 先例） |
| P4 | 1 | **§META last_delivery 漏更**: 仍 `4f08bed`（656）, 应 `dfceab9`（657）——七字段原子漏更第三例（654 header/CHAIN_TAIL → 本次 last_delivery） | rev101 本端修正 ✓ + **规范 v3.4**（PART 2 §1.658-A.0） |
| P4 | 1 | **金丝雀 HTTP 超预算 12/10（+2）**: tag 路径假设 `/tag/{省名}` 404×5 → 绕道 `/` + `/category/sjtjgb` + 直链; 已自报（http_overrun_reason 字段）+ 失败形式第 5 例 TAG_PATH_ASSUMPTION_ERROR 登记（不入主库, 记 U6 审计） | 658 固化 category-first URL 发现模式（索引已验 145 篇）; 预算放宽按 658 任务书 |
| N-1 | 注记 | docs/82 节号 5 vs 任务书"§1-§6"——§6（下一步+不宣称）内容并入 §5 收官叙事, 内容齐备不缺项; 不构成问题 | 无需修正 |

## §RED. 红线复核（657）

1 不补零 ✓（16 INSERT 双 R 按实报）/ 2 不静默硬编码 ✓ / 3 不爬网 ✓（主 spike HTTP 4/12; 金丝雀 12/10 超支已自报 P4-2）/ 4 不改既有 docs ✓（docs/80/81 零改动; docs/82 新建——§1.2 错误属新建文件内容错误非改动, 记 P3）/ 5 SHA 全等 ✓（2 NEW + 5 金丝雀锁）/ 6 数据源 ✓（主 spike 政府门户; 金丝雀 hongheiku per U6 用户裁定 + 守门全过）/ 7 lineage ✓（retry_of=N/A 双首试 + 金丝雀三重标注模板）/ 8 本地 ✓ / 9 三重留痕 ✓ / 10 回执 13 节 ✓ / 11 spike 蓝 本不入库 ✓（金丝雀不 INSERT observation 遵守）/ 12 m2 零 diff ✓✓ / 13 不自动宣布 ✓（24 里程碑）/ 14 BLOCKED 留痕 ✓（本刀无 BLOCKED; 池 EXHAUSTED 沿用）+ U6 §5 附加五条全 ✓（docs/81 零改动 ✓）。

## §VERDICT

- ☑ **PASS（有限通过）**【定案 2026-09-02】— 18 文件集 **311/311 两遍复跑** + m2 零 diff×2 + **金丝雀 CANARY_PASS 独立逐字段验证**（U6 批量解锁）+ 双 REACHABLE 收官（31/31 实际达成）; **1×P3 + 2×P4** → 658 内修正 P3-1 + rev101 修 P4-1 + 规范 v3.4。
- **658 = M2 批量刀**（26 省 + 三次产业真实入库）——页面真实化倒数第二刀（659 = mart flip + 前端切源）。

---

# PART 2 — 658 任务书（M2 批量补齐 26 省 + 三次产业 via U6〔金丝雀已过〕+ P3-1 修正）

## §1.658 主体: M2.1+M2.2 批量真实入库（26 省 × 5 指标）

- **授权链**: U6 用户裁定（docs/81）→ 657-A 金丝雀 CANARY_PASS 5/5 → 用户指令"5/5 一致即批量补 26 省 + 三次产业，全自动化"
- **对象**: 26 省（31 − 5 主体〔京/沪/鲁/鄂/川已有官方 observation〕）2024 年《国民经济和社会发展统计公报》hongheiku 转载页
- **提取**: 每省 GDP 总量(亿元) + 增速(%) + 一产/二产/三产增加值(亿元) = 5 指标/省
- **URL 发现（category-first, 金丝雀教训固化）**: `/category/sjtjgb` 索引页（1 req, 已验 108KB/145 篇含各省 2024 文章）→ 26 省直链; **禁止再走 /tag/ 路径**（第 5 例失败形式）
- **HTTP 预算**: **≤32**（1 索引 + 26 文章 + ≤5 探查/retry）; 限速 sleep ≥1s; 不绕反爬
- **INSERT（真实入库; 红线 11 为 spike 蓝本线, observation 表为数据表不适用）**: 26 省 observation 行（5 指标/省）+ source_registry 行（`source='hongheiku_tjgb'` + `origin='XX省统计局'` + `ruling='U6 2026-09-02'` + note 转载字节非官方字节, 金丝雀 5/5 验证）; **某省缺页/缺值 → BLOCKED 留痕 missing_reason 禁补零; 三次产业单值缺 → NULL + missing_reason, 不影响该省 GDP 总量入库**
- **SHA**: 26 文章页字节全锁; lineage 三重标注全行

## §1.658-A.1: 国家锚 + 自洽双核对

- **国家锚**: 31 省 GDP 加总 vs NBS 国家公报 **1,349,084.0 亿元**——差值登记说明（省级汇总 vs 国家核算口径差, 历史上约 ±2-3%）
- **省内自洽**: 每省 一产+二产+三产 ≈ GDP 总量（容差 ≤0.5% 登记; 超差该省标 QUARANTINED 待复核）

## §1.658-A.2: P3-1 修正（docs/82 §1.2 重写）

- §1.2 重写为 **31 行全对账**: 29 spike 行（**25 REACHABLE + 4 BLOCKED**, 刀号按链实证逐一核: 651=SHAANXI/SICHUAN, 652=XINJIANG/NEI_MENGGU, 653=SHANDONG/HUBEI 复试 B〔retry 647/649 R〕, 654=GANSU/QINGHAI B, 655=NINGXIA B/XIZANG R, 656=GUANGXI B/HAINAN R, 657=HEBEI/SHANXI R, 642-650 各省按链补正）+ 2 M2-only 行（BEIJING/SHANGHAI, M2-c/d/e 刀号）
- §5 计数更正: 删"剩余 9 省+特殊行政/TIBET 补充"虚构行; 终态句 = **31/31 全落定（25R+4B+2M2）**
- 红线 4 例外依据: 650 P4×2 / 651 P3-1 行内更正先例（事实错误必须修正, 修正注记行内标〔658-A.2 P3-1 更正〕）

## §1.658-A.3: M2.3 跨源覆盖升级评估

- 复跑 m2 crosscheck（**--output tmp_path 只读模式**, 红线 12）→ 31/31 覆盖报告
- QUARANTINED-WEAK → 升级评估登记（5 官方 + 26 hongheiku 金丝雀锚定; **不宣称 M2 PASS**）

## §1.658-A.0: 规范 v3.4（§META 五字段与链对账自检）

- ✓ 沿用 v3.1/v3.2/v3.3 全条款
- ✓ **新增**: 每个 C.x 收口 commit 前, §META 五字段（status/last_audit/tasking/last_delivery/last_receipt）**逐一对链核验**（last_delivery = 本刀 delivery SHA, last_receipt = 本刀 receipt SHA）; 657 P4-1（last_delivery 漏更第三例）杜绝

## §658-B. 测试与复现口径

- 18 文件集 311 回归 + `test_u6_batch_26prov` ≥15（26 省齐/SHA 锁/lineage 三重/缺省 BLOCKED 口径/国家锚容差/自洽容差/不补零/P3-1 修正守门〔docs/82 §1.2 31 行 + 真刀号〕/observation INSERT 数/registry 行/source 口径）= **≥326 green（底限 ≥316）**
- 连跑两遍 m2 零 diff×2 沿用; 审计按 19 文件集（+test_u6_batch_26prov）

## §658-C. 产物与链

- `scripts/fetch_m2_u6_batch_26prov_2024.py` + `scripts/seed_m2_u6_batch_26prov.sql` + `evidence_pack/u6_batch_26prov_fetch_20260902.json` + `evidence_pack/u6_batch_26prov_anchor_20260902.json`（国家锚+自洽）+ **`docs/83-m2-u6-batch-26prov-20260902.md`** + `docs/reports/u6_batch_26prov_20260902.md` + tests + receipt 13 节
- 七字段原子 rev101→rev102; v3.4 首签; amend-first 沿用; 双推三 ref 全等

## §658-D. 红线

红线 1-14 沿用 + U6 §5 五条（SHA 锁转载字节/lineage 三重/不绕反爬/docs/81 零改动/缺省禁部分采信→整省 BLOCKED）; **24 里程碑不宣布; O1 仍 OPEN 零动作**; 既有 registry 行 SHA 零漂移; 4 fixture 锁值零触碰。

---

— End 657 审计 + 658 任务书 20260902 —

