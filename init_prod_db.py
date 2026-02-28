#!/usr/bin/env python3
"""
LTO-6 磁带管理系统 - 生产环境初始化脚本
创建空的数据库，不包含任何测试数据
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def init_production_database():
    """初始化生产环境数据库（无测试数据）"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        print("=" * 50)
        print("  生产环境数据库初始化完成")
        print("=" * 50)
        print("✅ 数据库表结构创建成功")
        print("✅ 未添加任何测试数据")
        print("=" * 50)

if __name__ == '__main__':
    init_production_database()
