import secrets  
import hashlib  
import json  
import os  
from typing import Dict, List  

class UserManager:  
    def __init__(self, users_file='users.json', passwords_file='initial_passwords.json'):  
        self.users_file = users_file  
        self.passwords_file = passwords_file  
        self.users: Dict[str, Dict] = {}  
        self.raw_passwords: Dict[str, str] = {}  

    def hash_password(self, password: str) -> str:  
        """  
        使用 SHA-256 哈希密码  
        
        :param password: 原始密码  
        :return: 哈希后的密码  
        """  
        return hashlib.sha256(password.encode()).hexdigest()  

    def add_specific_users(self, accounts: Dict[str, Dict]) -> Dict[str, Dict]:  
        """  
        添加指定的用户账号  
        
        :param accounts: 用户账号字典，格式为 {username: {"secret": password}}  
        :return: 更新后的用户字典  
        """  
        for username, info in accounts.items():  
            password = info["secret"]  
            hashed_password = self.hash_password(password)  
            
            self.users[username] = {  
                'password_hash': hashed_password,  
                'role': 'user'  
            }  
            
            # 保存原始密码（仅用于测试）  
            self.raw_passwords[username] = password  
        
        return self.users  

    def load_users(self):  
        """  
        从文件加载用户数据  
        """  
        # 加载用户数据  
        try:  
            users_path = os.path.join('users', self.users_file)  
            if os.path.exists(users_path):  
                with open(users_path, 'r', encoding='utf-8') as f:  
                    self.users = json.load(f)  
                print(f"已加载 {len(self.users)} 个现有用户")  
            else:  
                print("未找到用户文件，将创建新文件")  
                self.users = {}  
        except Exception as e:  
            print(f"加载用户数据时出错: {e}")  
            self.users = {}  

        # 加载原始密码数据  
        try:  
            passwords_path = os.path.join('users', self.passwords_file)  
            if os.path.exists(passwords_path):  
                with open(passwords_path, 'r', encoding='utf-8') as f:  
                    self.raw_passwords = json.load(f)  
                print(f"已加载 {len(self.raw_passwords)} 个密码数据")  
            else:  
                print("未找到密码文件，将创建新文件")  
                self.raw_passwords = {}  
        except Exception as e:  
            print(f"加载密码数据时出错: {e}")  
            self.raw_passwords = {}  

        return self.users  

    def save_users(self):  
        """  
        将用户数据保存到文件  
        """  
        # 创建 users 目录（如果不存在）  
        os.makedirs('users', exist_ok=True)  
        
        # 保存用户数据  
        with open(os.path.join('users', self.users_file), 'w', encoding='utf-8') as f:  
            json.dump(self.users, f, indent=2)  
        
        # 保存原始密码  
        with open(os.path.join('users', self.passwords_file), 'w', encoding='utf-8') as f:  
            json.dump(self.raw_passwords, f, indent=2)  
        
        print(f"已保存 {len(self.users)} 个用户数据")  

def main():  
    # 创建用户管理器  
    user_manager = UserManager()  
    
    # 加载现有用户数据  
    user_manager.load_users()  
    
    # 获取新增用户数量  
    original_user_count = len(user_manager.users)  
    
    # 添加指定账号  
    accounts = {  
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
    user_manager.add_specific_users(accounts)  
    
    # 保存合并后的用户数据  
    user_manager.save_users()  
    
    # 计算新增用户数量  
    added_users = len(user_manager.users) - original_user_count  
    
    print(f"\n新增了 {added_users} 个用户账号")  
    print(f"总计 {len(user_manager.users)} 个用户")  
    
    # 打印新增的账号示例  
    print("\n新增用户示例:")  
    for i, username in enumerate(accounts.keys(), 1):  
        print(f"{i}. 用户名: {username}")  
        print(f"   角色: user")  
        print(f"   密码: {accounts[username]['secret']}\n")  

if __name__ == '__main__':  
    main()  