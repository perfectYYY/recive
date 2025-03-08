import os  
from datetime import timedelta  

# 获取项目根目录  
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

class Config:  
    """  
    应用配置  
    """  
    # 基础配置  
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'  
    
    # SQLite 数据库配置   
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, '..', 'drone_data.db')  
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    
    # JWT配置  
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)  
    
    # 加密配置  
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or \
        b'your-32-byte-base64-encoded-key'  
    
    # 安全配置  
    ALLOWED_DEVICES = [  
        'drone_001',   
        'drone_002',   
        # 添加更多允许的设备ID  
    ]