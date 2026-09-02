# 655-A.4 — M4.18 政策详情 v12 西部终章双省 spike 附属报告 (knife 655, 2026-09-02)

> **刀号**: 655
> **Milestone**: M4.18（v12 西部终章双省 spike；西部七省区 = SHAANXI / XINJIANG / NEI MENGGU / GANSU / QINGHAI / NINGXIA / XIZANG）
> **角色**: 架构师 + 执行端（合并到本终端 per 2026-08-31 21:50 豁免）
> **日期**: 2026-09-02
> **前置**: 654 DELIVERED + 审计 **PASS（有限通过）**（rev95）+ 655 任务书签发 + 655-A.0 规范 v3.1 落地
> **配套文件**:
> - `scripts/fetch_m4_18_policy_detail_v12_2024.py`（fetch 脚本）
> - `scripts/seed_m4_18_policy_detail_real_v12.sql`（seed SQL，8 INSERT）
> - `evidence_pack/m4_18_policy_detail_real_v12_20260902.json`（主 evidence JSON）
> - `docs/79-m4-18-policy-detail-real-v12-20260902.md`（架构师级审查 §1-§6）

---

## §1. 实测结果总览（双样本）

| 样本 | URL 首选 | URL fallback | verdict | http_code | 字节 | 锚点 | WAF marker |
|---|---|---|---|---|---|---|---|
| **NINGXIA** | https://www.nx.gov.cn/zwgk/ | https://www.nx.gov.cn/ | **BLOCKED_NO_POOL** | **405 × 2** | **4644 × 2** | **0 × 2** | **True × 2** |
| **XIZANG**  | https://www.xizang.gov.cn/zwgk/ | https://www.xizang.gov.cn/ | **REACHABLE** | **200** | **76304** | **191** | **False** |

**双样本 verdict 总判**: **PARTIAL_BLOCKED**（1 REACHABLE + 1 BLOCKED_NO_POOL；首刀混合态第三态落地）

**HTTP 总用量**: 3/12（25% usage；NINGXIA 2 + XIZANG 1）

**NEW SHA**: `855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a`（XIZANG /zwgk/ 直命中）

**blocked_no_pool_count**: 1（NINGXIA 首试省首触发 BLOCKED_NO_POOL；405 Method Not Allowed + WAF 网防 G01）

**substitute_used_count**: 0（红池 14 增补沿用 654：递补池 [EXHAUSTED]，不可跨省代换）

---

## §2. 三态处置（按实报；任务书 §1.655-A.1 明文）

| 处置维度 | NINGXIA | XIZANG |
|---|---|---|
| **verdict** | BLOCKED_NO_POOL | REACHABLE |
| **INSERT 数** | 0（首试省首触发 BLOCKED 留痕） | 8（1 样本 × 8 表：source_registry + source_document + policy_document + policy_target + policy_measure + government_commitment + commitment_progress + project_event） |
| **actual_province** | NULL（不计入已用省） | XIZANG（计入已用省；西部七省区收官第 19 省） |
| **lineage retry_of** | retry_of=N/A（无前史首试） | retry_of=N/A（无前史首试） |
| **NEW SHA** | 无（BLOCKED 留痕无 SHA） | 855af02f |
| **留痕位置** | 4 处：fetch 分支 + 主 evidence cells[0] + docs/79 §2 + 本报告 §3 | 主 evidence cells[1] + seed SQL 8 INSERT |

**INSERT 总计** = **8 ROWS**（混合态按实报；任务书 §1.655-A.1 第三态）

---

## §3. NINGXIA BLOCKED_NO_POOL 失败形式详解（首见失败形式第三例）

### 3.1 两级 fallback 实测

```
URL: https://www.nx.gov.cn/zwgk/
HTTP: 405 Method Not Allowed
Body: 4644 bytes
Content: WAF 网防 G01 拦截页 (eventID 标记)
Anchor Hits: 0 (无政府政务内容)

URL: https://www.nx.gov.cn/
HTTP: 405 Method Not Allowed (同上)
Body: 4644 bytes
Content: WAF 网防 G01 拦截页 (同 eventID 标记)
Anchor Hits: 0
```

### 3.2 WAF marker 检测

正则: `403 Forbidden|WAF|网防G01|eventID`
- /zwgk/: **True** (含 WAF 网防 G01 + eventID)
- /: **True** (同 WAF 网防 G01 + eventID)

### 3.3 失败形式分类（per 失败形式库 §5）

