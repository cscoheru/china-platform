# Stage 2 S2.0.2 — 真实 SHA 样本 / 探针真实化 启动规划

- 编号：`docs/35-stage2-s202-real-sha-probe-plan-20260825.md`
- 拥有者：CC
- 前置：`153`（S2.0.1 PASS）、`154`（S2.0.2 任务书）、`docs/34` §4.1 序 2
- 范围：**规划 only**；实现另开
- 状态：草案；不宣布 Gate 1 / Gate 2 PASS

---

## 1. S2.0.2 目标

把 S2.0.1 骨架里**所有**「DEMO sentinel」替换为真实数据，让前端演示从「mock 渲染」升级到「真实证据链」。两条独立的可验收刀：

1. **真实 SHA-locked 江苏样本** — 让 `frontend/app/provinces/jiangsu/page.tsx` 在切换 `NEXT_PUBLIC_USE_MOCK=false` 后，调用 `/api/indicator/.../series` 拿到 5 行真实数据；每行 `lineage.is_demo` 不再是 `"true"`，`<DemoBadge />` 自动隐藏（已设计）。
2. **URL probe 真实化（可选）**）** — `scripts/url_health_probe.py`（per docs/32 §2.1）从 fixture/mock 模式切换到本地 `URL_HEALTH_LIVE=1` 时跑真实 HEAD。

**关键约束**：`S2.0.2` 不爬业务数据；真实 SHA 样本来自**用户上传**（S1.13 admin upload）或**本地归档**，不来自 HTTP 抓取。

---

## 2. Gate 2 收口所需（per docs/08 §3.2）

| 验收项 | S2.0.2 贡献 |
|---|---|
| 5 个省/10 个地市观察页面上线 | ❌ 不在本刀（5 省扩展属 S2.7-b~e） |
| 六段证据链完整可点击 | ❌ 不在本刀（属 S2.7-b） |
| 七维度观察卡可展开 | ❌ 不在本刀（属 S2.8） |
| **没有「官员能力总分」** | ✅ 继承（红线） |
| 每条 governance 观察标注 INFERENCE/JUDGMENT | ❌ 不在本刀 |
| **至少 1 个反例被显式登记并展示** | ❌ 不在本刀（属 S2.6） |
| doc 10 测试 3.1-3.5 全过 | 🟡 部分（见 §6） |

**S2.0.2 不直接推进 Gate 2 验收项**；它是 Stage 1 OPEN（`142` §书面接受）收口刀，为后续 S2.1+ 提供真实数据底座。

---

## 3. 继承的 Stage 1 OPEN 清单

per `142` §书面接受；S2.0.2 直接收口其中两项：

| OPEN 项 | 状态 | S2.0.2 处置 |
|---|---|---|
| 真实 SHA-locked 江苏样本 | OPEN | **本刀主目标**（§4） |
| URL probe 真实化 | OPEN | **本刀次目标**（§5） |
| cron / 通知 | OPEN | **不收口**（Stage 2 运维刀；移交 S2.10 Gate 评审准备） |
| OCR 生产路径 | OPEN | 不在 S2.0.2 scope（属 S2.2/S2.4 政策文件入库配套） |
| `is_demo` 机制 | ✅ S1.18 | **保留为复用**；S2.0.2 演示其自动隐藏契约 |

---

## 4. 真实 SHA 样本路径（**不爬网**）

### 4.1 三条来源路径（钉死上限）

| 路径 | 输入 | 何时用 | 红线 |
|---|---|---|---|
| **(a) 用户上传**（S1.13 admin upload） | 真实 PDF/CSV/Excel 经 `/admin/upload` 落入 `/tmp/cegr_uploads/`（per `backend/src/china_platform/api/config.py`）；admin token 鉴权 | **默认 / 推荐** | 走 S1.13 既定契约；不绕 admin |
| **(b) 本地归档** | `data/seed_archives/jiangsu_gdp_2020_2024.{pdf,csv,xlsx}` 经 `scripts/compute_file_sha.py` 算 SHA-256 | 开发机 / 测试 fixture | 仅本机文件；不入 git |
| **(c) HTTP 抓取** | **🚫 禁止**（per docs/08 §3.3 + PRD） | — | — |

