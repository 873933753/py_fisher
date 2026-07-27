# 构建上下文应为 fisher/（见 docker-compose.yml 的 build.context）
# 与 fisher/.python-version 对齐
FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 暂时注释，build 慢时可按需打开
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends curl \
#     && rm -rf /var/lib/apt/lists/*

# 以下路径相对 build context（fisher/），不是相对本 Dockerfile 所在目录
COPY requirements.txt .

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 阿里云备用：
# ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
#     PIP_TRUSTED_HOST=mirrors.aliyun.com \
#     PIP_DEFAULT_TIMEOUT=100

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8010

# ENTRYPOINT：启动前准备；CMD：默认进程（可被 compose command 覆盖）
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# 0.0.0.0：允许外部访问；8000：默认端口
# 无reload：生产环境不使用
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8010"]
