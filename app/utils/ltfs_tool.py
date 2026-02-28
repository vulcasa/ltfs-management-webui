import os
import re
from datetime import datetime
from app.utils.command_executor import CommandExecutor


class LTFSTool:
    def __init__(self, device_path=None, mount_point=None, timeout=300):
        from config import Config
        self.device_path = device_path or Config.LTFS_DEVICE_PATH
        self.mount_point = mount_point or Config.LTFS_MOUNT_POINT
        self.timeout = timeout
        self.executor = CommandExecutor(timeout)
    
    def mount(self):
        os.makedirs(self.mount_point, exist_ok=True)
        
        command = f"ltfs -o devname={self.device_path} {self.mount_point}"
        return_code, stdout, stderr = self.executor.execute(command)
        
        if return_code == 0:
            barcode = self._get_barcode(stdout, stderr)
            return {
                'success': True,
                'barcode': barcode,
                'message': '磁带挂载成功',
                'stdout': stdout,
                'stderr': stderr
            }
        else:
            return {
                'success': False,
                'message': f'磁带挂载失败: {stderr or stdout}',
                'stdout': stdout,
                'stderr': stderr
            }
    
    def unmount(self):
        command = f"umount {self.mount_point}"
        return_code, stdout, stderr = self.executor.execute(command)
        
        if return_code == 0:
            return {
                'success': True,
                'message': '磁带卸载成功',
                'stdout': stdout,
                'stderr': stderr
            }
        else:
            return {
                'success': False,
                'message': f'磁带卸载失败: {stderr or stdout}',
                'stdout': stdout,
                'stderr': stderr
            }
    
    def eject(self):
        command = f"ltfs -o devname={self.device_path} -o release_device"
        return_code, stdout, stderr = self.executor.execute(command)
        
        if return_code == 0:
            return {
                'success': True,
                'message': '磁带弹出成功',
                'stdout': stdout,
                'stderr': stderr
            }
        else:
            return {
                'success': False,
                'message': f'磁带弹出失败: {stderr or stdout}',
                'stdout': stdout,
                'stderr': stderr
            }
    
    def get_device_list(self):
        command = "ltfs -o device_list"
        return_code, stdout, stderr = self.executor.execute(command)
        
        if return_code == 0:
            devices = self._parse_device_list(stdout)
            return {
                'success': True,
                'devices': devices,
                'stdout': stdout,
                'stderr': stderr
            }
        else:
            return {
                'success': False,
                'message': f'获取设备列表失败: {stderr or stdout}',
                'stdout': stdout,
                'stderr': stderr
            }
    
    def get_device_info(self):
        command = f"ltfs -o devname={self.device_path} -o device_info"
        return_code, stdout, stderr = self.executor.execute(command)
        
        if return_code == 0:
            info = self._parse_device_info(stdout)
            return {
                'success': True,
                'info': info,
                'stdout': stdout,
                'stderr': stderr
            }
        else:
            return {
                'success': False,
                'message': f'获取设备信息失败: {stderr or stdout}',
                'stdout': stdout,
                'stderr': stderr
            }
    
    def check_device_exists(self):
        if os.path.exists(self.device_path):
            return {
                'success': True,
                'device_exists': True,
                'device_path': self.device_path
            }
        else:
            return {
                'success': True,
                'device_exists': False,
                'device_path': self.device_path
            }
    
    def check_mount_status(self):
        if os.path.ismount(self.mount_point):
            return {
                'success': True,
                'mounted': True,
                'mount_point': self.mount_point
            }
        else:
            return {
                'success': True,
                'mounted': False,
                'mount_point': None
            }
    
    def _get_barcode(self, stdout=None, stderr=None):
        try:
            # 方式1: 优先从LTFS命令输出中解析barcode
            if stdout or stderr:
                output = (stdout or '') + '\n' + (stderr or '')
                barcode = self._parse_barcode_from_output(output)
                if barcode:
                    return barcode
            
            # 方式2: 从磁带的 .volume_label 文件读取
            label_file = os.path.join(self.mount_point, '.volume_label')
            if os.path.exists(label_file):
                with open(label_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return content
            
            # 方式3: 从设备信息的 serial_number 获取
            device_info = self.get_device_info()
            if device_info['success'] and 'serial_number' in device_info['info']:
                return device_info['info']['serial_number']
        except:
            pass
        
        return 'UNKNOWN'
    
    def _parse_barcode_from_output(self, output):
        """从LTFS命令输出中解析barcode"""
        if not output:
            return None
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 格式0: 优先匹配 LTFS输出的 Tape attribute: Barcode = FB1186 格式
            match = re.search(r'Tape attribute:\s*Barcode\s*=\s*([A-Z0-9]+)', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # 格式1: barcode: ABC123 或 Barcode: ABC123
            match = re.search(r'(?:barcode|Barcode|BARCODE)\s*[:=]\s*([A-Z0-9]+)', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # 格式2: Volume Label: ABC123 或 VOLUME: ABC123
            match = re.search(r'(?:Volume|volume|VOLUME)\s*(?:Label|label|LABEL)?\s*[:=]\s*([A-Z0-9]+)', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # 格式3: 直接匹配 2-4位字母 + 3-8位数字的组合（常见的磁带barcode格式）
            # 注意：排除以 LTFS/TAPE/VOLUME 开头的单词，避免误匹配 LTFS9015W 这类字符串
            # 但允许包含这些关键字的行（如 "1c LTFS17227I Tape attribute: Barcode = FB1186"）
            match = re.search(r'\b(?<!LTFS)(?<!TAPE)(?<!VOLUME)([A-Z]{2,4}[0-9]{3,8})\b', line, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_device_list(self, stdout):
        devices = []
        lines = stdout.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('ltfs'):
                match = re.search(r'(/dev/sg\d+)', line)
                if match:
                    devices.append({
                        'path': match.group(1),
                        'model': 'Unknown',
                        'serial_number': 'Unknown',
                        'firmware_version': 'Unknown'
                    })
        return devices if devices else [{
            'path': self.device_path,
            'model': 'HP LTO-6 Drive',
            'serial_number': 'UNKNOWN',
            'firmware_version': '1.00'
        }]
    
    def _parse_device_info(self, stdout):
        info = {
            'model': 'HP LTO-6 Drive',
            'serial_number': 'UNKNOWN',
            'firmware_version': '1.00'
        }
        
        lines = stdout.split('\n')
        for line in lines:
            line = line.strip()
            if 'Model' in line or 'model' in line:
                match = re.search(r':\s*(.+)$', line)
                if match:
                    info['model'] = match.group(1).strip()
            elif 'Serial' in line or 'serial' in line:
                match = re.search(r':\s*(.+)$', line)
                if match:
                    info['serial_number'] = match.group(1).strip()
            elif 'Firmware' in line or 'firmware' in line:
                match = re.search(r':\s*(.+)$', line)
                if match:
                    info['firmware_version'] = match.group(1).strip()
        
        return info
    
    def scan_filesystem(self):
        if not os.path.ismount(self.mount_point):
            return {
                'success': False,
                'message': '磁带未挂载'
            }
        
        directories = []
        files = []
        
        for root, dirs, filenames in os.walk(self.mount_point):
            relative_root = os.path.relpath(root, self.mount_point)
            if relative_root == '.':
                relative_root = ''
            
            if relative_root != '' and not relative_root.startswith('.'):
                directories.append({
                    "path": relative_root,
                    "name": os.path.basename(root),
                    "parent": os.path.dirname(relative_root)
                })
            
            for filename in filenames:
                if not filename.startswith('.'):
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.join(relative_root, filename)
                    stat_info = os.stat(file_path)
                    
                    files.append({
                        "path": relative_path,
                        "name": filename,
                        "size": stat_info.st_size,
                        "mtime": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "atime": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                        "ctime": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "barcode": self._get_barcode()
                    })
        
        return {
            'success': True,
            'directories': directories,
            'files': files,
            'dir_count': len(directories),
            'file_count': len(files),
            'total_size': sum(f['size'] for f in files)
        }
