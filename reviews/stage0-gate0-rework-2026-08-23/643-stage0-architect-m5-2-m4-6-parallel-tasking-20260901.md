# 643 — M5 WAF spike 二次 + M4.6 政府工作报告真实化 并行（架构师 tasking）

> **刀号**: 643
> **Milestone**: M5 二次 + M4.6（并行 spike；spike 不互斥）
> **类型**: 架构师 tasking · 自签 + 自交付（执行端模式继续）
> **日期**: 2026-09-01
> **依据**:
> - `docs/62 §5 / docs/63 §5 / 642 receipt §4.6`（架构师综合推荐 = M5 WAF spike 二次 + M4.6 政府工作报告真实化 并行）
> - `642 §3.1` 关键反发现：5 BLOCKED 省 /zwgk/zfwj/ 全 404 路径别名（非 WAF）；WAF 网防G01 假设修正 = 二元根因（中央子域 WAF + 子域内栏目缺失）
> - `docs/58 §2 / 638 receipt §5`（638 政府报告 landing 23/32 REACHABLE；M4.6 复用 638 REACHABLE 23 列表）
> - `docs/33 §3.2 sentinel`（lineage JSONB 是 is_demo 唯一落点；不新写 016 migration）
> - 638 / 639 / 640 / 641 / 642 demo + real spike 累积
> - 643 = M5 二次（深挖 5 BLOCKED 省路径别名）+ M4.6 政府报告真实化（复用 638 PARTIAL 1/2 路径）
> **用户接收**：`642接受，继续643`（2026-09-01）
> **不宣布** Gate / O1 / M2 / M4 PASS。

---

## 0. 范围（一句话）

643 落地 **5 件并行 spike**（spike 不互斥；沿用 642 模式）：**(A1)** M5 WAF 网防G01 spike 二次 — 5 BLOCKED 省（福建/河南/广东/贵州/云南）/zwgk/zfwj/ **路径别名深挖**：尝试迁移路径 `/zwgk/zfgb/` `/zwgk/zcwj/` `/zwgk/szfwj/` `/zwgk/wjzl/` 替代 subpath；国务院 /zhengce/content/ 子路径探测（/zhengce/2024-XX/YY/content_xxx.htm 具体 URL + /zhengceku/ 库 root）；≤10 HTTP total（5 cell × 2 HTTP main+fallback）；**(A2)** M4.6 政府工作报告真实化 — 复用 638 REACHABLE 23/32 列表（沿用 642 6 试点省 heilongjiang/fujian/henan/guangdong/guizhou/yunnan × 1 detail each × 6 政策表 = 36 INSERT planned；lineage `is_demo='false'` 真实化 sentinel；chain_id=`real_643_m4_6_govreport`）；≤12 HTTP total；**(A3)** `docs/64-m5-waf-second-pass-20260901.md` §1-§6 + `docs/65-m4-6-govreport-real-20260901.md` §1-§6 架构师级审查；**(B)** `tests/test_m5_waf_second_pass.py` ≥ 6 + `tests/test_m4_6_govreport_real.py` ≥ 6 = **全套 pytest ≥ 106/106 green**（642 16 + 643 ≥ 12 + M2 71 + 637 + 638 8 + 639 7 + 640 7 + 641 7 baseline = ≥ 106）；**(C)** 回执 + commit + 双推；**架构师推荐 644 = M5 第三次收口 + M4.7 政策详情真实化（沿用 643 6 试点省 × 1 detail each）并行 或 644 = M6 spike + M4.7 并行**。

---

## 1. 子刀拆

