# M2-d 2024 GDP Crosscheck Report (knife 635 §1.D)

> Generated: inline  ·  top verdict: **QUARANTINED-WEAK**

## 1. Sources cross-checked

| source | scope | value (亿元) | caveat |
| --- | --- | --- | --- |
| A: 国家统计局 2024 公报 (NBS NATIONAL_BULLETIN) | COUNTRY | 1,349,084.0 | observation SUCCESS, missing_reason IS NULL |
| B: Sum of 5 province observations (level=PROVINCE) | PROVINCE×5 | 327,045.6 | weak sum (only 16.1% of provinces covered) |

## 2. Per-province breakdown

| province_zh | value (亿元) | share of national | caveat (前 60) |
| --- | --- | --- | --- |
| 上海市 | 53,926.71 | 4.00% | 2024 年上海市地区生产总值（GDP）；初步核算。 |
| 北京市 | 49,843.10 | 3.69% | 2024 年北京市地区生产总值；按不变价格计算；初步核算。 |
| 四川省 | 64,697.00 | 4.80% | 2024 年四川省地区生产总值（GDP）；按不变价格计算；初步核算。 |
| 山东省 | 98,565.80 | 7.31% | 2024 年山东省地区生产总值；按不变价格计算；初步核算。 |
| 湖北省 | 60,012.97 | 4.45% | 2024 年湖北省全省生产总值；按可比价格计算；初步核算。 **NOT** 复用 M1 hubei_2026_06.xl |

## 3. Verdicts

| check | verdict | metric | threshold | reason |
| --- | --- | --- | --- | --- |
| absolute relative diff (sum vs national) | QUARANTINED | 75.7580% | <0.5% | sum=327,045.6; national=1,349,084.0 |
| coverage-implied plausibility | PASS | sum_ratio=0.2424 | ≥ coverage_ratio×0.5 = 0.0806 | sum/national=0.2424 ≥ coverage_ratio×0.5=0.0806 (coverage=5/31) |

## 4. Top-level verdict: **QUARANTINED-WEAK**

> relative diff 75.76% > ±0.5%; method limitation: only 5/31 provinces covered, sum_ratio=0.2424 (expected <1.0); see docs/54 §08b for weak-crosscheck protocol.

## 5. Method limitations

- Knife 635 §1.D: '无国家分省表时：用「31 省库内加总 vs 国家 GDP」作 弱核对'. 本 crosscheck is therefore WEAK by design.
- 当前覆盖 5/31 省级 (16.1%); 覆盖率 < 100% 时 sum_ratio 期望 < 1.0 (差距 = 未覆盖省合计).
- 31 省全 COVERED 后, 此 crosscheck 自动升级为 STRONG (±0.5% 阈值).
- 本脚本不修改 observation.value; verdict 是 read-only 报告.

## 6. Provenance

- indicator_id: `M2_GDP_ANNUAL` = `a2000000-0000-0000-0000-00000000a001` (knife 633)
- calendar_period_id: `2024Y` = `a2000000-0000-0000-0000-000020240101`
- national geo_entity_id: `a2000000-0000-0000-0000-000000000000` (synthetic, not in GB/T 2260)
- threshold: docs/54 §08b = ±0.5% relative diff

