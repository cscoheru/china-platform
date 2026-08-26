# 首个公开源 connector — Cursor 审验 ACK

- 文件编号：`332-stage0-cursor-s330-public-source-connector-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `04702f1` / `218b4d6` + 回执 `331`
- 任务书：`330`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| `scripts/auto_ingest_public_source.py`：6 步 + 仅 NBS pilot + AUTH 报告 | 源码 | ✅ |
| 无 headless / 无 `--url` / 无登录绕过 flag | 源码 + pytest | ✅ |
| `tests/test_auto_ingest_public_source_s52.py` | **26 passed** | ✅ |
| dry-run 无网络成功 | CLI | ✅ |
| 未宣布 Gate/O1 PASS；未改 registry / CF | 扫描 | ✅ |
| pack | **648 / 648 / 648** | ✅ |
| 回执 `331` | `reviews/` + manifest | ✅ |

**connector 脚手架通过。** 说明：live 路径当前要求下载字节 SHA == registry 样本哈希；NBS 列表页会漂移 → 下一刀补 **drift→候选归档**（不绕 AUTH）并做一次 live 探测。

— End —
