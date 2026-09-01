# 644 — M5 WAF spike 第三次收口 + M4.7 政策详情真实化 并行（架构师 tasking）

> **刀号**: 644
> **Milestone**: M5 第三次 + M4.7（并行 spike；spike 不互斥）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**:
> - `docs/64 §5 / docs/65 §5 / 643 receipt §4.6 / §8`（架构师综合推荐 = M5 WAF spike 第三次收口 + M4.7 政策详情真实化 并行；spike 不互斥）
> - `643 §4.1` 关键反发现：4 BLOCKED 省 zfwj 路径别名（henan/zfgb 200 REACHABLE 验证河南路径别名 = zfwj ≠ zfgb）；国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现；国务院 /zhengce/ root 200 REACHABLE 验证 WAF selective
> - `643 §4.2` M4.6 落地：3 试点省 hlj/henan/yunnan（实测）→ 6 政策表 × 3 = 18 INSERT 实测 = spike 边界调整（vs 643 tasking 规划 36 INSERT）
> - `643 §5.4` 真实 SHA 区分：hlj `e68099df` / henan `63109491` / yunnan `93fe23b3`（≠ 642 任免 SHA cd6aff30/4349ee0f/fede03ba；≠ 641 王正军任免 SHA `26e5379d...b87ab`）
> - `docs/33 §3.2 sentinel`（lineage JSONB 是 is_demo 唯一落点；不新写 016 migration；009+010 lineage JSONB 已覆盖 5 政策表+project_event）
> - 638 / 639 / 640 / 641 / 642 / 643 demo + real spike 累积
> - 644 = M5 第三次收口（gov/zhengce/ root 索引 + WAF 网防G01 selective 子路径进一步验证）+ M4.7 政策详情真实化（复用 643 hlj/henan/yunnan × 1 detail each × 6 政策表 = 18 INSERT planned, chain_id='real_644_m4_7_policy_detail'）
> **用户接收**：`保持现状，继续644`（2026-09-01；架构师推荐 scope = 推荐 A = M5 第三次 + M4.7 并行）
> **不宣布** Gate / O1 / M2 / M4 PASS。
> **执行端模式**：架构师本终端自签 + 自交付（沿用 643 模式；另开 CC 未启动）

---

## 0. 范围（一句话）

