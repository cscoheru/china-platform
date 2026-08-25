# Stage 1 / S1.13 — `/admin/upload` 人工上传入口规划

> **规划 only。** 不写上传实现代码；不宣布 Gate 1 PASS。Cursor 拥有 `00-CC-CURRENT.md`，本文档由 CC 起草。

- 编号：`docs/28-stage1-s13-admin-upload-plan-20260825`
- 前置：`96` 用户代号 A（继续 Stage 1 缺口）；`97` 任务书；`docs/09` R08 措施 4/7；`docs/27` §4.3
- 范围：**Stage 1 缺口 S1.13 — `/admin/upload` 人工上传入口设计 + 范围 + 风险**
- 不在本刀：实际代码实现；OCR 引擎切换；URL 探针产品化；IAM 完整化

---

## §0. 目标与边界

### §0.1 目标

按 `docs/09` R08 措施 4/7 提供**强制**人工上传入口（`/admin/upload` 或等价 CLI），覆盖：

1. **受限源**：年鉴版权、验证码、付费墙、CDN/JS 渲染反爬
2. **扫描 PDF**：spike 04 验证 BLOCKED 状态；OCR 管线代码就绪但**缺公开样本**；强制走上传入口可解 BLOCKED
3. **手工研究数据**：研究员/数据工程师本地整理的对照数据（如 S1.12 江苏 GDP DEMO seed 可被替换为真实 SHA-256-locked XLSX）

### §0.2 边界声明

| 项 | 在范围 | 不在范围 |
|---|---|---|
| 接口形态 | `POST /admin/upload` (REST) + `scripts/admin_upload.py` (CLI) | 公网暴露；公开 IAM；多租户 |
| 文件类型 | PDF / XLSX / XLS / CSV / HTML | 任意二进制；流式；分块上传 |
| 大小 | ≤100 MB | TB 级；流式 |
| OCR 触发 | 上传后自动触发（spike 04 引擎已就绪） | 引擎切换；新 OCR 模型 |
| 鉴权 | Stage 1 共享 secret（`ADMIN_UPLOAD_TOKEN`） | OAuth/SAML/SSO |
| 网络 | 内网/本地部署；HTTP only | HTTPS/TLS 终止；WAF |
| IAM | 单角色（admin） | 多角色；审计日志（Stage 2） |
| 存储 | 本地 `uploads/` + MinIO/S3（同 puer-hub 既有） | 新对象存储；CDN |

---

## §1. API / CLI 形状

### §1.1 REST — `POST /admin/upload`

**最小契约**（Stage 1 实施范围）：

```
POST /admin/upload
Authorization: Bearer ${ADMIN_UPLOAD_TOKEN}
Content-Type: multipart/form-data

Fields:
  - file:           binary (≤100MB)
  - source_id:      UUID (必填；上传到哪个 source_registry)
  - declared_url:   TEXT (必填；声明来源 URL；可为空字符串=纯本地)
  - copyright_note: TEXT (必填；授权声明；最小长度 20)
  - uploader_id:    TEXT (必填；上传者标识)
  - period_label:   TEXT (可选；如 "2024" / "2026-H1")
  - purpose_note:   TEXT (可选)
  - force_replace:  BOOL (默认 false；true 时覆盖同 source_id 的旧 source_document)

Response 200:
  {
    "source_document_id": "uuid",
    "file_hash_sha256": "64hex",
    "file_size_bytes": int,
    "stored_path": "uploads/{source_id}/{yyyy}/{mm}/{hash[0:2]}/{hash}.pdf",
    "extraction_trigger": "OCR_QUEUED" | "MANUAL_PIPELINE_NEEDED",
    "verification_status": "UNVERIFIED",
    "next_steps": ["review observation_quality_flag", "rerun GE checkpoint"]
  }

Response 4xx:
  - 400 INVALID_FILE_TYPE
  - 400 MISSING_AUTH_DECLARATION (copyright_note < 20 chars)
  - 401 INVALID_TOKEN
  - 413 FILE_TOO_LARGE
  - 422 SOURCE_NOT_FOUND (source_id 不在 source_registry)
  - 409 SHA_COLLISION (file_hash_sha256 已在其他 source_document)
```

### §1.2 CLI — `scripts/admin_upload.py`

**对称设计**（Stage 1 同等可用；便于无 Web 环境的离线/批处理）：

```bash
python3 scripts/admin_upload.py \
  --source-id a0000000-0000-0000-0000-000000000004 \
  --file /path/to/shaanxi_fiscal_2026.pdf \
  --declared-url 'https://wb.flk.npc.gov.cn/...' \
  --copyright-note '陕西省财政预算管理条例 2010 全文; public domain by 《著作权法》第五条排除' \
  --uploader-id ops@cegr.local \
  --purpose-note 'replacing DEMO SHA-256 placeholder'
```

