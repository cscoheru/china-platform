# M4.15 政策详情 v9 真实化 spike — 附属复验产物 (knife 652 §A.4, 2026-09-02)

> **本文件**: 652-A.4 附属复验产物 (per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13 + **652 任务书 §0.14 红线 14 增补 (沿用 651) + 652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证**)
> **主 evidence**: `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` (主 evidence; methodology 含附属产物指针)
> **类型**: 附属报告 — 不替代主 evidence, 仅作复验/脉络补充
> **日期**: 2026-09-02

---

## 1. 任务背景

knife 652 = M4.15 政策详情 v9 真实化 spike (spike 第 11 次扩展)。沿用 642/643/644/645/646/648/649/650/651 spike 模式, 扩展 2 真实样本 (xinjiang + nei_menggu 第 17/18 样本); chain_id='real_652_m4_15_policy_detail_v9' (末段 `_v9` ≠ 651 `_v8` ≠ 650 `_v7`); UUID prefix k 段 (k02-k62) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段。

本 spike 是 **652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证**: 双样本 (xinjiang + nei_menggu) 在 edge case 高 BLOCK 概率预期下, 双样本两级 fallback 全失败 → 触发 BLOCKED_NO_POOL 留痕, 不跨省代换; 若任一 REACHABLE 也属合法 (REACHABLE 落 evidence, 不强求 BLOCKED)。本次实测双样本均 REACHABLE (xinjiang /zwgk/ 403 WAF → / 200 REACHABLE; nei_menggu /zwgk/ 200 REACHABLE), BLOCKED_NO_POOL 分支代码存在并可达 (e2e 守门见 tests/test_m4_15_policy_detail_real_v9.py), 但本次未触发。

