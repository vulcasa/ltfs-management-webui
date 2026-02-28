from flask import render_template, jsonify, request
import os
import uuid
import pytz
from app import app, db
from app.models import Tape, File, Directory, Operation, SystemError
from config import Config
from datetime import datetime
from app.utils.command_executor import progress_tracker
from app.utils.error_monitor import error_monitor
from app.utils.ltfs_tool import LTFSTool as LTFSProvider

# 上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

def get_shanghai_now():
    """获取当前上海时区时间"""
    return datetime.now(SHANGHAI_TZ).replace(tzinfo=None)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    # 统计数据
    tape_count = Tape.query.count()
    file_count = File.query.count()
    mounted_count = Tape.query.filter_by(status='mounted').count()
    
    # 计算总容量
    total_capacity = 0
    tapes = Tape.query.all()
    for tape in tapes:
        if tape.capacity:
            # 简化计算：假设容量格式为 "XTB" 或 "XGB"
            if 'TB' in tape.capacity:
                total_capacity += float(tape.capacity.replace('TB', '')) * 1024 * 1024 * 1024 * 1024
            elif 'GB' in tape.capacity:
                total_capacity += float(tape.capacity.replace('GB', '')) * 1024 * 1024 * 1024
            elif 'MB' in tape.capacity:
                total_capacity += float(tape.capacity.replace('MB', '')) * 1024 * 1024
    
    # 格式化总容量
    if total_capacity >= 1024 * 1024 * 1024 * 1024:
        formatted_capacity = f"{total_capacity / (1024 * 1024 * 1024 * 1024):.1f}TB"
    elif total_capacity >= 1024 * 1024 * 1024:
        formatted_capacity = f"{total_capacity / (1024 * 1024 * 1024):.1f}GB"
    elif total_capacity >= 1024 * 1024:
        formatted_capacity = f"{total_capacity / (1024 * 1024):.1f}MB"
    else:
        formatted_capacity = f"{total_capacity} Bytes"
    
    return render_template('index.html', 
                         tape_count=tape_count, 
                         file_count=file_count, 
                         mounted_count=mounted_count, 
                         total_capacity=formatted_capacity)

@app.route('/tapes')
def tapes():
    tapes = Tape.query.all()
    return render_template('tapes.html', tapes=tapes)

@app.route('/files')
def files():
    search = request.args.get('search', '')
    if search:
        files = File.query.filter(File.name.ilike(f'%{search}%')).all()
    else:
        files = File.query.all()
    return render_template('files.html', files=files)

@app.route('/logs')
def logs():
    operations = Operation.query.order_by(Operation.timestamp.desc()).limit(1000).all()
    return render_template('logs.html', operations=operations)

@app.route('/backup')
def backup():
    return render_template('backup.html')


@app.route('/errors')
def errors():
    return render_template('errors.html')

@app.route('/api/tapes', methods=['GET'])
def api_tapes():
    tapes = Tape.query.all()
    return jsonify([{
        'id': t.id,
        'barcode': t.barcode,
        'label': t.label,
        'status': t.status,
        'capacity': t.capacity,
        'used_space': t.used_space
    } for t in tapes])

