# S1.13 — `/admin/upload` 人工上传入口规划任务书

- 编号：`97-stage1-s13-admin-upload-planning-tasking-20260825`
- 前置：用户裁定 **A**（`96`）；`docs/09` R08 措施 4；`docs/27` §4.3
- 范围：**规划 only**（不写上传实现代码）

## NOW（CC 交付）

1. 起草 **`docs/28-stage1-s13-admin-upload-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - 目标：扫描 PDF / 受限源 **强制**走人工上传 + 授权声明（R08）
   - API/CLI 形状（建议最小：`POST /admin/upload` 或等价 CLI；内网、无公网暴露假设）
   - 鉴权边界（Stage 1：共享 secret / 本地-only；不做完整 IAM）
   - 存储：raw → 对象路径/哈希 → `source_document` 登记；与现有 connector/OCR 衔接
   - 与 S1.12 DEMO seed 关系（upload 可替换占位 SHA）
   - 测试策略 + 红线（不爬网、不绕过验证码/付费墙、不 Gate 1 PASS）
3. 规划 only — 实现另开任务书

## 红线

不 Gate 1 PASS；不 DSH；不批量爬取；不绕过验证码/付费墙；Cursor 不写 `docs/28` 正文。
