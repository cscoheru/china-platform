# Knife 669c-2025 probe — 0 HTTP cache hit verification DELIVERED

> **HEAD**: (no commit, 0 HTTP verification only, follows 669b-2025 / 669fix-b-2025 baseline 翻转判定 pattern)
> **Status**: ✅ DELIVERED (zero-harvest verdict confirmed via 3-layer cache probe)
> **Date**: 2026-09-09
> **Pattern**: 独立探针, 0 HTTP, 仅 cache 文件验证, 与 669b-2025 / 669fix-b-2025 实证互补

---

## Context

承接 user "启动 Batch deploy and 669c-2025 probe" 三件套授权中第 3 件 (knife 959):
- 验证 cat_index_2025.html 收录的所有 2025 entry
- 区分 province level (/sjtjgb/, /xjtjgb/xj2020/) vs city level (/djs/)
- 不发起任何 HTTP 请求 (0 HTTP, 0 cache 写入)
- 输出 entry 列表 + 判定

判定:
- 若 cat_index_2025 含 ≥1 /djs/{eid}.html 城市 entry → 后续 knife 可 harvest
- 若仅 /sjtjgb/ province entry → 与 669b-2025 / 669fix-b-2025 一致, hongheiku 暂未收录 city level 2025

---

## 数据成果 (knife 669c-2025)

### harvest 概况

- **0 HTTP** (zero-cache, 仅本地 cache 读取)
- **HTTP 预算**: 0 ≤ 32 红线 ✓
- **cache files inspected**:
  - `/tmp/669b/_cat_index_2025.html` (108,278 bytes, 370 unique URLs)
  - `/tmp/669b/_search_*.html` (5 files: 广州2025年 / 成都2025年 / 杭州2025 / 武汉2025 / 长沙2025年)

---

## 三层 probe 实证 (cache-only, 0 HTTP)

### Layer 1: cat_index_2025.html 全 href 抽取

- **Total URLs**: 370 (unique: 221)
- **City level entries (/djs/)**: **0** ← critical signal
- **Province level entries (/sjtjgb/, /xjtjgb/)**: 148
  - Top 5 eids (新近): 72070 / 72067 / 72064 / 72041 / 69683 (省级公报, 2024 年度数据 publish 2026-04-30 ~ 2026-05-21)
  - 6 个 /xjtjgb/xj2020/ (新疆 2020 省级公报变体)
  - 注: cat_index_2025.html 实质是 category/sjtjgb 完整分页 (含 2024 历史 entries), 不限于 2025 年新增
- **Year index entries (/{eid}.html)**: 40
  - 2025 年新晋 index: 68085, 57063, 45926, 35003, 23939 (5 个 year index, 仍非 city)
- **Category entries**: 2 (/category/zgtjgb, /category/sjtjgb)
- **Tag entries**: 177 (URL-encoded, 含 31 省 tag + 地区 tag)

### Layer 2: search cache (5 city, 各 cache 文件读取)

| City | cache file | URLs | /djs/ (city) | /sjtjgb/ (province) |
|---|---|---|---|---|
| 广州 | `_search_广州2025年.html` | 10 | 0 | 0 |
| 成都 | `_search_成都2025年.html` | 10 | 0 | 0 |
| 杭州 | `_search_杭州2025.html` | 10 | 0 | 0 |
| 武汉 | `_search_武汉2025.html` | 10 | 0 | 0 |
| 长沙 | `_search_长沙2025年.html` | 10 | 0 | 0 |

- **city_djs hit**: 0/5 (0%)
- **province hit**: 0/5 (0%)

### Layer 3: verdict (与 669b-2025 / 669fix-b-2025 一致)

- **[ZERO-HARVEST]** cat_index_2025 has **0 /djs/ entries (city level)**
- cat_index_2025 only has 148 /sjtjgb/ entries (province level)
- search cache hit: city_djs 0/5, province 0/5
- **结论**: hongheiku 暂未收录 city level 2025 entry — 与 669b-2025 / 669fix-b-2025 实证一致

