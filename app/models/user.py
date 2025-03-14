from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """
        设置密码哈希
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        验证密码
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        转换为字典
        """
        return
