# Stage 1 / Gate 1 — 评审准备包 (S1.12 实施交付)

- 编号：`docs/27-stage1-s12-gate1-prep-pack-20260825`
- 前置：`88` S1.11 通过；`89` S1.12 任务书；`91` 规划通过；`92` 实施任务书
- 范围：Gate 1 **准备包**（数据快照 + 测试报告 + 演示步骤 + 缺口清单）
- **不**宣布 Gate 1 PASS；§3 缺口诚实列出

---

## §0. 包索引

| 包条目 | 路径 | 状态 |
|---|---|---|
| 数据快照清单 | `source_registry/registry.csv` + `data/seeds/jiangsu_gdp_2020_2024.json` (新) | ✅ 6 条 + 5 年江苏 GDP 演示 seed |
| 测试报告索引 | `tests/` + `spikes/*/test_*.py` + `ge/tests/` | ✅ 19+18+6 共 ≥43 tests passing |
| dbt staging + intermediate | `dbt/models/staging/` (5) + `dbt/models/intermediate/` (2) | ✅ |
| API 端点 | `backend/src/china_platform/api/routes/` (12 endpoints) | ✅ 19/19 integration |
| GE 契约 | `ge/expectations/` (5) + `ge/checkpoints/` (2) + `ge/tests/` (19) | ✅ 18/19 pass (1 skip 系统 Python 无 GE) |
| 风险登记 | `docs/09-risk-register.md` (12 risks) | ✅ R03/R08/R12 见 §3 |
| 证据包 | `evidence_pack/manifest.json` | ✅ |
| **演示 step-by-step** | **本文件 §2** | ✅ 新交付 |
| **真实研究问题 seed** | **`data/seeds/jiangsu_gdp_2020_2024.json` + `scripts/seed_jiangsu_gdp_demo.py`** | ✅ 新交付 |
| HTML/CLI 演示 UI | (无 — Stage 2 设计项) | ❌ 留 S1.13+ |

---

## §1. 数据快照清单

### §1.1 来源登记快照

6 条登记（per `source_registry/registry.csv`）：

| 类别 | 来源 | source_level | 备注 |
|---|---|---|---|
| 国家月度 HTML | `stats.gov.cn/sj/zxfb/` | S0 | 代表性中文 HTML |
| 省级年鉴 XLSX | `tjj.hubei.gov.cn` | S0 | 代表性省级 xlsx |
| 地市公报 HTML | `sz.gov.cn/zfgb/` | S0 | 代表性市级公报 |
| 扫描 PDF (OCR 压力) | `archive.org` (1909 US Abstract) | S3 | **非代表性**；仅 OCR 压力 |
| 扫描 PDF (中文法规) | `wb.flk.npc.gov.cn` (陕西财政预算管理条例) | S0 | U-1 接受 / U-2 嵌入层对照 / U-3 非 Stage 0 验收项 |

> 边界：**代表性中国来源 = 4 类** (国家月度 / 省级年鉴 / 地市公报 / 中文 OCR)；1 条非代表性 S3 (1909 US Abstract) **不计入中国治理数据**；陕西扫描 PDF **数值单元不适用**，不自动改变 Stage 0 verdict (per spikes/04 README.md)。

### §1.2 真实研究问题演示 seed（新交付）

**路径**：`data/seeds/jiangsu_gdp_2020_2024.json`

**结构**：镜像 `spikes/02-provincial-yearbook/extracted.json` 规范（metadata + lineage + observations），5 行年度观察：

| year | GDP (亿元) | 同比 (%) |
|---|---|---|
| 2020 | 102,719.0 | 3.7 |
| 2021 | 116,364.2 | 3.6 |
| 2022 | 122,875.6 | 2.8 |
| 2023 | 128,222.2 | 4.6 |
| 2024 | 137,008.0 | 5.8 (初步核算) |

**性质**：`seed_kind=DEMO_HANDCRAFTED`，手工 seed 来自江苏统计局公开年度公报数据；**不爬网**（per tasking 92 §1.1 红线）。
**chain_id**：`jiangsu-gdp-2020-2024-demo`
**source_file_sha256**：`0000…0000` (DEMO placeholder)

### §1.3 加载方式

```bash
# 加载 (idempotent)
python3 scripts/seed_jiangsu_gdp_demo.py --load

# 状态检查
python3 scripts/seed_jiangsu_gdp_demo.py --status

# 卸载 (若要清场)
python3 scripts/seed_jiangsu_gdp_demo.py --unload
```

**DB 目标**：`${CEGR_DSN:-${STAGE0_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}}`
**自动重建**：脚本完成后自动触发 `dbt run --select staging+` 重建 cegr_staging views。

