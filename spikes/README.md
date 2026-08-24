# spikes/

Stage 0 四类样本提取 spike。每个 spike 一个子目录，统一结构：

```
spikes/XX-name/
├── extract.py        提取脚本
├── test_extract.py   单元测试
├── README.md         样本说明 + 提取方法 + 验证结果
└── sample.html       或 sample.pdf / sample.xlsx（按需）
```

| Spike | 来源类型 | 验证能力 |
|---|---|---|
| `01-national-yearbook/` | 国家统计年鉴 Excel | Excel 解析、单位识别、表格定位 |
| `02-provincial-yearbook/` | 省级统计年鉴 Excel/HTML | 多源 schema 复用、省级口径差异 |
| `03-municipal-bulletin/` | 地市统计公报 HTML/PDF | 半结构化文本提取、口径变化 |
| `04-scanned-pdf/` | 扫描 PDF 表格 | OCR、版面坐标、置信度机制 |

四个 spike 全部完成后才能写 `docs/08-mvp-plan.md` 的实施时间估算。
