# Stage 1 — S1.4 NBS-MONTHLY 连接器规划

> 文件：`docs/18-stage1-s14-nbs-connector-plan-20260824.md`  
> 起草：Cursor（CC 未 pull 时代劳，避免流水线停滞）  
> 依据：`docs/08` S1.4、`spikes/01-national-yearbook/`、`docs/10` §2.1–2.6  
> 范围：**W2–W3 规划 + 单期试点**；不批量 2020–2025

---

## §0. TL;DR

| 项 | 决策 |
|---|---|
| 基线 spike | `01-national-yearbook`（HTML 月度 zxfb 表） |
| 试点 | **1 期**（已有 `sample.html` SHA 可复现） |
| 生产路径 | `backend/src/china_platform/connectors/nbs_monthly.py` |
| ingest | 写 `ingest_run` + `source_document` + observations（schema 已有） |
| 验证 | `docs/10` 2.1–2.6 映射到 pytest；Gate 1 前不全量 |
| 禁止 | 批量历史爬取；skip-as-PASS |

---

## §1. 目录与模块

```
backend/src/china_platform/
├── connectors/
│   ├── __init__.py
│   └── nbs_monthly.py      # 从 spike extract_01 提炼；HTTP 可选参数
├── ingest/
│   └── runner.py           # 创建 ingest_run、失败计数（S1.8 前最小版）
tests/
└── test_nbs_monthly_connector.py
```

**策略：** 先 **file:// 或 repo 内 sample.html** 跑通入库链；真 HTTP 仅 `--live-url` 显式开关且单 URL。

---

## §2. ingest_run 挂钩

1. `INSERT ingest_run (source_registry_id, status='RUNNING', ...)`
2. 解析 → `source_document`（file_hash_sha256 必填）
3. observations 批量 insert（关联 document_id + page_locator）
4. 成功 → `COMPLETED`；校验失败 → `FAILED` + error_summary

与 `tests/conftest.py` apply 链共用 `cegr_test` / 55440。

---

## §3. docs/10 §2.1–2.6 映射

| 测试 | 连接器责任 |
|---|---|
| 2.1 单位/数量级 | 保留 spike 单位字段；staging 层 dbt 前校验 |
| 2.2 合计 | 单行 obs 不做行内合计；留 Stage 1 dbt |
| 2.3 同比反算 | 提取 yoy 列时存 raw + parsed |
| 2.4 跨来源 | 本连接器仅 NBS；跨源 Stage 3 |
| 2.5 时间序列 | 单期试点仅 smoke |
| 2.6 修订 | metadata `revision_note` 占位 |

**S1.4 试点退出：** 1 期 HTML → DB → pytest 证明 hash 回溯 + ≥20 obs。

---

## §4. 失败 / 重试

- 网络：`failure_handling` 读 registry CSV（`docs/03`）
- 解析：rc=2，ingest_run FAILED，不部分 commit
- 禁止：`pytest.skip` 掩盖缺失样本

---

## §5. 下一刀（CC 或 Cursor 实现）

见 `reviews/.../36-stage1-s14-nbs-implementation-*.md`（Cursor 下发）：实现 `nbs_monthly.py` + 单期入库测试。

— End —