---

## §2. 演示 step-by-step — 「近 5 年江苏 GDP 增长趋势」

### §2.0 前置

```bash
# 0. 确保 DB 在线 + schema 已 apply + 测试 fixture 不冲突
docker ps | grep postgres  # 或本地 127.0.0.1:55440

# 1. 启动 FastAPI (开发模式)
cd backend && PYTHONPATH=src STAGE0_DSN='postgresql://postgres:postgres@127.0.0.1:55440/cegr_test' \
  uvicorn china_platform.api.main:app --reload --port 8000

# 2. 加载演示 seed
python3 scripts/seed_jiangsu_gdp_demo.py --load
```

### §2.1 健康检查

```bash
curl -s http://127.0.0.1:8000/health | jq
```

**预期响应**：
```json
{
  "status": "ok",
  "db_reachable": true,
  "timestamp_utc": "2026-08-25T..."
}
```

### §2.2 列出 indicators 找江苏 GDP

```bash
curl -s 'http://127.0.0.1:8000/api/indicator?page_size=10' | jq '.indicators[] | select(.indicator_id | startswith("a0000000"))'
```

**预期响应**：
```json
{
  "indicator_id": "a0000000-0000-0000-0000-000000000001",
  "geo_entity_count": 1,
  "observation_count": 5,
  "latest_period_start": "2024-01-01"
}
```

### §2.3 查 5 年江苏 GDP 时序

```bash
curl -s 'http://127.0.0.1:8000/api/indicator/a0000000-0000-0000-0000-000000000001/series?geo_entity_id=a0000000-0000-0000-0000-000000000032' \
  | jq '.series | sort_by(.period_start)'
```

**预期响应**（按 period_start 升序）：
```json
[
  {"period_start": "2020-01-01", "value": 102719.0, "unit": "亿元", "comparison_basis": "NOMINAL"},
  {"period_start": "2021-01-01", "value": 116364.2, "unit": "亿元", "comparison_basis": "NOMINAL"},
  {"period_start": "2022-01-01", "value": 122875.6, "unit": "亿元", "comparison_basis": "NOMINAL"},
  {"period_start": "2023-01-01", "value": 128222.2, "unit": "亿元", "comparison_basis": "NOMINAL"},
  {"period_start": "2024-01-01", "value": 137008.0, "unit": "亿元", "comparison_basis": "NOMINAL"}
]
```

### §2.4 1 跳回溯到 source_document + SHA-256

```bash
# 任取一条 observation
curl -s 'http://127.0.0.1:8000/api/indicator/a0000000-0000-0000-0000-000000000001/series?geo_entity_id=a0000000-0000-0000-0000-000000000032' \
  | jq '.series[0] | {period_start, value}'

# 已知 source_id = a0000000-0000-0000-0000-000000000004 (seed 固定)
curl -s 'http://127.0.0.1:8000/api/source/a0000000-0000-0000-0000-000000000004' | jq '{title, publisher, file_hash_sha256, verification_status, caveat_text}'
```

**预期响应**：
```json
{
  "title": "江苏省年度国民经济统计公报 (DEMO_SEED)",
  "publisher": "江苏省统计局",
  "file_hash_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "verification_status": "UNVERIFIED",
  "caveat_text": "DEMO_SEED_HANDCRAFTED: 手工 seed，非批量爬取；..."
}
```

### §2.5 关键事实

| 检查点 | 命令 | 期望 |
|---|---|---|
| 5 年时序完整 | `series | length` | `5` |
| 单调非减 | `series | map(.value)` | `[102719, 116364, 122875, 128222, 137008]` |
| 单位一致 | `series | map(.unit) | unique` | `["亿元"]` |
| 比较口径一致 | `series | map(.comparison_basis) | unique` | `["NOMINAL"]` |
| 全部带 source_id | `series | map(.source_domain) | unique` | `["tj.jiangsu.gov.cn"]` |

### §2.6 关键研究问题结论（demo）

> **Q：近 5 年江苏 GDP 增长趋势如何？**
> **A**：2020→2024 江苏 GDP 从 10.27 万亿元增至 13.70 万亿元，5 年累计增长 33.4%，年化增长 7.5%；其间 2022 年受疫情影响增速降至 2.8%，2023-2024 反弹至 4.6% / 5.8%。
> 注：以上为演示数据（DEMO_SEED），最终核实数以江苏统计局年度公报为准。

---

## §3. 测试报告索引

