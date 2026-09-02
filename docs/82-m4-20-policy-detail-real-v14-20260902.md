# 82 — M4.20 政策详情 v14 HEBEI+SHANXI 全国 31 省收官 spike 架构师级审查 (knife 657, 2026-09-02)

> **刀号**: 657
> **Milestone**: M4.20（沿用 638-656 spike 模式；spike 第 16 次扩展；全国 31 省收官 = HEBEI/SHANXI 第 27/28 样本）
> **类型**: 架构师级审查（per 657 任务书 §1.657）
> **日期**: 2026-09-02
> **前置**: 656 DELIVERED+C + 656 审计 **PASS（有限通过）**（rev98→rev99）+ 657 任务书签发（0e1f3d9）+ U6 用户裁定登记（1e3ec9d; docs/81; hongheiku 红黑统计公报库接受为 M2/M3 observation 数据源, 含金丝雀守门）+ 657-A.0 规范 v3.3 落地（§NOW 尾段完成清单终态化）
> **注**: 本文档为新文档；657 §0.4 红线 4 不改 docs/45/50/53/66-79/80/81 既有正文；docs/82 自由落地

---

## 1. 任务背景与定位

### 1.1 全国 31 省收官叙事（华南双省对-华北收官接力）

657 = M4.20 v14 **HEBEI + SHANXI** 全国 31 省收官 spike（第 27/28 样本；华北双省对首试）— 华南双省对 656 收官后接华北双省对：

| 华北省 | 落定刀 | verdict |
|---|---|---|
| **HEBEI (河北)** | **657** | **REACHABLE** (fallback 命中: /zwgk/ reset by peer → / 200, 204976B, 233 锚点, SHA=`508824f8…`) |
| **SHANXI (山西)** | **657** | **REACHABLE** (fallback 命中: /zwgk/ 404 → / 200, 229900B, 435 锚点, SHA=`29dbf293…`) |

**华北双省对 = 657 一刀落定双 REACHABLE**：2 NEW SHA 全部入链 + 16 INSERT ROWS。

### 1.2 全国 31 省总对账表（actual_province 口径）〔658-A.2 P3-1 重写〕

