# 公开源技术阻断报告（per tasking 339 §SCHEMA）

- 域：`tjj.hubei.gov.cn`
- 类目：`PROVINCIAL_BULLETIN`
- 触发时间（UTC）：`2026-08-26T09:57:48.639443+00:00`

## 1. 源 / URL

| 字段 | 值 |
|---|---|
| domain | `tjj.hubei.gov.cn` |
| category | `PROVINCIAL_BULLETIN` |
| URL | `https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/` |

## 2. 现象

下载字节仅 71 bytes,且包含 `<script>` 或 `window.location` 重定向标记。判定为 JS-only shell (per tasking 339 §SCHEMA)。connector **不执行 JS**,也**不切 headless browser** 跟随;等用户提供稳定直链或暂缓。

## 3. 需要什么（用户裁定 / 提供）

用户需提供稳定的直链 URL（registry.csv primary_url 改为直链）或 在 headless-free 的可达页面（HTML 含完整附件 href 列表）

## 4. 替代公开源

registry.csv 已有公开源：stats.gov.cn NATIONAL_BULLETIN(已落 drift 等用户)/ wb.flk.npc.gov.cn SCANNED_PDF_RESEARCH / archive.org SCANNED_PDF_UPLOAD （待 tasking 33X+ 落地）

## 5. 红线

- ❌ **不执行页面 JS**（per tasking 339 §红线 '不执行页面 JS';connector 静态解析 HTML）
- ❌ **不切 headless browser 跟随 JS 重定向**（per registry.csv Hubei access_method）
- ❌ **不盲爬外域**（deeplink 已用 urlparse 比 host,跨域一律过滤）
- ❌ **不把 JS 壳静默当 O1_AUTO_INTAKED**（本报告即非静默）
- ❌ **不静默失败**（5 字段 + 替代源 + 等用户裁定）
- ✅ **等用户裁定**：(a) 提供稳定直链 / (b) 换镜像 / (c) 暂缓

— End of tech-blocked report —