**输出**：
```
[upload] source_document_id=<uuid>
[upload] file_hash_sha256=<64hex>
[upload] stored_path=uploads/...
[upload] verification_status=UNVERIFIED
[upload] extraction_trigger=OCR_QUEUED
```

### §1.3 强制授权声明 (R08 措施 7)

`copyright_note` 必须 ≥ 20 字符；服务端校验 + DB 列约束（参考 `source_document.copyright_note` 已有列）；最小声明模板：

```
[来源类型: 公开/授权/内部] [法律依据] [使用范围: 研究/审核/公开]
例: 公开 / 《中华人民共和国著作权法》第五条（法律法规排除） / 研究 + 审核
```

---

## §2. 鉴权边界

### §2.1 Stage 1 简版

| 维度 | 裁定 |
|---|---|
| 鉴权方式 | 单 token (`ADMIN_UPLOAD_TOKEN`)，env 注入 |
| 来源 | 平台管理员人工生成；轮转由 ops 手工 |
| 范围 | 仅 `/admin/upload` 路由 |
| 传输 | 内网 HTTP（公网部署时前置 TLS，由反向代理终止；本刀不实现 TLS） |
| 审计 | 写入 `admin_upload_audit` 表：`timestamp / uploader_id / source_id / file_hash / client_ip` |

### §2.2 显式排除

- ❌ 不做 OAuth 2.0 / SAML / SSO（Stage 2）
- ❌ 不做完整 IAM（角色 / 权限组 / 用户管理）
- ❌ 不做审计日志查询 UI（DB 直查）
- ❌ 不做速率限制（Stage 1 假设管理员 + 内网，滥用风险低）
- ❌ 不暴露到公网（部署假设内网或本地）

### §2.3 风险

- 单 token 泄漏 = 全权上传；**轮转频率建议 ≤ 30 天**（待 Stage 2 引入 IAM 后改为自动轮转）
- 无速率限制 = 单点滥用；建议配合 ops 流程（人工审批）

---

## §3. 存储与登记

### §3.1 对象存储路径

```
uploads/{source_id}/{yyyy}/{mm}/{sha256[0:2]}/{sha256}.{ext}
例: uploads/a0000000-0000-0000-0000-000000000004/2026/08/a0/a0...64hex.pdf
```

**理由**：
- 按 source_id 分桶：检索"某源所有版本"
- 按年月分桶：避免单目录过深；运维可清理过期
- SHA-256 前缀分散：避免单目录 hash 子树过深
- 文件名 = 完整 SHA-256：内容寻址；天然去重

### §3.2 source_document 登记

每个上传文件 → 一行 `source_document`：

| 列 | 值 |
|---|---|
| `id` | 新 UUID（v4） |
| `source_registry_id` | 上传参数 `source_id` |
| `source_level` | 同 source_registry 的 `declared_source_level`（直到 VERIFIED 才升级） |
| `verification_status` | `UNVERIFIED`（上传默认） |
| `title` | 自动生成 `{source_registry.organization} - {filename} ({uploaded_at})` |
| `publisher` | `source_registry.organization` |
| `url` | `declared_url`（可为空） |
| `file_path` | 上面的对象存储路径 |
| `file_hash_sha256` | SHA-256（小写 64 hex；DB 约束） |
| `file_size_bytes` | 文件大小（DB 约束 > 0） |
| `file_format` | 扩展名 |
| `extraction_method` | `PDF_OCR` / `EXCEL_PARSE` / `HTML_PARSE`（按 file_format） |
| `copyright_note` | 上传参数 `copyright_note` |
| `caveat_text` | 自动：`UPLOADED_VIA_ADMIN; verification_status=UNVERIFIED` |
| `uploader_id` | 上传参数 `uploader_id` |
| `created_at` | NOW() |

### §3.3 与现有 connector/OCR 衔接

- **spike 04 OCR 引擎**：`extraction_method=PDF_OCR` 触发 → 复用 `spikes/04-scanned-pdf/extract_04*.py` 已就绪代码
- **spike 02 XLSX 解析**：`extraction_method=EXCEL_PARSE` → 复用 `extract_02_provincial_yearbook.py`
- **spike 01 HTML**：`extraction_method=HTML_PARSE` → 复用 `extract_01_national_yearbook.py`
- **OCR 置信度分流**：R04 措施 4；<0.7 入 `observation_quality_flag` 不入正式表（spike 04 已实现）

### §3.4 与 S1.12 DEMO seed 关系

S1.12 江苏 GDP DEMO seed 的 `source_document.file_hash_sha256=0000…0000` 占位；上传 `/admin/upload` 真实 XLSX 后：

1. 旧 `source_document`（SHA-256 全 0）的 `verification_status` → `REJECTED`
2. 新上传 → 新 `source_document`（真实 SHA-256）→ `verification_status=UNVERIFIED`
3. S1.12 5 行 observation 的 `source_id` 更新 → 新 source_document.id
4. DEMO seed 仍可保留（用于 demo 模式），但正式 Gate 走新 SHA

