-- docs/10 §2.4 + docs/31 §2.1 阈值断言 (R03 自动化)
--
-- 返回行 = 失败: 存在未闭环的 >5% 跨源冲突 (S0↔S0 域内).
-- 阈常量 2%/5% 镜像于 mart_source_disagreement.sql 的 CASE (docs/29 §7:
-- 参数化属 Stage 2, 改动须过用户).
-- 分层语义 (docs/10 §2.4): S0 之间应一致; 与 S1/S2 的差异由 mart 落表记录
-- 但不阻塞 — 故断言仅在 S0↔S0 范围生效.

SELECT *
FROM {{ ref('mart_source_disagreement') }}
WHERE severity   = 'NEEDS_REVIEW'
  AND resolution = 'PENDING'
  AND source_a_level = 'S0'
  AND source_b_level = 'S0'