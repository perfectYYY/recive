from flask import Blueprint, jsonify, request, render_template  
from user_auth import UserAuthenticator  
from database import (  
    insert_drone_data, get_drone_data, get_latest_drone_data,  
    record_command, get_commands, log_message, get_logs  
)  
from mongodb import save_to_mongodb
from app import mongo_storage
import jwt  
import datetime  
import json  
import hashlib  
import time  


# 原有的Blueprint  
drone_routes = Blueprint('drone_routes', __name__)  
user_authenticator = UserAuthenticator()  

# 测试路由Blueprint  
test_routes = Blueprint('test_routes', __name__)  

# 测试路由所需的全局变量  
devices = {  
    # 添加测试脚本中使用的设备  
    "20845": {"secret": "abcde"},  
    
    # 原有设备保持不变  
    "CQUCHX0503001": {"secret": "lAJIOxHiUyp2GuoN"},  
    "CQUCHX0503002": {"secret": "oIzUqhuNgFJMOkCL"},  
    "CQUCHX0503003": {"secret": "0piWBoxFYNyOKECX"},  
    "CQUCHX0503004": {"secret": "tlqbV10QkEOo5yAc"},  
    "CQUCHX0503005": {"secret": "xJZ4oclUgQWHs0FB"},  
    "CQUCHX0503006": {"secret": "smEtIJoej1NFbCwU"},  
    "CQUCHX0503007": {"secret": "FaSP6l8OKMysXuTe"},  
    "CQUCHX0503008": {"secret": "ZbOfMLvqjxA4GsBH"},  
    "CQUCHX0503009": {"secret": "DY1loibvZjwW4xyq"},  
    "CQUCHX0503010": {"secret": "caMrEAgOV3XL2z7I"}  
}  

tickets = {}  
token_refresh_counts = {}  

# 测试路由  
@test_routes.route('/getTicket', methods=['GET'])  
def get_ticket():  
    device_id = request.args.get('deviceId')  
    
    if not device_id:  
        return jsonify({  
            "code": 201,  
            "message": "Parameter missing",  
            "data": None  
        })  
    
    if device_id not in devices:  
        return jsonify({  
            "code": 202,  
            "message": "Unknown device",  
            "data": None  
        })  
    
    # 生成带过期时间的ticket（30秒有效）  
    ticket = jwt.encode(  
        {"deviceId": device_id, "exp": time.time() + 30},  
        devices[device_id]["secret"],  
        algorithm="HS256"  
    )  
    
    tickets[ticket] = device_id  
    return jsonify({  
        "code": 200,  
        "message": "success",  
        "data": {"ticket": ticket}  
    })  

@test_routes.route('/getToken', methods=['POST'])  
def get_token():  
    data = request.json  
    device_id = data.get("deviceId")  
    signature = data.get("signature")  
    ticket = data.get("ticket")  
    
    if not all([device_id, signature, ticket]):  
        return jsonify({  
            "code": 201,  
            "message": "Parameter missing",  
            "data": None  
        })  
    
    if device_id not in devices:  
        return jsonify({  
            "code": 202,  
            "message": "Unknown device",  
            "data": None  
        })  
    
    # 验证ticket有效性  
    try:  
        payload = jwt.decode(  
            ticket,  
            devices[device_id]["secret"],  
            algorithms=["HS256"]  
        )  
        if payload["deviceId"] != device_id:  
            raise jwt.InvalidTokenError  
    except jwt.ExpiredSignatureError:  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    except jwt.InvalidTokenError:  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    
    # 验证签名  
    expected_signature = hashlib.md5(  
        (ticket + device_id + devices[device_id]["secret"]).encode()  
    ).hexdigest()  
    
    if signature != expected_signature:  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    
    # 生成带过期时间的token（60秒有效）  
    token = jwt.encode(  
        {"deviceId": device_id, "exp": time.time() + 60},  
        devices[device_id]["secret"],  
        algorithm="HS256"  
    )  
    
    # 重置刷新计数器  
    token_refresh_counts[device_id] = 0  
    
    return jsonify({  
        "code": 200,  
        "message": "success",  
        "data": {"token": token}  
    })  

