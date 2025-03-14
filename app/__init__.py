from flask import Flask
from .extensions import db, ma, migrate
from .config import Config

def create_app(config_object=Config):
    """
    应用工厂函数
    
    :param config_object: 配置对象，默认使用 Config
    :return: Flask 应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_object)
    
    # 初始化扩展
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图（如果有）
    # 例如：
    # from .api.drone import drone_bp
    # app.register_blueprint(drone_bp, url_prefix='/api/drone')
    
    # 可选：创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
