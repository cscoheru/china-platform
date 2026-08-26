# O1 投递一页清单 — 缩刀任务书

- 编号：`321-stage2-o1-drop-checklist-tasking-20260826`
- 前置：`320` docs/45 PASS；`docs/48` intake；用户要尽快真数据
- 用户裁定：**D**；O1 仍 OPEN；不伪造/不爬网

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 写 **`docs/51`**：给用户的 O1 投递一页清单（放哪、叫什么、≥1KiB、如何跑 `intake_real_sha_if_present.py`、何时 `--confirm-o1`、成功后预览会看到什么）；链到 docs/48；**不**宣称已收口 |
| 本刀不做 | 伪造样本；爬网；实装 OCR；Gate PASS |
| 禁止 | Gate PASS；把 fixture 当 O1；擅自 O1 CLOSED |

## NOW

1. 落地 `docs/51`
2. 补 pack → 回执 **`322`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不伪造；不爬网；不宣布 O1 收口。
