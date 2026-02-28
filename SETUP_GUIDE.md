# 本地测试环境配置指南

## 系统要求

### 必需软件
- **Python 3.7 或更高版本**
- **pip (Python 包管理器)**

### 检查 Python 环境

在终端中运行以下命令检查：

```bash
# 检查 Python 版本
python3 --version

# 或者
python --version

# 检查 pip 版本
pip3 --version
```

## 安装依赖

### 方法一：使用 pip 直接安装（推荐）

在项目根目录下运行：

```bash
pip3 install flask flask-sqlalchemy python-dotenv
```

### 方法二：使用 requirements.txt

```bash
pip3 install -r requirements.txt
```

### macOS 用户注意事项

如果遇到 `xcrun: error` 错误，请先安装 Xcode Command Line Tools：

```bash
xcode-select --install
```

如果上述命令失败，也可以直接从 App Store 安装完整的 Xcode。

## 验证安装

运行以下命令验证依赖是否正确安装：

```bash
python3 -c "import flask; print('Flask:', flask.__version__)"
python3 -c "import flask_sqlalchemy; print('Flask-SQLAlchemy: OK')"
```

## 启动应用

### 快速启动（推荐）

```bash
python3 quick_start.py
```

### 手动启动

```bash
# 1. 初始化数据库（首次运行）
python3 init_db.py

# 2. 启动应用
python3 run.py
```

## 访问应用

在浏览器中打开：**http://localhost:5001**

## 常见问题

### 问题 1：Python 未找到
**症状**：`command not found: python3`

**解决**：
- 确认已安装 Python 3
- 检查 PATH 环境变量
- 尝试使用 `python` 而不是 `python3`

### 问题 2：权限错误
**症状**：权限被拒绝

**解决**：
```bash
# 尝试使用 --user 标志
pip3 install --user flask flask-sqlalchemy python-dotenv
```

### 问题 3：导入错误
**症状**：`ModuleNotFoundError`

**解决**：
```bash
# 重新安装依赖
pip3 install --upgrade flask flask-sqlalchemy python-dotenv
```

## 项目结构

```
ltfs-management/
├── app/                      # 应用代码
│   ├── __init__.py           # Flask 应用初始化
│   ├── models.py             # 数据库模型
│   ├── routes.py             # 路由和视图
│   ├── utils/                # 工具类
│   ├── templates/            # HTML 模板
│   └── static/              # 静态资源
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── quick_start.py           # 快速启动脚本
├── init_db.py               # 数据库初始化
├── run.py                   # 主入口
└── README.md                # 项目说明
```

## 下一步

应用启动后，您可以：

1. 查看首页系统概览
2. 管理测试磁带数据
3. 浏览测试文件列表
4. 查看操作日志
5. 测试备份恢复功能

## 技术支持

如遇到问题，请检查：
1. Python 版本是否符合要求
2. 所有依赖是否正确安装
3. 端口 5001 是否被占用
4. 浏览器是否支持现代 Web 技术
