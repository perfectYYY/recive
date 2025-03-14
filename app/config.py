import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///drone_management.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # 安全配置
    ALLOWED_DEVICES = ['device_001', 'device_002']
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 文件上传限制

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'

    # 系统配置
    DRONE_MAX_FLIGHT_ALTITUDE = 120  # 米
    DRONE_MAX_SPEED = 20  # m/s
