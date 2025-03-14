from app.extensions import db
from datetime import datetime
import enum

class DeviceStatusEnum(enum.Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    MAINTENANCE = 'maintenance'
    ERROR = 'error'
    EMERGENCY_LANDING = 'emergency_landing'

class MissionStatusEnum(enum.Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    FAILED = 'failed'

class DroneDevice(db.Model):
    """
    无人机设备模型
    """
    __tablename__ = 'drone_devices'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    
    status = db.Column(
        db.Enum(DeviceStatusEnum), 
        default=DeviceStatusEnum.INACTIVE
    )
    
    firmware_version = db.Column(db.String(50))
    last_maintenance_date = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    flight_logs = db.relationship('FlightLog', back_populates='device')
    mission_logs = db.relationship('Mission', back_populates='device')
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'model': self.model,
            'serial_number': self.serial_number,
            'status': self.status.value,
            'firmware_version': self.firmware_version,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class DroneData(db.Model):
    """
    无人机实时数据模型
    """
    __tablename__ = 'drone_data'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('drone_devices.id'))
    
    # 位置信息
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    
    # 飞行状态
    speed = db.Column(db.Float, default=0)
    direction = db.Column(db.Float)
    
    # 电池信息
    battery = db.Column(db.Float, nullable=False)
    battery_voltage = db.Column(db.Float)
    
    # 时间戳
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    device = db.relationship('DroneDevice', backref='data_logs')
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': self.id,
            'device_id': self.device_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'direction': self.direction,
            'battery': self.battery,
            'battery_voltage': self.battery_voltage,
            'timestamp': self.timestamp.isoformat()
        }

class GeoFence(db.Model):
    """
    地理围栏模型
    """
    __tablename__ = 'geofences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # 坐标存储为JSON
    coordinates = db.Column(db.JSON, nullable=False)
    max_altitude = db.Column(db.Float, default=120)
    min_altitude = db.Column(db.Float, default=0)
    
    # 启用状态
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'coordinates': self.coordinates,
            'max_altitude': self.max_altitude,
            'min_altitude': self.min_altitude,
            'is_active': self.is_active
        }

class Mission(db.Model):
    """
    无人机飞行任务模型
    """
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('drone_devices.id'))
    
    name = db.Column(db.String(100))
    mission_type = db.Column(db.String(50), nullable=False)
    
    # 航点存储为JSON
    waypoints = db.Column(db.JSON, nullable=False)
    
    status = db.Column(
        db.Enum(MissionStatusEnum), 
        default=MissionStatusEnum.PENDING
    )
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # 关联关系
    device = db.relationship('DroneDevice', back_populates='mission_logs')
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'mission_type': self.mission_type,
            'waypoints': self.waypoints,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None
        }

class FlightLog(db.Model):
    """
    飞行日志模型
    """
    __tablename__ = 'flight_logs'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('drone_devices.id'))
    
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=True)
    
    mission_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # 飞行数据摘要
    total_distance = db.Column(db.Float, default=0)
    max_altitude = db.Column(db.Float, default=0)
    avg_speed = db.Column(db.Float, default=0)
    
    # 关联关系
    device = db.relationship('DroneDevice', back_populates='flight_logs')
    mission = db.relationship('Mission')
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': self.id,
            'device_id': self.device_id,
            'mission_id': self.mission_id,
            'mission_type': self.mission_type,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_distance': self.total_distance,
            'max_altitude': self.max_altitude,
            'avg_speed': self.avg_speed
        }
 