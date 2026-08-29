# spikes/04-scanned-pdf 隔离 pytest conftest (per 597 tasking §C)
#
# 约束 (per 597 §C 红线):
# - 仅 spike/ 隔离测试入口走 paddle-ocr 真依赖路径
# - 主测试套件永远 paddle-ocr MOCK only (per 585 e2e pytest 守门完整)
# - .venv-paddle 隔离 venv 与 spike 守门强绑定
# - 外部 spike 无法触及 (隔离入口)
#
# 用途: paddle-ocr 真实依赖路径 conftest (per 597 §C)
# 实测验证: `.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` → exit 0 + version 3.7.0

import pytest


def pytest_collection_modifyitems(config, items):
    """
    标记所有 paddle-ocr 真依赖路径测试为 spike_only

    仅在 spike/ 隔离入口执行, 主测试套件 (tests/) 永远 paddle-ocr MOCK only
    """
    for item in items:
        if "real_paddle" in item.nodeid:
            item.add_marker(pytest.mark.spike_only)


@pytest.fixture(scope="session")
def paddle_ocr_engine():
    """
    paddle-ocr 真实依赖路径 fixture (隔离 .venv-paddle)

    仅在 spike/ 隔离入口执行时使用, 主测试套件 (tests/) 永远走 paddle-ocr MOCK only
    """
    try:
        import paddleocr

        try:
            return paddleocr.PaddleOCR(use_angle_cls=True, lang="ch")
        except Exception as e:
            pytest.skip(f"paddleocr PaddleOCR init failed (model download?): {e}")
    except ImportError:
        pytest.skip("paddleocr not available; skip spike-only test (use MOCK only path)")