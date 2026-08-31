# 628 — Cursor 审验：627 M1-b（T2+T3）PASS

- 日期：2026-08-31
- 对象：CC 回执 `627-stage0-cc-m1-b-t2-t3-receipt-20260831.md` + commit `0ee445e`
- 任务书：`627-stage0-architect-m1-b-t2-t3-observation-success-tasking-20260831.md`

---

## 判定：**PASS**

| 项 | 回执声称 | 独立复验 | 判定 |
|---|---|---|---|
| pytest 闸 | 15 passed | `pytest tests/test_m1_first_series.py tests/test_m1_reference_seed.py -q` → **15 passed** | ✅ |
| 无占位 UUID | 已删 `UUID(int=0)` | `provincial_yearbook.py` 无匹配 | ✅ |
| category | `PROVINCIAL_BULLETIN` | 代码 + 测试 fixture 一致 | ✅ |
| SUCCESS 语义 | 2/2 inserted | 测试 `test_ingest_status_success` 绿 | ✅ |
| GDP 真值 | value=31336.72 | `test_gdp_observation_count_ge_1` 绿 | ✅ |
| 一跳 SHA | c5cf5abe… | `test_observation_one_hop_to_source` + 文件 shasum 一致 | ✅ |
| 非首页 URL | tjyb index | `test_no_homepage_html_as_observation_source` 绿 | ✅ |
| 红线 | 未宣布 Gate/O1/M1 | 回执 §9 自审 + 本审无越界 | ✅ |

**不宣布：** Gate / O1 / M1 PASS（M1 仍缺 T4–T7 + 用户有限通过裁定）。

---

## ⚠️ 接受项（非阻塞）

1. **测试 fixture 绕过全表 `import_registry_csv`** — 仅 INSERT 湖北行；M1-a 已修 CSV 闸，生产路径仍应跑全表 import。记债，不 FAIL。
2. **migration 014 search_path** — 回执 §8 披露；不在本刀 scope；另开 hygiene 刀，不阻塞 M1-c。
3. **IAV 行 value=NULL + missing_reason** — 符合 schema CHECK；GDP 验收不受影响。bonus 测试合理。

---

## 下一刀

**M1-c（T4+T5）** — dbt timeseries view + series API。**等用户 ACK 再签任务书**（用户 2026-08-31 明示）。

— End 628 —