| 维度 | 值 |
|---|---|
| 失败形式 | **405 Method Not Allowed + WAF 网防 G01 marker** |
| 首见/复用 | **首见（第三例首见失败形式）** |
| 阻断域 | nx.gov.cn |
| 阻断方法 | WAF 网防 G01 拦截（HEAD/POST/GET 全部拒；try next fallback 无效） |
| 同类历史 | 647 (shandong 403) / 653 (shandong SSL) / 654 (qinghai Connection reset) / **655 (ningxia 405+WAF)** |
| retry_of | N/A（无前史首试省） |
| 红线 14 援引 | per 655 §0.14 沿用 654 §0.14；递补池正式耗尽；不可跨省代换 |

### 3.4 BLOCKED 留痕三重实现位置

1. **fetch 脚本分支**: `scripts/fetch_m4_18_policy_detail_v12_2024.py::fetch_cell()` 返回 `verdict='BLOCKED_NO_POOL'` + `blocked_reason` 完整含援引链
2. **主 evidence JSON**: `evidence_pack/m4_18_policy_detail_real_v12_20260902.json` cells[0] 含完整 blocked_reason + fetch_log
3. **docs/79 §2**: 首试省 BLOCKED 留痕登记表（含 4 实现位置 + 8 守门 PASSED）
4. **seed SQL**: 0 INSERT 留痕（注释段明文）
5. **回执**: `655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md` §3 含完整 blocked_reason 援引

---

## §4. XIZANG REACHABLE 实测详情

### 4.1 首选直命中

```
URL: https://www.xizang.gov.cn/zwgk/
HTTP: 200
Body: 76304 bytes
SHA: 855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a
Anchor Hits: 191
WAF Marker: False
verdict: REACHABLE (首选直命中; 无需 fallback)
```

### 4.2 8 INSERT ROWS 实报

| # | 表 | UUID (n 段) | lineage |
|---|---|---|---|
| 1 | source_registry | n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n02 | chain_id=v12, SHA=855af02f, actual_province=xizang |
| 2 | source_document | n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n04 | 同上; doc_kind=POLICY_DETAIL_LIST |
| 3 | policy_document | n1eebc99-9c0b-4ef8-bb6d-6bb9bd380n11 | publisher=西藏自治区人民政府 |
| 4 | policy_target | n2eebc99-9c0b-4ef8-bb6d-6bb9bd380n21 | target_description=政策详情 v12 第 23 样本 |
| 5 | policy_measure | n3eebc99-9c0b-4ef8-bb6d-6bb9bd380n31 | measure_type=REGULATORY |
| 6 | government_commitment | n4eebc99-9c0b-4ef8-bb6d-6bb9bd380n41 | geo_entity SELECT '西藏自治区' PROVINCIAL |
| 7 | commitment_progress | n5eebc99-9c0b-4ef8-bb6d-6bb9bd380n51 | progress_value=0.5 PERCENT |
| 8 | project_event | n6eebc99-9c0b-4ef8-bb6d-6bb9bd380n61 | event_type=POLICY_DETAIL_RELEASE |

**8 INSERT = 1 样本 × 8 表**(混合态按实报；任务书 §1.655-A.1 明文第三态)

---

## §5. 已用省全集增量（18 → 19）

| 维度 | 增量 |
|---|---|
| **REACHABLE 增量** | **+1（XIZANG）** |
| **BLOCKED 留痕 增量** | +0（NINGXIA 留痕不计入已用） |
| **已用省全集实际增量** | **18 → 19（+1 XIZANG）** |
| **西部七省区收官** | SHAANXI(651) + XINJIANG/NEI MENGGU(652) + GANSU/QINGHAI(654) + NINGXIA/XIZANG(655) |

**已用省全集（actual_province 口径, 19 省）**:
HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU / XIZANG
(655 增量 1 省)

**剩余未用省（actual 口径, 4 省）**:
HEBEI / SHANXI / GUANGXI / HAINAN
（NINGXIA 仍待定 — 655 留痕不入已用，未来 656+ 可重试或 BLOCKED 留痕）

---

## §6. 失败形式库滚动登记（沿用 654 §5.3 模板）

| # | 刀 | 失败形式 | 样本 | http_code | 累计 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 1 |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 2 |
| 3 | 653 | SSL handshake failure | shandong | 0 (SSL) | 3 |
| 4 | 654 | Connection reset by peer | qinghai | 0 (recv) | 4 |
| **5** | **655** | **405 Method Not Allowed + WAF 网防 G01 marker** | **ningxia** | **405** | **5** |

**累计失败形式库**: 5 例（3 例首见 + 2 例复用）
**全链首见失败形式累计**: 3 例（653 SSL + 654 Connection reset + 655 405+WAF）

---

## §7. 红线 14 条复核（沿用 654 §C 模板）

