# 变量参考文档

本文档详细列出项目中所有变量的声明、类型和作用。

---

## 1. 配置变量 (config.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `SECRET_KEY` | str | Flask应用安全密钥，用于会话加密 |
| `SQLALCHEMY_DATABASE_URI` | str | 数据库连接字符串 |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | bool | 是否跟踪模型修改（默认False） |
| `LTFS_DEVICE_PATH` | str | LTO磁带设备路径（默认`/dev/sg10`） |
| `LTFS_MOUNT_POINT` | str | 磁带挂载点（默认`/media/tape`） |
| `LTFS_TIMEOUT` | int | LTFS命令超时时间（秒，默认300） |
| `PORT` | int | Web服务器监听端口（默认5001） |
| `HOST` | str | Web服务器监听地址（默认`0.0.0.0`） |

---

## 2. 数据库模型字段 (app/models.py)

### 2.1 Tape（磁带）

| 字段名 | 类型 | 作用 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `barcode` | String(50) | 磁带条形码，唯一标识 |
| `label` | String(100) | 磁带标签/名称 |
| `status` | String(20) | 磁带状态：`unmounted`/`mounted`/`ejected` |
| `capacity` | String(20) | 磁带总容量（如"2.5TB"） |
| `used_space` | String(20) | 已使用空间 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 最后更新时间 |

### 2.2 Directory（目录）

| 字段名 | 类型 | 作用 |
|--------|------|------|
| `id` | Integer | 主键 |
| `tape_id` | Integer | 外键，关联磁带 |
| `parent_id` | Integer | 自外键，父目录ID（用于树形结构） |
| `name` | String(255) | 目录名称 |
| `path` | String(1000) | 相对路径 |
| `created_at` | DateTime | 创建时间 |

### 2.3 File（文件）

| 字段名 | 类型 | 作用 |
|--------|------|------|
| `id` | Integer | 主键 |
| `tape_id` | Integer | 外键，关联磁带 |
| `directory_id` | Integer | 外键，关联目录 |
| `name` | String(255) | 文件名称 |
| `size` | BigInteger | 文件大小（字节） |
| `mtime` | DateTime | 修改时间 |
| `atime` | DateTime | 访问时间 |
| `ctime` | DateTime | 创建时间 |
| `created_at` | DateTime | 记录创建时间 |

### 2.4 Operation（操作日志）

| 字段名 | 类型 | 作用 |
|--------|------|------|
| `id` | Integer | 主键 |
| `tape_id` | Integer | 外键，关联磁带 |
| `operation_type` | String(50) | 操作类型：`mount`/`unmount`/`eject`/`scan_filesystem`/`backup`/`restore` |
| `status` | String(20) | 操作状态：`success`/`error` |
| `message` | Text | 操作消息 |
| `command` | Text | 执行的命令 |
| `stdout` | Text | 标准输出 |
| `stderr` | Text | 标准错误 |
| `timestamp` | DateTime | 操作时间 |

### 2.5 SystemError（系统错误）

| 字段名 | 类型 | 作用 |
|--------|------|------|
| `id` | Integer | 主键 |
| `error_type` | String(100) | 错误类型（异常类名） |
| `severity` | String(20) | 严重程度：`error`/`critical` |
| `message` | Text | 错误消息 |
| `stack_trace` | Text | 堆栈跟踪 |
| `endpoint` | String(255) | 发生错误的API端点 |
| `user_agent` | String(255) | 客户端User-Agent |
| `ip_address` | String(50) | 客户端IP地址 |
| `resolved` | Boolean | 是否已解决 |
| `resolved_at` | DateTime | 解决时间 |
| `created_at` | DateTime | 创建时间 |

### 2.6 FileTransfer（文件传输）

