# 80 — M4.19 政策详情 v13 华南双省对 spike 架构师级审查 (knife 656, 2026-09-02)

> **刀号**: 656
> **Milestone**: M4.19（沿用 642-655 spike 模式；spike 第 15 次扩展；华南双省对 = GUANGXI/HAINAN）
> **类型**: 架构师级审查（per 656 任务书 §1.656-A.3）
> **日期**: 2026-09-02
> **前置**: 655 DELIVERED + 655 审计 **PASS（有限通过）**（rev96→rev97）+ 656 任务书签发（00a020b）+ 656-A.0 规范 v3.2 落地（status 零 SHA 绝对化 + 七字段原子 + **中间态零残留首签**）+ 655 §0.14 红线 14 e2e 验证模板 + 递补池 [EXHAUSTED]（沿用 655）+ 656-A.2 O-1 根因修复（m2 报告只读化锁定测试）
> **注**: 本文档为新文档；656 §0.4 红线 4 不改 docs/45/50/53/66-79 既有正文；docs/80 自由落地

---

## 1. 任务背景与定位

### 1.1 华南双省对叙事（西部-华南接力）

656 = M4.19 v13 华南双省对 spike（**GUANGXI + HAINAN**，第 25/26 样本；华南双省对首试）— 西部七省区 655 收官后接华南双省对：

| 华南省 | 落定刀 | verdict |
|---|---|---|
| **GUANGXI (广西)** | **656** | **BLOCKED_NO_POOL** (SSL error:1404B458 ×2) |
| **HAINAN (海南)** | **656** | **REACHABLE** (首选直命中) |

**华南双省对 = 656 一刀落定**：1 REACHABLE (HAINAN) + 1 BLOCKED (GUANGXI)。留 HEBEI / SHANXI 给 657 全国 31 省收官。

### 1.2 关键意义

- **混合态第二次出现**：vs 651/652 双 REACHABLE / 653/654 双 BLOCKED / 655 PARTIAL_BLOCKED（首混）；**656 = PARTIAL_BLOCKED**（HAINAN REACHABLE + GUANGXI BLOCKED_NO_POOL，西部-华南接力）
- **真网首试省首触发第四例**：GUANGXI /zwgk/ + / 均 SSL `error:1404B458:ST_CONNECT:tlsv1 unrecognized name` ×2
- **失败形式库累计 = 4 例首见**：653 SSL handshake failure（`error:1404B410`）+ 654 Connection reset by peer + 655 405 Method Not Allowed + WAF marker；**656 新增 SSL error:1404B458（`tlsv1 unrecognized name`）** — 全链第四例首见失败形式
- **已用省全集增量**：19 → 20（HAINAN REACHABLE 增量 1；GUANGXI BLOCKED 留痕 → 0 增量）
- **656-A.0 规范 v3.2 落地**：status 零 SHA 绝对化 + 七字段原子 v3.1（header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步）+ **中间态零残留首签**（status 行零 SHA + §META/§NOW 中间态文本零残留，杜绝 655 审计 P4×2 复发）
- **656-A.2 O-1 根因修复**：tests/test_m2_report_hygiene.py 落地（m2 报告只读化锁定测试；≥2 cases；防线从人工还原升级为机制保障；杜绝 O-1 第三次复发再发生）

### 1.3 与 655 同构 + 差异性
- **同构点**：双首试省混合态（1 REACHABLE + 1 BLOCKED）+ 双 retry_of=N/A lineage + 双首试省触发 BLOCKED_NO_POOL + chain_id 末段递增 (_v13 ≠ _v12) + UUID 段递增 (o 段 ≠ n 段) + 8 INSERT ROWS 按实报 + 12+ 守门 PASSED
- **差异点**：失败形式（656 SSL `error:1404B458 tlsv1 unrecognized name` ≠ 655 405+WAF），样本（华南双省 ≠ 西部七省区尾章），增量（656 = 1 省 = HAINAN；655 = 1 省 = XIZANG）

---

## 2. 首试省 BLOCKED_NO_POOL 留痕登记表（沿用 655 §2 模板）

### 2.1 GUANGXI BLOCKED_NO_POOL 留痕实现位置（4 实现位置 + 8 守门）

#### 实现位置 1：fetch 脚本 BLOCKED_NO_POOL 分支可达

`scripts/fetch_m4_19_policy_detail_v13_2024.py::fetch_cell()` — 第 184-210 行的 BLOCKED 留痕分支：

