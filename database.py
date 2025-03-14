import sqlite3  

DATABASE = 'drone_data.db'  

def init_db():  
    """初始化数据库"""  
    with sqlite3.connect(DATABASE) as conn:  
        cursor = conn.cursor()  
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS drone_data (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                altitude REAL,  
                speed REAL,  
                coordinates TEXT,  
                battery_level REAL,  
                wind_speed REAL,  
                position TEXT  
            )  
        ''')  
        conn.commit()  

def insert_drone_data(data):  
    """插入无人机数据"""  
    with sqlite3.connect(DATABASE) as conn:  
        cursor = conn.cursor()  
        cursor.execute('''  
            INSERT INTO drone_data (altitude, speed, coordinates, battery_level, wind_speed, position)  
            VALUES (?, ?, ?, ?, ?, ?)  
        ''', (data['altitude'], data['speed'], data['coordinates'], data['battery_level'], data['wind_speed'], data['position']))  
        conn.commit()  