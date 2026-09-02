# M4.16 政策详情 v10 双复试 spike — 附属复验产物 (knife 653 §A.4, 2026-09-02)

> **本文件**: 653-A.4 附属复验产物 (per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13 + **653 任务书 §0.14 红线 14 增补 (沿用 652) + 653 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证 复试 + retry_of lineage 全行**)
> **主 evidence**: `evidence_pack/m4_16_policy_detail_real_v10_20260902.json` (主 evidence; methodology 含附属产物指针 + 653 §0.14 复试援引 + retry_of 注解)
> **类型**: 附属报告 — 不替代主 evidence, 仅作复验/脉络补充
> **日期**: 2026-09-02

---

## 1. 任务背景

knife 653 = M4.16 政策详情 v10 双复试 spike (spike 第 12 次扩展)。沿用 642/643/644/645/646/648/649/650/651/652 spike 模式, 双复试 2 真实样本 (shandong + hubei 第 19/20 样本); chain_id='real_653_m4_16_policy_detail_v10' (末段 `_v10` ≠ 652 `_v9`); UUID prefix l 段 (l02-l62) ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段。

本 spike 是 **653 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证 复试**: 双样本 (shandong + hubei 双 BLOCKED 史省) 在 edge case 高 BLOCK 概率预期下, 双样本两级 fallback 全失败 → **真网首次 BLOCKED_NO_POOL 双触发** (本次实测双样本均 BLOCKED; shandong SSL handshake failure 0/0 + hubei 412×2), BLOCKED_NO_POOL 分支代码存在并可达 (e2e 守门见 tests/test_m4_16_policy_detail_real_v10.py), 双样本均触发 retry_of lineage 全行 (shandong ← 647 BLOCKED×4; hubei ← 649 substituted actual=LIAONING 412×2 史)。