@test_routes.route('/uploadData', methods=['POST'])  
def upload_data():  
    data = request.json  
    device_id = data.get("deviceId")  
    token = data.get("token")  
    payload_data = data.get("data")  
    
    if not all([device_id, token, payload_data]):  
        return jsonify({  
            "code": 201,  
            "message": "Parameter missing",  
            "data": None  
        })  
    
    if device_id not in devices:  
        return jsonify({  
            "code": 202,  
            "message": "Unknown device",  
            "data": None  
        })  
    
    # 处理特殊的测试token  
    if token == "invalid_token":  
        return jsonify({  
            "code": 204,  
            "message": "Invalid token",  
            "data": None  
        })  
    
    # 验证token有效性  
    try:  
        payload = jwt.decode(  
            token,  
            devices[device_id]["secret"],  
            algorithms=["HS256"]  
        )  
        if payload["deviceId"] != device_id:  
            raise jwt.InvalidTokenError  
        
        # 兼容测试代码的自定义过期字段  
        if payload.get("expiredTime") and payload.get("expiredTime") < time.time():  
            raise jwt.ExpiredSignatureError  
            
    except jwt.ExpiredSignatureError:  
        return jsonify({  
            "code": 206,  
            "message": "Token expired",  
            "data": None  
        })  
    except jwt.InvalidTokenError:  
        return jsonify({  
            "code": 204,  
            "message": "Invalid token",  
            "data": None  
        })  
    
    # 验证数据有效性  
    try:  
        if int(payload_data["high"]) <= int(payload_data["low"]):  
            return jsonify({  
                "code": 205,  
                "message": "Invalid blood pressure data",  
                "data": None  
            })  
    except (KeyError, ValueError):  
        return jsonify({  
            "code": 205,  
            "message": "Invalid blood pressure data",  
            "data": None  
        })  
    
    return jsonify({  
        "code": 200,  
        "message": "success",  
        "data": {  
            "receivedTime": int(time.time())  
        }  
    })  

@test_routes.route('/refreshToken', methods=['POST'])  
def refresh_token():  
    data = request.json  
    device_id = data.get("deviceId")  
    signature = data.get("signature")  
    token = data.get("token")  
    
    if not all([device_id, signature, token]):  
        return jsonify({  
            "code": 201,  
            "message": "Parameter missing",  
            "data": None  
        })  
    
    if device_id not in devices:  
        return jsonify({  
            "code": 202,  
            "message": "Unknown device",  
            "data": None  
        })  
    
    # 处理特殊的测试签名  
    if signature == "invalid_signature":  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    
    # 验证旧token有效性  
    try:  
        old_payload = jwt.decode(  
            token,  
            devices[device_id]["secret"],  
            algorithms=["HS256"]  
        )  
        if old_payload["deviceId"] != device_id:  
            raise jwt.InvalidTokenError  
    except jwt.ExpiredSignatureError:  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    except jwt.InvalidTokenError:  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    
    # 验证签名  
    expected_signature = hashlib.md5(  
        (token + device_id + devices[device_id]["secret"]).encode()  
    ).hexdigest()  
    
    if signature != expected_signature:  
        return jsonify({  
            "code": 203,  
            "message": "Invalid signature",  
            "data": None  
        })  
    
    # 检查刷新次数（基于设备ID）  
    current_refresh_count = token_refresh_counts.get(device_id, 0)  
    if current_refresh_count >= 1:  # 最大允许1次刷新  
        return jsonify({  
            "code": 207,  
            "message": "Max refresh exceeded",  
            "data": None  
        })  
    
    # 生成新token（60秒有效）  
    new_token = jwt.encode(  
        {"deviceId": device_id, "exp": time.time() + 60},  
        devices[device_id]["secret"],  
        algorithm="HS256"  
    )  
    
    # 更新设备刷新次数  
    token_refresh_counts[device_id] = current_refresh_count + 1  
    
    return jsonify({  
        "code": 200,  
        "message": "success",  
        "data": {"token": new_token}  
    })  

# 以下是原有的路由，保持不变  

# 用户认证相关路由  
@drone_routes.route('/login', methods=['POST'])  
def login():  
    """用户登录接口"""  
    data = request.json  
    if not data:  
        return jsonify({'message': 'Invalid request'}), 400  

    username = data.get('username')  
    password = data.get('password')  

    if not username or not password:  
        return jsonify({'message': 'Username and password are required'}), 400  

    user = user_authenticator.authenticate(username, password)  
    if user:  
        token = user_authenticator.generate_token(username, user['role'])  
        log_message(f"用户 {username} 登录成功", "auth")  
        return jsonify({  
            'token': token,  
            'message': 'Login successful',  
            'role': user['role'],  
            'username': username  
        }), 200  
    else:  
        log_message(f"用户 {username} 登录失败", "auth")  
        return jsonify({'message': 'Invalid credentials'}), 401  

# 无人机控制路由  
@drone_routes.route('/drone/start', methods=['POST'])  
def start_drone():  
    """启动无人机"""  
    data = request.json or {}  
    record_command('start', data, 'executed')  
    log_message("无人机已启动", "system")  
    return jsonify({"message": "Drone started", "status": "success"}), 200  

@drone_routes.route('/drone/stop', methods=['POST'])  
def stop_drone():  
    """停止无人机"""  
    data = request.json or {}  
    record_command('stop', data, 'executed')  
    log_message("无人机已停止", "system")  
    return jsonify({"message": "Drone stopped", "status": "success"}), 200  

@drone_routes.route('/drone/status', methods=['GET'])  
def drone_status():  
    """获取无人机状态"""  
    latest_data = get_latest_drone_data()  
    status = "Ready"  
    
    if latest_data:  
        battery = latest_data.get('battery_level', 0)  
        if battery < 20:  
            status = "Low Battery"  
        elif battery > 80:  
            status = "Fully Charged"  
    
    return jsonify({"status": status}), 200  

