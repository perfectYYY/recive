from flask import Flask, render_template  
from flask_cors import CORS  
from routes import drone_routes  
from database import init_db  

app = Flask(__name__, static_folder='static', template_folder='templates')  
CORS(app)  

# 初始化数据库  
init_db()  

# 注册API路由  
app.register_blueprint(drone_routes)  

# 添加前端页面路由  
@app.route('/')  
def index():  
    return render_template('index.html')  

@app.route('/dashboard')  
def dashboard():  
    return render_template('dashboard.html')  

@app.route('/logs')  
def logs():  
    return render_template('logs.html')  

if __name__ == '__main__':  
    app.run(debug=True, port=5001, host='0.0.0.0')  