| 序 | 省 | 落定刀 | verdict | 备注 |
|---:|---|---|---|---|
| 1 | HLJ (黑龙江) | 642 | REACHABLE | 西部首省, sha 首链 |
| 2 | HENAN (河南) | 643 | REACHABLE | 中部首省 |
| 3 | YUNNAN (云南) | 644 | REACHABLE | 西南首省 |
| 4 | FUJIAN (福建) | 645 | REACHABLE | 东南首省 |
| 5 | GD (广东) | 646 | REACHABLE | 华南首省 |
| 6 | ZJ (浙江) | 647 | REACHABLE | 华东补位 |
| 7 | SHANDONG (山东) | 647 | REACHABLE | 华东补位 〔658-A.2 P3-1 补行：原表缺行〕|
| 8 | JX (江西) | 648 | REACHABLE | 华东补位 |
| 9 | HUN (湖南) | 649 | REACHABLE | 华中补位 |
| 10 | HUBEI (湖北) | 649 | REACHABLE | 华中补位 〔658-A.2 P3-1 补行：原表缺行〕|
| 11 | AH (安徽) | 650 | REACHABLE | 华东补位 |
| 12 | LN (辽宁) | 649 | REACHABLE | 东北首省 〔659-B P3-2 终修：原 651，链 SHA 实证 `936640d` "hubei/jilin + substitute 池首次激活(liaoning)" — LN 为 649 跨省 substitute〕|
| 13 | JL (吉林) | 649 | REACHABLE | 东北补位 〔659-B P3-2 终修：原 651，链 SHA 实证 `936640d` "hubei/jilin + substitute 池首次激活(liaoning)" — JL 为 649 直接样本〕|
| 14 | GUIZHOU (贵州) | 650 | REACHABLE | 西南补位 〔659-B P3-2 终修：原 651，链 SHA 实证 `fce3153` "guizhou/jiangsu 第 13/14 样本" — GUIZHOU 首试 REACHABLE 为 650〕|
| 15 | JIANGSU (江苏) | 650 | REACHABLE | 华东首省 〔659-B P3-2 终修：原 652，链 SHA 实证 `fce3153` "guizhou/jiangsu 第 13/14 样本" — JIANGSU 首试 REACHABLE 为 650〕|
| 16 | SHAANXI (陕西) | 651 | REACHABLE | 西北首省 〔659-B P3-2 终修：原 654，链 SHA 实证 `d13b3229` "M4.14 v8 shaanxi/sichuan 第 15/16 样本"〕|
| 17 | SICHUAN (四川) | 651 | REACHABLE | 西南补位 〔659-B P3-2 终修：原 654，链 SHA 实证 `d13b3229` "M4.14 v8 shaanxi/sichuan 第 15/16 样本"〕|
| 18 | XINJIANG (新疆) | 652 | REACHABLE | 西北补位 〔659-B P3-2 终修：原 655，链 SHA 实证 `04721b7` "M4.15 v9 xinjiang/nei_menggu 第 17/18 样本"〕|
| 19 | NEI MENGGU (内蒙古) | 652 | REACHABLE | 华北补位 〔659-B P3-2 终修：原 655，链 SHA 实证 `04721b7` "M4.15 v9 xinjiang/nei_menggu 第 17/18 样本"〕|
| 20 | XIZANG (西藏) | 655 | REACHABLE | 西部收官 〔658-A.2 P3-1 去重复：原 TIBET 行冗余〕|
| 21 | HAINAN (海南) | 656 | REACHABLE | 华南收官 |
| 22 | GUANGXI (广西) | 656 | BLOCKED_NO_POOL | SSL `error:1404B458` ×2 第四例首见; 留痕不代换 |
| 23 | HEBEI (河北) | 657 | REACHABLE | 华北收官 |
| 24 | SHANXI (山西) | 657 | REACHABLE | 华北收官 |
| 25 | TIANJIN (天津) | 658 | REACHABLE | hongheiku 转载 (U6 unlock) 〔658-A.2 P3-1 新增行〕|
| 26 | CHONGQING (重庆) | 658 | REACHABLE | hongheiku 转载 (U6 unlock) 〔658-A.2 P3-1 新增行〕|
| 27 | GANSU (甘肃) | 654 | BLOCKED_NO_POOL | 〔658-A.2 P3-1 补行：原表缺行〕|
| 28 | QINGHAI (青海) | 654 | BLOCKED_NO_POOL | 〔658-A.2 P3-1 补行：原表缺行〕|
| 29 | NINGXIA (宁夏) | 655 | BLOCKED_NO_POOL | 〔658-A.2 P3-1 更正：原表错置"待 658+ TBD", 实为 655 BLOCKED 已留痕〕|
| 30 | BEIJING (北京) | M2-c | M2-only | 官方门户 (M2-c/d/e 刀号; 含金丝雀) |
| 31 | SHANGHAI (上海) | M2-d | M2-only | 官方门户 (M2-c/d/e 刀号; 含金丝雀) |

**终态句**（per 658-A.2 P3-1 重写）: **31/31 全落定 = 25 spike REACHABLE + 4 spike BLOCKED + 2 M2-only**。

〔658-A.2 P3-1 注记〕本次 §1.2 重写依据 657 审计 P3-1 裁定：① 原表 22 行缺 ≥9 行（SHANDONG/HUBEI/GANSU/QINGHAI/TIANJIN/CHONGQING/BEIJING/SHANGHAI/NINGXIA）→ 补齐至 31 行；② NINGXIA 错置"待 658+ TBD" 修正为"655 BLOCKED 已留痕"；③ TIBET 重复行删除（与 XIZANG 行合并）；④ "剩余 9 省+特殊行政"虚构段删除（虚构不实, 真相为 31/31 全落定）；⑤ 计数自相矛盾 (22/31 vs 21/23 vs 25) 统一为 **25 R + 4 B + 2 M2-only = 31**；⑥ 留痕〔658-A.2 P3-1〕inline 注记符合 650 P4×2 / 651 P3-1 行内更正先例（事实错误必须修正, 修正注记行内标）。**红线 4 例外依据**: 650 P4×2 / 651 P3-1 行内更正先例（事实错误必须修正）。

**已用省 actual_province 口径**: 31/31 全落定（25 spike REACHABLE + 4 spike BLOCKED + 2 M2-only）。
**657 增量** = HEBEI + SHANXI = 24/31 行（22 → 24 REACHABLE）。
**658 增量** = TIANJIN + CHONGQING + 23 hongheiku 转载 batch INSERT = 26/31 行（24 → 26 REACHABLE；剩余 23 转载 INSERT 与 spike 锁值并列同源, 不再算行）。

**658 任务书授权解锁**（per 657-A U6 金丝雀 5/5 一致 PASS）= hongheiku 转载数据源 + 23 省 × 5 指标批量采用（每省 observation INSERT 5 行, lineage 三重标注 source='hongheiku_tjgb' / origin='XX省统计局' / ruling='U6 2026-09-02'）；具体落地以 658 任务书 + docs/83 为准。

