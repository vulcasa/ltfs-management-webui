import subprocess
import threading
import queue
import time
import pytz
from datetime import datetime

# 上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

def get_shanghai_now():
    """获取当前上海时区时间（不带时区信息）"""
    return datetime.now(SHANGHAI_TZ).replace(tzinfo=None)


class CommandExecutor:
    def __init__(self, timeout=300):
        self.timeout = timeout
        self._current_progress = 0
        self._current_message = ''
        self._progress_lock = threading.Lock()
    
    def execute(self, command, progress_callback=None):
        result_queue = queue.Queue()
        
        def run_command():
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                if progress_callback:
                    for i in range(10):
                        time.sleep(0.5)
                        progress = (i + 1) * 10
                        message = f"步骤 {i + 1}/10"
                        with self._progress_lock:
                            self._current_progress = progress
                            self._current_message = message
                        progress_callback(progress, message)
                
                stdout, stderr = process.communicate()
                return_code = process.returncode
                result_queue.put((return_code, stdout, stderr))
            except Exception as e:
                result_queue.put((1, '', str(e)))
        
        thread = threading.Thread(target=run_command)
        thread.start()
        thread.join(self.timeout)
        
        if thread.is_alive():
            return (1, '', f"命令执行超时，超过 {self.timeout} 秒")
        
        return result_queue.get()
    
    def get_current_progress(self):
        with self._progress_lock:
            return {
                'progress': self._current_progress,
                'message': self._current_message
            }
    
    def reset_progress(self):
        with self._progress_lock:
            self._current_progress = 0
            self._current_message = ''


class OperationProgressTracker:
    def __init__(self):
        self._progress = {}
        self._lock = threading.Lock()
    
    def start_operation(self, operation_id, operation_type):
        with self._lock:
            self._progress[operation_id] = {
                'type': operation_type,
                'progress': 0,
                'message': '准备中...',
                'status': 'running',
                'started_at': get_shanghai_now().isoformat(),
                'completed': False
            }
    
    def update_progress(self, operation_id, progress, message):
        with self._lock:
            if operation_id in self._progress:
                self._progress[operation_id]['progress'] = progress
                self._progress[operation_id]['message'] = message
    
    def complete_operation(self, operation_id, success, message):
        with self._lock:
            if operation_id in self._progress:
                self._progress[operation_id]['progress'] = 100 if success else 0
                self._progress[operation_id]['message'] = message
                self._progress[operation_id]['status'] = 'success' if success else 'error'
                self._progress[operation_id]['completed'] = True
                self._progress[operation_id]['completed_at'] = get_shanghai_now().isoformat()
    
    def get_progress(self, operation_id):
        with self._lock:
            return self._progress.get(operation_id)
    
    def remove_operation(self, operation_id):
        with self._lock:
            if operation_id in self._progress:
                del self._progress[operation_id]
    
    def cleanup_old_operations(self, max_age_seconds=3600):
        with self._lock:
            now = get_shanghai_now()
            to_remove = []
            for op_id, op_data in self._progress.items():
                if op_data.get('completed'):
                    completed_at = datetime.fromisoformat(op_data['completed_at'])
                    if (now - completed_at).total_seconds() > max_age_seconds:
                        to_remove.append(op_id)
            
            for op_id in to_remove:
                del self._progress[op_id]


progress_tracker = OperationProgressTracker()