**本刀唯一新增 CLI**：`scripts/compute_file_sha.py` — 接受 (a) 或 (b) 路径文件，输出 64-char hex；与 `seed_jiangsu_gdp_demo.py` 的 `source_file_sha256` 字段对得上即视为真实。

### 4.2 `compute_file_sha` 最小设计

```python
# scripts/compute_file_sha.py
"""S2.0.2 — Compute SHA-256 of a local file for source_document.file_hash_sha256.

Per docs/35 §4.1: only reads files from (a) admin upload dir or (b) local archives.
Refuses to follow HTTP URLs (per PRD red line; no source crawl).
"""
import argparse, hashlib, sys
from pathlib import Path

ALLOWED_PREFIXES = ("/tmp/cegr_uploads/", "data/seed_archives/")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("path", help="local file path")
    args = p.parse_args()
    path = Path(args.path).resolve()
    if not any(str(path).startswith(pref) for pref in ALLOWED_PREFIXES):
        print(f"❌ {path} not under any allowed prefix", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"❌ {path} not a regular file", file=sys.stderr)
        return 1
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    print(h.hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**验收**：
- ✅ 给定合法文件 → 打印 64-char hex；exit 0
- ❌ 文件不存在 → exit 1
- ❌ 路径不在 ALLOWED_PREFIXES → exit 2
- ❌ 不接受 `--url URL` 参数（即便提供也忽略；防误用）

### 4.3 `replace_demo_with_real`（或等价）最小设计

**不**新增写 API；走 S1.13 admin upload 流程，让 `seed_jiangsu_gdp_demo.py` 的 loader 自然覆盖：

```bash
# 1. 用户把真实 PDF 放入 /tmp/cegr_uploads/jiangsu_gdp_2024.pdf
# 2. 算 SHA
python3 scripts/compute_file_sha.py /tmp/cegr_uploads/jiangsu_gdp_2024.pdf
# → 7a3f...e2c9

# 3. 走 admin upload（token 来自 CEGR_API_ADMIN_UPLOAD_TOKEN）
curl -X POST http://localhost:8000/admin/upload \
  -H "Authorization: Bearer $CEGR_API_ADMIN_UPLOAD_TOKEN" \
  -F "file=@/tmp/cegr_uploads/jiangsu_gdp_2024.pdf" \
  -F "chain_id=jiangsu_gdp_2020_2024" \
  -F "source_file_sha256=7a3f...e2c9"

