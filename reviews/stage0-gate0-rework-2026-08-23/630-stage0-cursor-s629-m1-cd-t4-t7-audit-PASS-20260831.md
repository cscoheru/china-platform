# 630 — Cursor 审验：629 M1-c+d（T4–T7）PASS

- 日期：2026-08-31
- 对象：CC 回执 `629-stage0-cc-m1-cd-t4-t7-receipt-20260831.md`
- 任务书：`629-stage0-architect-m1-cd-t4-t7-query-surface-tasking-20260831.md`
- 前置：628 M1-b PASS · `0ee445e`

---

## 判定：**PASS**（有限；≠ Gate / O1 / M1 PASS）

| PHOTO / 项 | 回执 | 独立复验 | 判定 |
|---|---|---|---|
| PHOTO-1 pytest | 29 passed | `…5 个 test_m1_*.py -q` → **29 passed in 2.64s** | ✅ |
| PHOTO-2 view | value=31336.72 · domain=tjj.hubei.gov.cn | SQL 1 行一致；period 2026-01-01..06-30 | ✅ |
| PHOTO-3 API | series≥1 · caveat · hash8=`c5cf5abe` | `test_m1_api_series.py` 3 passed（生命周期内 TestClient） | ✅ |
| PHOTO-4 SHA | `c5cf5abe…` | `shasum` 全长一致 | ✅ |
| PHOTO-5 smoke | exit 0 · §14 | smoke 末行含 M1 验收面 PASS；首页链 `/research/m1-series` | ✅ |
| PHOTO-6 红线 | 自审全 ✓ | 页头含「非 Gate PASS」；jiangsu 无 diff；无 MOCK UUID | ✅ |
| PHOTO-7 清单 | 17 路径 | 关键路径存在；docs/55 T4–T7 已勾、Gate 项未勾 | ✅ |
| T7 调度 | rev 51 · 等用户裁定 | EXEC-QUEUE / COMPASS（47 行）一致 | ✅ |

**不宣布：** Gate / O1 / M1 PASS。docs/55 仅勾「有限通过**候选**」。

---

## ⚠ 接受项（非阻塞）

1. **未入库 / 未双推** — HEAD 仍 `0ee445e`；629 改动在工作区（含回执）。回执 §3 已写「等用户授权 push」。**审验对象是工作树交付，不是 origin/main。** 授权 commit+双推后回填 `cc_head`。
2. **approach B** — `scripts/materialize_m1_views.sql` DROP+CREATE；`dbt/models/intermediate/int_indicator_timeseries.sql` **尚未**同步 `caveat_text` / `source_hash_prefix` 列。记 hygiene：下次 dbt 路径前对齐 model。
3. **§6 disclosure** — migration 014 不动；测试 `DISABLE TRIGGER`；connector 补 `extracted_at`+`confidence`：均合理，不 FAIL。
4. **裸 TestClient 无 lifespan** 会缺 `app.state.db`；以 pytest fixture 路径为准（已绿）。

---

## 下一刀

- **暂停签 M2** — 等用户对 **M1 有限通过候选** 的裁定。
- 用户若授权：commit 629 工作树 + 双推 + 回填 `cc_head`。
- 用户若 ACK M1 有限通过 → 再签 M2（08b 31 省 GDP）。

— End 630 —
