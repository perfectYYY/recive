from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

# 数据库扩展
db = SQLAlchemy()

# 序列化扩展
ma = Marshmallow()

# 数据库迁移
migrate = Migrate()

def setup_logging(app):
    """
    配置日志系统
    """
    # 确保日志目录存在
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # 配置日志处理器
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'], 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('系统启动')

def init_extensions(app):
    """
    初始化所有扩展
    """
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "allow_headers": [
                "Content-Type", 
                "Authorization", 
                "Access-Control-Allow-Headers"
            ]
        }
    })

    # 设置日志
    setup_logging(app)
