import jwt  
from flask import current_app, abort  
from .config import Config  
from datetime import datetime, timedelta  

def generate_device_token(device_id):  
    """  
    生成设备令牌  
    
    :param device_id: 设备ID  
    :return: JWT令牌  
    """  
    # 检查设备是否在允许列表  
    if device_id not in Config.ALLOWED_DEVICES:  
        raise ValueError("未授权的设备")  
    
    # 生成JWT  
    payload = {  
        'device_id': device_id,  
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES  
    }  
    
    return jwt.encode(  
        payload,   
        Config.JWT_SECRET_KEY,   
        algorithm='HS256'  
    )  

def verify_device_token(token):  
    """  
    验证设备令牌  
    
    :param token: JWT令牌  
    :return: 设备ID  
    """  
    if not token:  
        abort(401, description="缺少认证令牌")  
    
    try:  
        # 解码令牌  
        payload = jwt.decode(  
            token,   
            Config.JWT_SECRET_KEY,   
            algorithms=['HS256']  
        )  
        
        # 返回设备ID  
        return payload['device_id']  
    
    except jwt.ExpiredSignatureError:  
        abort(401, description="令牌已过期")  
    except jwt.InvalidTokenError:  
        abort(401, description="无效的令牌")