# S2.7-b — 10 地市观察页 + 证据链接入 规划任务书

- 编号：`253-stage2-s27b-cities-plan-tasking-20260826`
- 前置：`252` S2.10-lite PASS；`docs/45` §2 #1 OPEN；`docs/44` §5.1.2–§5.1.3；`docs/34` §4 序 5
- 用户裁定：Stage 2 **C**；缩刀节奏 **D**（本刀**只规划**）
- **自主推进**：用户 2026-08-26 授权 Cursor 按计划下刀（仅功能测试 / §BLOCKED 再找用户）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | **`docs/46-stage2-s27b-cities-evidence-plan-YYYYMMDD.md`** |
| 本刀 | **只规划**；不写 migration / 不全量 UI / 不接真 mart |
| **10 地市锁定**（Cursor 裁定，勿另挑） | 南京、苏州、无锡、南通；杭州、宁波、温州；广州、深圳、东莞 |
| 路由建议 | 规划中明确（如 `/cities/{slug}` 或挂省下）；须可被 Gate 2 #1 点名 |
| 缩刀落地预期 | 规划通过后 → **S2.7-b-lite**（10 城 mock 壳 + EvidenceChain 复用；仿 S2.7-a） |
| person/tenure 真数据 | 规划里写清接入契约 + **OPEN**；本规划刀与 lite **不**强制接满 mart |
| 禁止 | 宣布 Gate 1/2 PASS；官员评分/排名；DSH；爬网；伪造 SHA |

## NOW

1. 起草 `docs/46`：10 城清单与 slug、路由、与 5 省壳复用关系、EvidenceChain 接入边界、lite vs full 切刀、验收与红线、OPEN 清单
2. 补 pack；commit → `origin` + `github` → 回执 **`254`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不伪造 SHA / 证据；不擅自改已锁定的 10 城名单。
