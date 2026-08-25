# S2.0.2.3 — URL probe 真实化（`URL_HEALTH_LIVE`）实现任务书

- 编号：`165-stage2-s2023-url-probe-live-impl-tasking-20260825`
- 前置：`164` S2.0.2.2 PASS；`docs/35` §5 / §11.4
- 用户裁定：**C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 默认 | `URL_HEALTH_LIVE=0`（或未设）— 既有 mock/fixture 行为；`tests/test_url_health_probe.py` 仍绿 |
| 真实化 | `URL_HEALTH_LIVE=1` — 开发机可跑真实 HEAD；遵守 `docs/32` §2.1 全部上限 |
| CI | **不跑** live；新测默认 **skip**，仅 `URL_HEALTH_LIVE=1` 启用 |
| 生产 cron | **不接**（移交 Stage 2 运维刀） |
| 写库 | 仅 `ingestion_run`（`triggered_by='url_health_probe'`）；**不写**业务表 |

## NOW

1. 落地 `URL_HEALTH_LIVE` 开关于 `scripts/url_health_probe.py`（或等价）；live 模式遵守 §2.1 限速/超时/并发
2. 新增 `tests/test_url_health_probe_live.py`（默认 skip；live 下至少探 1 源 + 可选 `ingestion_run` 断言）；回归既有 probe 套件
3. commit → origin → 回执 **`166`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不爬业务数据；不绕验证码/付费墙；不接生产 cron；不 Gate PASS；不改 `gate_thresholds.json`。