# 4. 重跑 seed_jiangsu_gdp_demo.py --load；新行带真实 SHA + lineage.is_demo="false"
python3 scripts/seed_jiangsu_gdp_demo.py --load
```

**关键约定**：`lineage.is_demo="false"`（或缺失）即视为真实；`"true"` 即视为 DEMO sentinel。这是 `S1.18` 设计的**单一真相源**。

### 4.4 真实 SHA 时的 frontend 行为

- `frontend/lib/api.ts` 不变：`USE_MOCK=false` → fetch 真实 API
- `frontend/lib/mock.ts` 不变：仅 mock 模式用
- `frontend/app/provinces/jiangsu/page.tsx` 不变：每行调 `<DemoBadge lineage={pt.lineage} />`
- `<DemoBadge />` 内部判断 `lineage?.is_demo === "true"` → 不渲染（即「自动隐藏」）

**契约**：S1.18 已立；S2.0.2 不写新前端代码，只验证契约成立。

### 4.5 验收清单

| # | 验收 | 工具 |
|---|---|---|
| 1 | `compute_file_sha.py` 给定合法文件 → 64-char hex；exit 0 | pytest `test_compute_file_sha.py` |
| 2 | `compute_file_sha.py` 文件不存在 → exit 1 | 同上 |
| 3 | `compute_file_sha.py` 路径不在 ALLOWED_PREFIXES → exit 2 | 同上 |
| 4 | `compute_file_sha.py --help` 不显示 `--url` 选项（防误用） | 同上 |
| 5 | admin upload POST 200 + 新 `ingestion_run` 触发 seed 重写 | 手动 + `tests/test_admin_upload_s131.py` 复用 |
| 6 | seed 重写后 `cegr.observation.lineage->>'is_demo' = 'false'` | SQL count 查询 + `test_demo_sha_sentinel.py::test_demo_excluded_from_mart_cross_source` 仍绿 |
| 7 | frontend `NEXT_PUBLIC_USE_MOCK=false` 时 demo badge 隐藏 | 手工或 Playwright（**非本刀强制**） |

---

## 5. URL probe「真实化」范围

### 5.1 三种模式（钉死上限）

| 模式 | 触发 | 行为 | 红线 |
|---|---|---|---|
| **mock / fixture** | `URL_HEALTH_LIVE=0`（默认） | `unittest.mock` 替换 `requests.head` / `requests.get`；仅 fixture 断言（per docs/32 §3.4） | ✅ |
| **本地真实 HEAD** | `URL_HEALTH_LIVE=1` + dev 机 | 跑真实 HEAD；遵守 docs/32 §2.1 全部上限（HEAD 默认；GET Range ≤1KB；每源 ≤1req/s；并发 ≤4；总耗时 ≤60s） | ✅ |
| **生产 cron 真实化** | **🚫 禁止**（属 Stage 2 运维刀移交） | — | ❌ |

### 5.2 docs/32 §2.1 上限逐条核对（不变）

- ✅ HEAD 默认；GET + `Range: bytes=0-1023` 仅 PDF_PARSE 或 HEAD 拒绝
- ✅ 仅 `enabled=TRUE` 行；URL ≤2048
- ✅ 每源 ≤1 req/s；并发 worker ≤4
- ✅ connect 5s / read 10s / total 15s；重试 1 次指数退避 500ms
- ✅ 全表 60s 上限
- ✅ UA: `cegr-url-health/1.0 (+probe)`
- ✅ 验证码 / 付费墙 / 登录 → 放弃 + PARTIAL（**不绕过**）
- ✅ **不解析 robots.txt**（per docs/32 §2.1）
- ✅ 仅写 `ingestion_run`（triggered_by='url_health_probe'）；不写业务表

### 5.3 真实化范围（仅 §5.1 模式 2）

| 启用场景 | 命令 |
|---|---|
| 开发机本地验 | `URL_HEALTH_LIVE=1 python3 scripts/url_health_probe.py` |
| CI | **不跑**（per docs/32 §3.4 红线 6） |
| 生产 cron | **不接**（per docs/32 §5 移交清单；属 Stage 2 运维刀） |

### 5.4 验收清单

| # | 验收 | 工具 |
|---|---|---|
| 1 | `URL_HEALTH_LIVE=0`（默认）所有 pytest 全过；与 S1.17 既有行为一致 | `tests/test_url_health_probe.py`（既有） |
| 2 | `URL_HEALTH_LIVE=1` 在 dev 机能跑真实 HEAD；至少探 1 个源 URL；写 1 条 `ingestion_run` | 手动 + 截图 + `cegr.ingestion_run` count |
| 3 | URL_HEALTH_LIVE=1 仍遵守 docs/32 §2.1 上限（任何超时/限速违规 → pytest 报警） | 新增 `tests/test_url_health_probe_live.py`（**默认 skip**；`URL_HEALTH_LIVE=1` 启用） |

---

## 6. 与 S2.0.1 / S1.18 边界

| 边界 | S2.0.2 行为 |
|---|---|
| S2.0.1 骨架（frontend/） | **不动**；DemoBadge 自动隐藏契约由 lineage.is_demo 驱动，S2.0.2 不写新前端代码 |
| S1.18 `is_demo` sentinel | **复用**；`compute_file_sha.py` 输出 SHA 喂回 loader 即覆盖 sentinel |
| S1.13 admin upload | **复用为唯一上传路径**；不绕 admin |
| S1.10 FastAPI | **复用读 API**；不写新写 API |
| S1.17 URL probe | **复用为库**；S2.0.2 仅切换 mode（mock ↔ live） |
| `evidence_pack` | +1 documentation（docs/35）+1 schema_negative_test（test_compute_file_sha.py）= 506 → 508 |
| `00-CC-CURRENT.md` | 不碰（Cursor 拥有） |

---

## 7. 关键风险与回滚点

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| 真实 SHA 文件格式不兼容 seed loader | admin upload 后 loader 解析失败 | `--unload` 走 TRUNCATE CASCADE（per S1.18 修复）；重跑 `--load` |
| URL probe 真实化触发源站 WAF / 屏蔽 IP | dev 机 HEAD 频率超限 | docs/32 §2.1 已钉死每源 ≤1 req/s；保留 manual fallback to `URL_HEALTH_LIVE=0` |
| 用户上传真实文件但 SHA 不匹配 admin 元数据 | upload 时 SHA 校验失败 | admin upload 接口已记录 `error_log`；不退到 DEMO |
| `is_demo` 自动隐藏契约前端漏改 | 未来 S2.x 前端重构忘记 DemoBadge 判断 | pytest `test_demo_sha_sentinel.py::test_demo_excluded_from_mart_cross_source` 守门 |

---

## 8. 不做什么（per docs/08 §3.3 + PRD + 142 §书面接受 + docs/32 §6）

1. ❌ 不爬源站 / 不 HTTP 抓业务数据（**仅 HEAD / GET-bytes-0-1023**）
2. ❌ 不绕验证码 / 付费墙 / 登录（触发即 PARTIAL）
3. ❌ 不接生产 cron（属 Stage 2 运维刀）
4. ❌ 不批量 2020-2025
5. ❌ 不宣布 Gate 1 PASS
6. ❌ 不宣布 Gate 2 PASS
7. ❌ 不改 `gate_thresholds.json`（spike-04 评测构件，只读）
8. ❌ 不把 1909 代表中国 / 不把陕西标为门控
9. ❌ 不擅自 --force / --force-with-lease
10. ❌ 不替用户下裁定（cron 频率 / 通知渠道）
11. ❌ 不在 chat 复述 Cursor 长文
12. ❌ 不索要 PAT
13. ❌ 不碰 `00-CC-CURRENT.md`（Cursor 拥有）
14. ❌ Cursor 不写 `docs/35` 正文（CC 起草）

---

## 9. 验收策略

- **功能**：admin upload → compute_file_sha → seed 重写 → frontend demo badge 隐藏；URL probe 切 live 跑真实 HEAD 仍合规
- **测试**：新增 `tests/test_compute_file_sha.py`（≥5 case：合法/不存在/路径非法/无 --url 选项/SHA 格式）；既有 `tests/test_url_health_probe.py` 不动
- **演示**：jiansu page `NEXT_PUBLIC_USE_MOCK=false` 时无 DEMO badge；`=true` 时显 DEMO badge

---

## 10. 与现有文档的关系

- 继承 `docs/34` §4.1 序 2（S2.0.2 真实 SHA 江苏样本）
- 继承 `docs/32` §2.1（URL probe 上限钉死）+ §5（Stage 2 移交清单）
- 继承 `docs/33`（S1.18 demo SHA lock 机制）
- 继承 `docs/28`（S1.13 admin upload 契约）
- 继承 `docs/24`（S1.10 FastAPI 只读接口）
- 补充 `docs/04`（数据模型；`lineage.is_demo` JSONB 字段）

---

## 11. CC 建议（供 Cursor 审阅 / 用户裁定）

1. **采纳本规划**（默认：CC 起草，Cursor 审阅）
2. **S2.0.2.1** `compute_file_sha.py` + 5 pytest case（独立小刀；可与 S2.0.2.2 并行）
3. **S2.0.2.2** admin upload + seed 重写流程验收（手动 + SQL count 守门）
4. **S2.0.2.3** URL probe 真实化模式切换（`URL_HEALTH_LIVE=1`）；CI 不跑，生产 cron 不接
5. **不扩 scope**：S2.0.2 仅收口 Stage 1 OPEN 的 2/4 项（真实 SHA + probe 真实化）；cron/通知留 Stage 2 运维刀

— End —