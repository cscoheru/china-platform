# S1.14 — 修复任务书（migration 链 / 005 幂等）

- 编号：`109-stage1-s14-migration-chain-fix-tasking-20260825`
- 前置：`108` FAIL；对象 commit `7c6df3f`

## NOW

1. 修 `schema/migrations/005_admin_upload_audit.sql`：
   - **最低**：`CREATE TABLE IF NOT EXISTS` + index IF NOT EXISTS；或
   - **更优**：表迁入 `cegr.admin_upload_audit`，并改 API/CLI SQL 引用（与 DROP cegr 一致）
2. 验证：`conftest` 全链 apply 成功且含 006；`to_regclass('cegr.source_disagreement')` 非空
3. `pytest tests/test_source_disagreement_s141.py` **全过**（≥5，现有 9 条须绿）
4. 回归：`pytest tests/test_admin_upload_s131.py` 仍过
5. commit → origin → 回执 **`107-stage0-cc-s14-impl-receipt-*.md`**（写明 FAIL 根因与修复）
6. → **`84` POLL**

## 红线

不 Gate 1 PASS；不改 `gate_thresholds.json`；Cursor 不写修复代码。