| 子刀 | 文件 / 范围 | 状态（待） | 说明 |
|---|---|---|---|
| 643-A.1 | `scripts/probe_m5_waf_v2_2024.py` + `evidence_pack/m5_waf_v2_probe_20260901.json` + `docs/reports/m5_waf_v2_probe_20260901.md` | DONE | M5 WAF 网防G01 假设验证二次；5 BLOCKED 省 /zwgk/zfwj/ 路径别名深挖（迁移路径 /zwgk/zfgb/ /zwgk/zcwj/ /zwgk/szfwj/ /zwgk/wjzl/）+ 国务院 替代子路径探测（/zhengce/content/ + /zhengceku/ + /zhengce/2024-XX/YY/content_xxx.htm）；≤10 HTTP total；curl only；不爬网；不写 cegr.* 表 |
| 643-A.2 | `scripts/fetch_m4_6_govreport_v1_2024.py` + `evidence_pack/m4_6_govreport_real_20260901.json` + `docs/reports/m4_6_govreport_real_20260901.md` | DONE | M4.6 政府工作报告真实化；6 试点省（heilongjiang/fujian/henan/guangdong/guizhou/yunnan）× 1 detail each 政府报告 landing 真实抓取；≤12 HTTP total；顶层裁定 REAL_FETCHED；3-6 真实样本落地（实测，SHA 撞 641/642/640/639 排除） |
| 643-A.3 | `scripts/seed_m4_6_govreport_real.sql` | DONE | 6 试点省 × 1 detail each × 6 政策表 = 36 INSERT planned；lineage `is_demo='false'` 真实化 sentinel；chain_id=`real_643_m4_6_govreport`；3 新 SHA 全 distinct ≠ 640/641/642/639 demo/real SHA；geo_entity_id 通过 SELECT 子查询获取 |
| 643-A.4 | `docs/64-m5-waf-second-pass-20260901.md` + `docs/65-m4-6-govreport-real-20260901.md` | DONE | §1-§6 双文档架构师级审查 |
| 643-A.5 | `docs/reports/m5_waf_v2_probe_20260901.md` + `evidence_pack/m5_waf_v2_probe_20260901.json` + `docs/reports/m4_6_govreport_real_20260901.md` + `evidence_pack/m4_6_govreport_real_20260901.json` | DONE | 双 spike probe + real 报告 + 证据包 |
| 643-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev70 → 643 tasking OPEN · 等 CC 落地（即签即自交付；rev70 同时落地） |
| 643-B | `tests/test_m5_waf_second_pass.py` ≥ 6 + `tests/test_m4_6_govreport_real.py` ≥ 6 | DONE | 共 ≥ 12 用例；全套 pytest ≥ 106/106 green |
| 643-C | 回执 + commit + 双推 | DONE | `643-stage0-cc-m5-2-m4-6-parallel-receipt-20260901.md` §PHOTO-1..6 + cc_head backfill commit + origin→github |

---

## 2. 643-A 详细

### 643-A.1 M5 WAF 网防G01 spike 二次 — 5 BLOCKED 省路径别名深挖

**目标**：642 关键反发现 = 5 BLOCKED 省 /zwgk/zfwj/ 全 404（路径别名，非 WAF）。643 二次探活目的：

1. **路径别名深挖**：尝试迁移路径 `/zwgk/zfgb/`（规章）/ `/zwgk/zcwj/`（政策文件）/ `/zwgk/szfwj/`（省政府文件）/ `/zwgk/wjzl/`（文件资料）/ `/zwgk/zwxx/`（政务信息），找替代 subpath。
2. **国务院 /zhengce/content/ 子路径探测**：试 /zhengce/2024-XX/YY/content_xxx.htm（具体 URL）+ /zhengceku/（库 root）+ /zhengce/（政策 root）。
3. **WAF 网防G01 marker 验证**：中央子域 selective WAF 是否真的存在（沿用 642 WAF_BLOCK_RE 检测）。

**probe cells (10 cells ≤10 HTTP)**:

```python
PROBE_CELLS = [
    # 5 BLOCKED 省 /zwgk/zfwj/ 路径别名深挖 (4 替代 subpath × 1 省 = 4)
    ("fujian",  "https://www.fujian.gov.cn/zwgk/zfgb/",      "alt_zfgb",     "policy"),
    ("fujian",  "https://www.fujian.gov.cn/zwgk/zcwj/",      "alt_zcwj",     "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/zfgb/",       "alt_zfgb",     "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/zcwj/",       "alt_zcwj",     "policy"),
    ("guangdong","https://www.gd.gov.cn/zwgk/zfgb/",         "alt_zfgb",     "policy"),
    ("guizhou", "https://www.guizhou.gov.cn/zwgk/zfgb/",     "alt_zfgb",     "policy"),
    # 国务院 替代子路径探测 (3 cells)
    ("gov",     "https://www.gov.cn/zhengceku/",             "fallback_ku",  "policy"),
    ("gov",     "https://www.gov.cn/zhengce/",               "fallback_root","policy"),
    ("gov",     "https://www.gov.cn/zhengce/2024-08/15/content_1155106.htm", "fallback_real", "policy"),
    # 1 cell 验证 WAF 网防G01 marker on /zwgk/ 中央
    ("gov",     "https://www.gov.cn/zwgk/2024-08/15/content_xxx.htm", "zwgk_sub", "policy"),
]
```