---

## §4. 测试策略

### §4.1 单元测试（pytest；Stage 1 S1.13.1 任务书）

| 测试 | 范围 |
|---|---|
| `test_admin_upload_auth` | token 缺失/无效 → 401 |
| `test_admin_upload_copyright_too_short` | copyright_note < 20 → 400 |
| `test_admin_upload_file_type` | 非白名单扩展 → 400 |
| `test_admin_upload_source_not_found` | source_id 不存在 → 422 |
| `test_admin_upload_sha_collision` | 同 SHA 已存在 → 409 |
| `test_admin_upload_happy_path` | 合法 PDF/XLSX → 200 + 登记 |
| `test_admin_upload_audit_log` | 审计行写入 `admin_upload_audit` |

### §4.2 集成测试（dev DB）

- 上传 spike 04 真实 PDF（如已有 SHA-256 锁定样本）
- 验证 `source_document.file_hash_sha256` 与本地 SHA-256 一致
- 验证 OCR 触发（如配置 `auto_ocr_after_upload=true`）
- 验证 GE 契约（`d2_source_document_suite`）仍 PASS

### §4.3 E2E（手动；Gate 1 评审时）

- 浏览器（dev）→ `http://localhost:8000/docs` → 找到 `/admin/upload` → 上传测试文件
- CLI（无浏览器）→ `python3 scripts/admin_upload.py --file ...` 验证
- 网络中断恢复测试（`admin_upload_audit` 记录请求时刻）

---

## §5. 红线遵守（per `97` §红线）

- ❌ **不宣布 Stage 0 PASS / Gate 1 PASS**（本刀规划 only；不声称 Gate 1 通过）
- ❌ 不批量爬取 2020-2025 数据（upload 是单文件管理路径，不代替采集）
- ❌ 不 HTTP 爬源站（爬取另由 connector 负责；upload 仅接受**人工获取**的文件）
- ❌ 不绕过验证码/付费墙（违反 R08 措施 5）
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不替用户下裁定（§2 鉴权简版是规划建议，待 Stage 2 IAM 设计时复核）
- ❌ 不在聊天复述 Cursor 长文；不索要 PAT
- ❌ 不改 `gate_thresholds.json`
- ❌ 不把 1909 美国统计摘要代表中国 / 不把陕西标为 Gate 1 验证项
- ❌ Cursor 不写本文档正文（per `97` §红线 + `84` §0 唯一信道）

---

## §6. 已知缺口与风险

### §6.1 缺口（**诚实清单**）

1. **IAM 完整化缺失**：Stage 1 单 token 模型不够；多管理员轮转/吊销/审计 UI 缺
2. **TLS / WAF 缺**：公网部署时需前置；本刀假设内网
3. **审计日志查询 UI 缺**：DB 直查能力足够，但 ops 友好度低
4. **大文件上传限制 100 MB**：超大型年鉴（如全本 500MB+）需分块；本刀不实现
5. **OCR 引擎自检**：上传后 OCR 触发需手动验证置信度分流

### §6.2 风险（与 R08 关联）

| 风险 | 描述 | 缓解 |
|---|---|---|
| 单 token 泄漏 | 全权上传 | 30 天轮转 + 审计日志 + 内网假设 |
| 滥用上传 | 无速率限制 | 人工审批 + ops 流程 |
| 误上传错误文件 | 无内容校验（仅校验扩展名+SHA） | 后续 OCR/parser 自检 + 人工 review |
| OCR 置信度 <0.7 静默入表 | 触发器未接 ingest | R04 措施 4：写 `observation_quality_flag` 表不入正式；待 S1.18 |

---

## §7. 后续任务书建议

| ID | 范围 | 紧急度 |
|---|---|---|
| S1.13.1 | `/admin/upload` 实施：FastAPI route + CLI + audit 表 + 7 个 pytest | **高** |
| S1.13.2 | OCR 自动触发：上传 → 入队 → spike 04 引擎 → 置信度分流 | 中 |
| S1.13.3 | UI（最小 HTML）：上传页面 + 文件列表 + 审计查询 | 低 |
| S1.13.4 | `/admin/upload` 替代 S1.12 DEMO seed 占位 SHA | 中（Gate 1 后） |
| S1.18 | R12 URL 探针 + 失败率告警 | 中 |

---

## §8. 交付物

| 文件 | 类型 | 说明 |
|---|---|---|
| `docs/28-stage1-s13-admin-upload-plan-20260825.md` | 规划 | 本文件 |
| `reviews/stage0-gate0-rework-2026-08-23/98-stage0-cc-s13-plan-receipt-20260825.md` | 回执 | `98` 给 Cursor 审验 |

**Pack contract**：本刀为规划 only；不动 `evidence_pack/manifest.json`（role_count 不变）。等 S1.13.1 实施时再触发 pack 增量。

---

— CC @ queue_rev 32 —