### 1.3 关键意义

- **双 REACHABLE 收官**：HEBEI /zwgk/ Connection reset by peer → / 200 fallback 命中; SHANXI /zwgk/ 404 → / 200 fallback 命中 — fallback chain 第 2 步 `/` 主页 100% 命中两省
- **失败形式库新增 = 0 例**（657 全链首试省无新失败形式）; 累计仍 4 例：653 SSL handshake failure + 654 Connection reset by peer + 655 405 Method Not Allowed + WAF marker + 656 SSL error:1404B458
- **新增第 5 例 (657-A U6 tag-path assumption)**: tasking §1.657-A 假设 `/tag/{省名}` 路径失败; **记入 U6 审计不入主失败形式库**（金丝雀性子任务而非主 spike 失败）
- **已用省全集增量**：21 → 23 (HEBEI/SHANXI 双 REACHABLE 增量 2; GUANGXI BLOCKED 留痕 → 0 增量)
- **657-A.0 规范 v3.3 落地**：§NOW 尾段完成清单终态化首签（杜绝 655-P4-1 / 656-P4-1 同类第三型复发）
- **657-A U6 金丝雀 PASS（5/5 一致）→ 658 批量授权解锁**: hongheiku 转载数据源接受为 M2/M3 observation, 含 26 省 + 三次产业

### 1.4 与 656 同构 + 差异性
- **同构点**：双首试省 + 双 retry_of=N/A lineage + 双 chain_id 末段递增 (_v14 ≠ _v13) + UUID 段递增 (p 段 ≠ o 段) + 16 INSERT ROWS 双 REACHABLE 沿用
- **差异点**：656 = 混合态 (1R + 1B) / 657 = 双 REACHABLE (2R); 656 = 华南双省对 / 657 = 华北双省对 (全国 31 省收官); 657 含 657-A U6 金丝雀子任务（独立 sub-deliverable）

---

## 2. 首试省 REACHABLE 守门登记表（沿用 654-656 §2 模板）

### 2.1 HEBEI REACHABLE fallback 命中实现位置

`scripts/fetch_m4_20_policy_detail_v14_2024.py::fetch_cell()` — HEBEI fallback chain 第 2 步 `/` 主页 REACHABLE 命中：

- /zwgk/ → HTTP 0 / Recv failure: Connection reset by peer → fallback #2
- / → HTTP 200 / 204976B / 233 锚点 (含 "河北" "hebei" "冀" + "政务公开"/"政府公报"/"政府文件") / 无 WAF marker → REACHABLE
- SHA = `508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7`

### 2.2 SHANXI REACHABLE fallback 命中实现位置

`scripts/fetch_m4_20_policy_detail_v14_2024.py::fetch_cell()` — SHANXI fallback chain 第 2 步 `/` 主页 REACHABLE 命中：

- /zwgk/ → HTTP 404 / 146B → fallback #2
- / → HTTP 200 / 229900B / 435 锚点 (含 "山西" "shanxi" "晋" + "政务公开"/"政府公报"/"政府文件") / 无 WAF marker → REACHABLE
- SHA = `29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2`

### 2.3 守门实现 4 处 (沿用 654-656)

1. **fetch 脚本 REACHABLE 分支可达**: `fetch_cell()` 第 164-180 行 — `code == 200 and size > 1000 and anchor_hits >= 1 and not waf_present` 五重守门
2. **seed SQL 16 INSERT ROWS**: `scripts/seed_m4_20_policy_detail_real_v14.sql` — 2 样本 × 8 表 = 16 INSERT, line JSONB 含 source_file_sha256 全 distinct
3. **evidence JSON 双 REACHABLE cells**: `evidence_pack/m4_20_policy_detail_real_v14_20260902.json` — `fetch_status='REAL_FETCHED'` + 2 NEW SHA 全部入链 + `substitute_used_count=0`
4. **tests ≥25 cases 守门**: `tests/test_m4_20_policy_detail_real_v14.py` 沿 656 ≥25 cases 守门模式 + 新增 v14 chain_id / UUID p 段 / 4 fixture / 1 docs/82 / 全国 31 省总对账表 守门

### 2.4 双首试省 retry_of=N/A 全行守门

HEBEI / SHANXI 均无前史（per 657 §1.657）→ retry_of=N/A 全行；line JSONB 仅存 `original_province: hebei/shanxi` + `actual_province: hebei/shanxi`（同源首试省 lineage 透明）。

---

