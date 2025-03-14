from app.extensions import db
from ..models.drone import (
    DroneData, 
    DroneDevice, 
    GeoFence, 
    Mission, 
    FlightLog
)
from datetime import datetime, timedelta
import uuid
import logging

def receive_drone_data_service(data):
    """
    处理无人机数据接收
    
    :param data: 无人机数据字典
    :return: 保存的数据对象
    """
    try:
        # 验证数据完整性
        required_fields = [
            'device_id', 'latitude', 'longitude', 
            'altitude', 'speed', 'battery'
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必要字段: {field}")

        # 创建无人机数据记录
        drone_data = DroneData(**data)
        
        # 更新设备最后活动时间
        device = DroneDevice.query.get(data['device_id'])
        if device:
            device.last_active = datetime.utcnow()
        
        db.session.add(drone_data)
        db.session.commit()
        
        logging.info(f"成功接收设备 {data['device_id']} 的数据")
        return drone_data.to_dict()
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"接收数据时发生错误: {str(e)}")
        raise

def register_device_service(device_data):
    """
    注册新设备
    
    :param device_data: 设备信息字典
    :return: 注册的设备对象
    """
    try:
        # 生成唯一设备ID
        device_id = str(uuid.uuid4())
        device_data['id'] = device_id
        
        # 设置默认状态
        device_data.setdefault('status', 'inactive')
        
        # 创建设备
        device = DroneDevice(**device_data)
        
        db.session.add(device)
        db.session.commit()
        
        logging.info(f"成功注册新设备: {device_id}")
        return device
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"设备注册失败: {str(e)}")
        raise

def get_device_status_service():
    """
    获取所有设备状态
    
    :return: 设备状态列表
    """
    try:
        devices = DroneDevice.query.all()
        
        # 包括最近的数据
        device_statuses = []
        for device in devices:
            status = device.to_dict()
            
            # 获取最近的数据
            latest_data = DroneData.query.filter_by(
                device_id=device.id
            ).order_by(
                DroneData.timestamp.desc()
            ).first()
            
            if latest_data:
                status['latest_data'] = latest_data.to_dict()
            
            device_statuses.append(status)
        
        return device_statuses
    
    except Exception as e:
        logging.error(f"获取设备状态失败: {str(e)}")
        raise

def create_geofence_service(fence_data):
    """
    创建地理围栏
    
    :param fence_data: 围栏数据字典
    :return: 创建的围栏对象
    """
    try:
        # 验证围栏数据
        required_fields = ['name', 'coordinates', 'max_altitude']
        for field in required_fields:
            if field not in fence_data:
                raise ValueError(f"缺少必要字段: {field}")
        
        geofence = GeoFence(**fence_data)
        
        db.session.add(geofence)
        db.session.commit()
        
        logging.info(f"成功创建地理围栏: {geofence.name}")
        return geofence
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"创建地理围栏失败: {str(e)}")
        raise

def create_mission_service(mission_data):
    """
    创建飞行任务
    
    :param mission_data: 任务数据字典
    :return: 创建的任务对象
    """
    try:
        # 验证任务数据
        required_fields = ['device_id', 'waypoints', 'mission_type']
        for field in required_fields:
            if field not in mission_data:
                raise ValueError(f"缺少必要字段: {field}")
        
        mission = Mission(**mission_data)
        mission.status = 'pending'
        
        db.session.add(mission)
        db.session.commit()
        
        logging.info(f"成功创建飞行任务: {mission.id}")
        return mission
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"创建飞行任务失败: {str(e)}")
        raise

def get_battery_analytics_service(device_id=None, days=7):
    """
    获取电池使用分析
    
    :param device_id: 可选的设备ID
    :param days: 分析的天数
    :return: 电池使用分析数据
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = DroneData.query.filter(
            DroneData.timestamp.between(start_date, end_date)
        )
        
        if device_id:
            query = query.filter(DroneData.device_id == device_id)
        
        data = query.all()
        
        if not data:
            return {
                'avg_battery': 0,
                'min_battery': 0,
                'max_battery': 0,
                'battery_consumption_rate': 0
            }
        
        batteries = [d.battery for d in data]
        
        return {
            'avg_battery': sum(batteries) / len(batteries),
            'min_battery': min(batteries),
            'max_battery': max(batteries),
            'battery_consumption_rate': (max(batteries) - min(batteries)) / len(data)
        }
    
    except Exception as e:
        logging.error(f"获取电池分析失败: {str(e)}")
        raise

def perform_firmware_update_service(update_data):
    """
    执行固件更新
    
    :param update_data: 固件更新数据
    :return: 更新结果
    """
    try:
        device = DroneDevice.query.get(update_data['device_id'])
        
        if not device:
            raise ValueError("设备未找到")
        
        device.firmware_version = update_data['firmware_version']
        device.firmware_update_status = 'in_progress'
        
        db.session.commit()
        
        logging.info(f"设备 {device.id} 开始固件更新")
        return {
            'device_id': device.id,
            'new_version': device.firmware_version,
            'status': 'update_started'
        }
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"固件更新失败: {str(e)}")
        raise

def retrieve_flight_logs_service(params):
    """
    获取飞行日志
    
    :param params: 查询参数
    :return: 飞行日志列表
    """
    try:
        query = FlightLog.query
        
        if params.get('device_id'):
            query = query.filter_by(device_id=params['device_id'])
        
        if params.get('start_date'):
            query = query.filter(FlightLog.start_time >= params['start_date'])
        
        if params.get('end_date'):
            query = query.filter(FlightLog.end_time <= params['end_date'])
        
        logs = query.order_by(FlightLog.start_time.desc()).all()
        
        return [log.to_dict() for log in logs]
    
    except Exception as e:
        logging.error(f"检索飞行日志失败: {str(e)}")
        raise

def generate_performance_report_service(params):
    """
    生成性能报告
    
    :param params: 报告参数
    :return: 性能报告
    """
    try:
        device_id = params.get('device_id')
        period = params.get('period', 'monthly')
        
        end_date = datetime.utcnow()
        start_date = (
            end_date - timedelta(days=30) if period == 'monthly' 
            else end_date - timedelta(days=7)
        )
        
        query = DroneData.query
        if device_id:
            query = query.filter_by(device_id=device_id)
        
        data = query.filter(
            DroneData.timestamp.between(start_date, end_date)
        ).all()
        
        if not data:
            return {
                'total_flights': 0,
                'avg_speed': 0,
                'total_flight_time': 0
            }
        
        return {
            'total_flights': len(data),
            'avg_speed': sum(d.speed for d in data) / len(data),
            'total_flight_time': sum(
                d.flight_time if hasattr(d, 'flight_time') else 0 
                for d in data
            )
        }
    
    except Exception as e:
        logging.error(f"生成性能报告失败: {str(e)}")
        raise

def trigger_emergency_landing_service(data):
    """
    触发紧急降落
    
    :param data: 紧急降落数据
    :return: 紧急降落结果
    """
    try:
        device = DroneDevice.query.get(data['device_id'])
        
        if not device:
            raise ValueError("设备未找到")
        
        device.status = 'emergency_landing'
        
        # 记录紧急降落日志
        emergency_log = FlightLog(
            device_id=device.id,
            mission_type='emergency_landing',
            status='emergency'
        )
        
        db.session.add(emergency_log)
        db.session.commit()
        
        logging.warning(f"设备 {device.id} 触发紧急降落")
        
        return {
            'device_id': device.id,
            'status': 'emergency_landing_initiated',
            'log_id': emergency_log.id
        }
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"紧急降落失败: {str(e)}")
        raise
