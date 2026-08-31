# 632 — Cursor 审验：631 M2-a PASS

- 日期：2026-08-31
- 对象：CC 回执 `631-stage0-cc-m2-a-geo-inventory-receipt-20260831.md` + commit `ee8e285`
- 任务书：`631-stage0-architect-m2-a-geo-inventory-tasking-20260831.md`

---

## 判定：**PASS**（≠ M2 / Gate PASS）

| 项 | 回执 | 独立复验 | 判定 |
|---|---|---|---|
| pytest | 8 passed | `STAGE0_SKIP_SCHEMA_APPLY=1 pytest tests/test_m2_province_geo_seed.py -q` → **8 passed** | ✅ |
| M1 未破坏 | （隐含） | `test_m1_reference_seed.py` → **7 passed**；湖北 geo=`a1000000-…001` | ✅ |
| 31 省 geo | DONE | DB `level=PROVINCE` count=**31** | ✅ |
| inventory ≥31 | 声称 31 | CSV **32** 数据行（国家+31 省）；`≥31` 满足 | ✅ ⚠ 见下 |
| 无 FETCHED / 无根首页 | 0 FETCHED | Counter PENDING=31 BLOCKED=1 FETCHED=0；路径均非 `/` | ✅ |
| coverage 空矩阵 | 0/31 | 脚本 exit 0；KPI 0.0% | ✅ |
| INSERT 用 REGISTRY_ID | 已修 | seed INSERT 参数为 `GB_T_2260_REGISTRY_ID` | ✅ |
| 红线 | 自审 ✓ | 无 observation 写入；无补零；无 Gate/M2 宣告 | ✅ |

**不宣布：** Gate / O1 / M2 PASS。M2-a = 基线铺轨完成。

---

## ⚠ 接受项（非阻塞）

1. **回执/commit 文案行数漂移** — 写「31 行 / PENDING 30」，实测 **32 行 / PENDING 31 + BLOCKED 1**（国家+31 省）。测试闸为 `≥30 PENDING` / `≥31` 行，故仍绿。记笔误，不 FAIL。
2. **`unload()` 仍用 DOC_ID 删 source_registry** — `replace_all` 残留；load 路径已对。`unload` 会漏删 registry 行。**M2-b 前置一行修：`DOC_ID` → `REGISTRY_ID`**（并应删对应 `source_document`）。
3. **migration 014 / `STAGE0_SKIP_SCHEMA_APPLY=1`** — 披露成立；另开 hygiene，不挡 M2-b。
4. **candidate_url 多为公报目录而非 2024 定稿表** — M2-a 允许 PENDING；M2-b 必须落到可 SHA 锁的**表文件/定稿页**，禁止目录页当 FETCHED 完成。

---

## 用户披露的 deviation

| 项 | 审验 |
|---|---|
| CSV 多逗号列错位 → 已修 | ✅ 现行列对齐；status 在正确列 |
| REGISTRY_ID 被 replace_all 盖成 DOC_ID → INSERT 已修 | ✅；unload 未修完（上 ⚠#2） |
| schema apply 014 | ✅ 接受；测试环境变量路径绿 |

---

## 下一刀

签 **M2-b**：≥5 省（苏/粤/浙优先 + 国家 + 1）2024 GDP **表级**取数 → SHA 锁 → observation SUCCESS；修 unload；禁首页/目录页当完成。

— End 632 —