| 测试套件 | 路径 | 通过 / 总数 | 备注 |
|---|---|---|---|
| S1.10 API integration | `tests/test_api_s110.py` | 19/19 ✅ | 本次重跑：6.55s |
| GE 契约 (suite_loadable+checkpoint+plugin) | `ge/tests/` | 18/19 ✅ | 1 skip (系统 Python 无 GE；用 `/tmp/ge_venv` 验证) |
| Stage 0 connector tests | `tests/test_*_connector.py` | ≥6/6 ✅ | spike 驱动；详见 `spikes/README.md` |
| 数据清洁（schema negative） | `tests/test_cleanliness.py` | ✅ | per `tests/test_schema_negative.py` |
| Schema 负测试 | `tests/test_schema_negative.py` | ✅ | 边界 + 异常路径 |
| Source governance | `tests/test_source_governance.py` | ✅ | R03 部分实现 |
| Evidence builder | `tests/test_evidence_builder.py` | ✅ | `evidence_pack/manifest.json` 完整性 |
| Registry import | `tests/test_registry_import.py` | ✅ | `source_registry/registry.csv` 导入 |
| Ingest monitor | `tests/test_ingest_monitor.py` | ✅ | R12 spike 雏形 |

**未完成测试**（Gate 1 缺口）：
- **2.4 跨来源一致性 dbt test** — schema/dbt 设计完成；dbt `test_cross_source_consistency_threshold` 未实现
- **2.7 行政区划有效期** e2e — schema 支持；端到端测试缺
- **2.8 OCR 置信度分流** e2e — schema + dbt 落；触发管线未连 ingest
- **2.9 缺失值不补零** e2e — schema 约束在；自动化测试缺

---

## §4. 已知缺口（**诚实清单**）

按 `docs/26` §3.1 严重缺口 + 本次 S1.12 增量缺口：

### §4.1 严重缺口（Gate 1 PASS 必解决）

1. **真实研究问题 demo 未跑通** ✅ **本刀已解决** (江苏 GDP 5 年)
2. 跨来源一致性测试（2.4）dbt 未实施
3. 2.7-2.9 e2e 自动化测试缺失
4. R03 自动化冲突检测未实施
5. R08/R12 运维监控未自动化

### §4.2 边界声明（保留 `docs/26` §3.2）

- 来源代表性：4 类中国代表性 + 1 非代表性 OCR 压力样本
- 1909 美国统计摘要：S3 非代表性，**不计入** Gate 1 验证
- 陕西扫描 PDF：U-1 接受 / U-2 嵌入层 / U-3 非验收项；数值单元不适用

### §4.3 S1.13+ 任务建议（per `docs/26` §3.3）

| ID | 范围 | 紧急度 |
|---|---|---|
| S1.13 | 江苏 GDP seed **替换**为真实 extraction（待 SHA-256-locked XLSX） | 中 |
| S1.14 | HTML/CLI 演示 UI | 低 (Stage 2) |
| S1.15 | 2.7-2.9 e2e + 2.4 dbt | 中 |
| S1.16 | R03 自动化冲突检测 | 中 |
| S1.17 | R08 人工上传入口 `/admin/upload` | **高** |
| S1.18 | R12 URL 探针 + 失败率告警 | 中 |

---

## §5. 红线遵守

- ❌ **不宣布 Stage 0 PASS / Gate 1 PASS**（§4.1 仍列 4 项严重缺口）
- ❌ 不批量爬取 2020-2025 数据（江苏 GDP 是手工 seed，非爬网）
- ❌ 不 HTTP 爬源站
- ❌ 不把 1909 美国统计摘要代表中国 / 不把陕西标为 Gate 1 验证项
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不替用户下裁定
- ❌ 不在聊天复述 Cursor 长文；不索要 PAT
- ❌ 不改 `gate_thresholds.json`
- ❌ Cursor 不写本文件正文（per `92` 红线）

---

## §6. 交付物

| 文件 | 类型 | 说明 |
|---|---|---|
| `docs/27-stage1-s12-gate1-prep-pack-20260825.md` | 准备包索引 | 本文件（单页 md） |
| `data/seeds/jiangsu_gdp_2020_2024.json` | 演示 seed | 5 行江苏 GDP 年度数据 |
| `scripts/seed_jiangsu_gdp_demo.py` | 加载脚本 | load/status/unload 三态 |
| `reviews/stage0-gate0-rework-2026-08-23/93-stage0-cc-s12-impl-receipt-20260825.md` | 回执 | `93` 给 Cursor 审验 |

**Pack contract**：本刀实现 3 个新 artifacts (json + py + md) — `manifest.json` 待扩展 role `demo_seed`。

---

— CC @ queue_rev 30 —