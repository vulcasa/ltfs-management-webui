# LTO-6 磁带管理系统

一个基于 Docker 的 LTO-6 磁带管理系统，使用 LTFS 工具管理磁带，通过现代化 WebUI 实现磁带和文件的统一管理。

## 功能特性

- 磁带管理：条形码管理、状态跟踪、挂载/卸载/弹出操作
- 文件管理：元数据搜索、文件列表、所在磁带信息显示
- 系统监控：设备状态、操作日志（实时更新，上限1000条）
- 备份恢复：数据库备份下载/上传、文件校验、恢复验证
- 本地调试：虚拟磁带设备、LTFS 操作模拟器

## 技术栈

- 后端：Flask + SQLAlchemy
- 前端：Bootstrap 5 + Jinja2
- 数据库：SQLite
- 容器化：Docker
- 操作系统：Debian 11:stable
- LTFS：LinearTapeFileSystem 官方源码

## 项目结构

```
ltfs-management/
├── app/
│   ├── __init__.py              # Flask 应用初始化
│   ├── models.py                # 数据库模型
│   ├── routes.py                # 路由和视图函数
│   ├── utils/
│   │   └── ltfs_simulator.py    # LTFS 操作模拟器
│   ├── static/                  # 静态资源
│   ├── templates/               # HTML 模板
│   └── data/                    # 数据存储
├── config.py                    # 配置文件
├── requirements.txt              # Python 依赖
├── run.py                       # 主入口文件
├── init_db.py                  # 数据库初始化脚本
├── setup.sh                    # 本地环境设置脚本
├── start.sh                    # 快速启动脚本
├── .env.example                # 环境变量示例
└── README.md                   # 项目说明
```

## 快速开始

### 本地调试环境（推荐）

#### 方法一：使用自动化脚本（推荐）

1. **克隆或下载项目**
   ```bash
   cd ltfs-management
   ```

2. **运行环境设置脚本**
   ```bash
   ./setup.sh
   ```
   
   这个脚本会自动：
   - 创建 Python 虚拟环境
   - 安装项目依赖
   - 创建必要的目录
   - 初始化数据库（含测试数据）

3. **启动应用**
   ```bash
   ./start.sh
   ```

4. **访问应用**
    在浏览器中打开：http://localhost:5001

#### 方法二：手动设置

1. **创建 Python 虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   ```bash
   python3 init_db.py
   ```

4. **启动应用**
   ```bash
   python3 run.py
   ```

5. **访问应用**
    在浏览器中打开：http://localhost:5001

### Docker 部署

（待完善）

## 本地调试环境说明

### 虚拟磁带设备

项目包含一个完整的 LTFS 操作模拟器，本地开发时无需真实磁带设备：

- 虚拟磁带存储位置：`app/data/virtual_tape/`
- 磁带状态持久化到：`tape_metadata.json`
- 支持挂载/卸载/弹出等所有磁带操作
- 自动生成测试文件供文件扫描使用

### 测试数据

`init_db.py` 脚本会自动创建测试数据：
- 2 条测试磁带（TEST001、TEST002）
- 2 个测试目录（文档、图片）
- 4 个测试文件
- 1 条操作记录

### 调试技巧

1. **查看日志**
   - 应用日志会输出到控制台
   - 操作日志会显示在 WebUI 的"操作日志"页面

2. **重置数据库**
   ```bash
   rm tape_metadata.db
   python3 init_db.py
   ```

3. **使用虚拟磁带**
   - 本地环境默认使用虚拟磁带
   - 可通过修改 `config.py` 中的 `USE_VIRTUAL_TAPE` 配置

## 配置说明

主要配置项在 `config.py` 文件中：

- `LTFS_DEVICE_PATH`: 磁带设备路径（默认：/dev/sg10）
- `LTFS_MOUNT_POINT`: 磁带挂载点（默认：/media/tape）
- `USE_VIRTUAL_TAPE`: 是否使用虚拟磁带（默认：true）
- `LTFS_TIMEOUT`: LTFS 命令超时时间（默认：300秒）

环境变量可通过 `.env` 文件配置（参考 `.env.example`）。

## 使用说明

### 磁带管理

1. 点击"磁带管理"查看磁带列表
2. 点击"挂载磁带"按钮挂载新磁带
3. 对已挂载的磁带可以进行卸载或弹出操作

### 文件管理

1. 点击"文件管理"查看文件列表
2. 使用搜索框搜索文件（支持关键词搜索）
3. 查看文件所在磁带信息

### 操作日志

1. 点击"操作日志"查看最近1000条操作记录
2. 日志每30秒自动刷新

### 备份与恢复

1. 点击"备份与恢复"进入备份管理
2. 点击"下载备份文件"下载当前数据库
3. 上传备份文件进行恢复（支持SHA-256校验）

## 版本历史

### v10.0 (2024-02-25)
- 完整的项目初始化
- Flask 应用基础架构
- 数据库模型设计
- 现代化 WebUI 界面
- LTFS 操作模拟器
- 本地调试环境搭建
- 自动化设置和启动脚本

## 注意事项

- 本地开发时默认使用虚拟磁带设备
- 生产环境需要配置真实磁带设备
- 确保磁带设备权限正确
- 定期备份数据库以防止数据丢失

## 许可证

（待添加）

## 贡献

（待添加）