**probe 边界（硬性红线）**：

- ≤10 次 HTTP total（10 cells 实测，1 HTTP each）
- 不爬网（no recursion; no follow pagination）
- 仅探可达性（不抓内容入库）
- curl only（no JS / no headless browser）

**`scripts/probe_m5_waf_v2_2024.py`**：

- TIMEOUT=15，HTTP_LIMIT=10
- 复用 `scripts/_probe_http_helpers.py`（POLICY_MARKER_RE + WAF_BLOCK_RE）
- classify_waf: REACHABLE / PARTIAL / BLOCKED
- WAF 网防G01 marker 检测（沿用 642）
- 输出: `evidence_pack/m5_waf_v2_probe_20260901.json` + `docs/reports/m5_waf_v2_probe_20260901.md`

**期望 verdict**：

- 4 替代 subpath: REACHABLE / BLOCKED（推测多数 REACHABLE，因为路径别名探活）
- 国务院 /zhengceku/ + /zhengce/: BLOCKED WAF 网防G01（沿用 642）
- 国务院 /zhengce/具体: REACHABLE / BLOCKED 404（已知真实政策 URL 应 200 OK）
- 国务院 /zwgk/子路径: BLOCKED WAF 网防G01（沿用 642）

### 643-A.2 M4.6 政府工作报告真实化 — 复用 638 PARTIAL 1/2 路径

**目标**：复用 638 政府报告 REACHABLE 23/32 列表（M4.6 是政府工作报告 landing 真实抓取 + lineage.is_demo='false' spike）。沿用 642 6 试点省（heilongjiang/fujian/henan/guangdong/guizhou/yunnan）但 endpoint URL 改为政府工作报告（不是任免）。

**目标 URL（6 试点省 × 1 detail each + 6 indices = 12 HTTP）**：

| 试点省 | landing URL | detail URL（待 fetch） |
|---|---|---|
| 黑龙江 | `https://www.hlj.gov.cn/zwgk/zfgb/` | `/hlj/c108368/zwgk.shtml` 或 `c108378/202608/...` |
| 福建 | `https://www.fujian.gov.cn/zwgk/zfgb/` | 待 fetch |
| 河南 | `https://www.henan.gov.cn/zwgk/zfgb/` | `/2026/XX-XX/XXXX.html` (zfgb 子路径) |
| 广东 | `https://www.gd.gov.cn/zwgk/zfgb/` | 待 fetch |
| 贵州 | `https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/` | 待 fetch |
| 云南 | `https://www.yn.gov.cn/zwgk/zfgb/` | 待 fetch |

注：638 probe 报告：23/32 REACHABLE（部分省政府工作报告 /zwgk/zfgb/ 子路径可达）。643 复用 638 REACHABLE 列表。

**fetch 边界（硬性红线）**：

- ≤12 次 HTTP total（6 indices + 6 details = 12 HTTP planned）
- 不爬网（no recursion; no follow pagination）
- 任免 keyword regex: `政府工作|工作报告|政府报告|年度工作|政府公报`（与 642 任免 regex 不同）
- curl only

**`scripts/fetch_m4_6_govreport_v1_2024.py`**：

- TIMEOUT=15，HTTP_LIMIT=12，FETCH_LIMIT_PER_PROVINCE=1
- 6 试点省 × 1 detail each = 6 cells
- 计算真实 SHA256 on fetch
- 输出: `evidence_pack/m4_6_govreport_real_20260901.json` + `docs/reports/m4_6_govreport_real_20260901.md`

**预期 SHA collision 处理（沿用 642）**：