| 字段名 | 类型 | 作用 |
|--------|------|------|
| `id` | Integer | 主键 |
| `operation_id` | String(100) | 唯一操作ID（UUID） |
| `source_path` | Text | 源路径 |
| `target_path` | Text | 目标路径 |
| `transfer_type` | String(20) | 传输类型：`copy`/`move` |
| `transfer_direction` | String(30) | 传输方向：`container_to_tape`/`tape_to_container` |
| `status` | String(20) | 状态：`pending`/`in_progress`/`completed`/`failed`/`cancelled` |
| `total_size` | BigInteger | 总大小（字节） |
| `transferred_size` | BigInteger | 已传输大小 |
| `file_count` | Integer | 文件数量 |
| `current_file` | Text | 当前传输的文件名 |
| `progress` | Float | 进度百分比（0-100） |
| `average_speed` | Float | 平均速度（MB/s） |
| `file_list` | Text | 文件列表（JSON字符串） |
| `directory_structure` | Text | 目录结构（JSON字符串） |
| `error_message` | Text | 错误消息 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

## 3. 工具类全局变量

### 3.1 时区相关

| 变量名 | 类型 | 作用 | 位置 |
|--------|------|------|------|
| `SHANGHAI_TZ` | pytz.timezone | 上海时区对象 | models.py, routes.py, utils/* |
| `get_shanghai_now()` | function | 获取当前上海时区时间（无时区信息） | models.py, routes.py, utils/* |

### 3.2 命令执行器 (utils/command_executor.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `CommandExecutor` | class | 命令执行器，支持超时和进度回调 |
| `CommandExecutor.timeout` | int | 命令执行超时时间 |
| `CommandExecutor._current_progress` | int | 当前进度值 |
| `CommandExecutor._current_message` | str | 当前进度消息 |
| `CommandExecutor._progress_lock` | threading.Lock | 进度更新线程锁 |
| `OperationProgressTracker` | class | 操作进度跟踪器 |
| `OperationProgressTracker._progress` | dict | 存储所有操作进度 |
| `OperationProgressTracker._lock` | threading.Lock | 进度字典线程锁 |
| `progress_tracker` | OperationProgressTracker | 全局单例实例 |

### 3.3 错误监控器 (utils/error_monitor.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `ErrorMonitor` | class | 错误监控器类 |
| `error_monitor` | ErrorMonitor | 全局单例实例 |

### 3.4 LTFS工具 (utils/ltfs_tool.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `LTFSTool` | class | LTFS磁带操作工具类 |
| `LTFSTool.device_path` | str | 设备路径 |
| `LTFSTool.mount_point` | str | 挂载点 |
| `LTFSTool.timeout` | int | 超时时间 |
| `LTFSTool.executor` | CommandExecutor | 命令执行器实例 |

### 3.5 文件传输管理器 (utils/file_transfer.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `FileTransferManager` | class | 文件传输管理器类 |
| `FileTransferManager.active_transfers` | dict | 活跃的传输任务 |
| `FileTransferManager.lock` | threading.Lock | 线程锁 |
| `transfer_manager` | FileTransferManager | 全局单例实例 |

---

## 4. Flask应用变量 (app/__init__.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `app` | Flask | Flask应用实例 |
| `db` | SQLAlchemy | 数据库对象 |

---

## 5. 路由中的局部变量 (app/routes.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `tape_count` | int | 磁带总数 |
| `file_count` | int | 文件总数 |
| `mounted_count` | int | 已挂载磁带数 |
| `total_capacity` | float | 总容量（字节） |
| `formatted_capacity` | str | 格式化后的容量字符串 |
| `search` | str | 搜索关键词 |
| `operations` | list | 操作日志列表 |
| `operation_id` | str | 操作唯一ID（UUID） |
| `tape` | Tape | 磁带对象 |
| `ltfs` | LTFSTool | LTFS工具实例 |
| `result` | dict | 操作结果字典 |
| `dir_map` | dict | 目录路径到ID的映射 |
| `root_dir` | Directory | 统一根目录 |
| `file_obj` | File | 文件对象 |
| `total_size` | int | 总大小 |
| `limit` | int | 查询限制数量 |
| `since_id` | int | 起始ID（用于分页） |
| `tape_mount_point` | str | 磁带挂载点路径 |
| `db_mounted` | bool | 数据库中记录的挂载状态 |
| `is_mounted` | bool | 文件系统挂载状态 |
| `path` | str | 目录路径 |
| `items` | list | 目录内容列表 |
| `source_paths` | list | 源路径列表 |
| `target_path` | str | 目标路径 |
| `transfer_type` | str | 传输类型 |
| `transfer_direction` | str | 传输方向 |
| `backups` | list | 备份文件列表 |
| `filename` | str | 文件名 |
| `filepath` | str | 文件完整路径 |
| `file_size` | int | 文件大小 |
| `file_hash` | str | SHA-256哈希值 |
| `timestamp` | str | 时间戳字符串 |
| `severity` | str | 错误严重程度 |
| `resolved` | bool | 是否已解决 |
| `error` | SystemError | 错误对象 |
| `stats` | dict | 错误统计 |

---

## 6. 前端JavaScript变量 (app/static/js/file_browser.js)

### 6.1 FileBrowser 类属性

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `FileBrowser.leftPath` | str | 左侧（服务器）当前路径 |
| `FileBrowser.rightPath` | str | 右侧（磁带）当前路径 |
| `FileBrowser.leftSelectedItems` | Set | 左侧选中的文件/目录 |
| `FileBrowser.rightSelectedItems` | Set | 右侧选中的文件/目录 |
| `FileBrowser.pollingInterval` | number | 轮询定时器ID |
| `FileBrowser.previousTransfers` | Map | 上一次传输状态（用于检测完成） |

### 6.2 全局函数

| 函数名 | 作用 |
|--------|------|
| `refreshBrowser(side)` | 刷新指定侧的文件浏览器 |
| `transferToRight()` | 向磁带传输文件 |
| `transferToLeft()` | 从磁带接收文件 |
| `loadTransfers()` | 加载传输任务列表 |
| `window.fileBrowser` | FileBrowser实例全局引用 |

### 6.3 内部临时变量

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `data` | object | API响应数据 |
| `response` | Response | fetch响应对象 |
| `sourcePaths` | array | 源路径数组 |
| `targetPath` | str | 目标路径 |
| `transferType` | str | 传输类型（copy/move） |
| `side` | str | 侧（'left'/'right'） |
| `path` | str | 路径 |
| `item` | object | 文件/目录项 |
| `items` | array | 文件/目录列表 |
| `tr` | HTMLElement | 表格行元素 |
| `checkbox` | HTMLElement | 复选框元素 |
| `selectedSet` | Set | 当前选中的项目集合 |
| `transfer` | object | 传输任务对象 |
| `currentTransfers` | array | 当前传输列表 |

---

## 7. 环境变量（.env.example）

| 变量名 | 作用 |
|--------|------|
| `SECRET_KEY` | Flask密钥 |
| `DATABASE_URL` | 数据库URL |
| `LTFS_DEVICE` | 磁带设备路径 |
| `LTFS_MOUNT` | 挂载点 |
| `LTFS_TIMEOUT` | 超时时间 |
| `PORT` | 端口 |
| `HOST` | 主机地址 |

---

## 8. 数据库初始化变量 (init_db.py / init_prod_db.py)

| 变量名 | 类型 | 作用 |
|--------|------|------|
| `tape_barcodes` | list | 初始磁带条形码列表 |
| `mock_directories` | dict | 模拟目录结构数据 |
| `mock_files` | list | 模拟文件数据 |

---

## 附录：状态值参考

### 磁带状态 (Tape.status)
- `unmounted`: 未挂载
- `mounted`: 已挂载
- `ejected`: 已弹出

### 操作类型 (Operation.operation_type)
- `mount`: 挂载
- `unmount`: 卸载
- `eject`: 弹出
- `scan_filesystem`: 扫描文件系统
- `backup`: 备份
- `restore`: 恢复
- `device_list`: 获取设备列表

### 操作状态 (Operation.status)
- `success`: 成功
- `error`: 错误

### 错误严重程度 (SystemError.severity)
- `error`: 错误
- `critical`: 严重

### 传输状态 (FileTransfer.status)
- `pending`: 等待中
- `in_progress`: 传输中
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消

### 传输类型 (FileTransfer.transfer_type)
- `copy`: 复制
- `move`: 移动

### 传输方向 (FileTransfer.transfer_direction)
- `container_to_tape`: 服务器到磁带
- `tape_to_container`: 磁带到服务器

---

## 9. 数据库详细格式

### 9.1 数据库文件位置

- **开发环境**: `instance/tape_metadata.db`
- **生产环境**: `instance/tape_metadata.db`

### 9.2 完整SQL DDL（可直接用于参考）

```sql
-- =============================================
-- LTO-6 磁带管理系统数据库 schema
-- 版本: 1.0.2
-- 注意事项: 保持向下兼容，不要删除已有字段
-- =============================================

-- 磁带表
CREATE TABLE IF NOT EXISTS tape (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    label VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'unmounted',
    capacity VARCHAR(20),
    used_space VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 目录表（树形结构，自关联）
CREATE TABLE IF NOT EXISTS directory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tape_id INTEGER NOT NULL,
    parent_id INTEGER,
    name VARCHAR(255) NOT NULL,
    path VARCHAR(1000) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tape_id) REFERENCES tape(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES directory(id) ON DELETE CASCADE
);

-- 文件表
CREATE TABLE IF NOT EXISTS file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tape_id INTEGER NOT NULL,
    directory_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    size BIGINT,
    mtime DATETIME,
    atime DATETIME,
    ctime DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tape_id) REFERENCES tape(id) ON DELETE CASCADE,
    FOREIGN KEY (directory_id) REFERENCES directory(id) ON DELETE CASCADE
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tape_id INTEGER,
    operation_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT,
    command TEXT,
    stdout TEXT,
    stderr TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tape_id) REFERENCES tape(id) ON DELETE SET NULL
);

-- 系统错误表
CREATE TABLE IF NOT EXISTS system_error (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    stack_trace TEXT,
    endpoint VARCHAR(255),
    user_agent VARCHAR(255),
    ip_address VARCHAR(50),
    resolved BOOLEAN DEFAULT 0,
    resolved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 文件传输表
CREATE TABLE IF NOT EXISTS file_transfer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id VARCHAR(100) UNIQUE NOT NULL,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    transfer_type VARCHAR(20) NOT NULL,
    transfer_direction VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_size BIGINT DEFAULT 0,
    transferred_size BIGINT DEFAULT 0,
    file_count INTEGER DEFAULT 0,
    current_file TEXT,
    progress REAL DEFAULT 0.0,
    average_speed REAL,
    file_list TEXT,
    directory_structure TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 索引（用于提升查询性能）
-- =============================================

CREATE INDEX IF NOT EXISTS idx_tape_barcode ON tape(barcode);
CREATE INDEX IF NOT EXISTS idx_tape_status ON tape(status);
CREATE INDEX IF NOT EXISTS idx_directory_tape_id ON directory(tape_id);
CREATE INDEX IF NOT EXISTS idx_directory_parent_id ON directory(parent_id);
CREATE INDEX IF NOT EXISTS idx_file_tape_id ON file(tape_id);
CREATE INDEX IF NOT EXISTS idx_file_directory_id ON file(directory_id);
CREATE INDEX IF NOT EXISTS idx_file_name ON file(name);
CREATE INDEX IF NOT EXISTS idx_operation_tape_id ON operation(tape_id);
CREATE INDEX IF NOT EXISTS idx_operation_timestamp ON operation(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_error_severity ON system_error(severity);
CREATE INDEX IF NOT EXISTS idx_system_error_resolved ON system_error(resolved);
CREATE INDEX IF NOT EXISTS idx_file_transfer_status ON file_transfer(status);
CREATE INDEX IF NOT EXISTS idx_file_transfer_operation_id ON file_transfer(operation_id);
```

### 9.3 表关系图

```
┌─────────────────┐       ┌─────────────────┐
│     tape        │       │   operation     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ tape_id (FK)    │
│ barcode         │       │ id (PK)         │
│ status          │       │ operation_type  │
│ capacity        │       │ status          │
│ used_space      │       │ timestamp       │
└─────────────────┘       └─────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐       ┌─────────────────┐
│    directory    │       │      file       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ tape_id (FK)    │◄──────│ tape_id (FK)    │
│ parent_id (FK)  │       │ directory_id    │
│ name            │◄──────│ (FK)            │
│ path            │       │ name            │
│ created_at      │       │ size            │
└─────────────────┘       │ mtime/atime/    │
        │                 │ ctime           │
        │ 1:N             └─────────────────┘
        ▼
┌─────────────────┐
│   system_error  │
├─────────────────┤
│ id (PK)         │
│ error_type      │
│ severity        │
│ message         │
│ resolved        │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│   file_transfer │
├─────────────────┤
│ id (PK)         │
│ operation_id    │
│ source_path     │
│ target_path     │
│ transfer_type   │
│ transfer_dir    │
│ status          │
│ progress        │
│ total_size      │
│ current_file    │
│ created_at      │
└─────────────────┘
```

### 9.4 数据库向后兼容规范

> ⚠️ **重要**: 后续代码更新必须遵守以下规则，确保不破坏现有数据。

#### 9.4.1 禁止操作

| 操作 | 风险 | 替代方案 |
|------|------|----------|
| ❌ 删除已有字段 | 数据丢失 | 使用 nullable=True，保留字段 |
| ❌ 修改字段类型 | 数据转换失败 | 新增字段，保留原字段 |
| ❌ 修改字段长度 | 数据截断 | 增大长度，不减小 |
| ❌ 删除表 | 数据永久丢失 | 保留表，清空数据 |
| ❌ 删除索引 | 查询性能下降 | 保留索引 |

#### 9.4.2 允许操作

| 操作 | 说明 |
|------|------|
| ✅ 新增表 | 可直接创建 |
| ✅ 新增字段 | 使用 nullable=True, default=xxx |
| ✅ 增大字段长度 | VARCHAR(50) → VARCHAR(100) |
| ✅ 新增索引 | 提升查询性能 |
| ✅ 使用 Alembic 迁移 | 正式的数据迁移工具 |

#### 9.4.3 字段命名规范

- **小写 + 下划线**: `used_space`（不是 usedSpace 或 usedSpace）
- **表名**: 小写，单数，如 `tape`（不是 tapes）
- **外键命名**: `{表名}_id`，如 `tape_id`

#### 9.4.4 时区处理

- 所有 `DATETIME` 字段存储**不带时区信息**的时间
- 使用 `get_shanghai_now()` 获取当前时间
- 时区: `Asia/Shanghai`

#### 9.4.5 代码更新流程

```
1. 确认变更是否涉及数据库
   ├── 是 → 进入步骤2
   └── 否 → 直接提交

2. 检查变更类型
   ├── 新增字段 → 在 models.py 添加 nullable=True 的字段
   ├── 修改逻辑 → 确保不影响现有数据读取
   └── 删除操作 → 改为标记废弃，不实际删除

3. 测试
   ├── 使用现有数据库文件测试
   ├── 验证旧数据仍可正常读取
   └── 验证新增功能正常工作

4. 提交代码
```

#### 9.4.6 数据库备份

每次正式发布前，执行以下SQL备份：
```sql
-- 备份命令（在应用外执行）
sqlite3 instance/tape_metadata.db ".backup tape_metadata_backup.db"
```

或在应用中调用 `/api/backup/create` 接口。

---

## 10. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0.2 | 2026-04-20 | 初始版本，包含6个表 |

---

## 附录：快速参考

### 状态值枚举

| 类别 | 值 | 说明 |
|------|------|------|
| Tape.status | `unmounted` | 未挂载 |
| | `mounted` | 已挂载 |
| | `ejected` | 已弹出 |
| Operation.status | `success` | 成功 |
| | `error` | 错误 |
| SystemError.severity | `error` | 一般错误 |
| | `critical` | 严重错误 |
| FileTransfer.status | `pending` | 等待中 |
| | `in_progress` | 传输中 |
| | `completed` | 已完成 |
| | `failed` | 失败 |
| | `cancelled` | 已取消 |
| FileTransfer.transfer_type | `copy` | 复制 |
| | `move` | 移动 |
| FileTransfer.transfer_direction | `container_to_tape` | 服务器→磁带 |
| | `tape_to_container` | 磁带→服务器 |