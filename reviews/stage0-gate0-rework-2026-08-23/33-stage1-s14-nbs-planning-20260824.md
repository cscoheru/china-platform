# Stage 1 — S1.4 NBS 连接器规划（基于 spike 01）

- 文件编号：`33-stage1-s14-nbs-planning-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 前置：`32` S1.3 通过

---

## §0. NOW（禁止 IDLE）

| # | 任务 | 退出标准 |
|---|---|---|
| 1 | 新建 **`docs/18-stage1-s14-nbs-connector-plan-20260824.md`** | 基于 spike 01；范围 W2–W3；**不**批量爬 2020–2025 全量 |
| 2 | 规划含：目录结构、ingest_run 挂钩、doc 10 §2.1–2.6 映射、失败/重试、样本 1 期试点 | |
| 3 | 可选 scaffold：`backend/src/china_platform/connectors/nbs_monthly.py` 空壳 + 1 测试 skip 禁止 | 若 scaffold：须 `pytest.fail` 非 skip |
| 4 | commit 双推 + **`34-stage0-cc-s14-planning-receipt-*.md`** | |

**本刀禁止：** 真 HTTP 批量抓取；改 gate_thresholds；宣布 Gate 1 PASS。

---

## §1. 参考

- `spikes/01-national-yearbook/`
- `docs/08` S1.4
- `docs/10` 测试 2.1–2.6

— End —