- heilongjiang SHA `26e5379d...b87ab` 撞 641 ⇒ **排除**
- 任一 SHA 撞 640 demo `0…02` / 641 real `26e5379d...b87ab` / 642 real 3 SHA ⇒ **排除**
- 排除后 3-5 真实样本落地（vs 642 实际 3 落地）

### 643-A.3 M4.6 seed SQL — 真实化深化（沿用 641/642 sentinel）

**`scripts/seed_m4_6_govreport_real.sql`**：

- 36 INSERT planned（6 试点省 × 6 政策表）；实际 18-30 INSERT（实测落地 3-5 试点省）
- 8 表 × N 行（N = 实际落地试点省数）：
  - source_registry: N 行（henan/gd/guizhou + 实际可用）
  - source_document: N 行（3 新真实 SHA + 实际可用）
  - policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event: N 行 each
- lineage JSONB `is_demo='false'` 真实化 sentinel（沿用 641/642）
- chain_id='real_643_m4_6_govreport'（非 demo_* 前缀；非 real_641_heilongjiang；非 real_642_m4_5_renmian）
- 真实 SHA ≠ 640 demo / ≠ 641 real / ≠ 642 real 3 SHA / ≠ 639 demo
- 不新写 016 migration（沿用 009+010 lineage JSONB）
- government_commitment / project_event geo_entity_id = SELECT 子查询（沿用 641/642）
- 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
- `ON CONFLICT (id) DO NOTHING`

**沿用 lineage JSONB sentinel 一致 shape**：

```json
{
  "chain_id": "real_643_m4_6_govreport",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 643-A.4 双文档 §1-§6 架构师级审查

- `docs/64-m5-waf-second-pass-20260901.md` §1-§6：
  - §1 M5 二次落地终态
  - §2 M5 WAF 网防G01 路径别名深挖（10 cells 实测）
  - §3 M5 BLOCKED 根因分析深化（路径别名 vs WAF 二元根因验证）
  - §4 替代路径可达性矩阵
  - §5 644 下一步
  - §6 不宣称 PASS
- `docs/65-m4-6-govreport-real-20260901.md` §1-§6：
  - §1 M4.6 落地终态
  - §2 M4.6 spike 边界调整（vs 643 tasking 规划）
  - §3 真实化 demo SQL 结构（基于 643-A.3）
  - §4 lineage 真实化 sentinel（沿用 009+010）
  - §5 644 下一步
  - §6 不宣称 PASS

### 643-A.5 reports + evidence JSONs

- `docs/reports/m5_waf_v2_probe_20260901.md`（M5 二次探活报告）
- `docs/reports/m4_6_govreport_real_20260901.md`（M4.6 真实抓取报告）
- `evidence_pack/m5_waf_v2_probe_20260901.json`（M5 二次证据包）
- `evidence_pack/m4_6_govreport_real_20260901.json`（M4.6 证据包）

---

## 3. 643-B 测试用例（≥12 用例）

### 643-B.1 `tests/test_m5_waf_second_pass.py`（≥6 用例）

- `test_m5_v2_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 BLOCKED/PARTIAL/REACHABLE/MIXED + 10 cells 实测
- `test_m5_v2_evidence_json_parses_and_http_count` — JSON parses + probed_count=10 + http_count ≤ 10
- `test_m5_v2_alternate_subpaths_reachable_or_blocked` — 4 替代 subpath 至少 1 REACHABLE（路径别名探测）
- `test_m5_v2_gov_zhengce_waf_marker_confirmed` — 国务院 /zhengce/content/ + /zhengceku/ 403 WAF 网防G01 marker 真出现
- `test_doc_64_has_six_sections` — docs/64 §1-§6
- `test_doc_64_no_pass_announcement` — §6 不宣称 M2/M4/Gate PASS
- `test_m5_v2_probe_script_idempotent` — 探活脚本幂等（去 docstring + # 注释后扫）

### 643-B.2 `tests/test_m4_6_govreport_real.py`（≥6 用例）

