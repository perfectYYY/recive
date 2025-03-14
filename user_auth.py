import jwt  
import datetime  
import secrets  
import json  
import hashlib  

SECRET_KEY = secrets.token_hex(32)  # 秘钥，实际生产中应该是安全存储的环境变量  

class UserAuthenticator:  
    def __init__(self, users_file='users/users.json'):  
        self.users_file = users_file  
        self.users = self.load_users()  

    def load_users(self):  
        """从 JSON 文件加载用户数据"""  
        try:  
            with open(self.users_file, 'r', encoding='utf-8') as f:  
                users = json.load(f)  
                return users  
        except FileNotFoundError:  
            print("未找到用户文件，请先生成用户")  
            return {}  
        except json.JSONDecodeError:  
            print("用户文件解析错误")  
            return {}  

    def hash_password(self, password: str) -> str:  
        """使用 SHA-256 哈希密码"""  
        return hashlib.sha256(password.encode()).hexdigest()  

    def authenticate(self, username: str, password: str) -> dict:  
        """验证用户凭据"""  
        user = self.users.get(username)  
        if user and self.hash_password(password) == user['password_hash']:  
            return user  
        return None  

    def generate_token(self, username, role):  
        """生成 JWT token"""  
        payload = {  
            'username': username,  
            'role': role,  
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
        }  
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')  