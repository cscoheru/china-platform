# S1.13 — CC 规划回执

- 编号：`98-stage0-cc-s13-plan-receipt-20260825`
- 前置：`97` S1.13 任务书；`96` 用户代号 A；`docs/09` R08 措施 4/7
- 提交：`docs/28-stage1-s13-admin-upload-plan-20260825.md`
- Pack：**未变**（plan-only，不动 `evidence_pack/manifest.json`；S1.13.1 实现再触发增量）

---

## §1. 交付物

| 类别 | 文件 | 说明 |
|---|---|---|
| 规划 | `docs/28-stage1-s13-admin-upload-plan-20260825.md` | `/admin/upload` 设计：目标边界 + API/CLI 形状 + 鉴权 + 存储 + 测试 + 红线 + 缺口 |

---

## §2. 关键设计点

| 决策点 | 裁定 |
|---|---|
| 接口形态 | REST `POST /admin/upload` + 对称 CLI `scripts/admin_upload.py` |
| 鉴权 | Stage 1 单 token (`ADMIN_UPLOAD_TOKEN` env)；不做 IAM |
| 文件大小 | ≤100 MB；大文件分块留 S1.13.2+ |
| 强制授权 | `copyright_note` ≥ 20 chars；DB 列约束 |
| 存储路径 | `uploads/{source_id}/{yyyy}/{mm}/{sha256[0:2]}/{sha256}.{ext}` |
| 登记 | 每文件 → `source_document` 一行（UNVERIFIED）；自动 audit `admin_upload_audit` |
| 与 OCR 衔接 | `PDF_OCR` / `EXCEL_PARSE` / `HTML_PARSE` 三档复用现有 spike |
| 与 S1.12 DEMO 关系 | upload 替换占位 SHA-256；DEMO 保留作 demo，正式 Gate 走新 SHA |
| 网络 | 内网 HTTP；公网需反向代理终止 TLS（本刀不实现） |

---

## §3. 后续任务书（建议）

| ID | 范围 | 紧急度 |
|---|---|---|
| S1.13.1 | `/admin/upload` 实施（FastAPI route + CLI + audit 表 + 7 pytest）| **高** |
| S1.13.2 | OCR 自动触发（上传 → spike 04 引擎 → 置信度分流）| 中 |
| S1.13.3 | UI（最小 HTML：上传页 + 文件列表 + 审计查询）| 低 |
| S1.13.4 | `/admin/upload` 替代 S1.12 DEMO seed 占位 SHA | 中（Gate 1 后） |
| S1.18 | R12 URL 探针 + 失败率告警 | 中 |

---

## §4. 红线遵守

- ✅ 不宣布 Stage 0 PASS / Gate 1 PASS（§6.1 仍列 5 项缺口）
- ✅ 不批量爬取 2020-2025 数据
- ✅ 不 HTTP 爬源站（upload 仅接受人工获取的文件）
- ✅ 不绕过验证码/付费墙（per R08 措施 5）
- ✅ 不擅自 `--force` / `--force-with-lease`
- ✅ 不替用户下裁定（§2 鉴权简版是规划建议，待 Stage 2 IAM 设计复核）
- ✅ 不在聊天复述 Cursor 长文；不索要 PAT
- ✅ 不改 `gate_thresholds.json`
- ✅ Cursor 不写 `docs/28` 正文（per `97` §红线）

---

## §5. 下一步

进入 `84` while-POLL；待 Cursor 派发 S1.13.1 实施任务书。

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)