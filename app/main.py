from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from .services.drone_service import (
    receive_drone_data_service,
    register_device_service,
    get_device_status_service,
    create_geofence_service,
    create_mission_service,
    get_battery_analytics_service,
    perform_firmware_update_service,
    retrieve_flight_logs_service,
    generate_performance_report_service,
    trigger_emergency_landing_service
)
from .utils.security import token_required

drone_bp = Blueprint('drone', __name__)

@drone_bp.route('/data', methods=['POST'])
@token_required
def receive_drone_data():
    """
    接收无人机实时数据
    """
    try:
        data = request.get_json()
        result = receive_drone_data_service(data)
        return jsonify({
            'status': 'success',
            'message': '数据接收成功',
            'data': result
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/device/register', methods=['POST'])
@token_required
def register_device():
    """
    注册新的无人机设备
    """
    try:
        data = request.get_json()
        device = register_device_service(data)
        return jsonify({
            'status': 'success',
            'device_id': device.id,
            'message': '设备注册成功'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/device/status', methods=['GET'])
@token_required
def get_device_status():
    """
    获取所有设备的实时状态
    """
    try:
        status = get_device_status_service()
        return jsonify({
            'status': 'success',
            'devices': status
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/geofence', methods=['POST'])
@token_required
def create_geofence():
    """
    创建地理围栏
    """
    try:
        data = request.get_json()
        geofence = create_geofence_service(data)
        return jsonify({
            'status': 'success',
            'geofence_id': geofence.id,
            'message': '地理围栏创建成功'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/mission/plan', methods=['POST'])
@token_required
def create_mission():
    """
    创建无人机飞行任务
    """
    try:
        data = request.get_json()
        mission = create_mission_service(data)
        return jsonify({
            'status': 'success',
            'mission_id': mission.id,
            'message': '任务创建成功'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/battery/analytics', methods=['GET'])
@token_required
def battery_analytics():
    """
    获取电池使用分析
    """
    try:
        device_id = request.args.get('device_id')
        days = request.args.get('days', 7, type=int)
        analytics = get_battery_analytics_service(device_id, days)
        return jsonify({
            'status': 'success',
            'analytics': analytics
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/firmware/update', methods=['POST'])
@token_required
def firmware_update():
    """
    固件远程更新
    """
    try:
        data = request.get_json()
        update_result = perform_firmware_update_service(data)
        return jsonify({
            'status': 'success',
            'update_status': update_result
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/logs/flight', methods=['GET'])
@token_required
def get_flight_logs():
    """
    获取飞行日志
    """
    try:
        params = {
            'device_id': request.args.get('device_id'),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date')
        }
        logs = retrieve_flight_logs_service(params)
        return jsonify({
            'status': 'success', 
            'logs': logs
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/performance/report', methods=['GET'])
@token_required
def generate_performance_report():
    """
    生成无人机性能报告
    """
    try:
        params = {
            'device_id': request.args.get('device_id'),
            'period': request.args.get('period', 'monthly')
        }
        report = generate_performance_report_service(params)
        return jsonify({
            'status': 'success',
            'report': report
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@drone_bp.route('/emergency/land', methods=['POST'])
@token_required
def emergency_land():
    """
    紧急迫降指令
    """
    try:
        data = request.get_json()
        result = trigger_emergency_landing_service(data)
        return jsonify({
            'status': 'success',
            'action': result
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