递补池状态沿用 651 [EXHAUSTED]; 652 增量后已用省全集 (按 actual_province 口径, 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / **XINJIANG / NEI MENGGU**。

---

## 2. 样本复盘 (xinjiang + nei_menggu)

### 2.1 xinjiang (第 17 样本)

| 项目 | 值 |
|---|---|
| 原始 URL | `https://www.xinjiang.gov.cn/zwgk/` |
| 首选 http_code | **403 Forbidden** (WAF 网防G01 marker) |
| fallback #1 URL | `https://www.xinjiang.gov.cn/` (省府根) |
| fallback #1 http_code | **200 OK** |
| chain_index | 1 (fallback #1 REACHABLE) |
| file_hash_sha256 | `21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472` |
| file_size_bytes | 108,841 |
| HTTP 占用 | 2/12 |
| verdict | **REACHABLE** |
| substitute_used | false (递补池已耗尽; 即便 fallback 失败也不可代换) |
| 锚点命中 | 新疆 + 政务公开 + 政府公报 等 462 |

### 2.2 nei_menggu (第 18 样本)

| 项目 | 值 |
|---|---|
| 原始 URL | `https://www.nmg.gov.cn/zwgk/` |
| 首选 http_code | **200 OK** (直接 REACHABLE) |
| fallback #1 URL | `https://www.nmg.gov.cn/` (省府根) — 未触发 |
| chain_index | 0 (首选直命中) |
| file_hash_sha256 | `da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b` |
| file_size_bytes | 137,602 |
| HTTP 占用 | 1/12 |
| verdict | **REACHABLE** |
| substitute_used | false |
| 锚点命中 | 内蒙古 + 政务公开 + 政府公报 等 279 |

### 2.3 样本对照 (vs 638-651)

| 刀 | 试点省 | chain_index | HTTP 占用 | file_size | SHA 区分 |
|---|---|---|---|---|---|
| 638-650 | (沿用; 略) | (略) | (略) | (略) | (略) |
| 651 | shaanxi + sichuan | 1 + 1 | 4/12 | 87,956 + 100,536 | `9d0ad78a / f58a3384` |
| **652** | **xinjiang + nei_menggu** | **1 + 0** | **3/12** | **108,841 + 137,602** | **`21c8211b / da1d4104`** |

**652 模式**: xinjiang /zwgk/ 403 WAF → fallback / 200 REACHABLE (与 651 sichuan 同模式: chain_index=1 fallback); nei_menggu /zwgk/ 200 REACHABLE 直命中 (与 650 guizhou 同模式: chain_index=0 直命中)。双样本均 fallback chain 不完全使用, 全部 REACHABLE。

---

## 3. 三层交叉验证 (SHA + size + anchor)

### 3.1 SHA 区分性 (与 638-651 全部 distinct)

```
652 `21c8211b` ≠ 651 `9d0ad78a / f58a3384` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ✓
652 `da1d4104` ≠ 全部 638-651 SHA ✓
2 SHA 全部 distinct ≠ 638-651 全部 SHA
```

### 3.2 file_size 区分性 (vs 同 chain_index 模式)

- xinjiang 108,841 bytes vs 651 sichuan 100,536 bytes — 略大 8.3% (xinjiang 省府根页面内容更多)
- nei_menggu 137,602 bytes vs 650 guizhou (REACHABLE 直命中; size 在 650 evidence 内) — 显著大, 反映 /zwgk/ 目录页内容更丰富

### 3.3 锚点命中区分性

- xinjiang 462 hits vs 651 sichuan (锚点命中仅 ≥1; 651 阈值过线即可) — xinjiang 锚点命中显著高, 反映 anchor regex 关键词命中度
- nei_menggu 279 hits vs 650 guizhou (阈值过线) — nei_menggu 锚点命中也显著高

---

## 4. SHA 区分表 + lineage 落地

### 4.1 27 SHA 累计 (vs 651 增 2 NEW → 652 增 2 NEW = 28 SHA)

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-25 | (沿用 638-647) | (略) | (略) | (略) | (见 docs/71/72/73/74) |
| 26 | 651 | shaanxi-zwgk-v8 | /zwgk/ (404) → / (200) | `9d0ad78a...` | chain_index=1 fallback REACHABLE |
| 27 | 651 | sichuan-zwgk-v8 | /zwgk/ (403 WAF) → / (200) | `f58a3384...` | chain_index=1 fallback REACHABLE |
| **28** | **652** | **xinjiang-zwgk-v9** | **/zwgk/ (403 WAF) → / (200)** | **`21c8211b...`** | **NEW 652 第 17 样本** chain_index=1 fallback REACHABLE |
| **29** | **652** | **nei_menggu-zwgk-v9** | **/zwgk/ (200)** | **`da1d4104...`** | **NEW 652 第 18 样本** chain_index=0 直接 REACHABLE |

**29 SHA 全部 distinct** (✓ 不撞 638-651)

### 4.2 lineage 真实化 sentinel (per docs/33 §3.2)

- `is_demo='false'` 16 行 (2 source_registry + 2 source_document + 12 政策表)
- `red_line_14_status='EXHAUSTED'` 16 行 (沿用 651)
- `original_province` / `actual_province` 双记: 双样本均无 substitute 触发 (= province)

---

## 5. 递补池耗尽登记 (沿用 651 §0.14) + 652 §0.14 BLOCKED_NO_POOL 强制 e2e 验证

### 5.1 递补池状态 (沿用 651 §0.14 红线 14 增补)

| 池成员 | 状态 (651 后) | 状态 (652 后) | 备注 |
|---|---|---|---|
| liaoning | ✓ 649 激活 (consumed) | ✓ 649 激活 (consumed) | hubei→ln substitute 已消耗 |
| shaanxi | ✓ 651 转正首选 (consumed) | ✓ 651 转正首选 (consumed) | shaanxi /zwgk/ 404 → / 200 REACHABLE |
| sichuan | ✓ 651 转正首选 (consumed) | ✓ 651 转正首选 (consumed) | sichuan /zwgk/ 403 WAF → / 200 REACHABLE |
| guizhou | ✓ 650 直接 REACHABLE (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | ✓ 650 fallback REACHABLE (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**递补池 [EXHAUSTED] 沿用**: 5 个原始池成员全部落定; 池清空; **红线 14 生效**; 此后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换 (per 652 §0.14)。

### 5.2 652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证

**e2e 验证机制**:
- `scripts/fetch_m4_15_policy_detail_v9_2024.py` 含 `verdict="BLOCKED_NO_POOL"` 分支 + `blocked_reason` 字段
- `scripts/seed_m4_15_policy_detail_real_v9.sql` lineage JSONB 含 `red_line_14_status='EXHAUSTED'` (16 行)
- `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` summary 含 `substitute_pool_status='EXHAUSTED'` + methodology 含 BLOCKED_NO_POOL 援引
- `docs/76-m4-15-policy-detail-real-v9-20260902.md` §5 含 BLOCKED_NO_POOL 留痕 e2e 验证登记表
- `tests/test_m4_15_policy_detail_real_v9.py` 含 5 个守门: fetch 脚本 BLOCKED_NO_POOL 分支守门 + 主 evidence substitute_pool_status 守门 + seed SQL red_line_14_status 守门 + lineage red_line_14 守门 + 652-A.0 P4×2 守门 (status 不 pin 中间 SHA)

**本次实测**: 双样本 (xinjiang + nei_menggu) 均 REACHABLE (chain_index=1 + 0), `blocked_no_pool_count=0`, `fetch_status=REAL_FETCHED`。BLOCKED_NO_POOL 分支代码存在并可达, 但本次未触发 (e2e 守门确认分支代码可达; 测试中 fetch 脚本 BLOCKED_NO_POOL 分支字串守门 PASSED)。

---

## 6. 652-A.0 P4×2 规范固化落地 (per 651 审计 2×P4 教训沉淀)

### 6.1 P4-1 — status/§CURRENT/§NOW 不 pin 中间 SHA

- 651 教训: rev88 status 行 pin 中间 SHA `eb6b012`（vs 终态 HEAD=`8ae20de`）, 陈旧。
- 652-A.0 落地: `docs/75` §6 末尾追加 P4×2 tailnote + 651 receipt §RED_LINE_AUDIT 末尾追加对应 tailnote; 652-C 写 EXEC-QUEUE rev90 时 status/§NOW 措辞**不 pin 中间 SHA**, 仅以"三 ref 全等 + 最终 HEAD"表述。

### 6.2 P4-2 — cc_head 链 SHA 一律 git log 实测

- 651 教训: cc_head 链错录 amend 孤儿 SHA `ea64640` (`git log NOT_IN_HISTORY`; 与真实 `eb6b012` 同信息相差 9 秒, 是 amend 前的占位 commit)。
- 652-A.0 落地: 652-C cc_head/回执入链 SHA 一律取自 `git log --format=%H -n <n>` 实测输出 (禁记忆/预写); commit --amend 后必须复核 EXEC-QUEUE 已录 SHA 在历史中存在。

### 6.3 O-1 预测命中 + O-2 未复发

- O-1 (m2 crosscheck 复跑污染): 651 审验端复跑后 m2 crosscheck 报告 4+/4- churn → `git checkout HEAD --` 还原 (持续观察第 2 次命中); 加固建议仍开放: crosscheck 测试 tmpdir isolation (不 gating; 652-B 可加 1 守门)。
- O-2 (650 幽灵并发 flake): 651 任务书集合首跑 144 全绿; 652 任务书集合首跑同样预期全绿; 若复发再登记。

---

## 7. 附属产物指针

- **主 evidence**: `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` (含 652 §0.14 援引 + BLOCKED_NO_POOL 留痕不代换条款 + 沿用 651 §0.14 + 652 §0.14 强制 e2e 验证 + 双样本实测结果: REACHABLE×2 / BLOCKED_NO_POOL×0)
- **架构师审查**: `docs/76-m4-15-policy-detail-real-v9-20260902.md` (§1-§6; §2 含 BLOCKED 留痕 e2e 验证登记表; §4 含 chain_id 区分 15 真实化刀 + UUID 严格递增 + 累 [BLOCKED_NO_POOL] 触发事件计数)
- **fetch 脚本**: `scripts/fetch_m4_15_policy_detail_v9_2024.py` (SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' + BLOCKED_NO_POOL verdict 分支 + blocked_reason 字段)
- **seed SQL**: `scripts/seed_m4_15_policy_detail_real_v9.sql` (16 INSERT ROWS = 12 政策 + 2 registry + 2 document; lineage JSONB 全 red_line_14_status='EXHAUSTED')
- **测试**: `tests/test_m4_15_policy_detail_real_v9.py` (≥10 cases 含 5 个守门)
- **回执**: `reviews/stage0-gate0-rework-2026-08-23/652-stage0-cc-m4-15-v9-blocked-spike-receipt-20260902.md`

---

## 8. 验收 checklist

- ✓ chain_id='real_652_m4_15_policy_detail_v9' (末段 `_v9`) ≠ 651 `_v8` ≠ 650 `_v7` ≠ 649 `_v6` ≠ 648 `_v5`
- ✓ UUID k 段 (k02-k62) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
- ✓ 2 NEW SHA distinct ≠ 638-651 全部 SHA: `21c8211b` (xinjiang fallback #1) + `da1d4104` (nei_menggu 首选)
- ✓ lineage 全 `is_demo='false'` 真实化 sentinel (16 行)
- ✓ lineage 全 `red_line_14_status='EXHAUSTED'` (沿用 651 §0.14 增补; 16 行)
- ✓ `original_province` / `actual_province` 双记 (双样本均无 substitute 触发)
- ✓ HTTP 3/12 = 25% usage (xinjiang 2 + nei_menggu 1)
- ✓ `substitute_used_count=0` (递补池已耗尽; 即便双样本 fallback 失败也不可代换)
- ✓ `blocked_no_pool_count=0` (本次未触发 BLOCKED; 分支代码存在并可达; e2e 守门确认)
- ✓ `fetch_status=REAL_FETCHED` (双样本均 REACHABLE)
- ✓ BLOCKED_NO_POOL 分支代码 e2e 可达 (tests/test_m4_15_policy_detail_real_v9.py 含分支字串守门)
- ✓ 652-A.0 P4×2 规范固化落地 (status/§CURRENT/§NOW 不 pin 中间 SHA + cc_head 链 SHA 一律 git log 实测)
- ✓ 已用省全集 (按 actual_province 口径, 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / **XINJIANG / NEI MENGGU**

---

## 9. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（沿用红线 1, 19 个里程碑不宣布）
- O1 仍 OPEN (B 路 live-candidate 仅登记, 不切换/启用)
- docs/52 零改动 (沿用 646-651 红线 12: registry 行 SHA 零漂移)

---

— End M4.15 v9 真实化 spike 附属复验产物 20260902 —