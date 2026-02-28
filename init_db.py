#!/usr/bin/env python3
"""
LTO-6 磁带管理系统 - 生产环境数据库初始化脚本
创建空数据库
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def init_database():
    """初始化空数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        print("✅ 数据库表创建完成！")
        print("\n数据库初始化完成！")

if __name__ == '__main__':
    print("=" * 50)
    print("  LTO-6 磁带管理系统 - 生产环境数据库初始化")
    print("=" * 50)
    init_database()
