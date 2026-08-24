# backend/

Python 后端（FastAPI）。Stage 1 起开始落地代码；Stage 0 仅保留目录骨架。

规划模块：
- `china_platform.ingest` — 数据采集与原始文件归档
- `china_platform.normalize` — 地域/时间/单位/口径标准化
- `china_platform.analyze` — 派生指标、同类比较、条件化分析
- `china_platform.api` — FastAPI 路由（只读 API）
- `china_platform.agent` — 可选 DSH 研究 Agent 编排（Stage 4+）