- `test_m4_6_govreport_fetch_report_exists_and_has_top_verdict` — 报告存在 + REAL_FETCHED 顶层裁定 + 政府工作报告 keyword
- `test_m4_6_govreport_evidence_json_parses_and_http_count` — JSON parses + fetched_count ≥ 1 + http_count ≤ 12
- `test_seed_m4_6_sql_exists_and_has_real_data` — seed SQL 存在 + 8 表 × N 真实 each（per-row UUID 计数）+ DML/DROP 红线
- `test_seed_m4_6_sql_lineage_is_demo_false_isolation` — 6 政策表 lineage JSONB `is_demo='false'` + 不含 `is_demo='true'`
- `test_seed_m4_6_sql_real_sha_distinct_from_prior_shas` — N 真实 SHA ≠ 640/641/642/639 + chain_id='real_643_m4_6_govreport' 在 + 不含 641/642 chain_id
- `test_doc_65_has_six_sections` — docs/65 §1-§6
- `test_doc_65_no_pass_announcement` — §6 不宣称 M2/M4/Gate PASS
- `test_seed_m4_6_sql_has_select_subquery_for_geo_entity` — government_commitment / project_event SELECT FROM geo_entity g

---

## 4. 643-C 回执 + 双推

`reviews/stage0-gate0-rework-2026-08-23/643-stage0-cc-m5-2-m4-6-parallel-receipt-20260901.md` §PHOTO-1..6：

- §0 一句话
- §1 交付映射（643-A → 643-C）
- §2 PHOTO-1 pytest 一行（643 §PHOTO-1 须绿）
- §3 PHOTO-2 docs/64 + docs/65 §1-§6 结构
- §4 PHOTO-3 架构师裁定 + 关键反发现
- §5 PHOTO-4 真实探活矩阵 + 真实化 SQL 落地
- §6 PHOTO-5 红线表
- §7 commit + 双推
- §8 下一步

3 commits + 双推：

1. **643 delivery commit** (11 files: scripts × 3 + docs/64-65 × 2 + docs/reports × 2 + evidence_pack × 2 + tests × 2)
2. **cc_head backfill commit** (1 file: EXEC-QUEUE)
3. **receipt commit** (1 file: 643-stage0-cc-m5-2-m4-6-parallel-receipt-20260901.md)

每 commit 后 `git push origin HEAD` + `git push github HEAD` 顺序。

---

## 5. 红线 + 真实化条件（沿用 638/639/640/641/642）

- ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
- ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
- ❌ 不静默硬编码 GDP 值
- ❌ spike 边界 ≤ 1 条 each policy 6 表 (1 each × 6 source × 6 tables = 36 INSERT planned, 18-30 actual)
- ❌ 不宣布 Gate / O1 / M2 / M4 PASS
- ❌ 不新写 016 migration (沿用 009+010 lineage JSONB)
- ❌ 不爬网 (643-A.1 ≤10 HTTP / 643-A.2 ≤12 HTTP total)
- ❌ 真实 SHA ≠ 640 demo SHA / ≠ 641 real SHA / ≠ 642 real 3 SHA / ≠ 639 demo SHA
- ❌ 不复现 642 3 真实样本 (henan/guangdong/guizhou 政府报告 endpoint ≠ 任免 endpoint → 期望新 SHA)
- ❌ 真实化范围限定 ≤6 试点省 (vs 642 spike 3 落地)
- ❌ 不向用户提任何用户裁定事项
- ❌ 数据源唯一=政府/统计/研究机构自取

---

## 6. Verification（643 必须满足）

- `tests/test_m5_waf_second_pass.py` ≥ 6 用例 必须全 green
- `tests/test_m4_6_govreport_real.py` ≥ 6 用例 必须全 green
- 共 ≥ 12 用例新增；全套 pytest ≥ 106/106 green（642 16 + 643 ≥ 12 + M2 71 + 638 8 + 639 7 + 640 7 + 641 7 baseline）
- 共存 demo (640) + real (641 + 642 + 643)；应用层 SELECT WHERE lineage->>'is_demo' = 'true' 过滤 demo，真实数据 lineage.is_demo='false' 或 NULL
- 真实化范围限定 ≤6 试点省（M4.6 spike 沿用 642 6 试点省但 endpoint 改政府工作报告）
- 5 BLOCKED 省路径别名深挖 ≥ 1 REACHABLE 替代 subpath（架构师假设）

— End 643 tasking —