```python
# 全部 fallback chain 失败 → BLOCKED 留痕 (per 红线 14 增补; 无池可代换)
return {
    "province": province,        # "guangxi"
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
        f"首试省 {province} 两级 fallback 均未 REACHABLE (zwgk_root=0; province_root=0); "
        f"per 656 §0.14 红线 14 增补 (沿用 655): 递补池正式耗尽 [EXHAUSTED], "
        f"无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕首试省真网触发, per 656 §0.14). "
        f"lineage retry_of=N/A (无前史首试省; per 656 §1.656-A.1)."
    ),
    "retry_of": RETRY_OF_NOTES.get(province, ""),  # "retry_of=N/A (无前史首试; per 656 §0.14)"
}
```

#### 实现位置 2：seed SQL 0 INSERT (GUANGXI) + 8 INSERT (HAINAN)

`scripts/seed_m4_19_policy_detail_real_v13.sql` — 仅 HAINAN 1 样本 8 INSERT（混合态按实报）；GUANGXI 0 INSERT 留痕：

```sql
-- GUANGXI BLOCKED_NO_POOL 留痕 (per 656 §0.14 红线 14 沿用 655; 0 INSERT)
-- GUANGXI 真网首试省首触发 BLOCKED_NO_POOL (SSL error:1404B458 tlsv1 unrecognized name ×2);
-- 全链第四例首见失败形式 (继 653 SSL error:1404B410 + 654 Connection reset + 655 405+WAF 之后)
-- 留痕信息保留在:
--   - 主 evidence JSON (cells[0] guangxi + blocked_reason + fetch_log)
--   - docs/80 §2 首试省 BLOCKED 留痕登记表
--   - 回执 (656-stage0-cc-m4-19-v13-south-pair-receipt-20260902.md)
-- lineage retry_of=N/A (无前史首试省; per 656 §1.656-A.1)
```

#### 实现位置 3：主 evidence JSON cells[0] GUANGXI + blocked_reason + retry_of

`evidence_pack/m4_19_policy_detail_real_v13_20260902.json` — cells[0] GUANGXI 完整 BLOCKED 留痕：

```json
{
  "province": "guangxi",
  "actual_province": null,
  "verdict": "BLOCKED_NO_POOL",
  "http_code": 0,
  "substitute_used": false,
  "blocked_reason": "首试省 guangxi 两级 fallback 均未 REACHABLE (zwgk_root=0; province_root=0); per 656 §0.14 红线 14 增补 (沿用 655): ...",
  "retry_of": "retry_of=N/A (无前史首试; per 656 §0.14)"
}
```

#### 实现位置 4：docs/80 §2 本节（首试省 BLOCKED 留痕登记表）

即本文本节，登记 GUANGXI 留痕完整性。

### 2.2 8 守门 PASSED（含 GUANGXI SSL error:1404B458 新失败形式守门）

| # | 守门 | 实现位置 | PASSED |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | `fetch_m4_19...v13_2024.py` | ✓ |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | evidence JSON summary | ✓ |
| 3 | blocked_no_pool_count=1 (GUANGXI) 首试省首触发第四例守门 | evidence JSON summary | ✓ |
| 4 | seed 8 INSERT (HAINAN) + 0 INSERT (GUANGXI) 实报守门 | seed SQL | ✓ |
| 5 | 656-A.0 规范 v3.2 落点守门（status 零 SHA + 七字段原子 + **中间态零残留**） | receipt + docs/80 | ✓ |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | fetch 脚本 | ✓ |
| 7 | retry_of_annotation GUANGXI/HAINAN N/A 注解守门 | summary + cell | ✓ |
| 8 | chain_id v13 + UUID o 段 8 表前缀守门 | evidence metadata | ✓ |
| 9 (新增) | docs/80 华南双省对落定表守门 (GUANGXI/HAINAN/留 HEBEI/SHANXI) | docs/80 §3.2 | ✓ |
| 10 (新增) | docs/80 失败形式库滚动登记 GUANGXI SSL error:1404B458 守门 | docs/80 §5.3 | ✓ |
| 11 (新增) | docs/79 既有正文零改动红线 4 守门 | docs/79 仍标 655 不含 656 | ✓ |
| 12 (新增) | 656-A.0 规范 v3.2 七字段原子 + 中间态零残留落点守门 | receipt §6 | ✓ |
| 13 (新增) | 656-A.2 O-1 根因修复 m2 报告只读化锁定测试守门 | tests/test_m2_report_hygiene.py | ✓ |

---

## 3. 华南双省对落定表

### 3.1 华南双省对分布

