import os
import shutil
import threading
import uuid
import json
import time
from datetime import datetime
from app import app, db
from app.models import FileTransfer
from app.utils.command_executor import progress_tracker

class FileTransferManager:
    def __init__(self):
        self.active_transfers = {}
        self.lock = threading.Lock()

    def start_transfer(self, source_paths, target_dir, transfer_type='copy', transfer_direction='container_to_tape'):
        """
        启动文件传输任务
        :param source_paths: 源文件/目录路径列表
        :param target_dir: 目标目录
        :param transfer_type: 'copy' 或 'move'
        :param transfer_direction: 'container_to_tape' 或 'tape_to_container'
        :return: operation_id
        """
        operation_id = str(uuid.uuid4())
        
        # 收集文件列表和目录结构
        file_list = []
        directory_structure = {}
        total_size = 0
        file_count = 0
        
        for path in source_paths:
            if os.path.isfile(path):
                file_list.append(path)
                total_size += os.path.getsize(path)
                file_count += 1
            elif os.path.isdir(path):
                # 递归添加目录下的所有文件
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_list.append(file_path)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
        
        # 构建目录结构
        dir_structure = self._build_directory_structure(source_paths)
        
        # 创建数据库记录
        transfer = FileTransfer(
            operation_id=operation_id,
            source_path=','.join(source_paths),
            target_path=target_dir,
            transfer_type=transfer_type,
            transfer_direction=transfer_direction,
            status='pending',
            total_size=total_size,
            file_count=file_count,
            file_list=json.dumps(file_list),
            directory_structure=json.dumps(dir_structure)
        )
        db.session.add(transfer)
        db.session.commit()
        
        # 启动后台线程
        thread = threading.Thread(
            target=self._transfer_worker,
            args=(operation_id, source_paths, target_dir, transfer_type)
        )
        thread.daemon = True
        thread.start()
        
        with self.lock:
            self.active_transfers[operation_id] = thread
        
        return operation_id

    def _build_directory_structure(self, paths):
        """构建目录结构"""
        structure = {}
        for path in paths:
            if os.path.isfile(path):
                parent_dir = os.path.dirname(path)
                filename = os.path.basename(path)
                if parent_dir not in structure:
                    structure[parent_dir] = []
                structure[parent_dir].append(filename)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    if root not in structure:
                        structure[root] = []
                    for file in files:
                        structure[root].append(file)
        return structure

    def _transfer_worker(self, operation_id, source_paths, target_dir, transfer_type):
        """后台传输工作线程"""
        start_time = time.time()
        try:
            with app.app_context():
                transfer = FileTransfer.query.filter_by(operation_id=operation_id).first()
                if not transfer:
                    return
                
                transfer.status = 'in_progress'
                db.session.commit()
                
                transferred_size = 0
                
                for source_path in source_paths:
                    if os.path.isfile(source_path):
                        # 单个文件
                        filename = os.path.basename(source_path)
                        target_path = os.path.join(target_dir, filename)
                        
                        os.makedirs(target_dir, exist_ok=True)
                        
                        transfer.current_file = filename
                        db.session.commit()
                        
                        # 复制/移动文件（带进度）
                        if transfer_type == 'copy':
                            self._copy_file_with_progress(source_path, target_path, operation_id, transfer)
                        else:
                            self._move_file_with_progress(source_path, target_path, operation_id, transfer)
                        
                        transferred_size += os.path.getsize(target_path)
                        
                    elif os.path.isdir(source_path):
                        # 目录
                        dirname = os.path.basename(source_path)
                        target_subdir = os.path.join(target_dir, dirname)
                        
                        if transfer_type == 'copy':
                            self._copy_dir_with_progress(source_path, target_subdir, operation_id, transfer)
                        else:
                            self._move_dir_with_progress(source_path, target_subdir, operation_id, transfer)
                
                # 计算平均速度
                end_time = time.time()
                duration = end_time - start_time
                if duration > 0 and transfer.total_size > 0:
                    transfer.average_speed = (transfer.total_size / (1024 * 1024)) / duration
                
                # 传输完成
                transfer.status = 'completed'
                transfer.progress = 100.0
                transfer.transferred_size = transfer.total_size
                db.session.commit()
                
                progress_tracker.complete_operation(operation_id, True, "传输完成")
                
        except Exception as e:
            with app.app_context():
                transfer = FileTransfer.query.filter_by(operation_id=operation_id).first()
                if transfer:
                    transfer.status = 'failed'
                    transfer.error_message = str(e)
                    db.session.commit()
                
                progress_tracker.complete_operation(operation_id, False, str(e))

    def _copy_file_with_progress(self, src, dst, operation_id, transfer_obj):
        """带进度的文件复制"""
        file_size = os.path.getsize(src)
        chunk_size = 1024 * 1024
        
        with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
            copied = 0
            while True:
                chunk = f_src.read(chunk_size)
                if not chunk:
                    break
                f_dst.write(chunk)
                copied += len(chunk)
                
                transfer_obj.transferred_size += len(chunk)
                if transfer_obj.total_size > 0:
                    transfer_obj.progress = (transfer_obj.transferred_size / transfer_obj.total_size) * 100
                db.session.commit()

    def _copy_dir_with_progress(self, src, dst, operation_id, transfer_obj):
        """带进度的目录复制"""
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                self._copy_dir_with_progress(s, d, operation_id, transfer_obj)
            else:
                self._copy_file_with_progress(s, d, operation_id, transfer_obj)

    def _move_file_with_progress(self, src, dst, operation_id, transfer_obj):
        """带进度的文件移动（先复制再删除）"""
        file_size = os.path.getsize(src)
        chunk_size = 1024 * 1024
        
        with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
            copied = 0
            while True:
                chunk = f_src.read(chunk_size)
                if not chunk:
                    break
                f_dst.write(chunk)
                copied += len(chunk)
                
                transfer_obj.transferred_size += len(chunk)
                if transfer_obj.total_size > 0:
                    transfer_obj.progress = (transfer_obj.transferred_size / transfer_obj.total_size) * 100
                db.session.commit()
        
        os.remove(src)

    def _move_dir_with_progress(self, src, dst, operation_id, transfer_obj):
        """带进度的目录移动"""
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                self._move_dir_with_progress(s, d, operation_id, transfer_obj)
            else:
                self._move_file_with_progress(s, d, operation_id, transfer_obj)
        
        os.rmdir(src)

    def get_transfer_status(self, operation_id):
        """获取传输状态"""
        with app.app_context():
            transfer = FileTransfer.query.filter_by(operation_id=operation_id).first()
            if transfer:
                return {
                    'id': transfer.id,
                    'operation_id': transfer.operation_id,
                    'source_path': transfer.source_path,
                    'target_path': transfer.target_path,
                    'transfer_type': transfer.transfer_type,
                    'transfer_direction': transfer.transfer_direction,
                    'status': transfer.status,
                    'progress': transfer.progress,
                    'total_size': transfer.total_size,
                    'transferred_size': transfer.transferred_size,
                    'file_count': transfer.file_count,
                    'current_file': transfer.current_file,
                    'average_speed': transfer.average_speed,
                    'file_list': json.loads(transfer.file_list) if transfer.file_list else [],
                    'directory_structure': json.loads(transfer.directory_structure) if transfer.directory_structure else {},
                    'error_message': transfer.error_message,
                    'created_at': transfer.created_at.isoformat() if transfer.created_at else None,
                    'updated_at': transfer.updated_at.isoformat() if transfer.updated_at else None
                }
            return None

    def cancel_transfer(self, operation_id):
        """取消传输（标记状态，实际停止需要额外逻辑）"""
        with app.app_context():
            transfer = FileTransfer.query.filter_by(operation_id=operation_id).first()
            if transfer and transfer.status in ['pending', 'in_progress']:
                transfer.status = 'cancelled'
                db.session.commit()
                return True
            return False


# 全局单例
transfer_manager = FileTransferManager()
