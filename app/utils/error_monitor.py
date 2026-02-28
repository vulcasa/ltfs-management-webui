import traceback
from datetime import datetime
import pytz
from flask import request
from app import db
from app.models import SystemError

# 上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

def get_shanghai_now():
    """获取当前上海时区时间（不带时区信息）"""
    return datetime.now(SHANGHAI_TZ).replace(tzinfo=None)


class ErrorMonitor:
    def __init__(self):
        pass
    
    def record_error(self, error, severity='error', endpoint=None):
        """记录错误"""
        error_type = type(error).__name__
        message = str(error)
        stack_trace = traceback.format_exc()
        
        system_error = SystemError(
            error_type=error_type,
            severity=severity,
            message=message,
            stack_trace=stack_trace,
            endpoint=endpoint or (request.path if request else None),
            user_agent=(request.user_agent.string if request and request.user_agent else None),
            ip_address=(request.remote_addr if request else None)
        )
        
        db.session.add(system_error)
        db.session.commit()
        
        if severity == 'critical':
            self._trigger_alert(system_error)
        
        return system_error
    
    def _trigger_alert(self, error):
        """触发报警（可选实现）"""
        pass
    
    def get_errors(self, severity=None, resolved=None, limit=100):
        """获取错误列表"""
        query = SystemError.query
        
        if severity:
            query = query.filter_by(severity=severity)
        
        if resolved is not None:
            query = query.filter_by(resolved=resolved)
        
        return query.order_by(SystemError.created_at.desc()).limit(limit).all()
    
    def mark_resolved(self, error_id):
        """标记错误为已解决"""
        error = SystemError.query.get(error_id)
        if error:
            error.resolved = True
            error.resolved_at = get_shanghai_now()
            db.session.commit()
        return error
    
    def get_error_stats(self):
        """获取错误统计"""
        from sqlalchemy import func
        
        stats = db.session.query(
            SystemError.severity,
            func.count(SystemError.id)
        ).group_by(SystemError.severity).all()
        
        return {s[0]: s[1] for s in stats}


error_monitor = ErrorMonitor()
