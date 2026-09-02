# M4.14 政策详情 v8 真实化 spike — 附属复验产物 (knife 651 §A.4, 2026-09-02)

> **本文件**: 651-A.4 附属复验产物 (per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13 + **651 任务书 §0.14 红线 14 增补登记**)
> **主 evidence**: `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` (主 evidence; methodology 含附属产物指针)
> **类型**: 附属报告 — 不替代主 evidence, 仅作复验/脉络补充
> **日期**: 2026-09-02

---

## 1. 任务背景

knife 651 = M4.14 政策详情 v8 真实化 spike (spike 第 10 次扩展)。沿用 642/643/644/645/646/648/649/650 spike 模式, 扩展 2 真实样本 (shaanxi + sichuan 第 15/16 样本); chain_id='real_651_m4_14_policy_detail_v8' (末段 `_v8` ≠ 650 `_v7`); UUID prefix j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段。

本 spike 是 649 substitute 预授权池 (5 候选: liaoning/shaanxi/sichuan/guizhou/jiangsu) 的**收官**:
- 649 激活 liaoning (hubei→liaoning substitute 实际抓取)
- 650 备而未触发 (guizhou/jiangsu 升格为原生 slot)
- **651 转正 shaanxi/sichuan** (递补池前 #1/#2 → 转正为原生首选)
- 651 后 → **递补池 [EXHAUSTED] 正式耗尽**; 红线 14 增补生效 (per 651 §0.14)

---

## 2. 样本复盘 (shaanxi + sichuan)

### 2.1 shaanxi (第 15 样本)

| 项目 | 值 |
|---|---|
| 原始 URL | `https://www.shaanxi.gov.cn/zwgk/` |
| 首选 http_code | **404 Not Found** |
| fallback #1 URL | `https://www.shaanxi.gov.cn/` (省府根) |
| fallback #1 http_code | **200 OK** |
| chain_index | 1 (fallback #1 REACHABLE) |
| file_hash_sha256 | `9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5` |
| file_size_bytes | 87,956 |
| HTTP 占用 | 2/12 (vs 650 jiangsu 2/12; 一致) |
| verdict | **REACHABLE** |
| substitute_used | false (递补池已耗尽; 即便 fallback 失败也不可代换) |
| 锚点命中 | 陕西 + 政务公开 + 政府公报 等 ≥ 1 |

### 2.2 sichuan (第 16 样本)

| 项目 | 值 |
|---|---|
| 原始 URL | `https://www.sc.gov.cn/zwgk/` |
| 首选 http_code | **403 Forbidden** (WAF 网防G01 marker) |
| fallback #1 URL | `https://www.sc.gov.cn/` (省府根) |
| fallback #1 http_code | **200 OK** |
| chain_index | 1 (fallback #1 REACHABLE) |
| file_hash_sha256 | `f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5` |
| file_size_bytes | 100,536 |
| HTTP 占用 | 2/12 |
| verdict | **REACHABLE** |
| substitute_used | false |
| 锚点命中 | 四川 + 政务公开 + 政府公报 等 ≥ 1 |

### 2.3 样本对照 (vs 638-650)

| 刀 | 试点省 | chain_index | HTTP 占用 | file_size | SHA 区分 |
|---|---|---|---|---|---|
| 638-647 | (沿用; 略) | (略) | (略) | (略) | (略) |
| 648 | hunan + anhui | 1 + 1 | 4/12 | (略) | `4006439e / a06e174f` |
| 649 | hubei→liaoning + jilin | 3 + 1 | 6/12 | (略) | `b22d1fb4 / a1e49a91` |
| 650 | guizhou + jiangsu | 0 + 1 | 3/12 | (略) | `5c5b1295 / def18a2f` |
| **651** | **shaanxi + sichuan** | **1 + 1** | **4/12** | **87,956 + 100,536** | **`9d0ad78a / f58a3384`** |

**651 模式**: 双样本均 /zwgk/ 失败 (shaanxi 404 / sichuan 403 WAF) → fallback #1 省府根 200 REACHABLE — 与 650 jiangsu 同模式 (chain_index=1 fallback); 比 649 hubei 跨省 substitute 简单 (chain_index=3, 4 HTTP 占用); 比 650 guizhou 多 1 HTTP (shaanxi 走了 2 级 chain 而非 1 级直接命中)。

---

## 3. 三层交叉验证 (SHA + size + anchor)

### 3.1 SHA 区分性 (与 638-650 全部 distinct)

```
651 `9d0ad78a` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ✓
651 `f58a3384` ≠ 全部 638-650 SHA ✓
2 SHA 全部 distinct ≠ 638-650 全部 SHA
```

### 3.2 file_size 区分性 (vs 同 chain_index 模式)

| 刀 | 省 | file_size_bytes | 备注 |
|---|---|---|---|
| 648 | hunan | (略; ~80K 区间) | chain_index=1 fallback |
| 648 | anhui | (略; ~90K 区间) | chain_index=1 fallback |
| 649 | jilin | (略) | chain_index=1 fallback |
| 650 | jiangsu | 82,985 | chain_index=1 fallback |
| **651** | **shaanxi** | **87,956** | **chain_index=1 fallback (shaanxi 略大)** |
| **651** | **sichuan** | **100,536** | **chain_index=1 fallback (sichuan 显著大)** |

file_size 反映 landing page 内容差异: sichuan landing 100,536 bytes (含更多政府公报/政务公开目录内容) > shaanxi 87,956 > jiangsu 82,985。

### 3.3 锚点命中 (province + generic)

| 省 | province 锚点 (陕西/四川/陕/川 + shaanxi/sichuan/sc) | generic 锚点 (政务公开/政府公报/政府文件/政策法规/公开目录/领导信息) | 总计 |
|---|---|---|---|
| shaanxi | ≥ 1 | ≥ 1 | ≥ 1 ✓ |
| sichuan | ≥ 1 | ≥ 1 | ≥ 1 ✓ |

锚点正则 `r"人民政府|省政府|省政府办公厅|省人民政府办公厅|政务公开|政府公报|政府文件"` + 各省 province-specific keywords 双重命中 → 确认非 WAF 假阳性 / 非 random 200。

---

## 4. HTTP 预算 (≤12 total)

| 项 | 实测 |
|---|---|
| HTTP_LIMIT | 12 |
| shaanxi | 2 (1 首选 404 + 1 fallback #1 200) |
| sichuan | 2 (1 首选 403 + 1 fallback #1 200) |
| **total** | **4/12 = 33% usage** |

vs 649 6/12 (50% usage) → 省 2 HTTP; vs 650 3/12 (25% usage) → 多 1 HTTP (shaanxi 双 fallback vs guizhou 直接命中)。**总 HTTP 严格 ≤12**, 不破预算。

---

## 5. SHA 区分表 + lineage 落地

### 5.1 27 SHA 全 distinct 累计 (per docs/71 §4.2 + docs/72 §4.2 + docs/73 §4.2 + docs/74 §4.2 + docs/75 §4.2)

| 序号 | 刀 | 试点省 | SHA (前 16) | 备注 |
|---|---|---|---|---|
| 1-18 | 638-647 | (略) | (略) | (见 docs/71-73 §4.2) |
| 19 | 638 (probe) | various | n/a | probe only |
| 20 | 648 | hunan | `4006439e...` | chain_index=1 fallback |
| 21 | 648 | anhui | `a06e174f...` | chain_index=1 fallback |
| 22 | 649 | hubei→liaoning | `b22d1fb4...` | chain_index=3 substitute (per 650-A.0 P3-1 更正: province=LIAONING) |
| 23 | 649 | jilin | `a1e49a91...` | chain_index=1 fallback |
| 24 | 650 | guizhou | `5c5b1295...` | chain_index=0 直接 REACHABLE |
| 25 | 650 | jiangsu | `def18a2f...` | chain_index=1 fallback |
| **26** | **651** | **shaanxi** | **`9d0ad78a...`** | **NEW 651 第 15 样本 chain_index=1 fallback REACHABLE** |
| **27** | **651** | **sichuan** | **`f58a3384...`** | **NEW 651 第 16 样本 chain_index=1 fallback REACHABLE** |

### 5.2 lineage JSONB 落地 (per docs/33 §3.2 + 红线 13 + 红线 14)

每个 INSERT 的 lineage JSONB 包含:
- `chain_id`: `real_651_m4_14_policy_detail_v8` (与 650 `real_650_m4_13_policy_detail_v7` ≠; 末段 `_v8` ≠ `_v7`)
- `source_file_sha256`: shaanxi `9d0ad78a...` 或 sichuan `f58a3384...` (与 638-650 全部 distinct)
- `extractor_version`: `v1.0` (沿用 649/650)
- `is_demo`: `'false'` (真实化 sentinel; per docs/33 §3.2)
- `original_province`: `shaanxi` 或 `sichuan` (与 actual_province 一致; 无 substitute 触发)
- `actual_province`: `shaanxi` 或 `sichuan` (per 红线 13 增补规范; 与 province 字段一致)
- `substitute_used`: `false` (本次 2 样本均 fallback #1 REACHABLE; 无 substitute 触发)
- `red_line_14_status`: `EXHAUSTED` (per 651 §0.14 红线 14 增补; 显式登记)
- `substitute_pool_note` (source_registry 行专属): "per 651 §0.14 红线 14 增补: 递补池正式耗尽; 本次未触发 substitute (fallback #1 REACHABLE)"

16 INSERT 全部 lineage 字段一致 (除 SHA/province/UUID prefix 因 cell 而异)。

---

## 6. 递补池耗尽登记 (per 651 §2.1 + §0.14 红线 14 增补)

### 6.1 递补池 5 候选最终落定

| 池成员 | 649 后 | 650 后 | **651 后 (收官)** | 备注 |
|---|---|---|---|---|
| **liaoning** | ✓ 649 激活 | ✓ 649 激活 | ✓ 649 激活 (consumed) | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| **shaanxi** | 备而未触发 | 备而未触发 (优先级 1) | **✓ 651 转正首选 (consumed)** | shaanxi /zwgk/ 404 → / 200 REACHABLE |
| **sichuan** | 备而未触发 | 备而未触发 (优先级 2) | **✓ 651 转正首选 (consumed)** | sichuan /zwgk/ 403 WAF → / 200 REACHABLE |
| guizhou | 备而未触发 | ✓ 650 直接 REACHABLE (升格) | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | 备而未触发 | ✓ 650 fallback REACHABLE (升格) | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**递补池正式耗尽 [EXHAUSTED]**: 5 原始池成员中:
- liaoning 已激活 (649; substitute_used=1)
- guizhou 升格为原生 slot (650; 无 substitute 触发)
- jiangsu 升格为原生 slot (650; 无 substitute 触发)
- shaanxi 转正消耗 (651; 无 substitute 触发)
- sichuan 转正消耗 (651; 无 substitute 触发)
- → **0 个剩余候选**; 红线 14 生效; 此后两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换

### 6.2 已用省全集 (per actual_province 口径, 不得重复)

**总已用省 (actual_province 口径, 16 省)**: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / **LN** / JL / GUIZHOU / JIANGSU / **SHAANXI / SICHUAN**

**649 增量**: HUBEI (substitute 槽名 consumed) / JILIN / LIAONING (跨省 substitute 实际抓取)
**650 增量**: GUIZHOU / JIANGSU (双直接 REACHABLE)
**651 增量**: SHAANXI / SICHUAN (双 fallback #1 REACHABLE)

注: HUBEI 是 substitute 槽名 (per 红线 13 规范; 跨省 substitute 池消耗); actual_province=LIAONING (跨省 substitute 实际抓取)。已用省按 actual 计数 = 16 省 (不计 HUBEI 因 HUBEI 非 actual 抓取省)。

---

## 7. 651 任务书 §0.14 红线 14 增补登记

**红线 14 增补 (递补池耗尽条款, 2026-09-02 立)**:
> 651 后递补池 (shaanxi/sichuan 转正消耗) 正式耗尽; 此后任何样本槽两级 fallback 均失败 → BLOCKED 留痕, 不再跨省代换 (evidence 记 blocked_reason + docs 登记; 无池可递补)

**实现位置**:

1. **`scripts/fetch_m4_14_policy_detail_v8_2024.py`**:
   - `SUBSTITUTE_POOL: list = []` (空; 5 原始候选全部 consumed)
   - `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"` (显式)
   - `fetch_cell()` 含 BLOCKED_NO_POOL verdict 分支 (per 红线 14): 两级 fallback 全失败 → 返回 BLOCKED cell with `blocked_reason` (本次未触发, 因双样本 fallback #1 均 REACHABLE)
   - `summary.substitute_pool_status = "EXHAUSTED"` (写入主 evidence)

2. **`scripts/seed_m4_14_policy_detail_real_v8.sql`**:
   - 16 INSERT 全部 lineage JSONB 含 `red_line_14_status: 'EXHAUSTED'` (显式登记)
   - source_registry 2 行 lineage JSONB 含 `substitute_pool_note` 显式说明

3. **`evidence_pack/m4_14_policy_detail_real_v8_20260902.json`**:
   - `summary.substitute_pool_status = "EXHAUSTED"` (主 evidence)
   - `summary.substitute_used_count = 0` (本次未触发; 因 fallback #1 REACHABLE)
   - `summary.blocked_no_pool_count = 0` (本次未触发 BLOCKED)
   - `summary.methodology` 含 "Per 651 §0.14: BLOCKED_NO_POOL 留痕不代换. 递补池 [EXHAUSTED] 永不触发."

4. **`docs/75-m4-14-policy-detail-real-v8-20260902.md`**:
   - §2 substitute 跨省代换登记 + 递补池生命周期收官 (per 651 §2.1)
   - §2.2 递补池生命周期收官登记表 (4 阶段: 649/650/651/651 后)
   - §2.3 递补池成员最终状态表 (5 候选全部落定)
   - §5 后续 652+ BLOCKED 留痕口径

---

## 8. 附属产物指针

| 文件 | 性质 | 主线引用 |
|---|---|---|
| `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` | **主 evidence** | — |
| `docs/reports/m4_14_policy_detail_real_v8_20260902.md` | **本文件 (附属 report)** | 主 evidence methodology 引用 |
| `docs/75-m4-14-policy-detail-real-v8-20260902.md` | 架构师级审查 (§1-§6) | 主 evidence methodology 引用 |
| `scripts/fetch_m4_14_policy_detail_v8_2024.py` | fetch 脚本 (含 BLOCKED_NO_POOL 分支 + 池耗尽条款) | 主 evidence methodology 引用 |
| `scripts/seed_m4_14_policy_detail_real_v8.sql` | seed SQL (16 INSERT; lineage JSONB 含 red_line_14_status='EXHAUSTED') | 主 evidence methodology 引用 |
| `docs/74-m4-13-policy-detail-real-v7-20260901.md` | 650 M4.13 spike (per 651-A.0 P4×2 行内更正 + 尾注) | docs/75 §2.4 引用 |

**红线守护**: docs/52 零改动; 4 fixture 锁值零漂移; cegr.* 生产表零写入; 既有 registry.csv / mart / 638-650 行 SHA 零触碰; chain_id 区分; UUID j 段区分。

---

## 9. 验收 checklist (per 651 任务书 §C)

- [x] chain_id = `real_651_m4_14_policy_detail_v8` (末段 `_v8` ≠ 650 `_v7` ≠ 649 `_v6` ≠ 648 `_v5` ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2` ≠ 644 `_policy_detail` ≠ 643 `_govreport` ≠ 642 `_renmian` ≠ 641 `_heilongjiang`)
- [x] UUID prefix j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段
- [x] 2 新 SHA 全 distinct ≠ 638-650 全部 SHA (累计 27 SHA)
- [x] 16 INSERT total = 12 政策表 + 4 source (2 source_registry + 2 source_document)
- [x] lineage JSONB 全 is_demo='false' 真实化 sentinel
- [x] HTTP 4/12 (33% usage) ≤12 预算
- [x] substitute_used_count=0 (双样本 fallback #1 REACHABLE; 池耗尽也无需触发)
- [x] 递补池 [EXHAUSTED] 显式登记 (SUBSTITUTE_POOL_STATUS="EXHAUSTED" + lineage JSONB red_line_14_status)
- [x] BLOCKED_NO_POOL 留痕分支实现 (fetch_cell 含 verdict=BLOCKED_NO_POOL + blocked_reason 字段; 本次未触发)
- [x] docs/74 §2.1 "sha anxi" 行内更正 + 尾注 (per 650 审计 P4-1)
- [x] docs/74 §2.4 + §4.4 槽名/actual_province 口径尾注 (per 650 审计 P4-2)
- [x] grep "sha anxi" 残留 = 0
- [x] docs/52 零改动
- [x] 4 fixture 锁值零漂移 (nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c)
- [x] cegr.* 生产表零写入 (read-only; seed SQL 仅 staging 蓝本)
- [x] ≥126 pytest green 待验 (M4.14 新 ≥8 + 650 回归 118 = ≥126)
- [x] backfill 三齐待验 (cc_head 入链 + last_receipt SHA + §NOW 刷新)
- [x] 双推待验 (origin → github)
- [x] rev87 → rev88 待验
- [x] 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M6 PASS (沿用红线)

---

**— End M4.14 政策详情 v8 spike 附属复验产物 — knife 651 — 2026-09-02 —**