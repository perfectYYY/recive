from flask import Flask, render_template  
from flask_cors import CORS  
from .extensions import db, migrate, ma  
from .config import Config  
from .views import drone_bp  

def create_app(config_class=Config):  
    """  
    应用工厂函数  
    
    :param config_class: 配置类  
    :return: Flask应用实例  
    """  
    app = Flask(__name__)  
    
    # 加载配置  
    app.config.from_object(config_class)  
    
    # 初始化扩展  
    db.init_app(app)  
    migrate.init_app(app, db)  
    ma.init_app(app)  
    
    # 添加CORS支持  
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
    
    # 注册蓝图  
    app.register_blueprint(drone_bp, url_prefix='/api/drone')  
    
    # 添加根路由  
    @app.route('/')  
    def index():  
        """  
        首页路由  
        """  
        return render_template('index.html')  
    
    # 错误处理  
    @app.errorhandler(404)  
    def page_not_found(e):  
        """  
        404 错误处理  
        """  
        return render_template('404.html'), 404  
    
    return app