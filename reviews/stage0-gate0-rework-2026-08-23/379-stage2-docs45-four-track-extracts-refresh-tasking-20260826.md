# docs/45 四轨公开提取刷新 — 缩刀任务书

- 编号：`379-stage2-docs45-four-track-extracts-refresh-tasking-20260826`
- 前置：`378` PASS；`/public-extracts` 四轨（NBS sample/live + 深圳 + 湖北）
- 用户裁定：**C** 自主继续；**D**；仅卡住 escalate

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 刷新 `docs/45`：三轨→**四轨**（+湖北 PROVINCIAL_BULLETIN 21 行 / `c5cf5a…` / `public_extract_hubei.json` / 回执 `377`；live 仍 `enabled=FALSE`）；§1 + §6.2 + §7；(2) 可选：`docs/53` §5 第四区块一句；(3) 首页 `page.tsx` 链接文案「公开提取样本（NBS）」→「公开提取样本（四轨 demo）」；(4) 显式非 O1/Gate PASS；(5) 回执 **`380`**（`-cc-`）|
| 本刀不做 | 湖北 live；改 extract 字节；Gate/O1 PASS |
| 禁止 | 谎称四轨=O1；删减 OPEN 清单 |

## NOW

1. docs/45（+可选 53）+ 首页文案
2. pack → 回执 **`380`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不碰 fixture/extract 字节。
