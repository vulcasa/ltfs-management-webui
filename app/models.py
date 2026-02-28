from datetime import datetime
import pytz
from app import db

# 上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

def get_shanghai_now():
    """获取当前上海时区时间（不带时区信息，用于SQLite存储）"""
    return datetime.now(SHANGHAI_TZ).replace(tzinfo=None)

class Tape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(100))
    status = db.Column(db.String(20), nullable=False, default='unmounted')
    capacity = db.Column(db.String(20))
    used_space = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=get_shanghai_now)
    updated_at = db.Column(db.DateTime, default=get_shanghai_now, onupdate=get_shanghai_now)
    
    directories = db.relationship('Directory', backref='tape', lazy=True)
    files = db.relationship('File', backref='tape', lazy=True)
    operations = db.relationship('Operation', backref='tape', lazy=True)

class Directory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tape_id = db.Column(db.Integer, db.ForeignKey('tape.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('directory.id'))
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=get_shanghai_now)
    
    parent = db.relationship('Directory', remote_side=[id], backref='children')
    files = db.relationship('File', backref='directory', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tape_id = db.Column(db.Integer, db.ForeignKey('tape.id'), nullable=False)
    directory_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.BigInteger)
    mtime = db.Column(db.DateTime)
    atime = db.Column(db.DateTime)
    ctime = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_shanghai_now)

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tape_id = db.Column(db.Integer, db.ForeignKey('tape.id'))
    operation_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    command = db.Column(db.Text)
    stdout = db.Column(db.Text)
    stderr = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=get_shanghai_now)


class SystemError(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text)
    endpoint = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_shanghai_now)


class FileTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.String(100), unique=True, nullable=False)
    source_path = db.Column(db.Text, nullable=False)
    target_path = db.Column(db.Text, nullable=False)
    transfer_type = db.Column(db.String(20), nullable=False)
    transfer_direction = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    total_size = db.Column(db.BigInteger, default=0)
    transferred_size = db.Column(db.BigInteger, default=0)
    file_count = db.Column(db.Integer, default=0)
    current_file = db.Column(db.Text)
    progress = db.Column(db.Float, default=0.0)
    average_speed = db.Column(db.Float)
    file_list = db.Column(db.Text)
    directory_structure = db.Column(db.Text)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_shanghai_now)
    updated_at = db.Column(db.DateTime, default=get_shanghai_now, onupdate=get_shanghai_now)
