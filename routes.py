from flask import Blueprint, jsonify, request  
from user_auth import UserAuthenticator  
from database import insert_drone_data  
drone_routes = Blueprint('drone_routes', __name__)  
user_authenticator = UserAuthenticator()  

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
        return jsonify({'token': token, 'message': 'Login successful', 'role': user['role']}), 200  
    else:  
        return jsonify({'message': 'Invalid credentials'}), 401  

@drone_routes.route('/drone/start', methods=['POST'])  
def start_drone():  
    return jsonify({"message": "Drone started"}), 200  

@drone_routes.route('/drone/stop', methods=['POST'])  
def stop_drone():  
    return jsonify({"message": "Drone stopped"}), 200  

@drone_routes.route('/drone/status', methods=['GET'])  
def drone_status():  
    return jsonify({"status": "Ready"}), 200  

@drone_routes.route('/drone/coordinates', methods=['GET'])  
def drone_coordinates():  
    return jsonify({"latitude": 34.0522, "longitude": -118.2437}), 200  

@drone_routes.route('/drone/send_data', methods=['POST'])  
def send_drone_data():  
    """接收无人机数据"""  
    data = request.json  
    if not data:  
        return jsonify({'message': 'Invalid request'}), 400  
    
    # 插入数据到数据库  
    insert_drone_data(data)  
    return jsonify({'message': 'Drone data received successfully'}), 200 

@drone_routes.route('/drone/receive_commands', methods=['GET'])  
def receive_commands():  
    return jsonify({"commands": ["takeoff", "land", "hover"]}), 200  

@drone_routes.route('/drone/logs', methods=['GET'])  
def logs():  
    return jsonify({"logs": ["Livestream started", "Battery 80%"]}), 200  

@drone_routes.route('/drone/battery', methods=['GET'])  
def battery_status():  
    return jsonify({"battery": "75%"}), 200  

@drone_routes.route('/drone/fly', methods=['POST'])  
def fly():  
    return jsonify({"message": "Drone is flying"}), 200  

@drone_routes.route('/drone/arrived', methods=['POST'])  
def arrived():  
    return jsonify({"message": "Drone has arrived at the destination."}), 200  