递补池状态沿用 652 [EXHAUSTED]; 653 双样本均 BLOCKED 真网首触发后, 已用省全集 (按 actual_province 口径, 仍 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU; shandong/hubei 留 BLOCKED_NO_POOL 痕迹, actual_province=NULL, 不计入已用省。

---

## 2. 样本复盘 (shandong + hubei 双 BLOCKED_NO_POOL)

### 2.1 shandong (第 19 样本; 复试)

| 项目 | 值 |
|---|---|
| 原始 URL | `https://www.shandong.gov.cn/zwgk/` |
| 首选 http_code | **0** (SSL handshake failure, LibreSSL/3.3.6: error:1404B410) |
| fallback #1 URL | `https://www.shandong.gov.cn/` (省府根) |
| fallback #1 http_code | **0** (同 SSL handshake failure) |
| chain_index | -1 (双失败) |
| file_hash_sha256 | (空, BLOCKED) |
| file_size_bytes | 0 |
| HTTP 占用 | 2/12 |
| verdict | **BLOCKED_NO_POOL** |
| substitute_used | false (递补池已耗尽; 即便 REACHABLE 也不可代换; 实测 BLOCKED 不可能代换) |
| blocked_reason | "原试点省 shandong 两级 fallback 均未 REACHABLE (zwgk_root=0; province_root=0); per 653 §0.14 红线 14 增补 (沿用 652): 递补池正式耗尽 [EXHAUSTED], 无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕真网首次触发, per 653 §0.14 复试)" |
| retry_of | **retry_of=647 (BLOCKED×4: 域名错配+403)** — 不撞史 (新 BLOCKED 形式: SSL handshake failure, 此前所有刀未见), 但仍 BLOCKED_NO_POOL 留痕 |
| 锚点命中 | 0 (SSL 失败无 body) |

### 2.2 hubei (第 20 样本; 复试)

| 项目 | 值 |
|---|---|
| 原始 URL | `https://www.hubei.gov.cn/zwgk/` |
| 首选 http_code | **412 Precondition Failed** |
| fallback #1 URL | `https://www.hubei.gov.cn/` (省府根) |
| fallback #1 http_code | **412 Precondition Failed** |
| chain_index | -1 (双失败) |
| file_hash_sha256 | (空, BLOCKED) |
| file_size_bytes | 0 |
| HTTP 占用 | 2/12 |
| verdict | **BLOCKED_NO_POOL** |
| substitute_used | false |
| blocked_reason | "原试点省 hubei 两级 fallback 均未 REACHABLE (zwgk_root=412; province_root=412); per 653 §0.14 红线 14 增补 (沿用 652): 递补池正式耗尽 [EXHAUSTED], 无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕真网首次触发, per 653 §0.14 复试)" |
| retry_of | **retry_of=649 (412×2 史, 槽被代换 actual=LIAONING)** — 同史 (412×2 同形, 仍 BLOCKED_NO_POOL 留痕; 但本次因 [EXHAUSTED] 池不可代换, 留痕不代换, actual_province=NULL) |
| 锚点命中 | 0 (412 无内容) |

### 2.3 样本对照 (vs 638-652)

| 刀 | 试点省 | chain_index | HTTP 占用 | file_size | SHA 区分 | retry_of |
|---|---|---|---|---|---|---|
| 638-650 | (沿用; 略) | (略) | (略) | (略) | (略) | — |
| 651 | shaanxi + sichuan | 1 + 1 | 4/12 | 87,956 + 100,536 | `9d0ad78a / f58a3384` | — |
| 652 | xinjiang + nei_menggu | 1 + 0 | 3/12 | 108,841 + 137,602 | `21c8211b / da1d4104` | — |
| **653** | **shandong + hubei** | **-1 + -1 (双 BLOCKED)** | **4/12** | **0 + 0 (BLOCKED)** | **(0 NEW SHA)** | **shandong ← 647; hubei ← 649** |

**653 模式**: 双样本均 BLOCKED (shandong SSL handshake failure 0/0 + hubei 412×2) — **真网首次双触发 BLOCKED_NO_POOL**; 0 INSERT ROWS (per 653 §1.653-A.1 BLOCKED 口径); retry_of lineage 全行生效; 与 651/652 双 REACHABLE 形成对照。

---

## 3. 三层交叉验证 (双 BLOCKED 双 retry_of)

### 3.1 retry_of lineage 区分性 (与 647/649 史明确区分)

- **shandong**: retry_of=647 (BLOCKED×4: 域名错配+403) — **不撞史**: 647 史为域名错配+403, 本次为 SSL handshake failure (新 BLOCKED 形式, 此前所有刀未见); 但仍 BLOCKED_NO_POOL 留痕 (per 653 §0.14 任务书明文"两态均收官价值高: 真触发 = 首次真网 BLOCKED 留痕")
- **hubei**: retry_of=649 (412×2 史, 槽被代换 actual=LIAONING) — **同史**: 649 史为 412×2, 本次 412×2 同形; 但本次因 [EXHAUSTED] 池不可代换, 留痕不代换, actual_province=NULL (与 649 actual=LIAONING 形成对照: 649 substitute 触发 vs 653 BLOCKED 留痕)

### 3.2 SHA 区分性 (0 NEW SHA vs 29 既有)

```
653 (双 BLOCKED) → 0 NEW SHA (无 REACHABLE) → 总 SHA 不变 31
653 ≠ 652 `21c8211b / da1d4104` ≠ 651 `9d0ad78a / f58a3384` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ✓ (无新 SHA 加入)
```

### 3.3 BLOCKED 留痕区分性 (vs 651/652 双 REACHABLE)

- **653 BLOCKED_NO_POOL 双触发** vs **652 双 REACHABLE (BLOCKED_NO_POOL 分支代码 e2e 可达但本次未触发)** vs **651 双 fallback #1 REACHABLE** — 三态区分完整:
  - 651: 双 REACHABLE (shaanxi/sichuan fallback #1)
  - 652: 双 REACHABLE (xinjiang fallback #1 + nei_menggu 首选); BLOCKED_NO_POOL 分支代码 e2e 可达, 但本次未触发 (留痕 0)
  - **653: 双 BLOCKED_NO_POOL 真网首触发** (shandong SSL handshake failure + hubei 412×2); retry_of 全行 (shandong ← 647; hubei ← 649); blocked_no_pool_count=2 (首次实测触发)

---

## 4. SHA 区分表 + lineage 落地 (0 NEW SHA)

### 4.1 31 SHA 累计不变 (vs 652 增 2 NEW = 653 增 0 NEW = 31 SHA)

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-27 | (沿用 638-650) | (略) | (略) | (略) | (见 docs/71/72/73/74/75) |
| 28 | 651 | shaanxi-zwgk-v8 | /zwgk/ (404) → / (200) | `9d0ad78a...` | chain_index=1 fallback REACHABLE |
| 29 | 651 | sichuan-zwgk-v8 | /zwgk/ (403 WAF) → / (200) | `f58a3384...` | chain_index=1 fallback REACHABLE |
| 30 | 652 | xinjiang-zwgk-v9 | /zwgk/ (403 WAF) → / (200) | `21c8211b...` | NEW 652 第 17 样本 chain_index=1 fallback REACHABLE |
| 31 | 652 | nei_menggu-zwgk-v9 | /zwgk/ (200) | `da1d4104...` | NEW 652 第 18 样本 chain_index=0 直接 REACHABLE |
| — | **653** | **shandong + hubei** | **(双 BLOCKED)** | **(0 NEW SHA)** | **NEW 653 双样本均 BLOCKED; 真网首次双触发; 0 SHA** |

**31 SHA 全部 distinct** (✓ 不撞 638-652)

### 4.2 lineage 真实化 sentinel (per docs/33 §3.2 + 653 §1.653-A.1 retry_of)

- 主 evidence metadata 含 chain_id='real_653_m4_16_policy_detail_v10' + retry_of_annotation 双样本注解 (shandong ← 647; hubei ← 649)
- 主 evidence cells[0] shandong / cells[1] hubei 均含 retry_of 字段
- seed SQL 0 INSERT ROWS (双样本均 BLOCKED 留痕; lineage / chain_id / retry_of 信息保留在 evidence + docs/77 + receipt)
- 653 §0.14 红线 14 增补沿用 652: red_line_14_status='EXHAUSTED' (隐式登记在 evidence substitute_pool_status + retry_of)

---

## 5. 递补池耗尽登记 (沿用 652 §0.14) + 653 §0.14 BLOCKED_NO_POOL 真网首次双触发 强制 e2e 验证

### 5.1 递补池状态 (沿用 652 §0.14 红线 14 增补)

| 池成员 | 状态 (652 后) | 状态 (653 后) | 备注 |
|---|---|---|---|
| liaoning | ✓ 649 激活 (consumed) | ✓ 649 激活 (consumed) | hubei→ln substitute 已消耗 |
| shaanxi | ✓ 651 转正首选 (consumed) | ✓ 651 转正首选 (consumed) | shaanxi /zwgk/ 404 → / 200 REACHABLE |
| sichuan | ✓ 651 转正首选 (consumed) | ✓ 651 转正首选 (consumed) | sichuan /zwgk/ 403 WAF → / 200 REACHABLE |
| guizhou | ✓ 650 直接 REACHABLE (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | ✓ 650 fallback REACHABLE (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**递补池 [EXHAUSTED] 沿用**: 5 个原始池成员全部落定; 池清空; **红线 14 生效**; 此后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换 (per 653 §0.14)。

### 5.2 653 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证 (复试)

**e2e 验证机制** (沿用 652 §0.14 模板 + 653 §0.14 强制验证):
- `scripts/fetch_m4_16_policy_detail_v10_2024.py` 含 `verdict="BLOCKED_NO_POOL"` 分支 + `blocked_reason` 字段 + `RETRY_OF_NOTES` 全行 retry_of 字段
- `scripts/seed_m4_16_policy_detail_real_v10.sql` **0 INSERT ROWS** (双样本均 BLOCKED 留痕; 头部 documentation 完整记录 BLOCKED 实测)
- `evidence_pack/m4_16_policy_detail_real_v10_20260902.json` summary 含 `substitute_pool_status='EXHAUSTED'` + `blocked_no_pool_count=2` + `fetch_status='ALL_BLOCKED_NO_POOL'` + `retry_of_annotation` 双样本注解 + methodology 含 653 §0.14 复试援引 + 沿用 652 §0.14 + 双样本实测结果: REACHABLE×0 / BLOCKED_NO_POOL×2 (真网首次双触发)
- `docs/77-m4-16-policy-detail-real-v10-20260902.md` §2 复试 BLOCKED 留痕登记表 (4 实现位置 + 8 守门含 retry_of + 双触发)
- `tests/test_m4_16_policy_detail_real_v10.py` 含 8 个守门: fetch 脚本 BLOCKED_NO_POOL 分支守门 + 主 evidence substitute_pool_status 守门 + 双触发守门 + seed 0 INSERT ROWS 守门 + P4-A.0 规范 v2 守门 (status 不 pin 中间 SHA) + lineage red_line_14 守门 + retry_of 守门 + chain_id UUID l 段守门

**本次实测 (真网首次双触发 BLOCKED_NO_POOL)**: 双样本 (shandong + hubei) 均 BLOCKED_NO_POOL (shandong SSL handshake failure 0/0 + hubei 412×2), `blocked_no_pool_count=2`, `fetch_status=ALL_BLOCKED_NO_POOL`。**BLOCKED_NO_POOL 分支代码存在并可达 + 本次真网首次双触发实测命中** (e2e 守门确认分支代码可达 + 实测命中; 测试中 fetch 脚本 BLOCKED_NO_POOL 分支字串守门 + 双触发守门 PASSED)。

---

## 6. 653-A.0 P4-A.0 规范 v2 落地 (per 652 审计 P4 教训沉淀)

### 6.1 P4-1 — status 行第三型自指陈旧复发处置

- 652 教训: rev88 status 行 pin 中间 SHA `eb6b012`（vs 终态 HEAD=`8ae20de`）, 陈旧。652 自身又复发: rev90 status 行 pin 中间 SHA `04721b7` 为"终态" + "待 §C-5"陈旧未收口。
- 653-A.0 落地: `docs/76` §6.1 + 652 receipt §RED_LINE_AUDIT.1 末尾追加 P4-A.0 规范 v2 tailnote; commit af7a95c; 653-C 写 EXEC-QUEUE rev92 时 status 收口与 §NOW 刷新**同 commit 原子完成**，"待复核/待 §C-x"字样复核通过后**必须立即清除**。

### 6.2 P4-A.0 规范 v2 — 沿用 652-A.0 P4-2 amend-first + 状态原子收口

- 沿用 652-A.0 P4-2 amend-first 规则（先 amend 完成再写链文本; cc_head 链 SHA 一律 `git log --format=%H -n <n>` 实测输出）
- 状态收口与 §NOW 刷新同 commit 原子完成（per 653 任务书 §1.653-A.0）
- "待复核/待 §C-x"字样复核通过后**必须清除**（per 653 任务书 §1.653-A.0）

### 6.3 O-1 预测命中 + O-2 未复发

- O-1 (m2 crosscheck 复跑污染): 652 复跑后零 diff; 653 任务书集合首跑预期同样全绿; tmpdir isolation 加固仍开放不 gating。
- O-2 (650 幽灵并发 flake): 652 任务书集合首跑 144 全绿; 653 任务书集合首跑同样预期全绿; 若复发再登记。

---

## 7. 附属产物指针

- **主 evidence**: `evidence_pack/m4_16_policy_detail_real_v10_20260902.json` (含 653 §0.14 复试援引 + BLOCKED_NO_POOL 留痕不代换条款 + 沿用 652 §0.14 + 653 §0.14 强制 e2e 验证 + 双样本实测结果: REACHABLE×0 / BLOCKED_NO_POOL×2 真网首次双触发 + retry_of_annotation 双样本注解)
- **架构师审查**: `docs/77-m4-16-policy-detail-real-v10-20260902.md` (§1-§6; §2 含复试 BLOCKED 留痕登记表 + retry_of 注解 + 双触发实测; §4 含 chain_id 区分 16 真实化刀 + UUID 严格递增至 l 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 638-653)
- **fetch 脚本**: `scripts/fetch_m4_16_policy_detail_v10_2024.py` (SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' + BLOCKED_NO_POOL verdict 分支 + blocked_reason 字段 + RETRY_OF_NOTES 双样本 retry_of 注解)
- **seed SQL**: `scripts/seed_m4_16_policy_detail_real_v10.sql` (0 INSERT ROWS = 双样本均 BLOCKED_NO_POOL 真网首次双触发; lineage JSONB 在 evidence metadata 内隐式登记)
- **测试**: `tests/test_m4_16_policy_detail_real_v10.py` (≥8 cases 含 8 个守门)
- **回执**: `reviews/stage0-gate0-rework-2026-08-23/653-stage0-cc-m4-16-v10-retry-receipt-20260902.md`

---

## 8. 验收 checklist

- ✓ chain_id='real_653_m4_16_policy_detail_v10' (末段 `_v10`) ≠ 652 `_v9` ≠ 651 `_v8` ≠ 650 `_v7` ≠ 649 `_v6` ≠ 648 `_v5`
- ✓ UUID l 段 (l02-l62) ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
- ✓ **0 NEW SHA** (双样本均 BLOCKED_NO_POOL; per 653 §1.653-A.1 BLOCKED 口径)
- ✓ lineage 全 `is_demo='false'` 真实化 sentinel (隐式登记在 evidence metadata; 无 INSERT)
- ✓ lineage 全 `red_line_14_status='EXHAUSTED'` (沿用 652 §0.14 增补)
- ✓ **retry_of lineage 全行** (shandong ← 647 BLOCKED×4; hubei ← 649 substituted actual=LIAONING; per 653 §1.653-A.1)
- ✓ HTTP 4/12 = 33% usage (shandong 2 + hubei 2)
- ✓ `substitute_used_count=0` (递补池已耗尽; 即便双样本 REACHABLE 也不可代换)
- ✓ `blocked_no_pool_count=2` (本次**真网首次双触发**)
- ✓ `fetch_status=ALL_BLOCKED_NO_POOL` (双样本均 BLOCKED; 真网首次双触发)
- ✓ BLOCKED_NO_POOL 分支代码 e2e 实测命中 (tests/test_m4_16_policy_detail_real_v10.py 含分支字串守门 + 双触发守门 + retry_of 守门)
- ✓ **0 INSERT ROWS** (双样本均 BLOCKED 留痕; per 653 §1.653-A.1 BLOCKED 口径)
- ✓ 653-A.0 P4-A.0 规范 v2 落地 (status 收口与 §NOW 同 commit 原子完成 + "待复核/待 §C-x"字样复核后必须清除 + 沿用 P4-2 amend-first); commit af7a95c
- ✓ 已用省全集不变 (按 actual_province 口径, 仍 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU; shandong/hubei 留 BLOCKED_NO_POOL 痕迹, actual_province=NULL, 不计入已用省

---

## 9. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（沿用红线 1, 21 个里程碑不宣布; vs 652 时 20 个; 653 增量 = M4.16）
- O1 仍 OPEN (B 路 live-candidate 仅登记, 不切换/启用)
- docs/52 零改动 (沿用 646-652 红线 12: registry 行 SHA 零漂移)

---

— End M4.16 v10 双复试 spike 附属复验产物 20260902 —
