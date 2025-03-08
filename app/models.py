from sqlalchemy import text  
from .extensions import db, ma  
from marshmallow import fields  
from datetime import datetime  

class DroneData(db.Model):  
    """  
    无人机数据模型  
    """  
    __tablename__ = 'drone_data'  
    
    id = db.Column(db.Integer, primary_key=True)  
    device_id = db.Column(db.String(50), nullable=False, index=True)  
    latitude = db.Column(db.Float, nullable=False)  
    longitude = db.Column(db.Float, nullable=False)  
    altitude = db.Column(db.Float, nullable=False)  
    speed = db.Column(db.Float, nullable=False)  
    battery = db.Column(db.Float, nullable=False)  
    status = db.Column(db.String(50), nullable=False)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))  

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
            'battery': self.battery,  
            'status': self.status,  
            'timestamp': self.timestamp.isoformat() if self.timestamp else None  
        }  

class DroneDataSchema(ma.SQLAlchemyAutoSchema):  
    """  
    数据序列化/反序列化架构  
    """  
    class Meta:  
        model = DroneData  
        load_instance = True  
        include_fk = True  

    timestamp = fields.DateTime('iso')  

class DroneDataPayload:  
    """  
    无人机数据载荷  
    """  
    def __init__(self, encrypted_data, device_id, signature):  
        self.encrypted_data = encrypted_data  
        self.device_id = device_id  
        self.signature = signature  

    def decrypt(self, encryption_key):  
        """  
        解密数据载荷  
        
        :param encryption_key: 解密密钥  
        :return: 解密后的数据字典  
        """  
        from cryptography.fernet import Fernet  
        
        try:  
            fernet = Fernet(encryption_key)  
            decrypted_bytes = fernet.decrypt(self.encrypted_data.encode())  
            return eval(decrypted_bytes.decode())  
        except Exception as e:  
            raise ValueError(f"解密失败: {str(e)}")