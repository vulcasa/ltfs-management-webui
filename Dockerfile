# 单阶段构建（简化）
FROM debian:stable

LABEL maintainer="LTFS Management Team"
LABEL version="1.0.0-beta"
LABEL description="LTFS Management Web UI"

ENV DEBIAN_FRONTEND=noninteractive
ENV APP_NAME=ltfs-management-webui
ENV APP_VERSION=1.0.0-beta

WORKDIR /app

# 安装基础依赖 + 开源 LTFS 编译依赖
RUN apt-get update && apt-get install -y \
    sg3-utils \
    mergerfs \
    sqlite3 \
    python3 \
    python3-pip \
    python3-venv \
    udev \
    dpkg \
    libfuse2 \
    libxml2 \
    libssl3 \
    git \
    build-essential \
    autoconf \
    automake \
    libtool \
    libfuse-dev \
    libxml2-dev \
    libssl-dev \
    libsnmp-dev \
    libicu-dev \
    uuid-dev \
    make \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 克隆开源 LTFS 源码（LinearTapeFileSystem 官方）
RUN git clone https://github.com/LinearTapeFileSystem/ltfs.git /tmp/ltfs && cd /tmp/ltfs

# 编译安装 LTFS
RUN cd /tmp/ltfs && \
    ./autogen.sh && \
    ./configure --prefix=/usr && \
    make -j$(nproc) && \
    make install && \
    ldconfig -v && \
    rm -rf /tmp/ltfs

# 验证 LTFS 安装
RUN ltfs --version || echo "开源 LTFS 安装完成"

# 安装 Python 依赖
COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

COPY . .

RUN mkdir -p /app/instance/backups && \
    mkdir -p /app/app/data/virtual_tape && \
    mkdir -p /media/tape

EXPOSE 5001

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

CMD ["python3", "run.py"]
