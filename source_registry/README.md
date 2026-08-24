# source_registry/

数据源登记。所有来源先进入 `source_registry/registry.csv`，记录：

- 域名、机构、数据类别
- 更新频率、授权说明、访问方式
- 历史覆盖、稳定性、失败处理

模板字段详见 `docs/03-source-registry.md`。

CSV 用 Excel-friendly UTF-8 with BOM（便于统计局同人手工编辑）。