---

## URL pattern 分类规则 (新发现, 后续 knife 复用)

| Pattern | Level | 备注 |
|---|---|---|
| `/djs/{eid}.html` | **city level (市级公报)** | 25 省会需要此 pattern, 0 命中 |
| `/sjtjgb/{eid}.html` | province level (省级公报) | 148 命中, 全部非城市 |
| `/xjtjgb/xj2020/{eid}.html` | province level (新疆 2020 变体) | 6 命中 |
| `/{eid}.html` (eid > 20000) | year index page | 5 命中 (68085/57063/45926/35003/23939) |
| `/category/{...}` | category page | 2 (zgtjgb / sjtjgb) |
| `/tag/{url-encoded}` | tag listing | 177 (31 省 + 地区 tag, URL-encoded) |

---

## 红线守门 (knife 669c-2025 probe)

- ✓ **0 HTTP** ≤ 32 红线 (cache-only verification)
- ✓ **守红线-3** 不爬第三方 (仅 cache 文件读取)
- ✓ **不冒充 ops** (cache 文件已存在, 无 SSH / 无 fetch)
- ✓ **不写 mart** (探针模式, 无 mart SQL apply)
- ✓ **不手填** (仅 enumeration + 判定)
- ✓ **amend-first v3.5** (探针无需 commit, 仅 receipt 文件归档)

---

## 决策

knife 669c-2025 probe 与 knife 669b-2025 / 669fix-b-2025 共同实证:
**hongheiku 暂未收录 city level 2025 entry**, 因此 25 省会 × 2025 (250 cells) 必须走 zero-harvest 路径, 守红线-3 不手填。

**当前 mart 2025 状态**:
- Real cells: 18 (4 669a 城市 from K669a-2025)
- DATA_MISSING: 272 (250 省会 K669fix-b-2025 + 22 4 669a K669a-2025)
- lineage_ruling distinct: 2 (K669a-2025 + K669fix-b-2025)

---

## 文件清单 (1 new script + 1 receipt)

### Created (2)

| 路径 | 用途 |
|---|---|
| `scripts/probe_hongheiku_2025_city_669c.py` | 0 HTTP cache hit verification, parse cat_index + 5 search cache |
| `reviews/stage0-gate0-rework-2026-08-23/669c-2025-probe-zero-harvest-receipt-20260909.md` | 本文件 |

---

## Red Lessons (URL pattern 解析)

1. **cat_index HTML 用绝对 URL** — 原 plan 假设相对 URL `/xxx.html`, 实际 cat_index 用 `https://tjgb.hongheiku.com/xxx.html`, regex 必须匹配 `https://tjgb.hongheiku.com/[^"]+`
2. **cat_index 实质是分页全集** — 不是 2025 年新增, 而是 category/sjtjgb 完整分页; 真正的"2025 entry"应是 eid >= 68000 (year index 68085/57063/45926/35003/23939)
3. **/djs/ pattern = city level** — 25 省会所需; cat_index 0 命中 = 实证 hongheiku 未收录 city level 2025
4. **5 city search cache 命中 0 city entries** — 5 个搜索关键词 (广州/成都/杭州/武汉/长沙) + 2025 都只返回 generic title, 无 city bulletin

---

## Next Steps (待 user 裁定)

- **Batch deploy** (knife 934) — 668 + 669 unified newvps 4-step granular (per memory `china-platform-fastapi-missing-on-newvps.md`)
- **knife 669c-2025 probe artifacts commit** (script + receipt) — 需要 separate 双推授权 (per amend-first v3.5)
- **knife 669fix program 收口** — 5 刀 (2020/2021/2022/2023/2024/2025) 全部 DELIVERED, 累计 baseline real cells +890

— End Knife 669c-2025 probe DELIVERED (zero-harvest, 0 HTTP, baseline 翻转判定 3 层实证) —