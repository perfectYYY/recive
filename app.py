from flask import Flask  
from flask_cors import CORS  
from routes import drone_routes  
from database import init_db  

app = Flask(__name__)  
CORS(app)  

# 初始化数据库  
init_db()  

app.register_blueprint(drone_routes)  

if __name__ == '__main__':  
    app.run(debug=True, port=5001, host='0.0.0.0')  