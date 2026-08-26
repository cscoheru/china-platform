-- Migration 013 — S2.6-lite: 反例守门触发器 (assert_min_one_contradicts)
--
-- Per docs/41 §2.5 (Stage 2 / S2.6 规划) + Cursor tasking 232 §SCHEMA.
-- 用户裁定 D (缩刀节奏) — 与 S2.1-lite (008) / S2.2-lite (009) / S2.3-lite (010) /
-- S2.4-lite (011) / S2.5-lite (012) 同构 (本刀仅函数 + 触发器).
--
-- 本刀性质: **流程刀落地 (最小)** — 仅触发器 + 函数; 无新业务表; 无 seed 数据;
-- 不写 dbt mart; 不接 admin UI (per docs/41 §2.0 + §5 + §8).
--
-- 触发器设计 (per docs/41 §2.5):
--   时机: AFTER INSERT OR UPDATE OR DELETE ON claim_evidence_link
--   守门: 任意 claim_id 在变更后必须保留至少 1 条 CONTRADICTS 行
--   实现: PL/pgSQL 函数 assert_min_one_contradicts()
--   红线: PostgreSQL 不支持 subquery CHECK 约束 (docs/41 §10.6 红线);
--         故使用触发器 + 应用层 wrapper + mart 视图 三层守门.
--
-- 列选择 — deviation from docs/41 §2.5 示例:
--   docs/41 §2.5 示例使用 canonical_polarity 投影列;
--   本实现使用 polarity CHECK-locked 列 (per 01-core.sql §965).
--   理由:
--     1) polarity 由 schema CHECK (SUPPORTS/CONTRADICTS) 强制非空 + 合法值;
--        canonical_polarity 仅为 nullable TEXT 投影 (per migration 012 §67-71)
--     2) 若使用 canonical_polarity: 在 migration 012 未应用前 / canonical_polarity
--        尚未投影时, 真正的 CONTRADICTS 行不会被计入, 守门被绕过.
--     3) polarity 与 canonical_polarity 在 §4.2 应用层 100% 投影守门下应保持一致.
--   CC 提交 Cursor 审计时若坚持 docs/41 §2.5 字面, 可一行替换.
--
-- 评分/排名/总分字段 (score/rating/rank/total_score/confidence_score/credibility_score)
-- 红线: 一律不引入.
--
-- Per docs/33 §3.2 sentinel: 守门不依赖 lineage.is_demo (适用于真表 + demo 数据).
-- Per docs/04 §3.9 polarity 双显锁定: 既有 polarity CHECK (SUPPORTS/CONTRADICTS) 不动.
-- Per docs/06 §6.6 红线: 守门是计数 + 枚举 (NO_CONTRADICTING_EVIDENCE 等); 不评分.
--
-- 依赖: schema/01-core.sql §956-966 (claim_evidence_link 表)
--       + schema/migrations/012_inference_alignment.sql (additive 列)
--       + 既有 polarity CHECK (01-core.sql §965).

SET search_path = cegr, public;

-- ---------------------------------------------------------------------------
-- 1. 守门函数: assert_min_one_contradicts()
-- ---------------------------------------------------------------------------
--
-- 对任意受影响 claim_id, 变更后必须仍有至少 1 行 polarity='CONTRADICTS'.
-- 若为 0 行, 抛 RAISE EXCEPTION 拒绝变更 (docs/41 §2.5 + Gate 2 §3.2 硬要求).
--
-- 触发器上下文差异:
--   INSERT/UPDATE: NEW.claim_id 有效; OLD.claim_id 可能为 NULL
--   DELETE:        OLD.claim_id 有效; NEW 为 NULL
--   故本函数同时处理 NEW 与 OLD, 取非 NULL 者.

CREATE OR REPLACE FUNCTION assert_min_one_contradicts()
RETURNS TRIGGER AS $$
DECLARE
    affected_claim_id UUID;
    n_contradicts INTEGER;
BEGIN
    -- 1) 取受影响的 claim_id (兼容 INSERT/UPDATE/DELETE)
    affected_claim_id := COALESCE(NEW.claim_id, OLD.claim_id);

    IF affected_claim_id IS NULL THEN
        -- 理论上 claim_id 在 claim_evidence_link 上 NOT NULL (01-core.sql §958)
        -- 此分支仅作防御性守门
        RETURN COALESCE(NEW, OLD);
    END IF;

    -- 2) 守门: 该 claim 至少有 1 行 CONTRADICTS (用 polarity CHECK 列;
    --    canonical_polarity 是 nullable 投影, 见本文件 header 注释)
    SELECT COUNT(*)
      INTO n_contradicts
      FROM claim_evidence_link
     WHERE claim_id = affected_claim_id
       AND polarity = 'CONTRADICTS';

    IF n_contradicts = 0 THEN
        -- 3) 拒绝变更 — Gate 2 §3.2 硬要求
        RAISE EXCEPTION
            'gate 2 §3.2 violation: claim % has zero CONTRADICTS rows after this change',
            affected_claim_id
            USING ERRCODE = 'check_violation';
    END IF;

    -- 4) 守门通过, 返回原行 (AFTER 触发器返回值被忽略, 但仍需返回 NEW/OLD)
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION assert_min_one_contradicts() IS
    'S2.6-lite 反例守门: 变更后该 claim_id 必须仍有 ≥1 CONTRADICTS 行 (per docs/41 §2.5 + Gate 2 §3.2). 使用 polarity CHECK 列 (canonical_polarity 是 nullable 投影, 见 migration 013 header).';

-- ---------------------------------------------------------------------------
-- 2. 触发器: claim_evidence_link_after_change
-- ---------------------------------------------------------------------------
--
-- AFTER INSERT OR UPDATE OR DELETE:
--   - INSERT: 新行加入后守门 (若此行是首条 SUPPORTS 而无 CONTRADICTS, 拒绝)
--   - UPDATE: 任意行变更后守门 (如最后一条 CONTRADICTS 被改为 SUPPORTS, 拒绝)
--   - DELETE: 行删除后守门 (如最后一条 CONTRADICTS 被删, 拒绝)
--
-- DROP TRIGGER IF EXISTS + CREATE TRIGGER 组合保证幂等.

DROP TRIGGER IF EXISTS claim_evidence_link_after_change ON claim_evidence_link;

CREATE TRIGGER claim_evidence_link_after_change
    AFTER INSERT OR UPDATE OR DELETE ON claim_evidence_link
    FOR EACH ROW
    EXECUTE FUNCTION assert_min_one_contradicts();

COMMENT ON TRIGGER claim_evidence_link_after_change ON claim_evidence_link IS
    'S2.6-lite 反例守门触发器: 守门 assert_min_one_contradicts() 在 INSERT/UPDATE/DELETE 后调用; per docs/41 §2.5 + Gate 2 §3.2.';

RESET search_path;

-- End of migration 013.