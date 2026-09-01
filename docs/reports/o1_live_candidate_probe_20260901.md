# O1 B 路 live-candidate 探测登记（2026-09-01，knife 646 O1 side）

> **类型**: 646-A.2 O1 B路 live-candidate markdown-only 探测登记
> **作用域**: 仅登记 (registration only); 不启用; 不写 cegr.*; 不改 registry.csv
> **O1 状态**: **仍 OPEN** (B路 主路径 仅登记 candidate, 不切换/启用)
> **前置**: 645 DELIVERED + 审计 PASS (`645-stage0-cursor-s645-m6-m4-8-audit-PASS-20260901.md`)
> **架构师依据**: 646-A.2 spec; per docs/52 §13 B路 主路径 (per 599/601) + 用户零裁定铁律 2026-08-29

## 0. 顶层裁定

**REAL_PROBED** — 适用 1 HTTP, 实测 1 candidate。

O1 状态: **OPEN** (主路径 B路 live-candidate 仅登记, 不切换)
注册作用域: **markdown-only**
registry.csv 变更: **NONE**
cegr.* 表变更: **NONE**
connector enabled: **False**

## 1. Live-candidate 实体逐项

| 序号 | domain | organization | primary_url | sha256 (前 16) | file_size | registration_status |
|---|---|---|---|---|---|---|
| 1 | data.stats.gov.cn | 国家统计局 国家数据 (National Bureau of | https://data.stats.gov.cn/ | 1397e5de18153735 | 3198 | PENDING_CANDIDATE_ONLY |

## 2. Candidate spec 详情

| 字段 | 值 |
|---|---|
| domain | data.stats.gov.cn |
| organization | 国家统计局 国家数据 (National Bureau of Statistics - National Data) |
| category | NATIONAL_DATA_API |
| primary_url | https://data.stats.gov.cn/ |
| auth_note | 公开;无需授权 |
| access_method | HTML + JSON API |
| historical_coverage | 国家数据库月度/季度/年度指标 (1949-至今) |
| stability_note | URL 格式稳定; sub-domain 与现有 rows 不同, 不会冲突 |
| failure_handling | 重试 3 次 → archive.org 备份 → 人工上传入口 |
| update_frequency | MONTHLY/QUARTERLY/YEARLY (按指标不同) |
| purpose_note | O1 B路 live-candidate 探测登记; 与现有 stats.gov.cn/sj/zxfb/ (NATIONAL_BULLETIN) + sj/ndsj/ (NATIONAL_YEARBOOK) 不同 sub-domain; data.stats.gov.cn 提供月度/季度/年度指标 API + HTML 视图; 646 仅登记不启用; O1 仍 OPEN 等用户/架构师裁定启用时机 |

## 3. HTTP 抓取日志

| URL | domain | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|
| https://data.stats.gov.cn/ | data.stats.gov.cn | candidate_probe | 200 | ok | 2026-09-01T09:50:00.965940+00:00 |

## 4. 启用前置条件 (等用户/架构师裁定)

- [ ] M2 Gate 决策结果 (当前 O1 仍 OPEN)
- [ ] 用户/架构师对 data.stats.gov.cn connector 的明确启用授权
- [ ] connector 实现 + 端端 e2e 验证 (现有 B路 公开源自动获取六步流水线已就绪 per docs/52 §13)
- [ ] 单元测试 + 集成测试覆盖 (e.g. fetch 200 / SHA 校验 / 错误重试)

## 5. 红线遵守

- ✓ ≤1 HTTP total (硬性上限)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不改 registry.csv (registry 零改动)
- ✓ 不启用 connector (enabled=FALSE)
- ✓ O1 仍 OPEN (B路 主路径 仅登记, 不切换)
- ✓ 不静默硬编码 value (从抓取解析 SHA)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 数据源唯一 = 政府/统计局/研究机构自取 (data.stats.gov.cn = 国家统计局 国家数据, 满足)
- ✓ 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 / O1 B路 live-candidate PASS
