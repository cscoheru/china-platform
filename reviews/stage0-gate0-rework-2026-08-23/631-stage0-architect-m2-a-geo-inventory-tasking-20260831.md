# 631 — M2-a：31 省 geo 种子 + 2024 GDP 源清单（架构师任务书）

> **类型**: Architect 签发  
> **日期**: 2026-08-31  
> **依据**: `docs/54` §M2；`docs/56`；用户「M1 有限通过，开 M2」  
> **前置**: M1 T0–T7 全勾 · 630 PASS · 用户有限通过裁定  
> **禁止**: Gate/O1/M2 PASS；统计局**首页**当表源；补零；买商业库

---

## 0. 一句话

为 08b 铺轨：**31 个省级 `geo_entity` 幂等种子** + **2024 年 GDP 官方表源 inventory**（可解析表/年鉴/公报附件，禁止仅首页）+ **覆盖率空矩阵**可生成。

---

## 1. 交付（本刀 = M2-a only）

### A. Geo 种子

- 脚本：`scripts/seed_m2_province_geo.py`（幂等）
- 31 省级行政区（含直辖市）写入 `cegr.geo_entity` + 最小 `geo_code_version`（GB/T 2260 或现有约定）
- 稳定 UUID 命名空间建议：`a2000000-0000-0000-0000-…`（与 M1 `a1000000-…` 分离）
- 湖北 M1 UUID `a1000000-…001`：**兼容**（映射或 alias；禁止重复省实体）

### B. 源清单（inventory）

- 新建：`source_registry/m2_2024_gdp_inventory.csv`（或 `docs/inventories/`）
- 列建议：`province_zh, geo_code, candidate_url, asset_kind(TABLE|XLSX|PDF_TABLE|HTML_TABLE|UNKNOWN), local_sample_path, file_hash_sha256, status(PENDING|FETCHED|BLOCKED|MISSING), missing_reason, notes`
- **≥31 行**；`candidate_url` **不得**仅为省统计局根首页（须到可定位统计表/年鉴章节/公报数据页；若仅发现首页则 `status=BLOCKED` + reason）
- 国家行：NBS 2024 年 GDP 发布（表级）

### C. 覆盖率空表

- 脚本：`scripts/report_m2_gdp_coverage.py` → 打印/写出 `geo × 2024 × GDP`：有值 / missing_reason / 无登记
- 本刀允许 **全 0 有值**（空矩阵）；须可跑 exit 0

### D. 测试

新建 `tests/test_m2_province_geo_seed.py`：

1. 31 省 geo 存在（按 canonical_name 或 code）
2. 湖北不重复冲突
3. inventory 行数 ≥31 且无「仅根首页」的 FETCHED 行
4. coverage 脚本 exit 0

验收：`pytest tests/test_m2_province_geo_seed.py -q` exit 0。

---

## 2. 明确不做

- 不 ingest 31 省 observation（→ M2-b）
- 不改 `/provinces/jiangsu`；不扩四轨 HTML
- 不宣布 Gate 1/2 / M2 PASS
- 不买库；不 OCR 生产化

---

## 3. 回执

`631-stage0-cc-m2-a-geo-inventory-receipt-YYYYMMDD.md`：

- pytest 一行
- inventory 行数 + BLOCKED/PENDING 计数
- coverage 脚本输出摘要
- 红线自审（无首页 FETCHED）
- 双推

---

## 4. Cursor 审验点

- 31 geo + inventory ≥31
- 无「首页 URL + FETCHED」
- 湖北 M1 FK 未破坏（M1 pytest 子集仍绿）
- 未宣称 M2/Gate PASS

— End 631 —
