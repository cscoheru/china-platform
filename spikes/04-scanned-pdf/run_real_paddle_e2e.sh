#!/usr/bin/env bash
# spikes/04-scanned-pdf 隔离 pytest entrypoint (per 597 tasking §C)
#
# 约束 (per 597 §C 红线):
# - 仅 spike/ 隔离测试入口走 paddle-ocr 真依赖路径
# - 主测试套件永远 paddle-ocr MOCK only (per 585 e2e pytest 守门完整)
# - .venv-paddle 隔离 venv 与 spike 守门强绑定
# - 外部 spike 无法触及 (隔离入口)
# - 不污染主测试套件
#
# 用途: paddle-ocr 真实依赖路径验证 (per 597 §C)
# 实测验证: `.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` → exit 0 + version 3.7.0
#
# 用法:
#   bash spikes/04-scanned-pdf/run_real_paddle_e2e.sh
#
# 退出码:
#   0 = 通过 (paddle-ocr 真依赖路径在 .venv-paddle 隔离 venv 内可用)
#   非0 = 失败 (paddle-ocr 真依赖路径不可用, 走 MOCK only fallback per 585)

set -e

# Step 1: 激活 .venv-paddle 隔离 venv
source .venv-paddle/bin/activate

# Step 2: 验证 paddle-ocr 真依赖可导入
python -c "import paddleocr; print(f'OK paddleocr {paddleocr.__version__}')"

# Step 3: 隔离 pytest entrypoint (走真依赖路径)
# 仅在 spike/ 隔离入口执行, 主测试套件 (tests/) 永远 paddle-ocr MOCK only
export PYTHONPATH=spikes/04-scanned-pdf:$PYTHONPATH
python -m pytest spikes/04-scanned-pdf/test_real_paddle_e2e.py -v

echo "OK paddle-ocr 真依赖路径在 .venv-paddle 隔离 venv 内验证通过"