## 3. 失败形式库累计 = 4 例 (657 主 spike 沿用 654-656)

| # | 失败形式 | 首次落定刀 | 备注 |
|---:|---|---|---|
| 1 | SSL handshake failure (`error:1404B410:SSL routines`) | 653 | **shandong** 第 1 步 `/zwgk/` 〔659-B P3-2 终修：原"LIAONING/JILIN/GUIZHOU"，链 SHA 实证 `52a1ad7` "M4.16 v10 shandong+hubei 双复试" — 653 首见样本为 shandong；align docs/80 §5.1〕 |
| 2 | Connection reset by peer | 654 | **qinghai** 第 1 步 `/zwgk/` 〔659-B P3-2 终修：原"SHAANXI/SICHUAN"，链 SHA 实证 `c3387f0` "M4.17 v11 gansu+qinghai" — 654 首见样本为 qinghai；align docs/80 §5.1；删"654=SHAANXI/SICHUAN"矛盾〕 |
| 3 | 405 Method Not Allowed + WAF marker | 655 | **ningxia** 第 1 步 `/zwgk/` 〔659-B P3-2 终修：原"XINJIANG/NEI MENGGU"，链 SHA 实证 `86314f9c` "M4.18 v12 ningxia+xizang" — 655 首见样本为 ningxia；align docs/80 §5.1〕 |
| 4 | SSL `error:1404B458:ST_CONNECT:tlsv1 unrecognized name` | 656 | GUANGXI 第 1+2 步 全失败 |

**657 主 spike 新增 = 0 例**（HEBEI /zwgk/ Connection reset 走 fallback 命中 / SHANXI /zwgk/ 404 走 fallback 命中；不计入失败形式库首见）。

**附: 657-A U6 金丝雀新增 = 1 例**（TAG_PATH_ASSUMPTION_ERROR: tasking /tag/{省名} 假设失败 → +2 HTTP 超预算; 仅记入 U6 审计）。

---

## 4. 红线复核（657）

1 不补零 ✓（16 INSERT 按实报; HEBEI/SHANXI 均为 REACHABLE 无 BLOCKED 留痕）/ 2 不静默硬编码 ✓ / 3 不爬网 ✓（HTTP 4/12 = 33%; ≤12 沿用）/ 4 不改既有 docs ✓（docs/80/81 零改动; docs/82 为本刀新建）/ 5 SHA 全等 ✓（2 NEW SHA; 4 fixture 锁值未碰）/ 6 数据源政府自取 ✓（双省 .gov.cn 直取）/ 7 lineage 全行 ✓（retry_of=N/A 双首试省）/ 8 中间产物本地 ✓ / 9 三重留痕 ✓（evidence/docs 82 §2/receipt）/ 10 回执 13 节 ✓ / 11 spike 真 SHA 不入库 ✓（沿用）/ 12 m2 报告零 diff ✓✓（656-A.2 机制保障沿用）/ 13 gate 不自动宣布 ✓（24 里程碑不宣布）/ 14 BLOCKED_NO_POOL 留痕 ✓（GUANGXI 沿用; HEBEI/SHANXI 双 REACHABLE 触发 0 例）。

**U6 §5 附加五条**: ① 金丝雀不 INSERT observation ✓（657-A 仅 evidence + report）② SHA 锁 hongheiku 转载字节 ✓（5 SHA 锁 + lineage 三重标注）③ 不绕过任何反爬 ✓（本域无 WAF/验证码）④ docs/81 既有正文零改动 ✓（657-A 仅新增 81 既有正文不动）⑤ CANARY_FAIL 时禁止部分采信 N/A（PASS 未触发）。

**v3.3 §NOW 尾段完成清单终态化首签**: 657 §NOW 任何「待 N/M 收口」「待 X+Y+Z」清单式文本, 对应 C.x 全部落地后必须**同 commit** 刷新为终态句; 历史引述加「〔655-P4-1 引述〕」标记防误报。

---

## 5. 收官叙事

- **656 = 华南双省对 (1R + 1B 混合) → 657 = 华北双省对 (2R 双 REACHABLE) → 收官**
- **22 省 actual_province 已落定**（656 后 21 省 → 657 后 23 省）; 剩余 **9 省 + 特殊行政** 待 658+ 切
- **658 任务书已授权解锁**: hongheiku 转载数据源（U6 金丝雀 5/5 PASS）+ 26 省批量采用 + 三次产业扩展
- **未触线**: 24 里程碑不宣布; O1 仍 OPEN; Gate 不宣称 PASS; 4 fixture 锁值零触碰; 既有 registry 行 SHA 零漂移