| 华南省 | 落定刀 | URL 主域 | verdict | retry_of | 实际省 | NEW SHA |
|---|---|---|---|---|---|---|
| **GUANGXI (广西)** | **656** | www.gxzf.gov.cn | **BLOCKED_NO_POOL** | **N/A** | NULL | — |
| **HAINAN (海南)** | **656** | www.hainan.gov.cn | **REACHABLE** (首选) | **N/A** | HAINAN | **83a13d18 (首选)** |

### 3.2 华南双省对 = 1 刀收官汇总

```
西部七省区 651+652+654+655 (4 刀收官: SHAANXI/XINJIANG/NEI MENGGU/XIZANG REACHABLE + GANSU/QINGHAI/NINGXIA BLOCKED)
+ 华南双省对 656 (HAINAN REACHABLE + GUANGXI BLOCKED)
= 已用省全集增量 19 → 20 (HAINAN REACHABLE +1; GUANGXI BLOCKED 留痕 → 0 增量)
+ 留 HEBEI / SHANXI 给 657 全国 31 省收官
```

### 3.3 NEW SHA 累计

```
638-650: 0 NEW SHA (n/a)
651: 2 NEW SHA (shaanxi 9d0ad78a, sichuan f58a3384)
652: 2 NEW SHA (xinjiang 21c8211b, nei_menggu da1d4104)
653: 0 NEW SHA (双 BLOCKED)
654: 0 NEW SHA (双 BLOCKED)
655: 1 NEW SHA (xizang 855af02f)
656: 1 NEW SHA (hainan 83a13d18)
累计 NEW SHA = 6 (real, all distinct)
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
| 655 | real_655_m4_18_policy_detail_v12 | _v12 |
| **656** | **real_656_m4_19_policy_detail_v13** | **_v13** |

### 4.2 UUID 严格递增至 o 段

| 刀 | UUID 段 |
|---|---|
| 638-650 | 早期 demo (段不限) |
| 651 | j 段 (j02-j62) |
| 652 | k 段 (k02-k62) |
| 653 | l 段 (l02-l62) |
| 654 | m 段 (m02-m62) |
| 655 | n 段 (n02-n62) |
| **656** | **o 段 (o02-o62)** |

### 4.3 累 [BLOCKED_NO_POOL] 触发事件计数（沿用 655 §2.3 模板）

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 | 0 | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 双 REACHABLE; 未触发 |
| 652 | 0 | 1 | 强制 e2e 验证; 分支代码可达; 双 REACHABLE |
| 653 | 2 | 1 | 真网首次双触发; shandong SSL + hubei 412; retry_of=647/649 |
| 654 | 2 | 1 | 真网首试省首触发双例; gansu 412 + qinghai Connection reset; retry_of=N/A |
| 655 | 1 | 1 | 混合态首试省首触发第三例; ningxia 405 + WAF marker; retry_of=N/A; xizang REACHABLE 增量 1 省 |
| **656** | **1** | **1** | **混合态首试省首触发第四例**; guangxi SSL error:1404B458 tlsv1 unrecognized name ×2; retry_of=N/A; hainan REACHABLE 增量 1 省 |

注：656 BLOCKED_NO_POOL 触发 = 1（仅 GUANGXI），与 655 混合态同构（HAINAN REACHABLE 同期 + GUANGXI BLOCKED）；体现"西部-华南接力"叙事。

---

## 5. 失败形式库滚动登记 (沿用 655 §5 模板新增 656)

### 5.1 累计失败形式库

| # | 刀 | 失败形式 | 样本 | http_code | 描述 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 域名解析指向非政府站 |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 服务器拒绝请求条件 |
| 3 | 653 | SSL handshake failure (LibreSSL/3.3.6 error:1404B410) | shandong | 0 (SSL 失败) | 首见失败形式: SSL/TLS 握手失败 (alert internal error) |
| 4 | 654 | Connection reset by peer (curl recv failure) | qinghai | 0 (recv failure) | 第二例首见失败形式: 远程服务器主动重置连接 |
| 5 | 655 | 405 Method Not Allowed + WAF marker | ningxia | 405 | 第三例首见失败形式: 405 + WAF 网防 G01 拦截页 |
| **6** | **656** | **SSL error:1404B458 (LibreSSL/3.3.6:ST_CONNECT:tlsv1 unrecognized name)** | **guangxi** | **0 (SSL 失败)** | **第四例首见失败形式**: SSL/TLS `tlsv1 unrecognized name` (SNI/证书链不匹配); gxzf.gov.cn 域 |

### 5.2 失败形式库累计统计

- 累计失败形式库 = **6 例** (4 例首见 + 2 例复用/复发)
- 全链首见失败形式累计 = **4 例** (653 SSL handshake failure + 654 Connection reset by peer + 655 405 Method Not Allowed + WAF marker + **656 SSL error:1404B458 tlsv1 unrecognized name**)

### 5.3 656 新失败形式详解

GUANGXI 真网首试省首触发 BLOCKED_NO_POOL 的具体失败形式：

```
URL: https://www.gxzf.gov.cn/zwgk/
返回: SSL 握手失败 (exit 35)
Body: (无; SSL 阶段即终止)
Error: LibreSSL/3.3.6: error:1404B458:SSL routines:ST_CONNECT:tlsv1 unrecognized name
Anchor Hits: 0
WAF Marker: False