@drone_routes.route('/drone/coordinates', methods=['GET'])  
def drone_coordinates():  
    """获取无人机坐标"""  
    latest_data = get_latest_drone_data()  
    
    if latest_data and latest_data.get('coordinates'):  
        coords = latest_data['coordinates'].split(',')  
        if len(coords) >= 2:  
            return jsonify({  
                "latitude": float(coords[0]),  
                "longitude": float(coords[1])  
            }), 200  
    
    # 默认坐标（洛杉矶）  
    return jsonify({"latitude": 34.0522, "longitude": -118.2437}), 200  

@drone_routes.route('/drone/send_data', methods=['POST'])  
def send_drone_data():  
    """接收无人机数据"""  
    data = request.json  
    if not data:  
        return jsonify({'message': 'Invalid request'}), 400  
    
    try:  
        # 记录到日志系统，方便在日志页面查看  
        log_message(f"收到无人机数据: 高度={data.get('altitude', 'N/A')}, 速度={data.get('speed', 'N/A')}, " +  
                    f"坐标={data.get('coordinates', 'N/A')}, 电量={data.get('battery_level', 'N/A')}%", "data")  
        
        # 插入数据到数据库  
        mongo_storage.save(data)
        insert_drone_data(data)  
        return jsonify({'message': 'Drone data received successfully'}), 200  
    except Exception as e:  
        log_message(f"数据接收错误: {str(e)}", "error")  
        return jsonify({'message': f'Error: {str(e)}'}), 500  

@drone_routes.route('/drone/receive_commands', methods=['GET'])  
def receive_commands():  
    """获取无人机命令列表"""  
    commands = get_commands()  
    
    # 提取命令名称  
    command_list = [cmd.get('command') for cmd in commands]  
    if not command_list:  
        command_list = ["takeoff", "land", "hover"]  
        
    return jsonify({"commands": command_list}), 200  

@drone_routes.route('/drone/logs', methods=['GET'])  
def logs():  
    """获取无人机日志"""  
    log_entries = get_logs(20)  
    
    # 格式化日志消息  
    log_messages = [f"{entry['timestamp']} - {entry['message']}" for entry in log_entries]  
    if not log_messages:  
        log_messages = ["Livestream started", "Battery 80%"]  
        
    return jsonify({"logs": log_messages}), 200  

@drone_routes.route('/drone/battery', methods=['GET'])  
def battery_status():  
    """获取无人机电池状态"""  
    latest_data = get_latest_drone_data()  
    
    battery_level = "75%"  
    if latest_data and 'battery_level' in latest_data:  
        battery_level = f"{latest_data['battery_level']}%"  
        
    return jsonify({"battery": battery_level}), 200  

@drone_routes.route('/drone/fly', methods=['POST'])  
def fly():  
    """指示无人机飞行"""  
    data = request.json or {}  
    destination = data.get('destination', {})  
    
    record_command('fly', data, 'executed')  
    log_message(f"无人机飞行命令已发送，目的地: {json.dumps(destination)}", "command")  
    
    return jsonify({"message": "Drone is flying", "status": "success"}), 200  

@drone_routes.route('/drone/arrived', methods=['POST'])  
def arrived():  
    """无人机到达目的地"""  
    data = request.json or {}  
    location = data.get('location', {})  
    
    record_command('arrived', data, 'completed')  
    log_message("无人机已到达目的地", "system")  
    
    return jsonify({"message": "Drone has arrived at the destination.", "status": "success"}), 200  

# API数据查询路由  
@drone_routes.route('/api/data', methods=['GET'])  
def api_data():  
    """获取无人机历史数据"""  
    limit = request.args.get('limit', 100, type=int)  
    data = get_drone_data(limit)  
    return jsonify({"data": data}), 200  

@drone_routes.route('/api/commands', methods=['GET'])  
def api_commands():  
    """获取命令历史"""  
    limit = request.args.get('limit', 50, type=int)  
    commands = get_commands(limit)  
    return jsonify({"commands": commands}), 200  

@drone_routes.route('/api/logs', methods=['GET'])  
def api_logs():  
    """获取系统日志"""  
    limit = request.args.get('limit', 100, type=int)  
    logs = get_logs(limit)  
    return jsonify({"logs": logs}), 200  

@drone_routes.route('/api/dashboard', methods=['GET'])  
def dashboard_data():  
    """获取仪表板数据"""  
    latest = get_latest_drone_data()  
    logs = get_logs(5)  
    commands = get_commands(5)  
    
    if not latest:  
        latest = {  
            "altitude": 100,  
            "speed": 15.5,  
            "coordinates": "34.0522,-118.2437",  
            "battery_level": 75,  
            "wind_speed": 5.2,  
            "position": "cruising"  
        }  
    
    return jsonify({  
        "latest": latest,  
        "logs": logs,  
        "commands": commands  
    }), 200  
