# 保护 public_extracts — Cursor 审验 ACK

- 文件编号：`354-stage0-cursor-s352-protect-extracts-audit-PASS-20260826`
- 日期：2026-08-26
- 对象：CC `c33d3f4` / `5a94fde` + 回执 `353`
- 任务书：`352`

---

## §0. 判定：**PASS**

| 项 | 独立复验 | 判定 |
|---|---|---|
| `--extract-root` / `--archive-root` + `CEGR_*_ROOT` | 源码 | ✅ |
| pytest 后 NBS extract 仍 63 行 / SHA 未变 | pytest + 文件 | ✅ |
| `tests/…s52.py` | **72 passed** | ✅ |
| 回执名含 `-cc-` | 文件名 | ✅ |
| pack | **665 / 665 / 665** | ✅ |
| 回执 `353` | reviews + manifest | ✅ |

**通过。** 下一刀：收紧 JS-shell 误判（大页含 script ≠ 71B 壳），解锁 NBS live。

— End —
