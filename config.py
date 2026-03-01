import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-for-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/tape_metadata.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LTFS 设备配置
    LTFS_DEVICE_PATH = os.environ.get('LTFS_DEVICE') or '/dev/sg10'
    LTFS_MOUNT_POINT = os.environ.get('LTFS_MOUNT') or '/media/tape'
    LTFS_TIMEOUT = int(os.environ.get('LTFS_TIMEOUT', '300'))
    
    # 服务器配置
    PORT = int(os.environ.get('PORT', '5001'))
    HOST = os.environ.get('HOST', '0.0.0.0')
