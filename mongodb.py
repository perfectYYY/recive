# mongodb_tool.py
from __future__ import annotations
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
import threading
import traceback

class MongoDBDroneStorage:
    """MongoDB 无人机数据存储工具类"""
    
    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "drone_db",
        collection_name: str = "drone_states",
        buffer_size: int = 100
    ):
        """
        初始化 MongoDB 连接和存储配置
        
        参数:
            mongo_uri: MongoDB 连接字符串，默认为本地实例
            db_name: 数据库名称，默认为 `drone_db`
            collection_name: 集合名称，默认为 `drone_states`
            buffer_size: 批量写入的缓冲区大小，默认为 100 条
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.buffer_size = buffer_size
        self.buffer = []
        self.buffer_lock = threading.Lock()
        
        # 创建地理空间索引（推荐）
        self._ensure_index()

    def _ensure_index(self) -> None:
        """确保必要的数据库索引存在"""
        if "coordinates_2dsphere" not in self.collection.index_information():
            self.collection.create_index([("coordinates", "2dsphere")])

    def save(self, data: Dict[str, Any]) -> None:
        """
        保存单条数据（自动缓冲批量插入）
        
        参数:
            data: 包含无人机状态的字典，必须有以下字段：
                - timestamp (str/date)
                - coordinates (GeoJSON)
                - altitude (float)
                - speed (float)
                - battery_level (float)
                - wind_speed (float) [可选]
                - position (str)
        """
        try:
            # 数据校验
            required_fields = ["coordinates", "altitude", "speed", "battery_level", "position"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"缺失必填字段: {field}")

            # 转换时间戳
            if isinstance(data.get("timestamp"), datetime):
                data["timestamp"] = data["timestamp"].isoformat()

            # 添加数据到缓冲
            with self.buffer_lock:
                self.buffer.append(data)
                
                # 触发批量插入
                if len(self.buffer) >= self.buffer_size:
                    self._flush_buffer()

        except Exception as e:
            traceback.print_exc()
            print(f"数据缓存失败: {e}")

    def _flush_buffer(self) -> None:
        """执行批量插入并清空缓冲区"""
        try:
            if self.buffer:
                self.collection.insert_many(self.buffer)
                print(f"批量插入 {len(self.buffer)} 条数据成功")
                self.buffer.clear()
        except Exception as e:
            print(f"批量插入失败: {e}")

    def close(self) -> None:
        """关闭数据库连接（手动调用释放资源）"""
        self._flush_buffer()  # 确保写入剩余数据
        self.client.close()