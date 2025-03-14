import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from ..models.user import User

def generate_token(user_id, expires_delta=None):
    """
    生成JWT令牌
    """
    if not expires_delta:
        expires_delta = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + expires_delta
    }
    
    return jwt.encode(
        payload, 
        current_app.config['JWT_SECRET_KEY'], 
        algorithm='HS256'
    )

def decode_token(token):
    """
    解码JWT令牌
    """
    try:
        payload = jwt.decode(
            token, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    令牌验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从请求头获取令牌
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        
        if not token:
            return jsonify({
                'message': '认证令牌缺失',
                'status': 'error'
            }), 401
        
        # 解码令牌
        payload = decode_token(token)
        
        if payload is None:
            return jsonify({
                'message': '无效或已过期的令牌',
                'status': 'error'
            }), 401
        
        # 查找用户
        current_user = User.query.get(payload['user_id'])
        
        if not current_user:
            return jsonify({
                'message': '用户不存在',
                'status': 'error'
            }), 401
        
        # 在请求上下文中保存当前用户
        request.current_user = current_user
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_device_token(device_id):
    """
    为设备生成令牌
    """
    payload = {
        'device_id': device_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    
    return jwt.encode(
        payload, 
        current_app.config['SECRET_KEY'], 
        algorithm='HS256'
    )