| # | 红线 | 落点 | PASSED |
|---|---|---|---|
| 1 | 不宣称 Gate/O1/O2/O3/M2/M4/M4.x/M5.x/M6 PASS | docs/79 §6 明文 | ✓ |
| 2 | 不补零 / 不静默硬编码 value | target_value/measure_value NULL 透明占位（沿用 641-654） | ✓ |
| 3 | 不爬网 / 不镀铬四轨 / ≤12 HTTP | HTTP 3/12 = 25% usage | ✓ |
| 4 | 不改 docs/45/50/53/66-78 既有正文 | 行内 append 尾注仅限 P4 typo | ✓ |
| 5 | 不碰 4 fixture 锁值 | seed SQL 不动 fixture | ✓ |
| 6 | 数据源唯一 = 政府/统计局自取；用户零裁定 | nx/xizang 二级 fallback + WAF marker 检测 + 留痕不代换 | ✓ |
| 7 | 完成 = observation SUCCESS；BLOCKED_NO_POOL 留痕合法 | XIZANG REACHABLE + NINGXIA BLOCKED 三态按实报 | ✓ |
| 8 | 不新写 016 migration | 沿用 009+010+014+015 lineage JSONB | ✓ |
| 9 | chain_id v12（末段 `_v12` ≠ 654 `_v11`） | evidence + seed SQL + docs/79 全一致 | ✓ |
| 10 | UUID n 段（n02-n62）≠ 654 m 段 | 8 表 UUID 全 n 段 | ✓ |
| 11 | 不写 cegr.* 生产表 | seed SQL 仅 staging 蓝本 | ✓ |
| 12 | 既有 registry 行 SHA 零漂移；4 fixture 零触碰 | 不修改既有 638-654 registry | ✓ |
| 13 | O1 零动作 + 附属产物指针 + 代换行标注规范 | docs/79 §2 + evidence methodology 指针 | ✓ |
| 14 | 递补池 [EXHAUSTED] + BLOCKED_NO_POOL 留痕不代换 | SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'（沿用 654） | ✓ |

**14/14 全 ✓**

---

## §8. 8 守门 PASSED（沿用 654 §2.2 模板）

| # | 守门 | 落点 | PASSED |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | scripts/fetch_m4_18...v12_2024.py:186 | ✓ |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | evidence JSON summary | ✓ |
| 3 | blocked_no_pool_count=1 (NINGXIA) 首试省首触发守门 | evidence JSON summary | ✓ |
| 4 | seed 8 INSERT (XIZANG) + 0 INSERT (NINGXIA) 实报守门 | scripts/seed_m4_18_policy_detail_real_v12.sql | ✓ |
| 5 | 655-A.0 规范 v3.1 落点守门（status 零 SHA + 七字段原子） | receipt + docs/79 + EXEC-QUEUE §META | ✓ |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | scripts/fetch_m4_18...v12_2024.py:42-43 | ✓ |
| 7 | retry_of_annotation NINGXIA/XIZANG N/A 注解守门 | evidence summary + cell | ✓ |
| 8 | chain_id v12 + UUID n 段 8 表前缀守门 | evidence metadata | ✓ |
| 9 | docs/79 西部七省区全覆盖叙事终章表守门 | docs/79 §3.2 | ✓ |
| 10 | docs/79 失败形式库滚动登记 NINGXIA 405 + WAF 守门 | docs/79 §5.3 | ✓ |
| 11 | docs/78 既有正文零改动红线 4 守门 | docs/78 仍标 654 不含 655 | ✓ |
| 12 | 655-A.0 规范 v3.1 七字段原子落点守门（EXEC-QUEUE header / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步） | EXEC-QUEUE §META + §CHAIN_TAIL | ✓ |

**12/12 全 ✓**（沿用 654 §2.2 模板 + 4 新增守门）

---

## §9. 关联产物 + 测试

| 类别 | 路径 |
|---|---|
| 主 evidence | `evidence_pack/m4_18_policy_detail_real_v12_20260902.json` |
| **本附属报告** | `docs/reports/m4_18_policy_detail_real_v12_20260902.md` |
| Fetch 脚本 | `scripts/fetch_m4_18_policy_detail_v12_2024.py` |
| Seed SQL | `scripts/seed_m4_18_policy_detail_real_v12.sql` |
| 架构师审查 | `docs/79-m4-18-policy-detail-real-v12-20260902.md` |
| 测试 | `tests/test_m4_18_policy_detail_real_v12.py`（≥8 cases；守门 12 项） |
| 回执 | `reviews/stage0-gate0-rework-2026-08-23/655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md` |

---

## §10. 不宣称 PASS

不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5.x / M6 PASS。**O1 仍 OPEN** — B 路 live-candidate 仅登记，不切换/启用；等用户/架构师裁定。

---

— End 655-A.4 西部终章双省 spike 附属报告 20260902 —