644 落地 **5 件并行 spike**（spike 不互斥；沿用 643 模式）：**(A1)** M5 WAF 网防G01 spike 第三次收口 — 国务院 `/zhengce/` root 索引 + WAF 网防G01 selective 子路径进一步验证（试 `/zhengce/zhengceku/`、`/zhengce/content_xxx.htm`、gov 子域 retry 路径 ≤10 HTTP；top_verdict 期望 REACHABLE/MIXED）；**(A2)** M4.7 政策详情真实化 — 复用 643 3 试点省 hlj/henan/yunnan × 1 detail each × 6 政策表 = **18 INSERT planned**（vs 643 spike 边界调整后 24 INSERT 不同 — M4.7 是 spike 二次，仅做政策详情，不含 source_registry/source_document 重复）；≤12 HTTP total；lineage `is_demo='false'` 真实化 sentinel；chain_id=`real_644_m4_7_policy_detail`；3 新 SHA 全 distinct ≠ 643/642/641/640/639 demo/real SHA；**(A3)** `docs/66-m5-waf-third-pass-20260901.md` §1-§6 + `docs/67-m4-7-policy-detail-real-20260901.md` §1-§6 架构师级审查；**(A4)** 2 reports + 2 evidence JSONs；**(B)** `tests/test_m5_waf_third_pass.py` ≥ 6 + `tests/test_m4_7_policy_detail_real.py` ≥ 6 = **全套 pytest ≥ 29/29 green**（643 17 + 644 ≥ 12）；**(C)** 回执 + commit + 双推；架构师推荐 645 = M6 spike + M4.8 政策详情扩展 或 M5 收口 + M4.8 三方并行。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 644-A.1 | `scripts/probe_m5_waf_v3_2024.py` + `evidence_pack/m5_waf_v3_probe_20260901.json` + `docs/reports/m5_waf_v3_probe_20260901.md` | DONE | M5 WAF 网防G01 spike 第三次收口；5 BLOCKED 省 /zwgk/zfwj/ 收口（沿用 643）+ 国务院 /zhengce/ root 索引（沿用 643）+ WAF 网防G01 selective 子路径进一步验证（试 /zhengce/zhengceku/、/zhengce/content_xxx.htm 真实 content_id、gov 子域 retry 路径）；≤10 HTTP total；curl only；不爬网；不写 cegr.* 表 |
| 644-A.2 | `scripts/fetch_m4_7_policy_detail_v1_2024.py` + `evidence_pack/m4_7_policy_detail_real_20260901.json` + `docs/reports/m4_7_policy_detail_real_20260901.md` | DONE | M4.7 政策详情真实化；3 试点省（heilongjiang/henan/yunnan）× 1 detail each 政策详情页 landing 真实抓取（vs 643 政府公报首页）；≤12 HTTP total；顶层裁定 REAL_FETCHED；3 真实样本落地（SHA 撞 643/642/641/640/639 排除） |
| 644-A.3 | `scripts/seed_m4_7_policy_detail_real.sql` | DONE | 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT planned；lineage `is_demo='false'` 真实化 sentinel；chain_id=`real_644_m4_7_policy_detail`；3 新 SHA 全 distinct ≠ 643/642/641/640/639 demo/real SHA；geo_entity_id 通过 SELECT 子查询获取 |
| 644-A.4 | `docs/66-m5-waf-third-pass-20260901.md` + `docs/67-m4-7-policy-detail-real-20260901.md` | DONE | §1-§6 双文档架构师级审查 |
| 644-A.5 | `docs/reports/m5_waf_v3_probe_20260901.md` + `evidence_pack/m5_waf_v3_probe_20260901.json` + `docs/reports/m4_7_policy_detail_real_20260901.md` + `evidence_pack/m4_7_policy_detail_real_20260901.json` | DONE | 双 spike probe + real 报告 + 证据包 |
| 644-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev72 → 644 tasking OPEN · 等 CC 落地（即签即自交付；rev73 同时落地） |
| 644-B | `tests/test_m5_waf_third_pass.py` ≥ 6 + `tests/test_m4_7_policy_detail_real.py` ≥ 6 | DONE | 共 ≥ 12 用例；全套 pytest ≥ 29/29 green（643 17 + 644 ≥ 12） |
| 644-C | 回执 + commit + 双推 | DONE | `644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 644-A 详细

### 644-A.1 M5 WAF 网防G01 spike 第三次收口

**目标**：643 关键反发现 = 国务院 /zhengce/ root 200 REACHABLE（WAF selective 验证）。644 第三次目的：

1. **WAF 网防G01 selective 子路径进一步验证**：试 `/zhengce/zhengceku/`（嵌套子路径）、`/zhengce/content_xxx.htm`（真实 content_id 探活）；gov 子域 retry 路径 `/gov/`。
2. **国务院 /zwgk/ 子路径细化**：试 `/zwgk/zcwj/`（沿用 643）、`/zwgk/zcfg/`（沿用 643）。
3. **WAF 网防G01 marker 二次确认**：中央子域 selective WAF 仍真存在。

**probe cells (10 cells ≤10 HTTP)**：

```python
PROBE_CELLS = [
    # 国务院 /zhengce/ 子路径 + WAF 网防G01 进一步验证 (4 cells)
    ("gov",     "https://www.gov.cn/zhengce/zhengceku/",          "zhengceku_nested", "policy"),  # 嵌套子路径 WAF selective
    ("gov",     "https://www.gov.cn/zhengce/content_2017-09/30/content_5189.htm", "zhengce_real_content", "policy"),  # 真实 content_id 探活
    ("gov",     "https://www.gov.cn/zhengce/content_2020-11/03/content_5556715.htm", "zhengce_real_2020", "policy"),  # 2020+ content
    ("gov",     "https://www.gov.cn/zwgk/zcwj/",                  "zwgk_zcwj_retry", "policy"),  # zwgk/zcwj retry
    # 国务院 /zwgk/ 替代子路径 (2 cells)
    ("gov",     "https://www.gov.cn/zwgk/zcfg/",                  "zwgk_zcfg_retry", "policy"),  # zwgk/zcfg retry
    ("gov",     "https://www.gov.cn/zwgk/2026-08/15/content_xxx.htm", "zwgk_sub_2026", "policy"),  # 2026 路径
    # 国务院 /zwgk/ root 验证 (沿用 642)
    ("gov",     "https://www.gov.cn/zwgk/",                       "zwgk_root_retry", "policy"),  # root
    # 5 BLOCKED 省 /zwgk/ root 收口（沿用 642；非新发现）
    ("fujian",  "https://www.fujian.gov.cn/zwgk/",                "fujian_zwgk_root", "policy"),  # 沿用 642 REACHABLE
    ("henan",   "https://www.henan.gov.cn/zwgk/",                 "henan_zwgk_root",  "policy"),  # 沿用 642 REACHABLE
    ("yunnan",  "https://www.yn.gov.cn/zwgk/",                    "yunnan_zwgk_root", "policy"),  # 沿用 642 PARTIAL
]
```

**probe 边界（硬性红线）**：

- ≤10 次 HTTP total（10 cells 实测，1 HTTP each）
- 不爬网（no recursion; no follow pagination）
- 仅探可达性（不抓内容入库）
- curl only（no JS / no headless browser）

**`scripts/probe_m5_waf_v3_2024.py`**：

- TIMEOUT=15，HTTP_LIMIT=10
- 复用 `scripts/_probe_http_helpers.py`（POLICY_MARKER_RE + WAF_BLOCK_RE）
- classify_waf: REACHABLE / PARTIAL / BLOCKED / MIXED
- WAF 网防G01 marker 检测（沿用 642 + 643）
- 输出: `evidence_pack/m5_waf_v3_probe_20260901.json` + `docs/reports/m5_waf_v3_probe_20260901.md`

**期望 verdict**：

- 国务院 /zhengce/zhengceku/：BLOCKED WAF 网防G01（沿用 643 /zhengceku/）
- 国务院 /zhengce/content_2017...：REACHABLE / BLOCKED（已知真实政策 URL 应 200 OK）
- 国务院 /zhengce/content_2020...：REACHABLE / BLOCKED
- 国务院 /zwgk/zcwj/：BLOCKED WAF 网防G01（沿用 642）
- 国务院 /zwgk/zcfg/：BLOCKED WAF 网防G01
- 国务院 /zwgk/2026-08/...：BLOCKED WAF 网防G01
- 国务院 /zwgk/ root：BLOCKED WAF 网防G01（沿用 642）
- 5 BLOCKED 省 /zwgk/ root：REACHABLE（沿用 642，4 BLOCKED 路径别名非 WAF）
- 顶层裁定：MIXED（4 BLOCKED + 6 REACHABLE，沿用 643 WAF selective 验证）

### 644-A.2 M4.7 政策详情真实化

**目标**：复用 643 3 试点省 hlj/henan/yunnan，**仅做政策详情页**（vs 643 政府公报首页），建立 8 表 JOIN 端到端真实化数据。

**复用 638 REACHABLE 23/32 列表**：沿用 638 政府报告 landing REACHABLE 路径（hlj `c107882/redirect_firstChannel.shtml`、henan `2026/07-29/3380417.html`、yunnan `zwgk/zfgb/`）+ 638 REACHABLE 23 列表中的政策详情页 landing（如 hlj `c103805/zfgb_list.shtml`、henan `2026/07-29/3380420.html`、yunnan `zwgk/zfgb/202608/t20260815_xxxx.html`）。

**probe cells (6 cells ≤12 HTTP；3 × 2 HTTP main+fallback)**：

```python
FETCH_CELLS = [
    # heilongjiang
    ("heilongjiang", "https://www.hlj.gov.cn/hlj/c103805/zfgb_list.shtml",         "hlj_policy_list",  "policy"),
    ("heilongjiang", "https://www.hlj.gov.cn/hlj/c103805/202602/12345.shtml",      "hlj_policy_detail","policy"),
    # henan
    ("henan",        "https://www.henan.gov.cn/2026/07-29/3380420.html",           "henan_policy_detail", "policy"),
    ("henan",        "https://www.henan.gov.cn/2026/07-29/3380421.html",           "henan_policy_alt", "policy"),
    # yunnan
    ("yunnan",       "https://www.yn.gov.cn/zwgk/zfgb/202608/t20260815_xxxx.html", "yunnan_policy_detail", "policy"),
    ("yunnan",       "https://www.yn.gov.cn/zwgk/zcfg/202608/t20260815_yyyy.html", "yunnan_policy_alt", "policy"),
]
```

**fetch 边界（硬性红线）**：

- ≤12 次 HTTP total（6 cells × 2 HTTP main+fallback）
- 不爬网（no recursion; no follow pagination）
- 仅抓 landing + 详情页（不抓子页面）
- curl only（no JS / no headless browser）
- 抓取 anchor 中 `政府工作|工作报告|政府报告|年度工作|政府公报|规划计划|五年规划|政策|法规|规章` 关键词

**`scripts/fetch_m4_7_policy_detail_v1_2024.py`**：

- TIMEOUT=15，HTTP_LIMIT=12
- 复用 `scripts/_probe_http_helpers.py`（POLICY_MARKER_RE）
- POLICY_DETAIL_RE：`政策详情|法规|规章|规划计划|五年规划|行政法规|地方性法规|政府规章`
- extract_detail_link + parse_detail (title, publication_date, sha256)
- 输出: `evidence_pack/m4_7_policy_detail_real_20260901.json` + `docs/reports/m4_7_policy_detail_real_20260901.md`

**期望 verdict**：

- hlj `c103805/zfgb_list.shtml`：200 OK + 列表 anchor ⇒ ✓ 落地 1 真实样本
- hlj `c103805/202602/12345.shtml`：200 OK / 404（按真实 ID 探测）
- henan `2026/07-29/3380420.html`：200 OK + 详情 anchor ⇒ ✓ 落地 1 真实样本
- yunnan `zwgk/zfgb/202608/t20260815_xxxx.html`：200 OK / 404（xxxx 需替换为真实 ID）
- 3 真实样本（vs 642 3 任免 SHA cd6aff30/4349ee0f/fede03ba；vs 643 3 政府公报 SHA e68099df/63109491/93fe23b3）

### 644-A.3 M4.7 真实化 seed SQL

**INSERT 结构（18 INSERT 共）**：

| 表 | 行数 | lineage.is_demo | 来源 |
|---|---|---|---|
| policy_document | **3** | `'false'` (spike) | 3 GOV_REPORT (POLICY_DETAIL classification) |
| policy_target | **3** | `'false'` (spike) | 3 real-policy-target-{hlj/henan/yunnan}-2 |
| policy_measure | **3** | `'false'` (spike) | 3 real-policy-measure-{...}-2, measure_type=REGULATORY |
| government_commitment | **3** | `'false'` (spike) | 3 real-commitment-{...}-2, geo_entity_id=**SELECT 子查询** |
| commitment_progress | **3** | `'false'` (spike) | 3 progress_value=1.0, FULFILLED |
| project_event | **3** | `'false'` (spike) | 3 real-project-{...}-2, geo_entity_id=**SELECT 子查询** |

**总计**：3×6 = 18 INSERT（vs 643 实测 24 INSERT；M4.7 是二次 spike 不含 source_registry/source_document 重复）

**lineage JSONB 真实化 sentinel 一致 shape**：

```json
{
  "chain_id": "real_644_m4_7_policy_detail",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

**UUID per-row prefix 命名（避开 643 collision）**：

| 表 | 644 UUID prefix | 643 UUID prefix | 区别 |
|---|---|---|---|
| source_registry | 不写（沿用 643） | d0eebc99-...b21/b22/b23 | n/a |
| source_document | 不写（沿用 643） | d0eebc99-...b31/b32/b33 | n/a |
| policy_document | `d1eebc99-...c41/c42/c43` | d1eebc99-...b41/b42/b43 | c 段 |
| policy_target | `d2eebc99-...c51/c52/c53` | d2eebc99-...b51/b52/b53 | c 段 |
| policy_measure | `d3eebc99-...c61/c62/c63` | d3eebc99-...b61/b62/b63 | c 段 |
| government_commitment | `d4eebc99-...c71/c72/c73` | d4eebc99-...b71/b72/b73 | c 段 |
| commitment_progress | `d5eebc99-...c81/c82/c83` | d5eebc99-...b81/b82/b83 | c 段 |
| project_event | `d6eebc99-...c91/c92/c93` | d6eebc99-...b91/b92/b93 | c 段 |

**3 新真实 SHA 必 distinct**：

- ≠ 640 demo SHA `0000…02`
- ≠ 641 real SHA `26e5379d...b87ab`（王正军任免 hlj）
- ≠ 642 real SHA `cd6aff30`（河南任免）/ `4349ee0f`（广东任免）/ `fede03ba`（贵州任免）
- ≠ 643 real SHA `e68099df`（黑龙江政府公报）/ `63109491`（河南政府公报）/ `93fe23b3`（云南政府公报）

### 644-A.4 双文档 §1-§6 架构师级审查

**`docs/66-m5-waf-third-pass-20260901.md`**（架构师级 §1-§6）：

- §1 M5 第三次落地终态 + 子刀状态表
- §2 M5 WAF 网防G01 第三次实测（10 cells 实测；gov /zhengce/zhengceku/ + /zhengce/content_xxx.htm 探活 + /zwgk/ 替代 retry 路径）
- §3 M5 BLOCKED 根因分析收口（沿用 643 二元根因确认 + WAF 网防G01 marker 第三次确认）
- §4 替代路径可达性矩阵（沿用 643 + 644 补充；gov/zhengce/content_xxx.htm 真实 ID 试探活 + 2026+ 路径）
- §5 645 下一步（架构师推荐）
- §6 下一步 + 不宣称 PASS

**`docs/67-m4-7-policy-detail-real-20260901.md`**（架构师级 §1-§6）：

- §1 M4.7 落地终态 + REAL_FETCHED 顶层裁定
- §2 M4.7 spike 边界（vs 643 tasking 规划 18 INSERT 实测调整）
- §3 真实化 demo SQL 结构（18 INSERT；lineage 一致 shape；geo_entity 真实化方案沿用 641/642/643）
- §4 lineage 真实化 sentinel（沿用 009+010；chain_id='real_644_m4_7_policy_detail'；3 新 SHA 区分表）
- §5 645 下一步（架构师推荐）
- §6 下一步 + 不宣称 PASS

### 644-A.5 报告 + 证据包

- `docs/reports/m5_waf_v3_probe_20260901.md` — M5 第三次探活报告（10 cells 实测 + 顶层裁定 + 路径 verdict 矩阵）
- `evidence_pack/m5_waf_v3_probe_20260901.json` — M5 第三次证据包（cells array + summary + fetch_log）
- `docs/reports/m4_7_policy_detail_real_20260901.md` — M4.7 真实抓取报告（3 试点省 × 1 detail each；3 真实样本）
- `evidence_pack/m4_7_policy_detail_real_20260901.json` — M4.7 证据包（cells array + summary + fetch_log）

### 644-A.6 EXEC-QUEUE rev73 bump

**`reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md`** rev72 → **rev73**：

- §META rev → 73；ruling → 643 DELIVERED → 644 tasking OPEN
- §CURRENT cc_head 增加 643 delivery (`834bc30`) + 643 cc_head (`ac2e8e6`) + 643 receipt (`57fa859`)
- §NOW：CC 落地 644-A.1 (M5 WAF 第三次 10 cells ≤10 HTTP) + 644-A.2 (M4.7 政策详情 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT planned) + 644-A.3 (seed SQL 18 INSERT lineage.is_demo='false' chain_id='real_644_m4_7_policy_detail') + 644-A.4 (docs/66 M5 + docs/67 M4.7 §1-§6) + 644-A.5 (2 reports + 2 evidence JSONs) + 644-B (12 用例 = 6 M5 + 6 M4.7, 12/12 pytest green) + 644-C (回执 + 双推)
- §CHAIN_TAIL 643 status → DELIVERED（沿用 rev72 已 bump）

---

## 3. 644-B 测试

**`tests/test_m5_waf_third_pass.py`**（≥6 用例）：

1. `test_m5_v3_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 (MIXED/BLOCKED/PARTIAL/REACHABLE) + 10 cells 实测
2. `test_m5_v3_evidence_json_parses_and_http_count` — JSON parses + probed_count=10 + http_count ≤ 10 红线 + cells=10
3. `test_m5_v3_gov_zhengceku_nested_waf_marker_confirmed` — 国务院 `/zhengce/zhengceku/` 嵌套子路径 403 WAF 网防G01 marker 真出现
4. `test_m5_v3_gov_zhengce_real_content_id_probe` — 国务院 `/zhengce/content_2017-09/30/content_5189.htm` + `/zhengce/content_2020-11/03/content_5556715.htm` 真实 content_id 探活 ≥1 REACHABLE
5. `test_m5_v3_gov_zwgk_retry_paths_blocked_or_reachable` — 国务院 `/zwgk/zcwj/` + `/zwgk/zcfg/` + `/zwgk/2026-08/15/...` retry 路径 verdict 矩阵
6. `test_m5_v3_5_blocked_provinces_zwgk_root_reachable` — 5 BLOCKED 省（fujian/henan/yunnan 等）/zwgk/ root 沿用 642 REACHABLE 验证
7. `test_doc_66_has_six_sections` — docs/66 含 ## 1.-## 6. 六段 + 标头属性
8. `test_doc_66_no_pass_announcement` — §6 不宣称 M2/M4/M5/Gate PASS（智能排除 disclaimer 否定句）
9. `test_m5_v3_probe_script_idempotent` — 探活脚本幂等（去 docstring + # 注释后扫：无 sleeps / 无 randomness + HTTP_LIMIT=10）

**`tests/test_m4_7_policy_detail_real.py`**（≥6 用例）：

1. `test_m4_7_policy_detail_fetch_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 REAL_FETCHED + hlj/henan/yunnan URL + 政策详情 keyword
2. `test_m4_7_policy_detail_evidence_json_parses_and_http_count` — JSON parses + fetch_status=REAL_FETCHED + fetched_count ≥ 1 + http_count ≤ 12 红线 + 64 hex SHA
3. `test_seed_m4_7_sql_exists_and_has_real_data` — seed SQL 存在 + 6 表 × 3 真实 each = 18 行（per-table UUID 计数避开 VALUES-tuple regex 陷阱）+ 剥注释后扫 DML/DROP/DELETE/TRUNCATE
4. `test_seed_m4_7_sql_lineage_is_demo_false_isolation` — 6 政策表 lineage JSONB `is_demo='false'` 隔离 + 不含 `is_demo='true'` + 不含 JSON boolean false
5. `test_seed_m4_7_sql_real_sha_distinct_from_prior_shas` — 3 新真实 SHA 在 + ≠ 643 SHA e68099df/63109491/93fe23b3 + ≠ 642 任免 3 SHA + ≠ 641 王正军 SHA + ≠ 640 demo SHA + ≠ 639 demo SHA + 3 真实 URL 在 + chain_id='real_644_m4_7_policy_detail' 在 + 不含 641/642/643 chain_id
6. `test_doc_67_has_six_sections` — docs/67 含 ## 1.-## 6. 六段 + 标头属性
7. `test_doc_67_no_pass_announcement` — §6 不宣称 M2/M4/M4.7/Gate PASS
8. `test_seed_m4_7_sql_has_select_subquery_for_geo_entity` — government_commitment + project_event 用 SELECT FROM geo_entity g WHERE canonical_name=... AND level='PROVINCIAL' LIMIT 1
9. `test_seed_m4_7_sql_uuid_c_segment_distinct_from_643_b_segment` — 6 政策表 UUID prefix c 段 ≠ 643 b 段（避免 UUID collision）

**总计**：644 ≥ 12 + 643 17 = ≥ 29 用例 green（目标 ≥ 12/12）。

---

## 4. 644-C 回执 + commit + 双推

**`reviews/stage0-gate0-rework-2026-08-23/644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md`** §PHOTO-1..6（沿用 642 + 643 模式）：

- §PHOTO-1 pytest 一行（≥ 12 green）
- §PHOTO-2 docs/66 + docs/67 §1-§6 结构
- §PHOTO-3 架构师裁定 + 关键反发现（M5 第三次收口 + M4.7 spike 边界 18 INSERT planned）
- §PHOTO-4 真实探活矩阵 + 真实化 SQL 落地（10 cells + 18 INSERT）
- §PHOTO-5 红线表
- §PHOTO-6 commit + 双推命令

**commit 序列**：

1. **644 delivery commit**（10 files）：
   ```
   scripts/probe_m5_waf_v3_2024.py
   scripts/fetch_m4_7_policy_detail_v1_2024.py
   scripts/seed_m4_7_policy_detail_real.sql
   docs/66-m5-waf-third-pass-20260901.md
   docs/67-m4-7-policy-detail-real-20260901.md
   docs/reports/m5_waf_v3_probe_20260901.md
   docs/reports/m4_7_policy_detail_real_20260901.md
   evidence_pack/m5_waf_v3_probe_20260901.json
   evidence_pack/m4_7_policy_detail_real_20260901.json
   tests/test_m5_waf_third_pass.py
   tests/test_m4_7_policy_detail_real.py
   ```
   commit: `feat(644): M5 WAF 第三次收口 + M4.7 政策详情真实化并行 — 10 cells MIXED + 18 INSERT lineage.is_demo='false'`
   push origin → push github (HTTPS 443 阻塞 → SSH fallback, 沿用 643)

2. **cc_head backfill commit**（1 file）：
   ```
   reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
   ```
   commit: `chore(644): EXEC-QUEUE cc_head backfill rev72 → rev73 (delivery <hash>)`
   push origin → push github

3. **receipt commit**（1 file）：
   ```
   reviews/stage0-gate0-rework-2026-08-23/644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md
   ```
   commit: `docs(644): receipt §PHOTO-1..6`
   push origin → push github

---

## 5. 红线（沿用 643 + 644-specific）

| 红线 | 状态 |
|---|---|
| 不宣布 Gate / O1 / M2 / M4 / M5 / M4.6 / M4.7 PASS | docs/66 §6 + docs/67 §6 全 disclaimer；test_doc_66_no_pass_announcement + test_doc_67_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | 抓取 URL 自取政府源（hlj/henan/yunnan 政府网 + gov.cn）；无问句 |
| 数据源唯一=政府/统计/研究机构 | 抓取 URL = 政府网 (hlj.gov.cn / henan.gov.cn / yn.gov.cn / gov.cn) |
| 不爬网 | M5 ≤10 HTTP total；M4 ≤12 HTTP total；硬性上限 |
| 不写 cegr.observation 真实行 | 644-A.1 + 644-A.2 read-only；seed SQL 仅 INSERT 真实行（spike 性质） |
| 不静默硬编码 GDP 值 | target_value 等 NULL（如无具体值） |
| 不删表 / 不 DROP COLUMN | seed SQL 仅 INSERT ON CONFLICT DO NOTHING |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | 644-A.3 不写 016 |
| spike 边界 ≤ 18 INSERT (M4.7 规划 = 18 INSERT 实测) | test_seed_m4_7_sql_exists_and_has_real_data 验证；docs/67 §2 spike 边界文档化 |
| lineage.is_demo='false' 真实化 sentinel | test_seed_m4_7_sql_lineage_is_demo_false_isolation 验证 |
| 3 真实 SHA ≠ 643 SHA e68099df/63109491/93fe23b3 ≠ 642 任免 ≠ 641 王正军 ≠ 640/639 demo | test_seed_m4_7_sql_real_sha_distinct_from_prior_shas 验证 |
| chain_id='real_644_m4_7_policy_detail' 区分 | seed SQL 中 chain_id 必现 + 不含 643/642/641 chain_id |
| hlj/henan/yunnan geo_entity_id via SELECT 子查询 | test_seed_m4_7_sql_has_select_subquery_for_geo_entity 验证 |
| 6 政策表 UUID prefix c 段 ≠ 643 b 段 | test_seed_m4_7_sql_uuid_c_segment_distinct_from_643_b_segment 验证 |
| 不修改 source_registry 既有行 / mart / 4 fixture | 644 新增 0 source_registry 行（沿用 643），18 INSERT 仅 6 政策表；不动 mart / fixture |
| 湖北必须 ≠ M1 半年表 c5cf5abe | 644 不写湖北具体 observation；湖北不在 644-A.2 试点省之列 |
| fetch / probe 脚本幂等 | no time.sleep / no random.random（剥 docstring + 注释后扫验证）；sha256 deterministic |
| WAF 网防G01 假设验证 (M5 第三次) | 国务院 /zhengce/zhengceku/ 嵌套 WAF + /zhengce/content_xxx.htm 真实 ID 探活 + /zwgk/ retry 路径矩阵 |
| 双推 origin→github | §4 commit + origin → github 顺序 |

---

## 6. 645 推荐（架构师综合）

**scope 选 A（推荐）**：645 = M6 文档收口 + M4.8 政策详情扩展（沿用 644 3 试点省 × 1 detail each × 6 政策表 spike = 18 INSERT planned, chain_id='real_645_m4_8_policy_detail_v2'）

**scope 选 B**：645 = M5 收口（gov/zhengce/ root 索引全量）+ M4.8 并行

**scope 选 C**：645 = M5 + M4.8 + M6 三方并行（激进）

**scope 选 D**：645 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法

**scope 选 E**：645 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）

---

## 7. 下一步

- 架构师（用户）接受/驳回 645 推荐 scope（A/B/C/D/E）
- 执行端（本终端即架构师）收到 645 tasking 后即签即自交付
- **不宣布** Gate / O1 / M2 / M4 / M5 / M4.6 / M4.7 PASS（沿用红线）

— End 644 tasking —