# 更新日志

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.2] - 2026-02-28

### 新增

- **文件浏览器**
  - 双面板设计：左侧容器文件系统 (/mnt)，右侧磁带文件系统 (/media/tape)
  - 面包屑导航：路径导航，支持点击跳转
  - Finder 风格列表视图
  - 多选功能：支持选择多个文件/目录
  - 全选/取消全选

- **文件传输系统**
  - 双向传输：容器 → 磁带，磁带 → 容器
  - 传输类型：复制 (Copy) 和 移动 (Move)
  - 双向箭头按钮
  - 实时传输进度：进度条、百分比、已传输/总大小
  - 平均速度显示 (MB/s)
  - 自动刷新：每 2 秒刷新传输状态
  - 传输任务列表：显示最近 50 个传输任务

### 修复

- **面包屑导航**
  - 修复重复显示 /mnt 和 /media/tape 的问题
  - 重写路径处理逻辑，正确构建面包屑

- **目录树显示**
  - 确保统一根目录先创建
  - 按路径层级排序目录创建顺序
  - 正确建立父子关系
  - 根目录优先排序显示在最上面
  - 修复缩进问题（level * 20px）
  - 子目录按名称字母序排序

- **磁带挂载检测**
  - 新增 /api/tape/mounted API 检查挂载状态
  - 右侧浏览器未挂载时显示警告提示
  - 传输前检查挂载状态，未挂载时提示用户

### 数据库

- **新增 FileTransfer 模型**
  - 存储文件传输任务信息
  - 包含源路径、目标路径、传输类型、传输方向
  - 记录进度、已传输大小、总大小、文件数
  - 记录当前传输文件、平均速度、错误信息
  - 支持状态：pending, in_progress, completed, failed, cancelled

### API

- **新增磁带管理 API**
  - `GET /api/tape/mounted` - 检查磁带是否已挂载

- **新增文件浏览器 API**
  - `GET /api/browser/list` - 列出目录内容

- **新增文件传输 API**
  - `POST /api/transfer/start` - 启动文件传输
  - `GET /api/transfer/status/<operation_id>` - 获取传输状态
  - `POST /api/transfer/cancel/<operation_id>` - 取消传输
  - `GET /api/transfer/list` - 获取传输列表

### 文档

- 删除旧的项目规划文档
- 新增完整的项目文档：
  - `README.md` - 项目介绍和快速开始
  - `FEATURES.md` - 详细功能说明
  - `API.md` - API 接口文档
  - `DEPLOYMENT.md` - 部署指南
  - `CHANGELOG.md` - 更新日志

---

## [1.0.1] - 2026-02-28

### 新增

- **文件管理**
  - 添加文件路径列显示
  - 统合多张磁带的目录结构
  - 样式调整和优化

### 修复

- 目录结构统合显示问题
- 文件路径显示问题

---

## [1.0.0] - 2026-02-25

### 新增

- **初始版本发布**
  - 完整的磁带生命周期管理
  - 磁带管理页面
  - 文件管理页面
  - 操作日志页面
  - 备份与恢复页面
  - 错误监控页面
  - 首页统计概览
  - 完整的 RESTful API
  - Docker 容器化支持
  - 完整的错误处理和日志记录

### 功能特性

- 📼 磁带管理：挂载、卸载、弹出
- 📁 文件管理：目录树导航、文件搜索、文件系统扫描
- 📋 操作日志：完整的操作记录
- 💾 备份与恢复：数据库备份、恢复、验证
- 🚨 错误监控：系统错误捕获和管理
- 🐳 Docker 支持：一键容器化部署

---

## 版本说明

### 语义化版本控制

- **主版本号 (Major)**：不兼容的 API 修改
- **次版本号 (Minor)**：向下兼容的功能性新增
- **修订号 (Patch)**：向下兼容的问题修正

### 变更类型

- **新增 (Added)**：新功能
- **变更 (Changed)**：现有功能的变更
- **弃用 (Deprecated)**：即将移除的功能
- **移除 (Removed)**：已移除的功能
- **修复 (Fixed)**：bug 修复
- **安全 (Security)**：安全相关的修复

---

[1.0.2]: https://github.com/vulcasa/ltfs-management-webui/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/vulcasa/ltfs-management-webui/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/vulcasa/ltfs-management-webui/releases/tag/v1.0.0
