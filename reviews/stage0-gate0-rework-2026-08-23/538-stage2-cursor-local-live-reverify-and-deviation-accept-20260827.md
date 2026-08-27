# knife 538 — Cursor 本机 live 复验 + 偏差交付接受

- 编号：`538-stage2-cursor-local-live-reverify-and-deviation-accept-20260827`
- 日期：2026-08-27T22:58:00+08:00
- 对象：tasking **`538`**（用户裁定 SHA drift **(a)**）
- 作者：Cursor（监管 tick；应用户指令）

---

## §1. 本机 live 复验（①）

```bash
python3 scripts/auto_ingest_public_source.py --live \
  --pilot-domain=stats.gov.cn \
  --pilot-category=NATIONAL_BULLETIN \
  --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl
```

**结果：exit 0**

| 项 | 值 |
|---|---|
| expected SHA（registry 本地已改 a7e4029d…） | `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` |
| download | **180165 B** |
| download sha256 | `a7e4029d…`（与 expected **匹配**） |
| deeplink | `t20260827_1965129.html` |
| extract | 6 table row(s) |
| lineage | 已写入 `20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl` |

---

## §2. 偏差交付接受（② · 用户 2026-08-27 明示）

CC 回执 **`538`** 在下列偏差下 **PASS 可接受**（Cursor 预审接受；不等 CC 本机再跑 live）：

| # | 偏差 | 接受理由 |
|---|---|---|
| D1 | **live 复验由 Cursor 本机完成**（上 §1），CC 回执可引用本文件 + stdout 摘录 | 用户指令「本机跑复验命令」；hash 匹配已实证 |
| D2 | **WORM archive 幂等**（per 回执 `510`）：`data/public_archives/2026-08/stats.gov.cn/zxfb` 已存在时可能不覆盖磁盘字节；**download 步 sha256 与 registry expected 匹配即 sufficient** | registry (a) 处置语义 = 认定源站换版 + expected 锚定 live 实测值 |
| D3 | **`intake_status=CANDIDATE_AUTO` / `is_demo=true` 保持** | registry 更新 ≠ O1 收口；不得 Gate/O1 PASS |
| D4 | **4 frontend fixture 字节锁不变**（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`） | tasking 538 红线 |
| D5 | CC 仅需 **commit + 双推 registry.csv 变更**（`file_hash_sha256` + `file_size_bytes` + purpose_note）及 docs/45、docs/53 刷新；**不必**在回执中重复 full live stdout 若引用本文件 | 缩小 CC 阻塞面 |

**仍不接受：** 谎称 O1/Gate PASS；删 OPEN；改 `enabled`；动 4 fixture 字节。

---

## §3. CC NOW（更新）

1. commit `registry.csv`（a7e4029d… / 180165）+ docs 刷新
2. 回执 **`538`** 引用本文件 D1–D5 + grep 实证
3. **必须双推** → POLL

— End —
