import os
from datetime import datetime
from flask import Blueprint, request, jsonify  
from flask_cors import cross_origin  
from .models import DroneData, DroneDataSchema, DroneDataPayload  
from .extensions import db  
from .security import verify_device_token  
from .config import Config  

drone_bp = Blueprint('drone', __name__)  
drone_schema = DroneDataSchema()  
drones_schema = DroneDataSchema(many=True)  

@drone_bp.route('/data', methods=['POST'])  
@cross_origin()  
def receive_drone_data():  
    """  
    接收无人机数据  
    """  
    try:  
        # 获取请求数据  
        payload_data = request.get_json()  
        
        # 验证设备令牌  
        device_token = request.headers.get('Authorization')  
        device_id = verify_device_token(device_token)  
        
        # 创建数据载荷  
        payload = DroneDataPayload(  
            encrypted_data=payload_data.get('encrypted_data'),  
            device_id=device_id,  
            signature=payload_data.get('signature')  
        )  
        
        # 解密数据  
        decrypted_data = payload.decrypt(Config.ENCRYPTION_KEY)  
        
        # 创建无人机数据实例  
        drone_data = DroneData(  
            device_id=device_id,  
            **decrypted_data  
        )  
        
        # 保存到数据库  
        db.session.add(drone_data)  
        db.session.commit()  
        
        return jsonify({  
            'status': 'success',  
            'message': '数据接收成功',  
            'data_id': drone_data.id  
        }), 201  
    
    except Exception as e:  
        db.session.rollback()  
        return jsonify({  
            'status': 'error',  
            'message': str(e)  
        }), 400  


@drone_bp.route('/data/recent', methods=['GET'])  
@cross_origin()  
def get_recent_data():  
    """  
    获取最近的无人机数据  
    """  
    try:  
        # 获取最近50条数据  
        recent_data = DroneData.query.order_by(DroneData.timestamp.desc()).limit(50).all()  
        
        # 转换为字典列表  
        data_list = [drone.to_dict() for drone in recent_data]  
        
        return jsonify({  
            'status': 'success',  
            'data': data_list  
        }), 200  
    
    except Exception as e:  
        return jsonify({  
            'status': 'error',  
            'message': str(e)  
        }), 400  

@drone_bp.route('/data/device/<device_id>', methods=['GET'])  
@cross_origin()  
def get_device_data(device_id):  
    """  
    获取特定设备的数据  
    """  
    try:  
        # 获取特定设备的最近20条数据  
        device_data = DroneData.query.filter_by(device_id=device_id)\
            .order_by(DroneData.timestamp.desc())\
            .limit(20).all()  
        
        # 转换为字典列表  
        data_list = [drone.to_dict() for drone in device_data]  
        
        return jsonify({  
            'status': 'success',  
            'device_id': device_id,  
            'data': data_list  
        }), 200  
    
    except Exception as e:  
        return jsonify({  
            'status': 'error',  
            'message': str(e)  
        }), 400
    
@drone_bp.route('/health', methods=['GET'])  
@cross_origin()  
def health_check():  
    """  
    健康检查端点  
    """  
    return jsonify({  
        'status': 'healthy',  
        'message': 'Drone Data Receiver is running',  
        'timestamp': datetime.utcnow().isoformat()  
    }), 200