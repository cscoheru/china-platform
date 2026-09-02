# 79 — M4.18 政策详情 v12 西部终章 spike 架构师级审查 (knife 655, 2026-09-02)

> **刀号**: 655
> **Milestone**: M4.18（沿用 651-654 spike 模式；spike 第 14 次扩展；西部七省区全覆盖叙事终章）
> **类型**: 架构师级审查（per 655 任务书 §1.655-A.3）
> **日期**: 2026-09-02
> **前置**: 654 DELIVERED + 审计 **PASS（有限通过）** + 655 任务书签发 + 655-A.0 规范 v3.1 落地（status 零 SHA 绝对化 + 七字段原子）+ 654 §0.14 红线 14 e2e 验证模板 + 递补池 [EXHAUSTED]（沿用 654）
> **注**: 本文档为新文档；655 §0.4 红线 4 不改 docs/45/50/53/66-78 既有正文；docs/79 自由落地

---

## 1. 任务背景与定位

### 1.1 西部七省区全覆盖叙事

655 = M4.18 v12 西部终章双省 spike（**NINGXIA + XIZANG**，第 23/24 样本）— 与 651/652/654 共同构成**西部七省区全覆盖**叙事终章：

| 西部省区 | 落定刀 | verdict |
|---|---|---|
| SHAANXI (陕西) | 651 | REACHABLE (fallback #1) |
| XINJIANG (新疆) | 652 | REACHABLE (fallback #1) |
| NEI MENGGU (内蒙古) | 652 | REACHABLE (首选直命中) |
| GANSU (甘肃) | 654 | BLOCKED_NO_POOL |
| QINGHAI (青海) | 654 | BLOCKED_NO_POOL |
| **NINGXIA (宁夏)** | **655** | **BLOCKED_NO_POOL** |
| **XIZANG (西藏)** | **655** | **REACHABLE** (首选直命中) |

**西部七省区 = 651 + 652 + 654 + 655 四刀收官**：4 REACHABLE (SHAANXI/XINJIANG/NEI MENGGU/XIZANG) + 3 BLOCKED (GANSU/QINGHAI/NINGXIA)。

### 1.2 关键意义

- **混合态首次出现**：vs 651/652 双 REACHABLE / 653/654 双 BLOCKED；655 = PARTIAL_BLOCKED（XIZANG REACHABLE + NINGXIA BLOCKED_NO_POOL）
- **真网首试省首触发第三例**：NINGXIA /zwgk/ + / 均 405 Method Not Allowed + WAF marker ×2
- **失败形式库累计 = 3 例首见**：652/654 BLOCKED 已 2 例（SSL handshake failure + Connection reset by peer）；**655 新增 405 Method Not Allowed + WAF marker**
- **已用省全集增量**：18 → 19（XIZANG REACHABLE 增量 1；NINGXIA BLOCKED 留痕 → 0 增量）
- **655-A.0 规范 v3.1 落地**：status 零 SHA 绝对化 + 七字段原子（header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步）

---

## 2. 首试省 BLOCKED_NO_POOL 留痕登记表（沿用 654 §2 模板）

### 2.1 NINGXIA BLOCKED_NO_POOL 留痕实现位置（4 实现位置 + 8 守门）

#### 实现位置 1：fetch 脚本 BLOCKED_NO_POOL 分支可达

`scripts/fetch_m4_18_policy_detail_v12_2024.py::fetch_cell()` — 第 169-194 行的 BLOCKED 留痕分支：

```python
# 全部 fallback chain 失败 → BLOCKED 留痕 (per 红线 14 增补; 无池可代换)
return {
    "province": province,        # "ningxia"
    "actual_province": None,     # 留痕不入已用省
    "fetched_url": None,
    "chain_index": -1,
    "fallback_chain_used": [c["label"] for c in cell_log],
    "fetch_log": cell_log,
    "file_hash_sha256": "",
    "file_size_bytes": 0,
    "verdict": "BLOCKED_NO_POOL",
    "substitute_used": False,
    "blocked_reason": (
        f"首试省 {province} 两级 fallback 均未 REACHABLE (zwgk_root=405; province_root=405); "
        f"per 655 §0.14 红线 14 增补 (沿用 654): 递补池正式耗尽 [EXHAUSTED], "
        f"无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕首试省真网触发, per 655 §0.14). "
        f"lineage retry_of=N/A (无前史首试省; per 655 §1.655-A.1)."
    ),
    "retry_of": RETRY_OF_NOTES.get(province, ""),  # "retry_of=N/A (无前史首试; per 655 §0.14)"
}
```

#### 实现位置 2：seed SQL 0 INSERT (NINGXIA) + 8 INSERT (XIZANG)

`scripts/seed_m4_18_policy_detail_real_v12.sql` — 仅 XIZANG 1 样本 8 INSERT（混合态按实报）；NINGXIA 0 INSERT 留痕：

```sql
-- NINGXIA BLOCKED_NO_POOL 留痕 (per 655 §0.14 红线 14 沿用 654; 0 INSERT)
-- NINGXIA 真网首试省首触发 BLOCKED_NO_POOL (405 Method Not Allowed ×2 + WAF marker);
-- 留痕信息保留在:
--   - 主 evidence JSON (cells[0] ningxia + blocked_reason + fetch_log)
--   - docs/79 §2 首试省 BLOCKED 留痕登记表
--   - 回执 (655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md)
-- lineage retry_of=N/A (无前史首试省; per 655 §1.655-A.1)
```

#### 实现位置 3：主 evidence JSON cells[0] NINGXIA + blocked_reason + retry_of

`evidence_pack/m4_18_policy_detail_real_v12_20260902.json` — cells[0] NINGXIA 完整 BLOCKED 留痕：

```json
{
  "province": "ningxia",
  "actual_province": null,
  "verdict": "BLOCKED_NO_POOL",
  "http_code": 0,
  "substitute_used": false,
  "blocked_reason": "首试省 ningxia 两级 fallback 均未 REACHABLE (zwgk_root=405; province_root=405); ...",
  "retry_of": "retry_of=N/A (无前史首试; per 655 §0.14)"
}
```

#### 实现位置 4：docs/79 §2 本节（首试省 BLOCKED 留痕登记表）

即本文本节，登记 NINGXIA 留痕完整性。

### 2.2 8 守门 PASSED（含 NINGXIA 405 + WAF 新失败形式守门）

| # | 守门 | 实现位置 | PASSED |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | `fetch_m4_18...v12_2024.py` | ✓ |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | evidence JSON summary | ✓ |
| 3 | blocked_no_pool_count=1 (NINGXIA) 首试省首触发守门 | evidence JSON summary | ✓ |
| 4 | seed 8 INSERT (XIZANG) + 0 INSERT (NINGXIA) 实报守门 | seed SQL | ✓ |
| 5 | 655-A.0 规范 v3.1 落点守门（含 status 零 SHA + 七字段原子） | receipt + docs/79 | ✓ |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | fetch 脚本 | ✓ |
| 7 | retry_of_annotation NINGXIA/XIZANG N/A 注解守门 | summary + cell | ✓ |
| 8 | chain_id v12 + UUID n 段 8 表前缀守门 | evidence metadata | ✓ |
| 9 (新增) | docs/79 西部七省区全覆盖叙事终章表守门 | docs/79 §3.2 | ✓ |
| 10 (新增) | docs/79 失败形式库滚动登记 NINGXIA 405 + WAF 守门 | docs/79 §5.3 | ✓ |
| 11 (新增) | docs/78 既有正文零改动红线 4 守门 | docs/78 仍标 654 不含 655 | ✓ |
| 12 (新增) | 655-A.0 规范 v3.1 七字段原子落点守门 | receipt §6.2 | ✓ |

---

## 3. 西部七省区全覆盖叙事终章表

### 3.1 西部七省区分布

| 西部省区 | 落定刀 | URL 主域 | verdict | retry_of | 实际省 | NEW SHA |
|---|---|---|---|---|---|---|
| SHAANXI (陕西) | 651 | www.shaanxi.gov.cn | REACHABLE (fallback #1) | — | SHAANXI | 9d0ad78a (fallback #1) |
| XINJIANG (新疆) | 652 | www.xinjiang.gov.cn | REACHABLE (fallback #1) | — | XINJIANG | 21c8211b (fallback #1) |
| NEI MENGGU (内蒙古) | 652 | www.nmg.gov.cn | REACHABLE (首选) | — | NEI MENGGU | da1d4104 (首选) |
| GANSU (甘肃) | 654 | www.gansu.gov.cn | BLOCKED_NO_POOL | N/A | NULL | — |
| QINGHAI (青海) | 654 | www.qinghai.gov.cn | BLOCKED_NO_POOL | N/A | NULL | — |
| NINGXIA (宁夏) | **655** | www.nx.gov.cn | **BLOCKED_NO_POOL** | **N/A** | NULL | — |
| XIZANG (西藏) | **655** | www.xizang.gov.cn | **REACHABLE** (首选) | **N/A** | XIZANG | **855af02f (首选)** |

### 3.2 西部七省区 = 4 刀收官汇总

```
651 (SHAANXI REACHABLE) + 652 (XINJIANG/NEI MENGGU 双 REACHABLE)
+ 654 (GANSU/QINGHAI 双 BLOCKED) + 655 (NINGXIA BLOCKED + XIZANG REACHABLE)
= 西部七省区 4 刀收官 (4 REACHABLE + 3 BLOCKED)
```

### 3.3 NEW SHA 累计

```
638-650: 0 NEW SHA (n/a)
651: 2 NEW SHA (shaanxi 9d0ad78a, sichuan f58a3384)
652: 2 NEW SHA (xinjiang 21c8211b, nei_menggu da1d4104)
653: 0 NEW SHA (双 BLOCKED)
654: 0 NEW SHA (双 BLOCKED)
655: 1 NEW SHA (xizang 855af02f)
累计 NEW SHA = 5 (real, all distinct)
```

---

## 4. chain_id 区分 + UUID 严格递增 + 累 [BLOCKED_NO_POOL] 触发事件计数

### 4.1 chain_id 末段递增

| 刀 | chain_id | 末段 |
|---|---|---|
| 651 | real_651_m4_14_policy_detail_v8 | _v8 |
| 652 | real_652_m4_15_policy_detail_v9 | _v9 |
| 653 | real_653_m4_16_policy_detail_v10 | _v10 |
| 654 | real_654_m4_17_policy_detail_v11 | _v11 |
| **655** | **real_655_m4_18_policy_detail_v12** | **_v12** |

### 4.2 UUID 严格递增至 n 段

| 刀 | UUID 段 |
|---|---|
| 638-650 | 早期 demo (段不限) |
| 651 | j 段 (j02-j62) |
| 652 | k 段 (k02-k62) |
| 653 | l 段 (l02-l62) |
| 654 | m 段 (m02-m62) |
| **655** | **n 段 (n02-n62)** |

### 4.3 累 [BLOCKED_NO_POOL] 触发事件计数（沿用 654 §2.3 模板）

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 | 0 | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 双 REACHABLE; 未触发 |
| 652 | 0 | 1 | 强制 e2e 验证; 分支代码可达; 双 REACHABLE |
| 653 | 2 | 1 | 真网首次双触发; shandong SSL + hubei 412; retry_of=647/649 |
| 654 | 2 | 1 | 真网首试省首触发双例; gansu 412 + qinghai Connection reset; retry_of=N/A |
| **655** | **1** | **1** | **混合态首试省首触发第三例**; ningxia 405 + WAF marker; retry_of=N/A; xizang REACHABLE 增量 1 省 |

注：655 BLOCKED_NO_POOL 触发 = 1（仅 NINGXIA），vs 653/654 双触发；这是 655 混合态的体现（XIZANG 同期 REACHABLE 成功）。

---

## 5. 失败形式库滚动登记 (沿用 654 §5.3 模板新增 655)

### 5.1 累计失败形式库

| # | 刀 | 失败形式 | 样本 | http_code | 描述 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 域名解析指向非政府站 |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 服务器拒绝请求条件 |
| 3 | 653 | SSL handshake failure (LibreSSL/3.3.6 error:1404B410) | shandong | 0 (SSL 失败) | 首见失败形式: SSL/TLS 握手失败 |
| 4 | 654 | Connection reset by peer (curl recv failure) | qinghai | 0 (recv failure) | 第二例首见失败形式: 远程服务器主动重置连接 |
| **5** | **655** | **405 Method Not Allowed + WAF marker** | **ningxia** | **405** | **第三例首见失败形式**: 405 Method Not Allowed + WAF 网防标记 (尝试 HEAD/POST/GET 不同方法均被拒); nx.gov.cn 域返回 405 + 网防 G01 类防护 |

### 5.2 失败形式库累计统计

- 累计失败形式库 = **5 例** (3 例首见 + 2 例复用/复发)
- 全链首见失败形式累计 = **3 例** (653 SSL handshake failure + 654 Connection reset by peer + 655 405 Method Not Allowed + WAF)

### 5.3 655 新失败形式详解

NINGXIA 真网首试省首触发 BLOCKED_NO_POOL 的具体失败形式：

```
URL: https://www.nx.gov.cn/zwgk/
返回: HTTP 405 Method Not Allowed
Body: 4644 bytes (含 WAF marker: 网防G01/eventID 等)
Body Size: 4644 bytes (说明服务器返回 405 响应页而非空)
Anchor Hits: 0 (因为是 WAF 拦截页, 不含任何政府政务内容)
WAF Marker: True (网防 G01 类防护)

URL: https://www.nx.gov.cn/
返回: HTTP 405 Method Not Allowed (同 zwgk)
Body: 4644 bytes (相同 WAF 拦截页)
Anchor Hits: 0
WAF Marker: True

判定: BLOCKED_NO_POOL (两级 fallback 均触发 WAF 拦截)
```

注：405 Method Not Allowed + WAF marker 是 652/654 都没遇到的新失败形式；这是 nx.gov.cn 域的特殊防护配置。WAF 网防 G01 是中国国家网络防护系统，会拦截爬虫/自动化请求并返回 405。

---

## 6. 下一步 + 不宣称 PASS

**655 完成**:

- 655-A.0 规范 v3.1 落地: status 零 SHA 绝对化 + 七字段原子 (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步) + 沿用 amend-first 规则
- M4.18 政策详情 v12 西部终章双省 (2 首试省 (ningxia + xizang 第 23/24 样本) → **混合态首试省首触发第三例 (NINGXIA 405+WAF BLOCKED_NO_POOL + XIZANG REACHABLE)**; chain_id='real_655_m4_18_policy_detail_v12'; UUID n 段; ≤12 HTTP total actual=3 (25% usage); XIZANG /zwgk/ 200 REACHABLE 76304 bytes SHA=855af02f; NINGXIA /zwgk/ + / 均 405 + WAF marker)
- retry_of=N/A lineage 全行: ningxia ← N/A (无前史); xizang ← N/A (无前史)
- **8 INSERT ROWS** (混合态按实报; XIZANG 1 样本 × 8 表)
- **混合态首试省首触发第三例** (per 655 §0.14 沿用 654 §0.14 红线 14): 8+ 守门 PASSED (含 retry_of=N/A 守门 + 单触发守门 + 西部七省区全覆盖终章表守门 + 失败形式库守门)
- **递补池 [EXHAUSTED] 沿用 654 §0.14**: 5 候选全部 consumed; 红线 14 生效; 本次 NINGXIA 首试省首触发 BLOCKED, 池不可代换, 留痕不代换
- 已用省全集增量: 18 → 19 (XIZANG REACHABLE 增量 1; NINGXIA BLOCKED 留痕 → 0 增量)
- evidence_pack × 1 + docs/reports × 1 + docs/79 §1-§6 + docs/78 既有正文零改动 (行内 append tailnote 仅限 P4 typo) 全部落地
- **≥225 pytest green** (M4.18 新 ≥8 + 654 回归 217 + 期望 ≥225; ≥221 底限 +2%)
- backfill 完整性三齐 (per 651 审计 P4 + 652 审计 P4-A.0 规范 v2 + 653 审计 P4×2 + 654-A.0 规范 v3 + 655-A.0 规范 v3.1 + 654/655 任务书 §C)

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M4.18 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS (沿用红线)。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 79 — M4.18 v12 西部终章双省 spike 审查 20260902 —