@app.route('/api/tape/mount', methods=['POST'])
def api_mount_tape():
    """挂载磁带"""
    try:
        operation_id = str(uuid.uuid4())
        progress_tracker.start_operation(operation_id, 'mount')
        
        ltfs = LTFSProvider()
        
        if hasattr(ltfs, 'mount') and callable(getattr(ltfs, 'mount')):
            import inspect
            sig = inspect.signature(ltfs.mount)
            if 'operation_id' in [param.name for param in sig.parameters.values()]:
                result = ltfs.mount(operation_id=operation_id)
            else:
                result = ltfs.mount()
        else:
            result = ltfs.mount()
        
        if result['success']:
            # 检查磁带是否已存在
            tape = Tape.query.filter_by(barcode=result['barcode']).first()
            
            if not tape:
                tape = Tape(
                    barcode=result['barcode'],
                    label=f"磁带 {result['barcode']}",
                    status='mounted',
                    capacity="2.5TB",
                    used_space="0GB"
                )
                db.session.add(tape)
            else:
                tape.status = 'mounted'
            
            # 添加操作记录
            op = Operation(
                tape_id=tape.id,
                operation_type='mount',
                status='success',
                message=result['message'],
                command=result.get('command'),
                stdout=result.get('stdout'),
                stderr=result.get('stderr')
            )
            db.session.add(op)
            db.session.commit()
            
            progress_tracker.complete_operation(operation_id, True, result['message'])
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'operation_id': operation_id,
                'tape': {
                    'id': tape.id,
                    'barcode': tape.barcode,
                    'status': tape.status
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '挂载失败')
            }), 400
            
    except Exception as e:
        # 添加错误操作记录
        op = Operation(
            operation_type='mount',
            status='error',
            message=str(e)
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/tape/unmount', methods=['POST'])
def api_unmount_tape():
    """卸载磁带"""
    try:
        data = request.get_json()
        tape_id = data.get('tape_id')
        
        ltfs = LTFSProvider()
        result = ltfs.unmount()
        
        if result['success']:
            if tape_id:
                tape = Tape.query.get(tape_id)
                if tape:
                    tape.status = 'unmounted'
                    db.session.commit()
            else:
                # 如果没有指定磁带ID，检查是否有已挂载的磁带
                mounted_tape = Tape.query.filter_by(status='mounted').first()
                if mounted_tape:
                    mounted_tape.status = 'unmounted'
                    db.session.commit()
            
            # 添加操作记录
            tape = Tape.query.filter_by(status='unmounted').order_by(Tape.updated_at.desc()).first()
            op = Operation(
                tape_id=tape.id if tape else None,
                operation_type='unmount',
                status='success',
                message=result['message'],
                command=result.get('command'),
                stdout=result.get('stdout'),
                stderr=result.get('stderr')
            )
            db.session.add(op)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '卸载失败')
            }), 400
            
    except Exception as e:
        op = Operation(
            operation_type='unmount',
            status='error',
            message=str(e)
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/tape/eject', methods=['POST'])
def api_eject_tape():
    """弹出磁带"""
    try:
        data = request.get_json()
        tape_id = data.get('tape_id')
        
        ltfs = LTFSProvider()
        result = ltfs.eject()
        
        if result['success']:
            if tape_id:
                tape = Tape.query.get(tape_id)
                if tape:
                    tape.status = 'ejected'
                    db.session.commit()
            else:
                # 如果没有指定磁带ID，检查是否有已挂载的磁带
                mounted_tape = Tape.query.filter_by(status='mounted').first()
                if mounted_tape:
                    mounted_tape.status = 'ejected'
                    db.session.commit()
            
            # 添加操作记录
            tape = Tape.query.filter_by(status='ejected').order_by(Tape.updated_at.desc()).first()
            op = Operation(
                tape_id=tape.id if tape else None,
                operation_type='eject',
                status='success',
                message=result['message'],
                command=result.get('command'),
                stdout=result.get('stdout'),
                stderr=result.get('stderr')
            )
            db.session.add(op)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '弹出失败')
            }), 400
            
    except Exception as e:
        op = Operation(
            operation_type='eject',
            status='error',
            message=str(e)
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/tape/device-info', methods=['GET'])
def api_device_info():
    """获取磁带设备信息"""
    try:
        ltfs = LTFSProvider()
        info = ltfs.get_device_info()
        
        return jsonify({
            'success': True,
            'info': info['info']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/tape/device-list', methods=['GET'])
def api_device_list():
    """获取设备列表"""
    try:
        ltfs = LTFSProvider()
        devices = ltfs.get_device_list()
        
        return jsonify({
            'success': True,
            'devices': devices['devices']
        })
    except Exception as e:
        op = Operation(
            operation_type='device_list',
            status='error',
            message=str(e)
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/tape/filesystem', methods=['GET'])
def api_scan_filesystem():
    """扫描磁带文件系统"""
    try:
        ltfs = LTFSProvider()
        result = ltfs.scan_filesystem()
        
        if result['success']:
            # 保存到数据库
            with app.app_context():
                # 找到当前已挂载的磁带
                tape = Tape.query.filter_by(status='mounted').first()
                if not tape:
                    return jsonify({
                        'success': False,
                        'message': '没有已挂载的磁带，请先挂载磁带'
                    }), 400
                
                # 清理现有的目录和文件记录
                Directory.query.filter_by(tape_id=tape.id).delete()
                File.query.filter_by(tape_id=tape.id).delete()
                
                # 创建所有目录，并查找或创建对应的父目录（统合目录结构）
                dir_map = {}
                
                # 先处理所有目录，建立映射关系
                for dir_info in result['directories']:
                    # 检查是否已存在相同路径的目录（来自其他磁带）
                    existing_dir = Directory.query.filter_by(path=dir_info['path']).first()
                    
                    if existing_dir:
                        # 目录已存在，复用
                        dir_map[dir_info['path']] = existing_dir.id
                    else:
                        # 目录不存在，创建新的
                        directory = Directory(
                            tape_id=tape.id,
                            name=dir_info['name'],
                            path=dir_info['path']
                        )
                        
                        # 查找父目录
                        parent_path = os.path.dirname(dir_info['path'])
                        if parent_path == '':
                            # 根目录
                            directory.parent_id = None
                        else:
                            # 查找父目录
                            parent_dir = Directory.query.filter_by(path=parent_path).first()
                            if parent_dir:
                                directory.parent_id = parent_dir.id
                            else:
                                # 如果父目录不存在，设为根目录
                                directory.parent_id = None
                        
                        db.session.add(directory)
                        db.session.flush()
                        dir_map[dir_info['path']] = directory.id
                
                db.session.commit()
                
                # 保存文件信息
                for file_info in result['files']:
                    # 获取目录ID
                    dir_path = os.path.dirname(file_info['path'])
                    if dir_path == '':
                        # 根目录文件
                        # 查找或创建根目录
                        root_dir = Directory.query.filter_by(path='').first()
                        if not root_dir:
                            root_dir = Directory(
                                tape_id=tape.id,
                                name='根目录',
                                path=''
                            )
                            root_dir.parent_id = None
                            db.session.add(root_dir)
                            db.session.flush()
                        directory_id = root_dir.id
                    else:
                        # 其他目录，查找对应的Directory
                        parent_dir = Directory.query.filter_by(path=dir_path).first()
                        directory_id = parent_dir.id if parent_dir else None
                        
                        if not directory_id:
                            # 如果目录不存在，使用根目录
                            root_dir = Directory.query.filter_by(path='').first()
                            directory_id = root_dir.id if root_dir else None
                    
                    file_obj = File(
                        tape_id=tape.id,
                        directory_id=directory_id,
                        name=file_info['name'],
                        size=file_info['size'],
                        mtime=datetime.fromisoformat(file_info['mtime']),
                        atime=datetime.fromisoformat(file_info['atime']),
                        ctime=datetime.fromisoformat(file_info['ctime'])
                    )
                    db.session.add(file_obj)
                
                # 更新磁带的已使用空间
                total_size = result['total_size']
                if total_size >= 1024 * 1024 * 1024 * 1024:
                    tape.used_space = f"{total_size / (1024 * 1024 * 1024 * 1024):.1f}TB"
                elif total_size >= 1024 * 1024 * 1024:
                    tape.used_space = f"{total_size / (1024 * 1024 * 1024):.1f}GB"
                elif total_size >= 1024 * 1024:
                    tape.used_space = f"{total_size / (1024 * 1024):.1f}MB"
                elif total_size >= 1024:
                    tape.used_space = f"{total_size / 1024:.1f}KB"
                else:
                    tape.used_space = f"{total_size} Bytes"
                
                db.session.commit()
                
                # 添加操作记录
                op = Operation(
                    tape_id=tape.id,
                    operation_type='scan_filesystem',
                    status='success',
                    message=f'扫描完成: {result["dir_count"]}个目录, {result["file_count"]}个文件'
                )
                db.session.add(op)
                db.session.commit()
        
            return jsonify({
                'success': True,
                'directories': result['directories'],
                'files': result['files'],
                'dir_count': result['dir_count'],
                'file_count': result['file_count'],
                'total_size': result['total_size']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        op = Operation(
            operation_type='scan_filesystem',
            status='error',
            message=str(e)
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/directories', methods=['GET'])
def api_get_directories():
    """获取目录树结构"""
    try:
        tape_id = request.args.get('tape_id', type=int)
        parent_id = request.args.get('parent_id', type=int)
        
        query = Directory.query
        
        if tape_id:
            query = query.filter_by(tape_id=tape_id)
        
        if parent_id is not None:
            query = query.filter_by(parent_id=parent_id)
        
        directories = query.all()
        
        result = []
        for dir in directories:
            # 检查是否有子目录
            has_children = Directory.query.filter_by(parent_id=dir.id).first() is not None
            
            result.append({
                'id': dir.id,
                'name': dir.name,
                'path': dir.path,
                'parent_id': dir.parent_id,
                'has_children': has_children,
                'tape_id': dir.tape_id
            })
        
        return jsonify({
            'success': True,
            'directories': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files', methods=['GET'])
def api_get_files():
    """获取文件列表"""
    try:
        # 获取查询参数
        tape_id = request.args.get('tape_id', type=int)
        directory_id = request.args.get('directory_id', type=int)
        search = request.args.get('search', '')
        
        query = File.query
        
        if tape_id:
            query = query.filter_by(tape_id=tape_id)
        
        if directory_id:
            query = query.filter_by(directory_id=directory_id)
        
        if search:
            query = query.filter(File.name.ilike(f'%{search}%'))
        
        files = query.all()
        
        result = []
        for file in files:
            # 获取文件路径
            file_path = '/'
            if file.directory:
                if file.directory.path:
                    file_path = '/' + file.directory.path
            file_path = file_path + '/' + file.name
            
            result.append({
                'id': file.id,
                'name': file.name,
                'size': file.size,
                'mtime': file.mtime.isoformat() if file.mtime else None,
                'atime': file.atime.isoformat() if file.atime else None,
                'ctime': file.ctime.isoformat() if file.ctime else None,
                'tape_id': file.tape_id,
                'directory_id': file.directory_id,
                'tape_barcode': Tape.query.get(file.tape_id).barcode if file.tape_id else None,
                'file_path': file_path
            })
        
        return jsonify({
            'success': True,
            'files': result,
            'count': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/tape/current', methods=['GET'])
def api_get_current_tape():
    """获取当前磁带状态"""
    try:
        # 优先返回已挂载的磁带
        tape = Tape.query.filter_by(status='mounted').first()
        if not tape:
            # 如果没有已挂载的，返回状态不是 ejected 的最新磁带
            tape = Tape.query.filter(Tape.status != 'ejected').order_by(Tape.updated_at.desc()).first()
            
        if tape:
            return jsonify({
                'success': True,
                'tape': {
                    'id': tape.id,
                    'barcode': tape.barcode,
                    'status': tape.status,
                    'capacity': tape.capacity,
                    'used_space': tape.used_space
                }
            })
        else:
            # 所有磁带都是 ejected 或没有磁带，返回失败
            return jsonify({
                'success': False,
                'message': '无磁带信息'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/tape/device-status', methods=['GET'])
def api_device_status():
    """获取磁带设备状态"""
    try:
        ltfs = LTFSProvider()
        device_status = ltfs.check_device_exists()
        
        return jsonify({
            'success': True,
            'device_exists': device_status.get('device_exists', False),
            'device_path': device_status.get('device_path')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/backup/create', methods=['POST'])
def api_create_backup():
    """创建数据库备份"""
    import os
    import shutil
    from datetime import datetime
    
    try:
        # 确保备份目录存在
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名（带时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'tape_backup_{timestamp}.db')
        
        # 复制数据库文件
        db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tape_metadata.db')
        shutil.copy2(db_file, backup_file)
        
        # 获取备份文件信息
        file_size = os.path.getsize(backup_file)
        
        # 添加操作记录
        op = Operation(
            operation_type='backup',
            status='success',
            message=f'创建备份: tape_backup_{timestamp}.db ({file_size} bytes)'
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '备份创建成功',
            'backup_file': f'tape_backup_{timestamp}.db',
            'file_size': file_size
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/backup/list', methods=['GET'])
def api_list_backups():
    """获取备份文件列表"""
    import os
    from datetime import datetime
    
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        # 按创建时间倒序排序
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'backups': backups,
            'count': len(backups)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/backup/download/<filename>', methods=['GET'])
def api_download_backup(filename):
    """下载备份文件"""
    from flask import send_file
    import os
    
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': '备份文件不存在'
            }), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/backup/restore', methods=['POST'])
def api_restore_backup():
    """恢复数据库备份"""
    import os
    import shutil
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'message': '请指定备份文件'
            }), 400
        
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        backup_file = os.path.join(backup_dir, filename)
        
        if not os.path.exists(backup_file):
            return jsonify({
                'success': False,
                'message': '备份文件不存在'
            }), 404
        
        # 先备份当前数据库
        import time
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tape_metadata.db')
        current_backup = os.path.join(backup_dir, f'current_backup_{timestamp}.db')
        shutil.copy2(db_file, current_backup)
        
        # 恢复备份
        shutil.copy2(backup_file, db_file)
        
        # 添加操作记录
        op = Operation(
            operation_type='restore',
            status='success',
            message=f'恢复备份: {filename}'
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '备份恢复成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def calculate_sha256(filepath):
    """计算文件的SHA-256哈希值"""
    import hashlib
    
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


@app.route('/api/backup/upload', methods=['POST'])
def api_upload_backup():
    """上传备份文件并恢复"""
    import os
    import shutil
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        verify = request.form.get('verify', 'true') == 'true'
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '未选择文件'
            }), 400
        
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uploaded_filename = f'uploaded_{timestamp}_{file.filename}'
        uploaded_filepath = os.path.join(backup_dir, uploaded_filename)
        
        file.save(uploaded_filepath)
        
        if verify:
            file_hash = calculate_sha256(uploaded_filepath)
            if not file_hash:
                os.remove(uploaded_filepath)
                return jsonify({
                    'success': False,
                    'message': '文件校验失败'
                }), 400
        
        db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tape_metadata.db')
        current_backup = os.path.join(backup_dir, f'current_before_restore_{timestamp}.db')
        shutil.copy2(db_file, current_backup)
        
        shutil.copy2(uploaded_filepath, db_file)
        
        op = Operation(
            operation_type='restore',
            status='success',
            message=f'从上传文件恢复: {file.filename}'
        )
        db.session.add(op)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '备份恢复成功',
            'filename': uploaded_filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/backup/verify/<filename>', methods=['GET'])
def api_verify_backup(filename):
    """验证备份文件完整性"""
    import os
    
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': '备份文件不存在'
            }), 404
        
        file_hash = calculate_sha256(filepath)
        file_size = os.path.getsize(filepath)
        
        return jsonify({
            'success': True,
            'sha256': file_hash,
            'size': file_size,
            'filename': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/backup/delete/<filename>', methods=['DELETE'])
def api_delete_backup(filename):
    """删除备份文件"""
    import os
    
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': '备份文件不存在'
            }), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': '备份文件删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/operation/progress/<operation_id>', methods=['GET'])
def api_get_operation_progress(operation_id):
    """获取操作进度"""
    try:
        progress = progress_tracker.get_progress(operation_id)
        
        if progress:
            return jsonify({
                'success': True,
                'progress': progress
            })
        else:
            return jsonify({
                'success': False,
                'message': '操作不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/operation/remove/<operation_id>', methods=['DELETE'])
def api_remove_operation(operation_id):
    """移除完成的操作"""
    try:
        progress_tracker.remove_operation(operation_id)
        return jsonify({
            'success': True,
            'message': '操作已移除'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/errors', methods=['GET'])
def api_get_errors():
    """获取错误列表"""
    try:
        severity = request.args.get('severity')
        resolved = request.args.get('resolved')
        if resolved is not None:
            resolved = resolved.lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        
        errors = error_monitor.get_errors(severity, resolved, limit)
        
        return jsonify({
            'success': True,
            'errors': [{
                'id': e.id,
                'error_type': e.error_type,
                'severity': e.severity,
                'message': e.message,
                'endpoint': e.endpoint,
                'resolved': e.resolved,
                'created_at': e.created_at.isoformat() if e.created_at else None
            } for e in errors]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/errors/<int:error_id>', methods=['GET'])
def api_get_error_detail(error_id):
    """获取错误详情"""
    try:
        error = SystemError.query.get_or_404(error_id)
        
        return jsonify({
            'success': True,
            'error': {
                'id': error.id,
                'error_type': error.error_type,
                'severity': error.severity,
                'message': error.message,
                'stack_trace': error.stack_trace,
                'endpoint': error.endpoint,
                'user_agent': error.user_agent,
                'ip_address': error.ip_address,
                'resolved': error.resolved,
                'resolved_at': error.resolved_at.isoformat() if error.resolved_at else None,
                'created_at': error.created_at.isoformat() if error.created_at else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/errors/<int:error_id>/resolve', methods=['POST'])
def api_resolve_error(error_id):
    """标记错误为已解决"""
    try:
        error_monitor.mark_resolved(error_id)
        return jsonify({
            'success': True,
            'message': '错误已标记为已解决'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/errors/stats', methods=['GET'])
def api_error_stats():
    """获取错误统计"""
    try:
        stats = error_monitor.get_error_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    error_monitor.record_error(error, severity='critical')
    db.session.rollback()
    return render_template('index.html'), 500


@app.errorhandler(Exception)
def handle_exception(error):
    error_monitor.record_error(error, severity='error')
    return jsonify({
        'success': False,
        'message': '服务器错误'
    }), 500


@app.route('/health', methods=['GET'])
@app.route('/healthz', methods=['GET'])
def health_check():
    """应用健康检查端点"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': get_shanghai_now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/ready', methods=['GET'])
@app.route('/readyz', methods=['GET'])
def readiness_check():
    """应用就绪检查端点"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'ready',
            'timestamp': get_shanghai_now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': get_shanghai_now().isoformat()
        }), 503


@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    """获取操作日志，支持分页和最新检查"""
    try:
        limit = request.args.get('limit', 1000, type=int)
        since_id = request.args.get('since_id', type=int)
        
        query = Operation.query.order_by(Operation.timestamp.desc())
        
        if since_id:
            query = query.filter(Operation.id > since_id)
        
        operations = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'operations': [{
                'id': op.id,
                'tape_id': op.tape_id,
                'tape_barcode': op.tape.barcode if op.tape else None,
                'operation_type': op.operation_type,
                'status': op.status,
                'message': op.message,
                'command': op.command,
                'stdout': op.stdout,
                'stderr': op.stderr,
                'timestamp': op.timestamp.isoformat() if op.timestamp else None
            } for op in operations],
            'count': len(operations),
            'latest_id': operations[0].id if operations else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
