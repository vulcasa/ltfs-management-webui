cat > $BASE/docker/Dockerfile <<'DF'
FROM debian:stable-slim
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础依赖 + 开源 LTFS 编译依赖
RUN apt update && apt install -y \
    sg3-utils \
    mergerfs \
    sqlite3 \
    python3 \
    python3-pip \
    python3-flask \
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

