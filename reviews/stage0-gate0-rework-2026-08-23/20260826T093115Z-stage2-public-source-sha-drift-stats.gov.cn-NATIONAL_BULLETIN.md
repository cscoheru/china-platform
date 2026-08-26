# 公开源 SHA 漂移报告（per tasking 333 §SCHEMA）

- 域：`stats.gov.cn`
- 类目：`NATIONAL_BULLETIN`
- 触发时间（UTC）：`2026-08-26T09:31:15.864197+00:00`
- WORM 归档：`data/public_archives/2026-08/stats.gov.cn/zxfb`

## 1. 源 / URL

| 字段 | 值 |
|---|---|
| domain | `stats.gov.cn` |
| category | `NATIONAL_BULLETIN` |
| URL | `https://www.stats.gov.cn/sj/zxfb/` |

## 2. computed SHA-256（实测下载字节）

```
bb1a573af8ea5802c6d823bb108e54f8a76e7dde1059e70cb25930f66d70d768
```

## 3. expected SHA-256（registry.csv file_hash_sha256）

```
dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d
```

## 4. 状态

- `intake_status = CANDIDATE_AUTO`（非 O1_AUTO_INTAKED；drift ≠ 收口）
- `is_demo = true`（drift 候选绝不能伪装成真数据）
- WORM 归档实测字节：已写入 `data/public_archives/2026-08/stats.gov.cn/zxfb`
- registry.csv **未**被修改（connector 不自动改 registry）

## 5. 建议

用户确认后二选一：(a) 更新 registry.csv file_hash_sha256 为实测 computed_sha256（如认定是源站换版/换路径）；(b) 改用稳定的归档 URL （如 Wayback Machine 快照或稳定 PDF/EXCEL 直链）。本 connector 不会自动改 registry。

## 6. 红线

- ❌ **不自动改 registry.csv file_hash_sha256**（per tasking 333 §SCHEMA "不伪造、不自动改 registry"）
- ❌ **不把 drift 标成 O1_AUTO_INTAKED**（drift ≠ 收口）
- ❌ **不静默吞掉 drift**（本报告即非静默；含 5 字段 + WORM 归档位置）
- ❌ **不 headless / 不绕过反爬**获取"应该匹配的"内容
- ✅ **等用户裁定**：(a) 更新 registry 哈希 或 (b) 改用稳定 URL

— End of SHA drift report —
