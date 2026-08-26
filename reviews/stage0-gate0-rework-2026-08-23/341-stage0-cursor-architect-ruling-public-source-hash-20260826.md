# Cursor 架构裁定 — 公开源哈希 / 稳定直链（用户授权代判）

- 编号：`341-stage0-cursor-architect-ruling-public-source-hash-20260826`
- 日期：2026-08-26
- 触发：用户「你自己判断，我不懂」→ Cursor 代判；(a)/(b) 不再问用户

---

## §0. 裁定（生效）

| # | 裁定 |
|---|---|
| 1 | **不要**把「会每天变的列表页」今日哈希写进 `registry.csv` 当永久 `file_hash_sha256`（NBS `zxfb/`、湖北 `tjyb/` 索引页均属此类；今日对齐、明日必再漂）。 |
| 2 | **要**优先拿到 **稳定附件直链**（同域 `.xlsx` / `.xls` / 单篇固定 HTML），再对该文件计算 SHA 并允许写入 registry（`primary_url` + `file_hash_sha256` + size）。 |
| 3 | 列表页 live 快照只许 `CANDIDATE_AUTO` + `is_demo=true`；**禁止**因列表页偶发哈希相等就 `O1_AUTO_INTAKED`。 |
| 4 | JS 壳 / 无深链 / 仅验证码登录付费 → **停并报告用户**（AUTH/TECH）；**禁止 headless 执行 JS**。 |
| 5 | 深链成功拿到真实 xlsx/表数据后：CC **可直接**更新对应 registry 行（URL+SHA+size），无需再问用户；回执写明前后对比。 |
| 6 | 以后同类「源工程选择」默认 **Cursor 代判**；仅登录/验证码/付费/需账号时才打断用户。 |

## §1. 对当前两源

- **NBS**：继续深链/文章链；索引页保持候选。
- **湖北**：深链找 `.xlsx`；找到则 pin registry；找不到 → tech-blocked（已有刀 `339`）。

— End —
