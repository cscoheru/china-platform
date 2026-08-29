# Dockerfile - paddle-ocr / paddlepaddle runtime
# per 595 tasking §2 + docs/52 B 路 spec + 594 §1.4 备选 paddlepaddle==2.6.2
# 用途: paddle-ocr deps 引入运行时环境；非 production-critical；仅 spec 合规
# 治理红线: 零 cloud OCR / 零 GPU runtime / 零 requirements-dbt.txt 污染

FROM python:3.11-slim

# Install system dependencies (libgomp1 = paddlepaddle OpenMP runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy paddle deps manifest (per 595 tasking §3; 独立文件不污染 requirements-dbt.txt)
COPY requirements-paddle.txt /app/requirements-paddle.txt

# Install paddlepaddle (per 594 §1.4 主路径 paddlepaddle==2.6.2; 与 Python 3.11 兼容)
RUN pip install --no-cache-dir -r /app/requirements-paddle.txt

# Copy project source (保留以备扩展；当前非 production-critical)
COPY . /app/

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["--version"]