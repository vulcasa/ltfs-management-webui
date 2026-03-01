# API 文档

本文档详细介绍 LTFS 磁带管理系统的所有 API 端点。

## 目录

1. [磁带管理 API](#磁带管理-api)
2. [文件管理 API](#文件管理-api)
3. [文件浏览器 API](#文件浏览器-api)
4. [文件传输 API](#文件传输-api)
5. [操作日志 API](#操作日志-api)
6. [操作进度 API](#操作进度-api)
7. [备份与恢复 API](#备份与恢复-api)
8. [错误监控 API](#错误监控-api)
9. [健康检查](#健康检查)

---

## 磁带管理 API

### 获取所有磁带

```http
GET /api/tapes
```

**响应示例**:
```json
[
  {
    "id": 1,
    "barcode": "LTO001",
    "label": "磁带 LTO001",
    "status": "mounted",
    "capacity": "2.5TB",
    "used_space": "100GB"
  }
]
```

---

### 挂载磁带

```http
POST /api/tape/mount
```

**请求体**: 无

**响应示例**:
```json
{
  "success": true,
  "message": "磁带挂载成功",
  "operation_id": "uuid",
  "tape": {
    "id": 1,
    "barcode": "LTO001",
    "status": "mounted"
  }
}
```

---

### 卸载磁带

```http
POST /api/tape/unmount
```

**请求体**:
```json
{
  "tape_id": 1
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "磁带卸载成功"
}
```

---

### 弹出磁带

```http
POST /api/tape/eject
```

**请求体**:
```json
{
  "tape_id": 1
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "磁带弹出成功"
}
```

---

### 获取当前磁带

```http
GET /api/tape/current
```

**响应示例**:
```json
{
  "success": true,
  "tape": {
    "id": 1,
    "barcode": "LTO001",
    "status": "mounted",
    "capacity": "2.5TB",
    "used_space": "100GB"
  }
}
```

---

### 获取设备信息

```http
GET /api/tape/device-info
```

**响应示例**:
```json
{
  "success": true,
  "info": {...}
}
```

---

### 获取设备列表

```http
GET /api/tape/device-list
```

**响应示例**:
```json
{
  "success": true,
  "devices": [...]
}
```

---

### 检查设备状态

```http
GET /api/tape/device-status
```

**响应示例**:
```json
{
  "success": true,
  "device_exists": true,
  "device_path": "/dev/sg10"
}
```

---

### 检查磁带是否已挂载

```http
GET /api/tape/mounted
```

**响应示例**:
```json
{
  "success": true,
  "mounted": true,
  "mount_point": "/media/tape"
}
```

---

### 扫描文件系统

```http
GET /api/tape/filesystem
```

**响应示例**:
```json
{
  "success": true,
  "directories": [...],
  "files": [...],
  "dir_count": 10,
  "file_count": 100,
  "total_size": 1073741824
}
```

---

## 文件管理 API

### 获取目录树

```http
GET /api/directories?tape_id=1&parent_id=null
```

**查询参数**:
- `tape_id` (可选): 磁带 ID
- `parent_id` (可选): 父目录 ID

**响应示例**:
```json
{
  "success": true,
  "directories": [
    {
      "id": 1,
      "name": "根目录",
      "path": "",
      "parent_id": null,
      "has_children": true,
      "tape_id": 1
    }
  ]
}
```

---

### 获取文件列表

```http
GET /api/files?tape_id=1&directory_id=1&search=keyword
```

**查询参数**:
- `tape_id` (可选): 磁带 ID
- `directory_id` (可选): 目录 ID
- `search` (可选): 搜索关键词

**响应示例**:
```json
{
  "success": true,
  "files": [
    {
      "id": 1,
      "name": "example.txt",
      "size": 1024,
      "mtime": "2026-02-28T10:00:00",
      "atime": "2026-02-28T10:00:00",
      "ctime": "2026-02-28T10:00:00",
      "tape_id": 1,
      "directory_id": 1,
      "tape_barcode": "LTO001",
      "file_path": "/example.txt"
    }
  ],
  "count": 1
}
```

---

## 文件浏览器 API

### 列出目录内容

```http
GET /api/browser/list?path=/mnt
```

**查询参数**:
- `path`: 目录路径（支持 `/mnt` 和 `/media/tape`）

**响应示例**:
```json
{
  "success": true,
  "path": "/mnt",
  "items": [
    {
      "name": "documents",
      "path": "/mnt/documents",
      "type": "directory",
      "size": 0,
      "modified_at": "2026-02-28T10:00:00",
      "is_parent": false
    }
  ]
}
```

---

## 文件传输 API

### 启动文件传输

```http
POST /api/transfer/start
```

**请求体**:
```json
{
  "source_paths": ["/mnt/file1.txt", "/mnt/folder"],
  "target_path": "/media/tape",
  "transfer_type": "copy",
  "transfer_direction": "container_to_tape"
}
```

**字段说明**:
- `source_paths`: 源文件/目录路径数组
- `target_path`: 目标目录路径
- `transfer_type`: `copy` 或 `move`
- `transfer_direction`: `container_to_tape` 或 `tape_to_container`

**响应示例**:
```json
{
  "success": true,
  "operation_id": "uuid",
  "message": "传输任务已启动"
}
```

---

### 获取传输状态

```http
GET /api/transfer/status/<operation_id>
```

**响应示例**:
```json
{
  "success": true,
  "status": {
    "id": 1,
    "operation_id": "uuid",
    "source_path": "/mnt/file1.txt",
    "target_path": "/media/tape",
    "transfer_type": "copy",
    "transfer_direction": "container_to_tape",
    "status": "in_progress",
    "progress": 50.5,
    "total_size": 1048576,
    "transferred_size": 524288,
    "file_count": 10,
    "current_file": "file1.txt",
    "average_speed": 5.2,
    "file_list": [...],
    "directory_structure": {...},
    "error_message": null,
    "created_at": "2026-02-28T10:00:00",
    "updated_at": "2026-02-28T10:00:05"
  }
}
```

---

### 取消传输

```http
POST /api/transfer/cancel/<operation_id>
```

**响应示例**:
```json
{
  "success": true,
  "message": "传输已取消"
}
```

---

### 获取传输列表

```http
GET /api/transfer/list?limit=50
```

**查询参数**:
- `limit` (可选): 返回数量限制，默认 50

**响应示例**:
```json
{
  "success": true,
  "transfers": [...]
}
```

---

## 操作日志 API

### 获取操作日志

```http
GET /api/logs?limit=1000&since_id=0
```

**查询参数**:
- `limit` (可选): 返回数量限制，默认 1000
- `since_id` (可选): 起始 ID，用于增量查询

**响应示例**:
```json
{
  "success": true,
  "operations": [
    {
      "id": 1,
      "tape_id": 1,
      "tape_barcode": "LTO001",
      "operation_type": "mount",
      "status": "success",
      "message": "磁带挂载成功",
      "command": "ltfs /dev/sg10 /media/tape",
      "stdout": "...",
      "stderr": "",
      "timestamp": "2026-02-28T10:00:00"
    }
  ],
  "count": 1,
  "latest_id": 1
}
```

---

## 操作进度 API

### 获取操作进度

```http
GET /api/operation/progress/<operation_id>
```

**响应示例**:
```json
{
  "success": true,
  "progress": {...}
}
```

---

### 移除操作

```http
DELETE /api/operation/remove/<operation_id>
```

**响应示例**:
```json
{
  "success": true,
  "message": "操作已移除"
}
```

---

## 备份与恢复 API

### 创建备份

```http
POST /api/backup/create
```

**响应示例**:
```json
{
  "success": true,
  "message": "备份创建成功",
  "backup_file": "tape_backup_20260228_100000.db",
  "file_size": 1048576
}
```

---

### 获取备份列表

```http
GET /api/backup/list
```

**响应示例**:
```json
{
  "success": true,
  "backups": [
    {
      "filename": "tape_backup_20260228_100000.db",
      "size": 1048576,
      "created_at": "2026-02-28T10:00:00"
    }
  ],
  "count": 1
}
```

---

### 下载备份

```http
GET /api/backup/download/<filename>
```

**响应**: 文件下载

---

### 恢复备份

```http
POST /api/backup/restore
```

**请求体**:
```json
{
  "filename": "tape_backup_20260228_100000.db"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "备份恢复成功"
}
```

---

### 上传并恢复备份

```http
POST /api/backup/upload
Content-Type: multipart/form-data
```

**表单字段**:
- `file`: 备份文件
- `verify`: 是否校验（true/false，默认 true）

**响应示例**:
```json
{
  "success": true,
  "message": "备份恢复成功",
  "filename": "uploaded_20260228_100000_backup.db"
}
```

---

### 验证备份

```http
GET /api/backup/verify/<filename>
```

**响应示例**:
```json
{
  "success": true,
  "sha256": "abc123...",
  "size": 1048576,
  "filename": "tape_backup_20260228_100000.db"
}
```

---

### 删除备份

```http
DELETE /api/backup/delete/<filename>
```

**响应示例**:
```json
{
  "success": true,
  "message": "备份文件删除成功"
}
```

---

## 错误监控 API

### 获取错误列表

```http
GET /api/errors?severity=error&resolved=false&limit=100
```

**查询参数**:
- `severity` (可选): 严重级别（info/warning/error/critical）
- `resolved` (可选): 是否已解决（true/false）
- `limit` (可选): 返回数量限制，默认 100

**响应示例**:
```json
{
  "success": true,
  "errors": [
    {
      "id": 1,
      "error_type": "Exception",
      "severity": "error",
      "message": "Something went wrong",
      "endpoint": "/api/tapes",
      "resolved": false,
      "created_at": "2026-02-28T10:00:00"
    }
  ]
}
```

---

### 获取错误详情

```http
GET /api/errors/<error_id>
```

**响应示例**:
```json
{
  "success": true,
  "error": {
    "id": 1,
    "error_type": "Exception",
    "severity": "error",
    "message": "Something went wrong",
    "stack_trace": "...",
    "endpoint": "/api/tapes",
    "user_gent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1",
    "resolved": false,
    "resolved_at": null,
    "created_at": "2026-02-28T10:00:00"
  }
}
```

---

### 标记错误为已解决

```http
POST /api/errors/<error_id>/resolve
```

**响应示例**:
```json
{
  "success": true,
  "message": "错误已标记为已解决"
}
```

---

### 获取错误统计

```http
GET /api/errors/stats
```

**响应示例**:
```json
{
  "success": true,
  "stats": {
    "info": 10,
    "warning": 5,
    "error": 2,
    "critical": 0
  }
}
```

---

## 健康检查

### 健康检查

```http
GET /health
GET /healthz
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-28T10:00:00"
}
```

---

### 就绪检查

```http
GET /ready
GET /readyz
```

**响应示例**:
```json
{
  "status": "ready",
  "timestamp": "2026-02-28T10:00:00"
}
```

---

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {...}
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述"
}
```

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
