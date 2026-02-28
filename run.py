#!/usr/bin/env python3
"""
LTO-6 磁带管理系统
主入口文件
"""

from app import app, db
from app.models import Tape, Directory, File, Operation
import os

def init_database():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print("数据库初始化完成")

def reset_tape_status():
    """重置所有磁带状态为 ejected"""
    with app.app_context():
        from app.models import Tape
        count = Tape.query.update({'status': 'ejected'})
        db.session.commit()
        if count > 0:
            print(f"已重置 {count} 个磁带状态为 ejected")
        else:
            print("没有需要重置状态的磁带")

def main():
    """主函数"""
    print("=" * 50)
    print("      LTO-6 磁带管理系统")
    print("=" * 50)
    
    # 初始化数据库
    init_database()
    
    # 重置所有磁带状态
    reset_tape_status()
    
    # 启动 Flask 应用
    from config import Config
    print("\n正在启动应用服务器...")
    print(f"访问地址: http://{Config.HOST}:{Config.PORT}")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    app.run(host=Config.HOST, port=Config.PORT, debug=True)

if __name__ == '__main__':
    main()
