# 湖北公开源 EXCEL connector — 缩刀任务书

- 编号：`336-stage2-hubei-excel-public-connector-tasking-20260826`
- 前置：`335` NBS drift PASS；NBS 收口等用户 (a)/(b)；本刀并行推进第二试点
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 扩展 `auto_ingest_public_source.py`（或等价模块）支持 pilot=`tjj.hubei.gov.cn` / `PROVINCIAL_BULLETIN`：discover→download→sha256→archive→extract(xlsx)→observation；(2) **禁止 headless**（registry 注明）；curl/requests 直链；(3) 复用 AUTH + SHA drift（`CANDIDATE_AUTO`）路径；(4) dry-run 默认；一次 `--live` 探测证据入回执；(5) ≥8 pytest；(6) 回执 **`337`** |
| 本刀不做 | 擅自改 NBS registry 哈希（等用户裁定）；深圳源；OCR；Gate/O1 PASS；绕 AUTH |
| 禁止 | headless；静默失败；把 drift 标 O1_AUTO_INTAKED |

## NOW

1. 落地 Hubei pilot + tests + 一次 live 探测
2. 补 pack → 回执 **`337`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不绕 AUTH；不 headless；不伪造；NBS 哈希等用户。
