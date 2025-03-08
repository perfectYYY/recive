from app import create_app  
from app.extensions import db  
import os  

app = create_app()  

def init_db():  
    """  
    初始化数据库  
    """  
    with app.app_context():  
        # 检查数据库文件是否存在  
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')  
        if not os.path.exists(db_path):  
            print(f"正在创建数据库: {db_path}")  
            db.create_all()  
            print("数据库创建成功")  

if __name__ == '__main__':  
    init_db()  
    app.run(host='0.0.0.0', port=8000, debug=True)