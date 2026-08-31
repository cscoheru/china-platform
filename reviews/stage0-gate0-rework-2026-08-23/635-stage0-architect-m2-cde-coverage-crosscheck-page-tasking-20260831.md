# 635 — M2-c+d+e 合刀：31 省覆盖 + 跨源核对 + 08b 研究页（架构师任务书）

> **类型**: Architect 签发 · **大任务合刀**（集中摄影）  
> **日期**: 2026-08-31  
> **依据**: `docs/56` §M2-c/d/e；`docs/08b` §1.2；634 PASS；用户「签发一个大任务」  
> **前置**: M2-b `634 PASS` · 省级 COVERED 5/31 + 国家 1/1  
> **禁止**: Gate/O1/M2 PASS；首页/目录 FETCHED；补零；静默硬编码 value；买库

---

## 0. 一句话

一次交付把 08b 问到「可回答」：**剩余省 2024 GDP 尽量 COVERED（缺省写 missing）→ 国家 vs 省核对表 → `/research/q1-2024-gdp` 真值页**；**一份回执 §PHOTO 集中摄影**。

---

## 1. 范围（三块合一）

### Block C — 扩覆盖（原 M2-c）

**目标：** 省级 `COVERED + BLOCKED(有 missing_reason) ≥ 20/31`；能取尽取。  
**硬闸：** 若 COVERED&lt;20 **且** 无 missing 的 PENDING/EMPTY 仍多 → **不得交卷**（docs/56）。

**必做：**

1. 优先补 **苏 / 浙 / 粤**（M2-b 反爬失败）；换 UA/镜像/用户投递 PDF 表均可，须 SHA 锁。  
2. 其余 PENDING 省：定稿页/xlsx → archive → FETCHED + observation SUCCESS；失败 → `BLOCKED` + **诚实** `missing_reason`（不得假 FETCHED）。  
3. **解析纪律（相对 633 收紧）：**  
   - value **必须以源文件解析为主**；  
   - 硬编码仅允许作 *expected 交叉校验*；  
   - regex 与 expected 差 &gt;0.5 亿 → **FAIL 该省**（禁止 `return expected` 静默回落）。  
4. 重跑 `report_m2_gdp_coverage.py`；更新 `docs/reports/`。

### Block D — 跨源核对（原 M2-d）

**目标：** 国家公布的分省 GDP（或国家公报中的汇总口径）vs 本库各省 observation。

**交付：**

- `docs/reports/m2_2024_gdp_crosscheck_YYYYMMDD.md`（或 CSV）  
- 规则（docs/54 / 08b）：相对差 **&lt;0.5% → CONSISTENT**；否则 **QUARANTINED** + caveat  
- 无国家分省表时：用「31 省库内加总 vs 国家 GDP」作 **弱核对**，并标注方法局限  
- pytest：`tests/test_m2_crosscheck.py`（至少：报告存在；QUARANTINED 行有理由；无静默改 value）

### Block E — 研究页（原 M2-e）

**目标：** `frontend/app/research/q1-2024-gdp/page.tsx`

- 页头：**「08b · 2024 年国家+31 省 GDP 一致率 · 非 Gate PASS」**  
- `USE_MOCK=false` → 真 API / 或只读 coverage+crosscheck 聚合 API（新建最小 endpoint 亦可）  
- 展示：覆盖率、CONSISTENT/QUARANTINED 计数、可点回 SHA 前 8  
- smoke-check + `tests/test_m2_q1_page.py`  
- **不改** `/provinces/jiangsu` 冒充全国

### Block F 切片（文档，轻量）

- `docs/56` / `docs/54` M2 指针勾选 C/D/E  
- EXEC-QUEUE §NOW → 「M2 待用户有限通过」或「M2-f 回补 2001」  
- **不**自动宣布 M2 PASS

---

## 2. 集中摄影（§PHOTO — 唯一回执）

回执：`635-stage0-cc-m2-cde-receipt-YYYYMMDD.md`

| 块 | 内容 |
|---|---|
| PHOTO-1 | `pytest tests/test_m2_*.py tests/test_m1_reference_seed.py -q` 一行（须绿） |
| PHOTO-2 | coverage Summary：COVERED / BLOCKED / PENDING；**COVERED+诚实 BLOCKED≥20** |
| PHOTO-3 | 苏浙粤三行状态（FETCHED 或 BLOCKED+reason） |
| PHOTO-4 | crosscheck 表头 + CONSISTENT/QUARANTINED 计数 |
| PHOTO-5 | `/research/q1-2024-gdp` smoke 末行 |
| PHOTO-6 | 证明无静默硬编码回落（grep 或测试：parse mismatch → fail） |
| PHOTO-7 | 红线表 + 文件清单 |

双推后 5m POLL。

---

## 3. 明确不做

- 不宣布 Gate / M2 PASS  
- 不买商业库；不 OCR 生产化挡路  
- 不镀铬四轨；不改 docs/45/50 正文  
- 不把目录页标 FETCHED  

---

## 4. Cursor 审验点

- COVERED+诚实缺口 ≥20/31  
- 无 `return expected` 静默路径（或测试锁死）  
- crosscheck 存在且不改 observation.value  
- q1 页非 mock、非 Gate 宣告  

— End 635 —