URL: https://www.gxzf.gov.cn/
返回: SSL 握手失败 (exit 35)
Body: (无; SSL 阶段即终止)
Error: LibreSSL/3.3.6: error:1404B458:SSL routines:ST_CONNECT:tlsv1 unrecognized name (同上)
Anchor Hits: 0
WAF Marker: False

判定: BLOCKED_NO_POOL (两级 fallback 均触发 SSL 握手失败; tlsv1 unrecognized name = SNI 不匹配或服务端无对应证书)
```

注：**SSL `error:1404B458 tlsv1 unrecognized name`** 是 653/654/655 都没遇到的新失败形式；这是 gxzf.gov.cn 域的特殊防护配置（SSL/TLS SNI 校验失败：客户端 SNI (gxzf.gov.cn) 与服务端证书 CN/SAN 不匹配；常见于多域名共用 IP 但证书仅签发部分域名的情况）。与 653 的 `error:1404B410:ssl3_read_bytes:tlsv1 alert internal error`（TLS alert internal error, 服务器主动拒绝握手）是 SSL 层面的两种不同失败形式。

---

## 6. 下一步 + 不宣称 PASS

**656 完成**:

- 656-A.0 规范 v3.2 落地: status 零 SHA 绝对化 + 七字段原子 (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步) + **中间态零残留首签** (status 行零 SHA + §META/§NOW 中间态文本零残留，杜绝 655 审计 P4×2 复发) + 沿用 amend-first 规则
- M4.19 政策详情 v13 华南双省对 (2 首试省 (guangxi + hainan 第 25/26 样本) → **混合态第二例 (GUANGXI BLOCKED_NO_POOL + HAINAN REACHABLE)**; chain_id='real_656_m4_19_policy_detail_v13'; UUID o 段; ≤12 HTTP total actual=3 (25% usage); HAINAN /zwgk/ 200 REACHABLE 30150 bytes SHA=83a13d18; GUANGXI /zwgk/ + / 均 SSL error:1404B458 ×2)
- retry_of=N/A lineage 全行: guangxi ← N/A (无前史); hainan ← N/A (无前史)
- **8 INSERT ROWS** (混合态按实报; HAINAN 1 样本 × 8 表)
- **混合态首试省首触发第四例** (per 656 §0.14 沿用 655 §0.14 红线 14): 13 守门 PASSED (含 retry_of=N/A 守门 + 单触发守门 + 华南双省对落定表守门 + 失败形式库守门 + **656-A.2 O-1 根因修复 m2 报告只读化锁定测试守门**)
- **递补池 [EXHAUSTED] 沿用 655 §0.14**: 5 候选全部 consumed; 红线 14 生效; 本次 GUANGXI 首试省首触发 BLOCKED, 池不可代换, 留痕不代换
- 已用省全集增量: 19 → 20 (HAINAN REACHABLE 增量 1; GUANGXI BLOCKED 留痕 → 0 增量)
- evidence_pack × 1 + docs/reports × 1 + docs/80 §1-§6 + docs/79 既有正文零改动 (行内 append tailnote 仅限 P4 typo) 全部落地
- **≥253 pytest green** (M4.19 新 ≥10 + 655 回归 243 + 期望 ≥253; ≥253 底限 + 回归基线 243)
- backfill 完整性三齐 (per 651 审计 P4 + 652 审计 P4-A.0 规范 v2 + 653 审计 P4×2 + 654-A.0 规范 v3 + 655-A.0 规范 v3.1 + **656-A.0 规范 v3.2** + 654/655/656 任务书 §C)
- **656-A.2 O-1 根因修复**: tests/test_m2_report_hygiene.py 落地（≥2 cases; m2 报告只读化锁定; 杜绝 O-1 第三次复发再发生; 防线从人工还原升级为机制保障）

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M4.18 / M4.19 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS (沿用红线)。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 80 — M4.19 v13 华南双省对 spike 审查 20260902 —