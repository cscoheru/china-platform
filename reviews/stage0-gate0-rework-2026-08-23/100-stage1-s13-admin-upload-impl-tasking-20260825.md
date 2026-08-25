# S1.13.1 — `/admin/upload` 实现任务书

- 编号：`100-stage1-s13-admin-upload-impl-tasking-20260825`
- 前置：`99` 规划通过；`docs/28`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 接口 | **`POST /admin/upload`** + **`scripts/admin_upload.py`** |
| 鉴权 | **`ADMIN_UPLOAD_TOKEN`**（Bearer / header）；缺 token → 401 |
| 存储 | 本地 `uploads/...` 路径（`docs/28` §3）；算 SHA-256；写 `source_document` |
| audit | 最小 `admin_upload_audit`（migration 或等价表） |
| OCR 自动触发 | **本刀可选/可 stub**；完整入队留 S1.13.2 |
| 替换 DEMO SHA | **本刀不做**（S1.13.4） |

## NOW

1. FastAPI `/admin/upload` + token 鉴权 + 文件落盘 + `source_document` 登记
2. CLI `scripts/admin_upload.py`（对称能力）
3. migration / DDL for audit（若需）
4. **≥7** pytest（鉴权失败、成功上传、重复 SHA、缺 copyright_note、过大文件等 — 对齐 `docs/28` §4）
5. commit → **origin 优先** → 回执 **`101-stage0-cc-s13-impl-receipt-*.md`**
6. → **立即再进 `84` while-POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不绕过验证码/付费墙；不改 `gate_thresholds.json`。
