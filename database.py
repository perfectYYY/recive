import hashlib  
import sqlite3  
import json  
import os  

DATABASE = 'drone_data.db'  

def get_db_connection():  
    """获取数据库连接"""  
    conn = sqlite3.connect(DATABASE)  
    conn.row_factory = sqlite3.Row  # 使结果可通过列名访问  
    return conn  

def init_db():  
    """初始化数据库"""  
    with sqlite3.connect(DATABASE) as conn:  
        cursor = conn.cursor()  
        
        # 无人机数据表  
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS drone_data (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                altitude REAL,  
                speed REAL,  
                coordinates TEXT,  
                battery_level REAL,  
                wind_speed REAL,  
                position TEXT,  
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP  
            )  
        ''')  
        
        # 无人机命令表  
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS drone_commands (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                command TEXT NOT NULL,  
                parameters TEXT,  
                status TEXT,  
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP  
            )  
        ''')  
        
        # 无人机日志表  
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS drone_logs (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                message TEXT NOT NULL,  
                type TEXT,  
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP  
            )  
        ''')  
        
        conn.commit()  
        print("数据库初始化完成")  

def verify_data_integrity(received_data, received_hash):  
    """验证接收到的数据完整性"""  
    # 将接收到的 JSON 数据（字典形式）转换为字符串，保证键的顺序一致  
    data_str = json.dumps(received_data, sort_keys=True)  

    # 计算接收到数据的哈希值  
    hash_object = hashlib.sha256(data_str.encode())  
    generated_hash = hash_object.hexdigest()  

    # 比较生成的哈希值与接收到的哈希值是否相同  
    if generated_hash == received_hash:  
        return True  
    else:  
        return False  

def insert_drone_data(data, received_hash=None):  
    """接收并插入无人机数据，同时验证数据完整性"""  
    # 如果提供了哈希值，则进行数据完整性验证  
    if received_hash and not verify_data_integrity(data, received_hash):  
        print("数据完整性验证失败！")  
        return None  
        
    try:  
        # 插入数据库  
        with sqlite3.connect(DATABASE) as conn:  
            cursor = conn.cursor()  
            cursor.execute('''  
                INSERT INTO drone_data (altitude, speed, coordinates, battery_level, wind_speed, position)  
                VALUES (?, ?, ?, ?, ?, ?)  
            ''', (  
                data.get('altitude', 0),   
                data.get('speed', 0),   
                data.get('coordinates', '0,0'),   
                data.get('battery_level', 0),   
                data.get('wind_speed', 0),   
                data.get('position', 'unknown')  
            ))  
            conn.commit()  
            return cursor.lastrowid  
    except Exception as e:  
        print(f"数据库插入错误: {e}")  
        raise  

def get_drone_data(limit=100):  
    """获取无人机数据记录"""  
    conn = get_db_connection()  
    cursor = conn.cursor()  
    cursor.execute('SELECT * FROM drone_data ORDER BY id DESC LIMIT ?', (limit,))  
    rows = cursor.fetchall()  
    conn.close()  
    
    # 确保行数据被正确转换为字典  
    result = []  
    for row in rows:  
        # 将sqlite3.Row对象转换为字典  
        row_dict = dict(row)  
        # 添加时间戳如果不存在  
        if 'timestamp' not in row_dict:  
            row_dict['timestamp'] = 'N/A'  
        result.append(row_dict)  
        
    return result   

def get_latest_drone_data():  
    """获取最新的无人机数据"""  
    conn = get_db_connection()  
    cursor = conn.cursor()  
    cursor.execute('SELECT * FROM drone_data ORDER BY id DESC LIMIT 1')  
    row = cursor.fetchone()  
    conn.close()  
    return dict(row) if row else None  

def record_command(command, parameters=None, status="pending"):  
    """记录发送的命令"""  
    with sqlite3.connect(DATABASE) as conn:  
        cursor = conn.cursor()  
        params_json = json.dumps(parameters) if parameters else None  
        cursor.execute('''  
            INSERT INTO drone_commands (command, parameters, status)  
            VALUES (?, ?, ?)  
        ''', (command, params_json, status))  
        conn.commit()  
        # 记录日志  
        log_message(f"已发送命令: {command}", "command")  
        return cursor.lastrowid  

def get_commands(limit=50):  
    """获取命令历史"""  
    conn = get_db_connection()  
    cursor = conn.cursor()  
    cursor.execute('SELECT * FROM drone_commands ORDER BY id DESC LIMIT ?', (limit,))  
    rows = cursor.fetchall()  
    conn.close()  
    return [dict(row) for row in rows]  

def log_message(message, type="info"):  
    """记录系统日志"""  
    with sqlite3.connect(DATABASE) as conn:  
        cursor = conn.cursor()  
        cursor.execute('''  
            INSERT INTO drone_logs (message, type)  
            VALUES (?, ?)  
        ''', (message, type))  
        conn.commit()  
        return cursor.lastrowid  

def get_logs(limit=100):  
    """获取系统日志"""  
    conn = get_db_connection()  
    cursor = conn.cursor()  
    cursor.execute('SELECT * FROM drone_logs ORDER BY id DESC LIMIT ?', (limit,))  
    rows = cursor.fetchall()  
    conn.close()  
    return [dict(row) for row in rows]  