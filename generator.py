
import secrets
import hashlib
import json
import os
from typing import Dict, List

class UserManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.users: Dict[str, Dict] = {}

    def generate_username(self, prefix: str = 'user', start: int = 1, total: int = 1000) -> List[str]:
        """
        按照特定规律生成用户名
        
        :param prefix: 用户名前缀
        :param start: 起始编号
        :param total: 生成用户总数
        :return: 用户名列表
        """
        return [f"{prefix}{str(i).zfill(4)}" for i in range(start, start + total)]

    def hash_password(self, password: str) -> str:
        """
        使用 SHA-256 哈希密码
        
        :param password: 原始密码
        :return: 哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_users(self, total: int = 1000, roles: List[str] = None) -> Dict[str, Dict]:
        """
        生成用户数据
        
        :param total: 生成用户总数
        :param roles: 可选的角色列表
        :return: 用户字典
        """
        if roles is None:
            roles = ['user', 'editor', 'admin']
        
        usernames = self.generate_username(total=total)
        
        # 固定密码为 user123
        fixed_password = 'user123'
        hashed_password = self.hash_password(fixed_password)
        
        for username in usernames:
            # 根据用户名后几位确定角色
            role_index = int(username[-2:]) % len(roles)
            
            self.users[username] = {
                'password_hash': hashed_password,
                'role': roles[role_index],
                'raw_password': fixed_password  # 实际系统中不应保存
            }
        
        return self.users

    def save_users(self):
        """
        将用户数据保存到文件
        """
        # 创建 users 目录（如果不存在）
        os.makedirs('users', exist_ok=True)
        
        # 保存用户数据（排除原始密码）
        safe_users = {
            username: {
                'password_hash': user['password_hash'],
                'role': user['role']
            } for username, user in self.users.items()
        }
        
        with open(os.path.join('users', self.users_file), 'w', encoding='utf-8') as f:
            json.dump(safe_users, f, indent=2)
        
        # 单独保存初始密码（仅用于测试）
        passwords = {
            username: user['raw_password'] 
            for username, user in self.users.items()
        }
        
        with open(os.path.join('users', 'initial_passwords.json'), 'w', encoding='utf-8') as f:
            json.dump(passwords, f, indent=2)
        
        print(f"已生成 {len(self.users)} 个用户，所有用户密码均为 user123")

    def load_users(self):
        """
        从文件加载用户数据
        """
        try:
            with open(os.path.join('users', self.users_file), 'r', encoding='utf-8') as f:
                self.users = json.load(f)
            return self.users
        except FileNotFoundError:
            print("未找到用户文件")
            return {}

def main():
    # 创建用户管理器
    user_manager = UserManager()
    
    # 生成用户
    users = user_manager.generate_users(
        total=1000, 
        roles=['user', 'editor', 'admin']
    )
    
    # 保存用户
    user_manager.save_users()
    
    # 打印一些示例用户
    print("用户示例:")
    for i, (username, user_info) in enumerate(list(users.items())[:5], 1):
        print(f"{i}. 用户名: {username}")
        print(f"   角色: {user_info['role']}")
        print(f"   初始密码: user123\n")

if __name__ == '__main__':
    main()