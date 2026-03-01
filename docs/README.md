# LTFS 磁带管理系统

基于 LTFS (Linear Tape File System) 的 LTO-6 磁带存储管理 Web 界面。

## 特性

- 📼 **磁带管理** - 挂载、卸载、弹出磁带
- 📁 **文件管理** - 目录树导航、文件搜索、文件系统扫描
- 🔄 **文件浏览器** - 双面板文件管理，支持容器↔磁带双向传输
- 📋 **操作日志** - 完整的操作记录和日志查看
- 💾 **备份与恢复** - 数据库备份、恢复、验证
- 🚨 **错误监控** - 系统错误捕获和管理
- 🐳 **Docker 支持** - 一键容器化部署

## 快速开始

### 本地开发

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python3 init_db.py

# 4. 启动应用
python3 run.py
```

访问 http://localhost:5001

### Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问 http://localhost:5001

## 文档

- [功能说明](./FEATURES.md) - 详细的功能介绍
- [API 文档](./API.md) - API 接口文档
- [部署指南](./DEPLOYMENT.md) - 部署和配置指南
- [更新日志](./CHANGELOG.md) - 版本更新记录

## 技术栈

- **后端**: Flask + SQLAlchemy
- **前端**: Bootstrap 5 + 原生 JavaScript
- **数据库**: SQLite
- **容器化**: Docker + Docker Compose
- **时区**: Asia/Shanghai

## 项目结构

```
ltfs/
├── app/                      # 主应用
│   ├── templates/           # HTML 模板
│   ├── static/              # 静态资源
│   ├── utils/               # 工具模块
│   ├── models.py            # 数据库模型
│   └── routes.py            # 路由和 API
├── config.py                # 配置文件
├── requirements.txt         # Python 依赖
├── run.py                   # 应用入口
├── docker-compose.yml       # Docker Compose 配置
└── docs/                    # 文档
```

## 许可证

MIT License
