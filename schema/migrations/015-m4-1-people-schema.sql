-- ============================================================================
-- Migration 015 — M4.1: 人物表 schema 收口 (knife 638)
-- ============================================================================
-- Per knife 638 / docs/54 §M4.1 / docs/57 §6 (M4.1 = 人物表 schema 收口 +
-- 政府工作报告数据可得性 probe).
--
-- 性质: 纯加性 DDL (继承 008 additive-only 规则). 不 DROP / 不 RENAME /
--   不改既有 NOT NULL / 不加 FK 约束 / 不加 CHECK 约束 (CHECK 在 demo/real
--   分层后由后续刀 016+ 单独议).
--
-- Red lines (per docs/34 §7 + tasking 638 §红线):
--   * ❌ 不 DROP / 不 RENAME 既有列 — additive only
--   * ❌ 不加 FK 约束 — 与 008 一致;FK 落到 016+
--   * ❌ 不加 CHECK 约束 — 既有行 NULL 处理需先 backfill;CHECK 后置
--   * ❌ 不动 gate_thresholds.json (spike-04 评测构件, 只读)
--   * ❌ 不做官员能力分 / 总分 / 排名 — is_demo 是隔离标记, 非评分字段
--   * ❌ 不爬网抓履历 — 本刀 0 行业务数据;probe 单独跑
--   * ❌ 不写首批 ≤30 person 真实/演示履历 — 本刀 schema only
--   * ❌ 不改 source_registry / mart_*.sql / 4 frontend fixture bytes
--
-- Columns added (加性, 全部 nullable / 有 default):
--   person:
--     + is_demo            BOOLEAN NULL  -- M4.1: TRUE = demo/示例数据;FALSE = 真实数据
--     + last_verified_at   TIMESTAMPTZ NULL  -- 最近一次成功一跳回源验证戳
--   appointment_event:
--     + is_demo            BOOLEAN NULL  -- 与 person.is_demo 一致 (propagation 留 016+)
--
-- Indexes (light, no CONCURRENTLY per 008):
--   + idx_person_is_demo             ON person(is_demo)
--   + idx_person_last_verified        ON person(last_verified_at)
--   + idx_appointment_event_is_demo  ON appointment_event(is_demo)
--
-- Verification (this knife must satisfy):
--   * 现有 stage0 schema_negative tests 必须仍 pass
--   * tests/test_m4_1_people_probe.py ≥ 8 用例 必须全 green
--   * 638 不写 observation / 不爬网 / 不静默硬编码 value
-- ============================================================================

SET search_path = cegr, public;

-- ----- person -----
ALTER TABLE person
    ADD COLUMN IF NOT EXISTS is_demo          BOOLEAN,
    ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ;

COMMENT ON COLUMN person.is_demo IS
    'M4.1 (docs/54 §M4.1 / docs/57 §6): TRUE = demo/示例数据 (无真实 source 一跳);
     FALSE = 真实数据 (有 source_document_id + appointment_event.source_id NOT NULL);
     默认 NULL = 既有数据, 待 016+ 迁移脚本 backfill 为 FALSE.
     is_demo 是隔离标记, 非评分 / 非排名 / 非能力字段 (per docs/34 §7 红线).';

COMMENT ON COLUMN person.last_verified_at IS
    'M4.1: 最近一次成功一跳回源验证的时间戳;NULL = 从未验证;
     trigger / job 由 016+ 单独实装 (本刀仅 DDL).';

-- ----- appointment_event -----
ALTER TABLE appointment_event
    ADD COLUMN IF NOT EXISTS is_demo BOOLEAN;

COMMENT ON COLUMN appointment_event.is_demo IS
    'M4.1: TRUE = demo 数据;FALSE = 真实数据;默认 NULL = 既有数据, 待 016+ 补标.
     与 person.is_demo 保持一致 (异构表同语义, 防止 demo 隔离破坏).';

-- ----- indexes (light, no CONCURRENTLY per 008) -----
CREATE INDEX IF NOT EXISTS idx_person_is_demo             ON person(is_demo);
CREATE INDEX IF NOT EXISTS idx_person_last_verified        ON person(last_verified_at);
CREATE INDEX IF NOT EXISTS idx_appointment_event_is_demo  ON appointment_event(is_demo);

RESET search_path;