# 部署指南

本文档详细介绍 LTFS 磁带管理系统的部署和配置方法。

## 目录

1. [系统要求](#系统要求)
2. [本地开发部署](#本地开发部署)
3. [Docker 部署](#docker-部署)
4. [配置说明](#配置说明)
5. [生产环境部署](#生产环境部署)
6. [故障排查](#故障排查)

---

## 系统要求

### 硬件要求

- **CPU**: 双核或更高
- **内存**: 2GB 或更高
- **磁盘**: 至少 10GB 可用空间
- **磁带设备**: LTO-6 或兼容设备（可选，用于生产环境）

### 软件要求

- **操作系统**: Linux（推荐 Debian 11 或 Ubuntu 20.04+）
- **Python**: 3.7 或更高
- **Docker**: 20.10 或更高（可选，用于容器化部署）
- **Docker Compose**: 1.29 或更高（可选）

---

## 本地开发部署

### 步骤 1: 克隆项目

```bash
git clone https://github.com/vulcasa/ltfs-management-webui.git
cd ltfs-management-webui
```

### 步骤 2: 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

### 步骤 3: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 4: 配置环境变量（可选）

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据需要修改配置：

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///tape_metadata.db
LTFS_DEVICE=/dev/sg10
LTFS_MOUNT=/media/tape
LTFS_TIMEOUT=300
PORT=5001
HOST=0.0.0.0
```

### 步骤 5: 初始化数据库

```bash
python3 init_db.py
```

### 步骤 6: 启动应用

```bash
python3 run.py
```

### 步骤 7: 访问应用

打开浏览器访问：http://localhost:5001

---

## Docker 部署

### 使用 Docker Compose（推荐）

#### 步骤 1: 克隆项目

```bash
git clone https://github.com/vulcasa/ltfs-management-webui.git
cd ltfs-management-webui
```

#### 步骤 2: 配置 Docker Compose

编辑 `docker-compose.yml`，根据需要修改配置：

```yaml
version: '3.8'

services:
  ltfs-management-webui:
    build: .
    image: ltfs-management-webui:1.0.2
    privileged: true
    ports:
      - "5001:5001"
    volumes:
      - ./instance:/app/instance
      - /mnt:/mnt
      - tape-media:/media/tape
    devices:
      - /dev/sg10:/dev/sg10
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  tape-media:
```

#### 步骤 3: 构建并启动

```bash
docker-compose up -d
```

#### 步骤 4: 查看日志

```bash
docker-compose logs -f
```

#### 步骤 5: 访问应用

打开浏览器访问：http://localhost:5001

#### 常用命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新镜像并重启
docker-compose pull
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 仅使用 Docker

#### 构建镜像

```bash
docker build -t ltfs-management-webui:1.0.2 .
```

#### 运行容器

```bash
docker run -d \
  --name ltfs-management \
  --privileged \
  -p 5001:5001 \
  -v $(pwd)/instance:/app/instance \
  -v /mnt:/mnt \
  -v tape-media:/media/tape \
  --device /dev/sg10:/dev/sg10 \
  --restart unless-stopped \
  ltfs-management-webui:1.0.2
```

---

## 配置说明

### 配置文件 (config.py)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 密钥，用于会话加密 | `dev-secret-key-change-for-production` |
| `SQLALCHEMY_DATABASE_URI` | 数据库连接 URI | `sqlite:///tape_metadata.db` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | SQLAlchemy 跟踪修改 | `False` |
| `LTFS_DEVICE_PATH` | 磁带设备路径 | `/dev/sg10` |
| `LTFS_MOUNT_POINT` | 磁带挂载点 | `/media/tape` |
| `LTFS_TIMEOUT` | LTFS 命令超时（秒） | `300` |
| `PORT` | 服务端口 | `5001` |
| `HOST` | 服务监听地址 | `0.0.0.0` |

### 环境变量

可以通过环境变量覆盖配置：

| 环境变量 | 对应配置项 |
|----------|-----------|
| `SECRET_KEY` | `SECRET_KEY` |
| `DATABASE_URL` | `SQLALCHEMY_DATABASE_URI` |
| `LTFS_DEVICE` | `LTFS_DEVICE_PATH` |
| `LTFS_MOUNT` | `LTFS_MOUNT_POINT` |
| `LTFS_TIMEOUT` | `LTFS_TIMEOUT` |
| `PORT` | `PORT` |
| `HOST` | `HOST` |

### 数据库配置

#### SQLite（默认）

无需额外配置，应用会自动创建 `tape_metadata.db` 文件。

#### PostgreSQL（推荐生产环境）

修改 `config.py`：

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/ltfs'
```

或通过环境变量：

```env
DATABASE_URL=postgresql://user:password@localhost/ltfs
```

#### MySQL

修改 `config.py`：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/ltfs'
```

---

## 生产环境部署

### 安全建议

1. **修改 SECRET_KEY**
   ```env
   SECRET_KEY=your-production-secret-key-here
   ```

2. **使用 HTTPS**
   - 配置 Nginx 或 Apache 作为反向代理
   - 使用 Let's Encrypt 获取免费 SSL 证书

3. **配置防火墙**
   ```bash
   # 仅允许特定 IP 访问
   ufw allow from 192.168.1.0/24 to any port 5001
   ```

4. **定期备份**
   - 使用应用的备份功能
   - 或定期备份 `instance/` 目录

### Nginx 反向代理配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 使用 systemd 管理服务

创建 `/etc/systemd/system/ltfs-management.service`：

```ini
[Unit]
Description=LTFS Management WebUI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ltfs-management
Environment="PATH=/opt/ltfs-management/venv/bin"
ExecStart=/opt/ltfs-management/venv/bin/python /opt/ltfs-management/run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
systemctl daemon-reload
systemctl enable ltfs-management
systemctl start ltfs-management
systemctl status ltfs-management
```

---

## 故障排查

### 应用无法启动

**检查日志**：
```bash
python3 run.py  # 直接运行看错误
# 或
docker-compose logs ltfs-management-webui
```

**常见原因**：
- 端口被占用：修改 `PORT` 配置
- 依赖未安装：运行 `pip install -r requirements.txt`
- 数据库文件权限：检查 `tape_metadata.db` 的读写权限

### 磁带无法挂载

**检查设备**：
```bash
lsscsi -g  # 查看 SCSI 设备
ls -l /dev/sg*  # 检查设备文件
```

**检查权限**：
```bash
sudo chmod 666 /dev/sg10  # 临时修改权限
# 或添加用户到 tape 组
sudo usermod -a -G tape $USER
```

### Docker 容器无法访问设备

**确保使用 `--privileged` 或正确配置设备**：

```yaml
devices:
  - /dev/sg10:/dev/sg10
```

### 数据库损坏

**从备份恢复**：
1. 使用应用的备份与恢复功能
2. 或手动替换 `tape_metadata.db` 文件

**重新初始化**：
```bash
rm tape_metadata.db
python3 init_db.py
```

### 文件传输失败

**检查源路径和目标路径**：
- 确保源文件存在
- 确保目标路径有写权限
- 检查磁盘空间

**查看传输任务**：
- 访问操作日志页面
- 或访问文件浏览器的传输进度面板

---

## 监控和维护

### 健康检查

应用提供健康检查端点：

```bash
curl http://localhost:5001/health
curl http://localhost:5001/ready
```

### 日志查看

- **应用日志**: 查看控制台输出或 Docker 日志
- **操作日志**: 访问 `/logs` 页面
- **错误日志**: 访问 `/errors` 页面

### 定期维护任务

1. **备份数据库**: 每周或每月
2. **清理旧日志**: 定期清理过期的操作日志
3. **检查磁盘空间**: 确保有足够的可用空间
4. **更新系统**: 定期更新操作系统和依赖包

---

## 获取帮助

- **GitHub Issues**: https://github.com/vulcasa/ltfs-management-webui/issues
- **文档**: 查看本项目的 `docs/` 目录
